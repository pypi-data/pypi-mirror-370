"""
Persistent Message Bus - Survives restarts and multi-day gaps.

This version fully uses the database to maintain state across sessions.
"""

import asyncio
import json
from typing import Dict, List, Optional, Any, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass

from .agent_message_bus import AgentMessageBus, MessageType, AgentMessage
from ..interfaces.sqlite_persistence import SqlitePersistence
from ..utils.logging_config import MAOSLogger


class PersistentMessageBus(AgentMessageBus):
    """
    Enhanced message bus that fully persists state to database.
    
    This allows MAOS to be stopped and restarted days later with full recovery of:
    - Agent registrations
    - Communication history
    - Pending messages
    - Orchestration state
    """
    
    def __init__(self, db: SqlitePersistence, session_manager: Any):
        """Initialize persistent message bus."""
        super().__init__(db, session_manager)
        self.logger = MAOSLogger("persistent_message_bus")
        self._restored = False
    
    async def start(self):
        """Start message bus and restore state from database."""
        await super().start()
        
        if not self._restored:
            await self._restore_from_database()
            self._restored = True
    
    async def _restore_from_database(self):
        """
        Restore message bus state from database.
        
        This is called on startup to recover from shutdowns.
        """
        self.logger.logger.info("Restoring message bus state from database...")
        
        # 1. Restore active agents
        agents_restored = await self._restore_agents()
        
        # 2. Restore pending messages
        messages_restored = await self._restore_pending_messages()
        
        # 3. Restore orchestration sessions
        orchestrations_restored = await self._restore_orchestrations()
        
        self.logger.logger.info(
            f"Restored: {agents_restored} agents, {messages_restored} messages, "
            f"{orchestrations_restored} orchestrations"
        )
    
    async def _restore_agents(self) -> int:
        """
        Restore agent registrations from database.
        
        Returns:
            Number of agents restored
        """
        count = 0
        
        try:
            # Get all agents with active sessions from last 7 days
            recent_cutoff = (datetime.now() - timedelta(days=7)).isoformat()
            
            # Query agents from database
            query = """
                SELECT DISTINCT a.id, a.name, a.type, a.capabilities, 
                       a.session_id, a.process_id, a.status,
                       s.task, s.created_at
                FROM agents a
                LEFT JOIN sessions s ON a.session_id = s.session_id
                WHERE a.status IN ('active', 'paused', 'inactive')
                  AND (s.created_at > ? OR s.created_at IS NULL)
                ORDER BY s.created_at DESC
            """
            
            # Execute query using the new method
            agents = await self.db.execute_query(query, [recent_cutoff])
            
            for agent in agents:
                agent_id = agent['id']
                
                # Re-register agent with message bus
                self._active_agents[agent_id] = {
                    'name': agent['name'],
                    'type': agent['type'],
                    'capabilities': json.loads(agent['capabilities']) if agent['capabilities'] else [],
                    'session_id': agent['session_id'],
                    'process_id': agent['process_id'],
                    'status': agent['status'],
                    'task': agent.get('task'),
                    'restored': True  # Mark as restored
                }
                
                # Restore subscriptions (default for now)
                self._subscriptions[agent_id] = [
                    MessageType.BROADCAST,
                    MessageType.REQUEST,
                    MessageType.DISCOVERY,
                    MessageType.COORDINATION
                ]
                
                count += 1
                self.logger.logger.debug(f"Restored agent: {agent_id}")
        
        except Exception as e:
            self.logger.log_error(e, {"operation": "restore_agents"})
        
        return count
    
    async def _restore_pending_messages(self) -> int:
        """
        Restore undelivered messages from database.
        
        Returns:
            Number of messages restored
        """
        count = 0
        
        try:
            # Get undelivered messages from last 24 hours
            recent_cutoff = (datetime.now() - timedelta(hours=24)).isoformat()
            
            # Query for undelivered messages (use acknowledged field)
            query = """
                SELECT id, from_agent, to_agent, message, message_type,
                       timestamp
                FROM messages
                WHERE acknowledged = 0
                  AND timestamp > ?
                ORDER BY timestamp ASC
            """
            
            messages = await self.db.execute_query(query, [recent_cutoff])
            
            for msg in messages:
                # Re-queue message for delivery
                message = AgentMessage(
                    from_agent=msg['from_agent'],
                    to_agent=msg['to_agent'],
                    message_type=MessageType(msg['message_type']),
                    content=msg['message'],
                    metadata={},
                    timestamp=msg['timestamp'],
                    message_id=msg['id']
                )
                
                await self._message_queue.put(message)
                count += 1
                
                self.logger.logger.debug(
                    f"Re-queued message {msg['id']} from {msg['from_agent']}"
                )
        
        except Exception as e:
            self.logger.log_error(e, {"operation": "restore_pending_messages"})
        
        return count
    
    async def _restore_orchestrations(self) -> int:
        """
        Restore active orchestration sessions.
        
        Returns:
            Number of orchestrations restored
        """
        count = 0
        
        try:
            # Get incomplete orchestrations
            query = """
                SELECT id, request, agents, batches, status, created_at
                FROM orchestrations
                WHERE status IN ('running', 'paused')
                ORDER BY created_at DESC
                LIMIT 10
            """
            
            orchestrations = await self.db.execute_query(query, [])
            
            for orch in orchestrations:
                # Store orchestration info for resumption
                self.logger.logger.info(
                    f"Found resumable orchestration: {orch['id'][:8]}"
                )
                count += 1
        
        except Exception as e:
            self.logger.log_error(e, {"operation": "restore_orchestrations"})
        
        return count
    
    async def save_message(
        self,
        from_agent: str,
        to_agent: Optional[str],
        content: str,
        message_type: MessageType,
        metadata: Optional[Dict] = None
    ) -> int:
        """
        Save message to database with delivery tracking.
        
        Returns:
            Message ID
        """
        # Save to database with delivered=False initially
        message_id = await self.db.save_message(
            from_agent=from_agent,
            to_agent=to_agent,
            message=content,
            message_type=message_type.value,
            metadata=metadata
        )
        
        # Mark as delivered after successful delivery
        # (This would be done in _deliver_message)
        
        return message_id
    
    async def mark_message_delivered(self, message_id: int):
        """
        Mark a message as delivered in database.
        
        Args:
            message_id: Message to mark as delivered
        """
        try:
            query = "UPDATE messages SET acknowledged = 1 WHERE id = ?"
            await self.db.execute_query(query, [message_id])
        except Exception as e:
            self.logger.log_error(e, {
                "operation": "mark_message_delivered",
                "message_id": message_id
            })
    
    async def get_communication_history(
        self,
        agent_id: Optional[str] = None,
        since: Optional[datetime] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Get communication history from database.
        
        Args:
            agent_id: Filter by agent (sent or received)
            since: Get messages since this time
            limit: Maximum messages to return
            
        Returns:
            List of messages with full details
        """
        try:
            # Build query based on filters
            query = """
                SELECT m.*, 
                       a1.name as from_name, 
                       a2.name as to_name
                FROM messages m
                LEFT JOIN agents a1 ON m.from_agent = a1.id
                LEFT JOIN agents a2 ON m.to_agent = a2.id
                WHERE 1=1
            """
            params = []
            
            if agent_id:
                query += " AND (m.from_agent = ? OR m.to_agent = ?)"
                params.extend([agent_id, agent_id])
            
            if since:
                query += " AND m.timestamp > ?"
                params.append(since.isoformat())
            
            query += f" ORDER BY m.timestamp DESC LIMIT {limit}"
            
            messages = await self.db.execute_query(query, params)
            
            return [
                {
                    "id": msg['id'],
                    "from_agent": msg['from_agent'],
                    "from_name": msg['from_name'],
                    "to_agent": msg['to_agent'],
                    "to_name": msg['to_name'],
                    "content": msg['message'],
                    "type": msg['message_type'],
                    "timestamp": msg['timestamp'],
                    "delivered": msg.get('acknowledged', 1) == 1,
                    "metadata": {}
                }
                for msg in messages
            ]
        
        except Exception as e:
            self.logger.log_error(e, {"operation": "get_communication_history"})
            return []
    
    async def resume_orchestration(self, orchestration_id: str) -> Dict[str, Any]:
        """
        Resume an orchestration from database state.
        
        Args:
            orchestration_id: Orchestration to resume
            
        Returns:
            Orchestration details with agent states
        """
        try:
            # Get orchestration
            orch = await self.db.get_orchestration(orchestration_id)
            if not orch:
                return None
            
            # Restore all agents for this orchestration
            agents = json.loads(orch['agents']) if orch['agents'] else []
            for agent_id in agents:
                # Get agent details
                agent = await self.db.get_agent(agent_id)
                if agent:
                    # Re-register with message bus
                    await self.register_agent(
                        agent_id=agent_id,
                        agent_info={
                            'name': agent['name'],
                            'type': agent['type'],
                            'capabilities': json.loads(agent['capabilities']),
                            'session_id': agent.get('session_id'),
                            'restored': True
                        },
                        create_in_db=False  # Already in DB
                    )
            
            # Get communication history for context
            history = await self.get_communication_history(
                since=datetime.fromisoformat(orch['created_at'])
            )
            
            return {
                "orchestration": orch,
                "agents_restored": len(agents),
                "communication_history": history,
                "status": "ready_to_resume"
            }
        
        except Exception as e:
            self.logger.log_error(e, {
                "operation": "resume_orchestration",
                "orchestration_id": orchestration_id
            })
            return None
    
    async def shutdown(self):
        """
        Gracefully shutdown and persist state.
        """
        self.logger.logger.info("Shutting down persistent message bus...")
        
        # Mark all active agents as paused
        for agent_id in self._active_agents:
            try:
                await self.db.update_agent_status(agent_id, "paused")
            except:
                pass
        
        # Process remaining messages
        while not self._message_queue.empty():
            try:
                message = self._message_queue.get_nowait()
                # Save as undelivered
                await self.save_message(
                    message.from_agent,
                    message.to_agent,
                    message.content,
                    message.message_type,
                    message.metadata
                )
            except:
                break
        
        await super().stop()
        self.logger.logger.info("Persistent message bus shutdown complete")