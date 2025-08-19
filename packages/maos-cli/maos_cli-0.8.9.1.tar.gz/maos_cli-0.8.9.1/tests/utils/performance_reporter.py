"""
Performance reporting and regression detection utilities.
"""

import json
import sqlite3
import statistics
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns


class PerformanceReporter:
    """Generate comprehensive performance reports with trend analysis."""
    
    def __init__(self, results_db_path: str = "tests/performance_results.db"):
        self.db_path = Path(results_db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_database()
    
    def _init_database(self):
        """Initialize SQLite database for performance results."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS performance_results (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    test_name TEXT NOT NULL,
                    git_commit TEXT,
                    branch TEXT,
                    environment TEXT,
                    metrics TEXT NOT NULL,
                    tags TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_test_name_timestamp 
                ON performance_results (test_name, timestamp)
            """)
    
    def store_result(
        self, 
        test_name: str, 
        metrics: Dict[str, Any], 
        git_commit: str = None,
        branch: str = None,
        environment: str = "test",
        tags: List[str] = None
    ):
        """Store performance test results."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO performance_results 
                (timestamp, test_name, git_commit, branch, environment, metrics, tags)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                datetime.utcnow().isoformat(),
                test_name,
                git_commit,
                branch,
                environment,
                json.dumps(metrics),
                json.dumps(tags or [])
            ))
    
    def get_results(
        self, 
        test_name: str = None, 
        days_back: int = 30,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Retrieve performance results."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            
            query = """
                SELECT * FROM performance_results 
                WHERE timestamp >= ? 
            """
            params = [(datetime.utcnow() - timedelta(days=days_back)).isoformat()]
            
            if test_name:
                query += " AND test_name = ?"
                params.append(test_name)
            
            query += " ORDER BY timestamp DESC LIMIT ?"
            params.append(limit)
            
            rows = conn.execute(query, params).fetchall()
            
            results = []
            for row in rows:
                result = dict(row)
                result['metrics'] = json.loads(result['metrics'])
                result['tags'] = json.loads(result['tags'] or '[]')
                results.append(result)
            
            return results
    
    def detect_regression(
        self, 
        test_name: str, 
        metric_name: str,
        threshold_percent: float = 10.0,
        baseline_days: int = 7
    ) -> Dict[str, Any]:
        """Detect performance regressions."""
        results = self.get_results(test_name, days_back=30)
        
        if len(results) < 2:
            return {"status": "insufficient_data", "message": "Need at least 2 data points"}
        
        # Get recent values and baseline
        recent_results = results[:3]  # Last 3 runs
        baseline_results = [
            r for r in results 
            if (datetime.utcnow() - datetime.fromisoformat(r['timestamp'])).days >= baseline_days
        ][:10]  # Up to 10 baseline points
        
        if not baseline_results:
            return {"status": "no_baseline", "message": "No baseline data available"}
        
        # Extract metric values
        recent_values = [
            r['metrics'].get(metric_name) 
            for r in recent_results 
            if metric_name in r['metrics']
        ]
        
        baseline_values = [
            r['metrics'].get(metric_name) 
            for r in baseline_results 
            if metric_name in r['metrics']
        ]
        
        if not recent_values or not baseline_values:
            return {"status": "missing_metric", "message": f"Metric {metric_name} not found"}
        
        # Calculate statistics
        recent_avg = statistics.mean(recent_values)
        baseline_avg = statistics.mean(baseline_values)
        baseline_std = statistics.stdev(baseline_values) if len(baseline_values) > 1 else 0
        
        # Calculate percentage change
        percent_change = ((recent_avg - baseline_avg) / baseline_avg) * 100
        
        # Determine regression status
        is_regression = abs(percent_change) > threshold_percent
        
        # Check if change is statistically significant (basic check)
        significance_threshold = 2 * baseline_std  # 2 standard deviations
        is_significant = abs(recent_avg - baseline_avg) > significance_threshold
        
        return {
            "status": "regression_detected" if is_regression else "no_regression",
            "metric_name": metric_name,
            "recent_average": recent_avg,
            "baseline_average": baseline_avg,
            "percent_change": percent_change,
            "is_statistically_significant": is_significant,
            "threshold_percent": threshold_percent,
            "recent_values": recent_values,
            "baseline_values": baseline_values
        }
    
    def generate_trend_report(self, test_name: str, days_back: int = 30) -> Dict[str, Any]:
        """Generate trend analysis report."""
        results = self.get_results(test_name, days_back)
        
        if not results:
            return {"error": "No data available"}
        
        # Extract all available metrics
        all_metrics = set()
        for result in results:
            all_metrics.update(result['metrics'].keys())
        
        trends = {}
        for metric in all_metrics:
            values = []
            timestamps = []
            
            for result in results:
                if metric in result['metrics']:
                    values.append(result['metrics'][metric])
                    timestamps.append(datetime.fromisoformat(result['timestamp']))
            
            if len(values) >= 3:  # Need at least 3 points for trend
                # Simple linear trend calculation
                x_vals = [(ts - timestamps[0]).total_seconds() for ts in timestamps]
                if len(set(x_vals)) > 1:  # Avoid division by zero
                    slope = self._calculate_slope(x_vals, values)
                    
                    trends[metric] = {
                        "values": values,
                        "timestamps": [ts.isoformat() for ts in timestamps],
                        "trend": "increasing" if slope > 0.01 else "decreasing" if slope < -0.01 else "stable",
                        "slope": slope,
                        "min_value": min(values),
                        "max_value": max(values),
                        "avg_value": statistics.mean(values),
                        "std_dev": statistics.stdev(values) if len(values) > 1 else 0
                    }
        
        return {
            "test_name": test_name,
            "period_days": days_back,
            "total_runs": len(results),
            "trends": trends,
            "generated_at": datetime.utcnow().isoformat()
        }
    
    def _calculate_slope(self, x_values: List[float], y_values: List[float]) -> float:
        """Calculate linear regression slope."""
        if len(x_values) != len(y_values) or len(x_values) < 2:
            return 0.0
        
        n = len(x_values)
        sum_x = sum(x_values)
        sum_y = sum(y_values)
        sum_xy = sum(x * y for x, y in zip(x_values, y_values))
        sum_x2 = sum(x * x for x in x_values)
        
        # Linear regression slope formula
        denominator = n * sum_x2 - sum_x * sum_x
        if abs(denominator) < 1e-10:  # Avoid division by zero
            return 0.0
        
        slope = (n * sum_xy - sum_x * sum_y) / denominator
        return slope
    
    def generate_performance_charts(
        self, 
        test_name: str, 
        output_dir: str = "tests/performance_charts",
        days_back: int = 30
    ):
        """Generate performance visualization charts."""
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        results = self.get_results(test_name, days_back)
        if not results:
            print(f"No results found for {test_name}")
            return
        
        # Prepare data for plotting
        df_data = []
        for result in results:
            base_data = {
                'timestamp': result['timestamp'],
                'git_commit': result['git_commit'],
                'branch': result['branch']
            }
            
            for metric, value in result['metrics'].items():
                row = base_data.copy()
                row['metric'] = metric
                row['value'] = value
                df_data.append(row)
        
        if not df_data:
            print(f"No metric data found for {test_name}")
            return
        
        df = pd.DataFrame(df_data)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        # Create visualizations
        plt.style.use('seaborn-v0_8')
        
        # Get unique metrics
        metrics = df['metric'].unique()
        
        # Create subplots for each metric
        fig, axes = plt.subplots(len(metrics), 1, figsize=(12, 6 * len(metrics)))
        if len(metrics) == 1:
            axes = [axes]
        
        for i, metric in enumerate(metrics):
            metric_data = df[df['metric'] == metric]
            
            axes[i].plot(metric_data['timestamp'], metric_data['value'], 
                        marker='o', linewidth=2, markersize=6)
            axes[i].set_title(f'{test_name}: {metric}', fontsize=14, fontweight='bold')
            axes[i].set_xlabel('Date')
            axes[i].set_ylabel(metric)
            axes[i].grid(True, alpha=0.3)
            
            # Add trend line
            if len(metric_data) > 2:
                z = np.polyfit(range(len(metric_data)), metric_data['value'], 1)
                p = np.poly1d(z)
                axes[i].plot(metric_data['timestamp'], p(range(len(metric_data))), 
                           '--', alpha=0.8, color='red', label='Trend')
                axes[i].legend()
        
        plt.tight_layout()
        chart_path = output_path / f"{test_name.replace('/', '_')}_trend.png"
        plt.savefig(chart_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"Performance chart saved to {chart_path}")
    
    def generate_comparison_report(
        self, 
        test_names: List[str], 
        metric_name: str,
        days_back: int = 30
    ) -> Dict[str, Any]:
        """Compare performance across multiple tests."""
        comparison_data = {}
        
        for test_name in test_names:
            results = self.get_results(test_name, days_back)
            values = [
                r['metrics'].get(metric_name) 
                for r in results 
                if metric_name in r['metrics']
            ]
            
            if values:
                comparison_data[test_name] = {
                    "count": len(values),
                    "mean": statistics.mean(values),
                    "median": statistics.median(values),
                    "std_dev": statistics.stdev(values) if len(values) > 1 else 0,
                    "min": min(values),
                    "max": max(values),
                    "latest": values[0] if values else None
                }
        
        return {
            "metric_name": metric_name,
            "period_days": days_back,
            "tests": comparison_data,
            "generated_at": datetime.utcnow().isoformat()
        }
    
    def export_results(
        self, 
        output_file: str, 
        test_name: str = None, 
        days_back: int = 30
    ):
        """Export results to JSON or CSV."""
        results = self.get_results(test_name, days_back)
        
        output_path = Path(output_file)
        
        if output_path.suffix.lower() == '.json':
            with open(output_path, 'w') as f:
                json.dump(results, f, indent=2)
        
        elif output_path.suffix.lower() == '.csv':
            # Flatten metrics for CSV export
            flat_data = []
            for result in results:
                base_row = {
                    'timestamp': result['timestamp'],
                    'test_name': result['test_name'],
                    'git_commit': result['git_commit'],
                    'branch': result['branch'],
                    'environment': result['environment']
                }
                
                for metric, value in result['metrics'].items():
                    row = base_row.copy()
                    row['metric_name'] = metric
                    row['metric_value'] = value
                    flat_data.append(row)
            
            df = pd.DataFrame(flat_data)
            df.to_csv(output_path, index=False)
        
        else:
            raise ValueError(f"Unsupported output format: {output_path.suffix}")
        
        print(f"Results exported to {output_path}")
    
    def create_dashboard_data(self, days_back: int = 30) -> Dict[str, Any]:
        """Create data for performance dashboard."""
        all_results = self.get_results(days_back=days_back, limit=1000)
        
        # Group by test name
        tests = {}
        for result in all_results:
            test_name = result['test_name']
            if test_name not in tests:
                tests[test_name] = []
            tests[test_name].append(result)
        
        dashboard_data = {
            "summary": {
                "total_tests": len(tests),
                "total_runs": len(all_results),
                "period_days": days_back,
                "last_updated": datetime.utcnow().isoformat()
            },
            "tests": {}
        }
        
        for test_name, test_results in tests.items():
            # Get latest result
            latest = test_results[0] if test_results else {}
            
            # Calculate key metrics
            all_metrics = set()
            for result in test_results:
                all_metrics.update(result['metrics'].keys())
            
            test_summary = {
                "runs": len(test_results),
                "latest_run": latest.get('timestamp'),
                "latest_commit": latest.get('git_commit'),
                "metrics": {}
            }
            
            for metric in all_metrics:
                values = [
                    r['metrics'][metric] 
                    for r in test_results 
                    if metric in r['metrics']
                ]
                
                if values:
                    test_summary["metrics"][metric] = {
                        "latest": values[0],
                        "average": statistics.mean(values),
                        "trend": self._get_simple_trend(values[:5])  # Last 5 values
                    }
            
            dashboard_data["tests"][test_name] = test_summary
        
        return dashboard_data
    
    def _get_simple_trend(self, values: List[float]) -> str:
        """Get simple trend direction from recent values."""
        if len(values) < 2:
            return "stable"
        
        # Compare first half with second half
        mid = len(values) // 2
        first_half_avg = statistics.mean(values[:mid])
        second_half_avg = statistics.mean(values[mid:])
        
        change_percent = ((second_half_avg - first_half_avg) / first_half_avg) * 100
        
        if change_percent > 5:
            return "increasing"
        elif change_percent < -5:
            return "decreasing"
        else:
            return "stable"


class RegressionDetector:
    """Automated performance regression detection."""
    
    def __init__(self, reporter: PerformanceReporter):
        self.reporter = reporter
    
    def check_all_tests(
        self, 
        threshold_percent: float = 10.0,
        days_back: int = 14
    ) -> Dict[str, Any]:
        """Check all tests for regressions."""
        # Get all unique test names
        all_results = self.reporter.get_results(days_back=days_back, limit=1000)
        test_names = list(set(r['test_name'] for r in all_results))
        
        regressions = {}
        for test_name in test_names:
            test_results = [r for r in all_results if r['test_name'] == test_name]
            if len(test_results) < 3:  # Need at least 3 runs
                continue
            
            # Get all metrics for this test
            all_metrics = set()
            for result in test_results:
                all_metrics.update(result['metrics'].keys())
            
            test_regressions = {}
            for metric in all_metrics:
                regression = self.reporter.detect_regression(
                    test_name, metric, threshold_percent
                )
                
                if regression['status'] == 'regression_detected':
                    test_regressions[metric] = regression
            
            if test_regressions:
                regressions[test_name] = test_regressions
        
        return {
            "regressions_found": len(regressions),
            "tests_checked": len(test_names),
            "threshold_percent": threshold_percent,
            "regressions": regressions,
            "checked_at": datetime.utcnow().isoformat()
        }
    
    def create_regression_report(self, output_file: str):
        """Create comprehensive regression report."""
        regressions = self.check_all_tests()
        
        with open(output_file, 'w') as f:
            json.dump(regressions, f, indent=2)
        
        print(f"Regression report saved to {output_file}")
        
        if regressions['regressions_found'] > 0:
            print(f"⚠️  Found {regressions['regressions_found']} performance regressions!")
            for test_name, test_regressions in regressions['regressions'].items():
                print(f"  - {test_name}: {list(test_regressions.keys())}")
        else:
            print("✅ No performance regressions detected")
        
        return regressions


# CLI interface for performance reporting
def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='MAOS Performance Reporting')
    parser.add_argument('--db', default='tests/performance_results.db', 
                       help='Performance results database path')
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Trend report
    trend_parser = subparsers.add_parser('trend', help='Generate trend report')
    trend_parser.add_argument('test_name', help='Test name')
    trend_parser.add_argument('--days', type=int, default=30, help='Days back')
    
    # Regression check
    regress_parser = subparsers.add_parser('regression', help='Check for regressions')
    regress_parser.add_argument('--threshold', type=float, default=10.0, 
                               help='Regression threshold percentage')
    regress_parser.add_argument('--output', help='Output file for report')
    
    # Export results
    export_parser = subparsers.add_parser('export', help='Export results')
    export_parser.add_argument('output_file', help='Output file (JSON or CSV)')
    export_parser.add_argument('--test', help='Specific test name')
    export_parser.add_argument('--days', type=int, default=30, help='Days back')
    
    # Generate charts
    chart_parser = subparsers.add_parser('chart', help='Generate charts')
    chart_parser.add_argument('test_name', help='Test name')
    chart_parser.add_argument('--output-dir', default='tests/performance_charts', 
                             help='Output directory')
    chart_parser.add_argument('--days', type=int, default=30, help='Days back')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    reporter = PerformanceReporter(args.db)
    
    if args.command == 'trend':
        report = reporter.generate_trend_report(args.test_name, args.days)
        print(json.dumps(report, indent=2))
    
    elif args.command == 'regression':
        detector = RegressionDetector(reporter)
        if args.output:
            detector.create_regression_report(args.output)
        else:
            regressions = detector.check_all_tests(args.threshold)
            print(json.dumps(regressions, indent=2))
    
    elif args.command == 'export':
        reporter.export_results(args.output_file, args.test, args.days)
    
    elif args.command == 'chart':
        reporter.generate_performance_charts(args.test_name, args.output_dir, args.days)


if __name__ == '__main__':
    main()