"""
Redis Cluster Manager for distributed state management.

Handles Redis cluster operations, failover, and load balancing.
"""

import asyncio
import random
import time
from typing import Dict, List, Optional, Any
from uuid import uuid4
import aioredis
from aioredis import Redis
from aioredis.exceptions import RedisError, ConnectionError, ClusterError

from ...maos.utils.logging_config import MAOSLogger
from ...maos.utils.exceptions import MAOSError


class RedisClusterManager:
    """
    Manages Redis cluster connections with automatic failover and load balancing.
    """
    
    def __init__(
        self,
        redis_urls: List[str],
        max_retries: int = 3,
        retry_delay: float = 0.1,
        connection_pool_settings: Dict[str, Any] = None,
        health_check_interval: int = 30
    ):
        """Initialize Redis cluster manager."""
        self.redis_urls = redis_urls
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.connection_pool_settings = connection_pool_settings or {}
        self.health_check_interval = health_check_interval
        
        self.logger = MAOSLogger("redis_cluster_manager", str(uuid4()))
        
        # Connection pools
        self.connections: Dict[str, Redis] = {}
        self.connection_health: Dict[str, bool] = {}
        self.primary_url: Optional[str] = None
        
        # Performance tracking
        self.node_performance: Dict[str, Dict[str, float]] = {}
        
        # Background tasks
        self._health_check_task: Optional[asyncio.Task] = None
        self._shutdown_event = asyncio.Event()
    
    async def initialize(self) -> None:
        """Initialize all cluster connections."""
        self.logger.logger.info("Initializing Redis cluster connections")
        
        # Initialize connections to all nodes
        for url in self.redis_urls:
            try:
                redis_conn = aioredis.from_url(
                    url,
                    **self.connection_pool_settings
                )
                
                # Test connection
                await redis_conn.ping()
                
                self.connections[url] = redis_conn
                self.connection_health[url] = True
                self.node_performance[url] = {
                    'avg_latency_ms': 0.0,
                    'success_rate': 100.0,
                    'total_requests': 0,
                    'failed_requests': 0
                }
                
                self.logger.logger.info(f"Connected to Redis node: {url}")
                
            except Exception as e:
                self.logger.log_error(e, {
                    'operation': 'initialize_connection',
                    'url': url
                })
                self.connection_health[url] = False
        
        if not self.connections:
            raise MAOSError("Failed to connect to any Redis nodes")
        
        # Select primary connection
        await self._select_primary()
        
        # Start health check task
        self._health_check_task = asyncio.create_task(self._health_check_loop())
        
        self.logger.logger.info(
            f"Redis cluster initialized with {len(self.connections)} nodes",
            extra={
                'primary_url': self.primary_url,
                'total_nodes': len(self.redis_urls),
                'healthy_nodes': sum(self.connection_health.values())
            }
        )
    
    async def _select_primary(self) -> None:
        """Select the primary connection based on performance."""
        if not self.connections:
            return
        
        # For initial selection, just pick the first healthy connection
        for url, is_healthy in self.connection_health.items():
            if is_healthy and url in self.connections:
                self.primary_url = url
                break
        
        if not self.primary_url:
            # Fallback to any available connection
            self.primary_url = next(iter(self.connections.keys()))
        
        self.logger.logger.info(f"Selected primary Redis node: {self.primary_url}")
    
    def get_primary_connection(self) -> Redis:
        """Get the primary Redis connection."""
        if not self.primary_url or self.primary_url not in self.connections:
            raise MAOSError("No primary Redis connection available")
        
        return self.connections[self.primary_url]
    
    def get_replica_connection(self) -> Optional[Redis]:
        """Get a replica connection for read operations."""
        # Filter out primary and get healthy replicas
        replica_urls = [
            url for url, is_healthy in self.connection_health.items()
            if is_healthy and url != self.primary_url and url in self.connections
        ]
        
        if not replica_urls:
            return None
        
        # Select replica based on performance
        best_replica_url = min(
            replica_urls,
            key=lambda url: self.node_performance[url]['avg_latency_ms']
        )
        
        return self.connections[best_replica_url]
    
    def get_random_connection(self) -> Redis:
        """Get a random healthy connection for load balancing."""
        healthy_urls = [
            url for url, is_healthy in self.connection_health.items()
            if is_healthy and url in self.connections
        ]
        
        if not healthy_urls:
            raise MAOSError("No healthy Redis connections available")
        
        random_url = random.choice(healthy_urls)
        return self.connections[random_url]
    
    async def execute_with_failover(
        self,
        operation_func,
        *args,
        prefer_primary: bool = False,
        **kwargs
    ) -> Any:
        """
        Execute operation with automatic failover.
        
        Args:
            operation_func: Redis operation to execute
            prefer_primary: Whether to prefer primary node
            *args, **kwargs: Arguments for the operation
            
        Returns:
            Operation result
        """
        # Determine connection preference
        if prefer_primary:
            connections_to_try = [self.get_primary_connection()]
            connections_to_try.extend([
                conn for url, conn in self.connections.items()
                if url != self.primary_url and self.connection_health[url]
            ])
        else:
            # Try replica first, then primary, then others
            replica_conn = self.get_replica_connection()
            if replica_conn:
                connections_to_try = [replica_conn, self.get_primary_connection()]
            else:
                connections_to_try = [self.get_primary_connection()]
            
            # Add remaining healthy connections
            connections_to_try.extend([
                conn for url, conn in self.connections.items()
                if conn not in connections_to_try and self.connection_health[url]
            ])
        
        last_exception = None
        
        for i, connection in enumerate(connections_to_try):
            try:
                start_time = time.time()
                
                # Execute operation
                result = await operation_func(connection, *args, **kwargs)
                
                # Record performance
                latency_ms = (time.time() - start_time) * 1000
                await self._record_performance(connection, latency_ms, success=True)
                
                return result
                
            except (ConnectionError, RedisError) as e:
                last_exception = e
                
                # Record performance
                await self._record_performance(connection, 0, success=False)
                
                # Mark connection as unhealthy
                connection_url = self._get_connection_url(connection)
                if connection_url:
                    self.connection_health[connection_url] = False
                
                self.logger.log_error(e, {
                    'operation': 'execute_with_failover',
                    'attempt': i + 1,
                    'connection_url': connection_url
                })
                
                # Try next connection if available
                if i < len(connections_to_try) - 1:
                    await asyncio.sleep(self.retry_delay * (i + 1))
                    continue
            
            except Exception as e:
                # Non-connection related error, don't retry
                self.logger.log_error(e, {
                    'operation': 'execute_with_failover',
                    'error_type': 'non_connection_error'
                })
                raise
        
        # All connections failed
        raise MAOSError(f"All Redis connections failed. Last error: {last_exception}")
    
    def _get_connection_url(self, connection: Redis) -> Optional[str]:
        """Get URL for a connection object."""
        for url, conn in self.connections.items():
            if conn is connection:
                return url
        return None
    
    async def _record_performance(
        self,
        connection: Redis,
        latency_ms: float,
        success: bool
    ) -> None:
        """Record performance metrics for a connection."""
        connection_url = self._get_connection_url(connection)
        if not connection_url or connection_url not in self.node_performance:
            return
        
        perf = self.node_performance[connection_url]
        perf['total_requests'] += 1
        
        if success:
            # Update average latency (exponential moving average)
            alpha = 0.1
            perf['avg_latency_ms'] = (
                alpha * latency_ms + (1 - alpha) * perf['avg_latency_ms']
            )
        else:
            perf['failed_requests'] += 1
        
        # Update success rate
        if perf['total_requests'] > 0:
            perf['success_rate'] = (
                (perf['total_requests'] - perf['failed_requests']) / 
                perf['total_requests'] * 100
            )
    
    async def health_check(self) -> Dict[str, bool]:
        """Check health of all connections."""
        health_status = {}
        
        for url, connection in self.connections.items():
            try:
                await connection.ping()
                health_status[url] = True
                self.connection_health[url] = True
                
            except Exception as e:
                health_status[url] = False
                self.connection_health[url] = False
                
                self.logger.log_error(e, {
                    'operation': 'health_check',
                    'url': url
                })
        
        # Re-select primary if current primary is unhealthy
        if (self.primary_url and 
            not self.connection_health.get(self.primary_url, False)):
            await self._select_primary()
        
        return health_status
    
    async def get_cluster_status(self) -> Dict[str, Any]:
        """Get comprehensive cluster status."""
        health_status = await self.health_check()
        
        return {
            'mode': 'cluster',
            'total_nodes': len(self.redis_urls),
            'healthy_nodes': sum(health_status.values()),
            'unhealthy_nodes': len(health_status) - sum(health_status.values()),
            'primary_url': self.primary_url,
            'node_health': health_status,
            'node_performance': self.node_performance,
            'connections_available': len(self.connections)
        }
    
    async def get_cluster_info(self) -> Dict[str, Any]:
        """Get detailed cluster information."""
        cluster_info = {}
        
        for url, connection in self.connections.items():
            try:
                info = await connection.info()
                cluster_info[url] = {
                    'redis_version': info.get('redis_version', 'unknown'),
                    'used_memory': info.get('used_memory', 0),
                    'used_memory_human': info.get('used_memory_human', '0B'),
                    'connected_clients': info.get('connected_clients', 0),
                    'total_commands_processed': info.get('total_commands_processed', 0),
                    'keyspace_hits': info.get('keyspace_hits', 0),
                    'keyspace_misses': info.get('keyspace_misses', 0),
                    'uptime_in_seconds': info.get('uptime_in_seconds', 0)
                }
                
            except Exception as e:
                cluster_info[url] = {
                    'error': str(e),
                    'healthy': False
                }
        
        return cluster_info
    
    async def rebalance_load(self) -> None:
        """Rebalance load across cluster nodes."""
        # Sort nodes by performance
        sorted_nodes = sorted(
            self.node_performance.items(),
            key=lambda x: (x[1]['avg_latency_ms'], -x[1]['success_rate'])
        )
        
        # Select new primary if needed
        current_primary_perf = self.node_performance.get(self.primary_url, {})
        best_node_url = sorted_nodes[0][0]
        
        # Switch primary if significant performance difference
        if (best_node_url != self.primary_url and
            self.connection_health.get(best_node_url, False)):
            
            best_latency = sorted_nodes[0][1]['avg_latency_ms']
            current_latency = current_primary_perf.get('avg_latency_ms', float('inf'))
            
            # Switch if best node is significantly better (>20% improvement)
            if current_latency > best_latency * 1.2:
                old_primary = self.primary_url
                self.primary_url = best_node_url
                
                self.logger.logger.info(
                    f"Rebalanced primary from {old_primary} to {best_node_url}",
                    extra={
                        'old_latency_ms': current_latency,
                        'new_latency_ms': best_latency
                    }
                )
    
    async def _health_check_loop(self) -> None:
        """Background task for periodic health checks."""
        while not self._shutdown_event.is_set():
            try:
                await asyncio.sleep(self.health_check_interval)
                
                # Perform health check
                await self.health_check()
                
                # Rebalance load if needed
                await self.rebalance_load()
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.log_error(e, {'operation': 'health_check_loop'})
    
    async def add_node(self, redis_url: str) -> bool:
        """Add a new node to the cluster."""
        if redis_url in self.connections:
            return True
        
        try:
            redis_conn = aioredis.from_url(
                redis_url,
                **self.connection_pool_settings
            )
            
            # Test connection
            await redis_conn.ping()
            
            self.connections[redis_url] = redis_conn
            self.connection_health[redis_url] = True
            self.node_performance[redis_url] = {
                'avg_latency_ms': 0.0,
                'success_rate': 100.0,
                'total_requests': 0,
                'failed_requests': 0
            }
            
            self.logger.logger.info(f"Added Redis node to cluster: {redis_url}")
            return True
            
        except Exception as e:
            self.logger.log_error(e, {
                'operation': 'add_node',
                'url': redis_url
            })
            return False
    
    async def remove_node(self, redis_url: str) -> bool:
        """Remove a node from the cluster."""
        if redis_url not in self.connections:
            return True
        
        try:
            # Close connection
            await self.connections[redis_url].close()
            
            # Remove from tracking
            del self.connections[redis_url]
            del self.connection_health[redis_url]
            del self.node_performance[redis_url]
            
            # Select new primary if needed
            if redis_url == self.primary_url:
                await self._select_primary()
            
            self.logger.logger.info(f"Removed Redis node from cluster: {redis_url}")
            return True
            
        except Exception as e:
            self.logger.log_error(e, {
                'operation': 'remove_node',
                'url': redis_url
            })
            return False
    
    async def shutdown(self) -> None:
        """Shutdown cluster manager."""
        self.logger.logger.info("Shutting down Redis cluster manager")
        
        # Signal shutdown
        self._shutdown_event.set()
        
        # Cancel health check task
        if self._health_check_task:
            self._health_check_task.cancel()
            try:
                await self._health_check_task
            except asyncio.CancelledError:
                pass
        
        # Close all connections
        for url, connection in self.connections.items():
            try:
                await connection.close()
            except Exception as e:
                self.logger.log_error(e, {
                    'operation': 'shutdown_connection',
                    'url': url
                })
        
        self.connections.clear()
        self.connection_health.clear()
        self.node_performance.clear()
        
        self.logger.logger.info("Redis cluster manager shutdown completed")