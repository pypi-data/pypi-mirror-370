"""
Test coverage configuration and reporting utilities.
"""

import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Any
import json
import xml.etree.ElementTree as ET


class CoverageAnalyzer:
    """Analyze and report on test coverage metrics."""
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.coverage_file = self.project_root / "coverage.xml"
        self.html_dir = self.project_root / "tests" / "coverage_html"
    
    def run_coverage(self, test_paths: List[str] = None) -> Dict[str, Any]:
        """Run pytest with coverage and return results."""
        if test_paths is None:
            test_paths = ["tests/"]
        
        cmd = [
            sys.executable, "-m", "pytest",
            "--cov=src/maos",
            "--cov=src/communication",
            f"--cov-report=xml:{self.coverage_file}",
            f"--cov-report=html:{self.html_dir}",
            "--cov-report=term-missing:skip-covered",
            "--cov-branch",  # Include branch coverage
            "--cov-fail-under=95",  # Fail if coverage below 95%
        ] + test_paths
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, cwd=self.project_root)
            
            return {
                "success": result.returncode == 0,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "returncode": result.returncode
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "returncode": -1
            }
    
    def parse_coverage_xml(self) -> Dict[str, Any]:
        """Parse coverage XML file and extract metrics."""
        if not self.coverage_file.exists():
            return {"error": "Coverage XML file not found"}
        
        try:
            tree = ET.parse(self.coverage_file)
            root = tree.getroot()
            
            # Overall coverage
            overall_coverage = {
                "line_rate": float(root.attrib.get("line-rate", 0)) * 100,
                "branch_rate": float(root.attrib.get("branch-rate", 0)) * 100,
                "lines_covered": int(root.attrib.get("lines-covered", 0)),
                "lines_valid": int(root.attrib.get("lines-valid", 0)),
                "branches_covered": int(root.attrib.get("branches-covered", 0)),
                "branches_valid": int(root.attrib.get("branches-valid", 0)),
                "complexity": float(root.attrib.get("complexity", 0))
            }
            
            # Package-level coverage
            packages = {}
            for package in root.findall(".//package"):
                package_name = package.attrib.get("name", "unknown")
                packages[package_name] = {
                    "line_rate": float(package.attrib.get("line-rate", 0)) * 100,
                    "branch_rate": float(package.attrib.get("branch-rate", 0)) * 100,
                    "complexity": float(package.attrib.get("complexity", 0))
                }
            
            # Class/file-level coverage
            files = {}
            for cls in root.findall(".//class"):
                filename = cls.attrib.get("filename", "unknown")
                class_name = cls.attrib.get("name", "unknown")
                
                files[filename] = {
                    "class_name": class_name,
                    "line_rate": float(cls.attrib.get("line-rate", 0)) * 100,
                    "branch_rate": float(cls.attrib.get("branch-rate", 0)) * 100,
                    "complexity": float(cls.attrib.get("complexity", 0))
                }
            
            return {
                "overall": overall_coverage,
                "packages": packages,
                "files": files,
                "timestamp": self.coverage_file.stat().st_mtime
            }
        
        except Exception as e:
            return {"error": f"Failed to parse coverage XML: {str(e)}"}
    
    def generate_coverage_report(self) -> Dict[str, Any]:
        """Generate comprehensive coverage report."""
        coverage_data = self.parse_coverage_xml()
        
        if "error" in coverage_data:
            return coverage_data
        
        overall = coverage_data["overall"]
        files = coverage_data["files"]
        
        # Identify coverage gaps
        low_coverage_files = {
            filename: data for filename, data in files.items()
            if data["line_rate"] < 80.0
        }
        
        uncovered_files = {
            filename: data for filename, data in files.items()
            if data["line_rate"] < 50.0
        }
        
        excellent_coverage_files = {
            filename: data for filename, data in files.items()
            if data["line_rate"] >= 95.0
        }
        
        # Calculate coverage distribution
        coverage_ranges = {
            "excellent (95-100%)": 0,
            "good (80-94%)": 0,
            "moderate (60-79%)": 0,
            "poor (40-59%)": 0,
            "very_poor (0-39%)": 0
        }
        
        for data in files.values():
            rate = data["line_rate"]
            if rate >= 95:
                coverage_ranges["excellent (95-100%)"] += 1
            elif rate >= 80:
                coverage_ranges["good (80-94%)"] += 1
            elif rate >= 60:
                coverage_ranges["moderate (60-79%)"] += 1
            elif rate >= 40:
                coverage_ranges["poor (40-59%)"] += 1
            else:
                coverage_ranges["very_poor (0-39%)"] += 1
        
        # Generate recommendations
        recommendations = []
        
        if overall["line_rate"] < 95:
            recommendations.append(
                f"Overall line coverage is {overall['line_rate']:.1f}%, below the 95% target"
            )
        
        if overall["branch_rate"] < 85:
            recommendations.append(
                f"Branch coverage is {overall['branch_rate']:.1f}%, consider adding more edge case tests"
            )
        
        if low_coverage_files:
            recommendations.append(
                f"Found {len(low_coverage_files)} files with <80% coverage, prioritize testing these"
            )
        
        if uncovered_files:
            recommendations.append(
                f"Found {len(uncovered_files)} files with <50% coverage, these need immediate attention"
            )
        
        return {
            "overall_metrics": overall,
            "file_count": len(files),
            "coverage_distribution": coverage_ranges,
            "low_coverage_files": low_coverage_files,
            "uncovered_files": uncovered_files,
            "excellent_coverage_files": excellent_coverage_files,
            "recommendations": recommendations,
            "meets_target": overall["line_rate"] >= 95.0,
            "report_generated_at": coverage_data["timestamp"]
        }
    
    def create_coverage_badge(self, output_file: str = "coverage_badge.svg"):
        """Create a coverage badge SVG."""
        coverage_data = self.parse_coverage_xml()
        
        if "error" in coverage_data:
            coverage_percent = 0
        else:
            coverage_percent = coverage_data["overall"]["line_rate"]
        
        # Determine badge color
        if coverage_percent >= 95:
            color = "brightgreen"
        elif coverage_percent >= 85:
            color = "green"
        elif coverage_percent >= 75:
            color = "yellowgreen"
        elif coverage_percent >= 60:
            color = "yellow"
        elif coverage_percent >= 40:
            color = "orange"
        else:
            color = "red"
        
        # SVG template
        svg_template = f"""<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="104" height="20">
    <linearGradient id="b" x2="0" y2="100%">
        <stop offset="0" stop-color="#bbb" stop-opacity=".1"/>
        <stop offset="1" stop-opacity=".1"/>
    </linearGradient>
    <clipPath id="a">
        <rect width="104" height="20" rx="3" fill="#fff"/>
    </clipPath>
    <g clip-path="url(#a)">
        <path fill="#555" d="M0 0h63v20H0z"/>
        <path fill="{color}" d="M63 0h41v20H63z"/>
        <path fill="url(#b)" d="M0 0h104v20H0z"/>
    </g>
    <g fill="#fff" text-anchor="middle" font-family="DejaVu Sans,Verdana,Geneva,sans-serif" font-size="110">
        <text x="325" y="150" fill="#010101" fill-opacity=".3" transform="scale(.1)" textLength="530">coverage</text>
        <text x="325" y="140" transform="scale(.1)" textLength="530">coverage</text>
        <text x="825" y="150" fill="#010101" fill-opacity=".3" transform="scale(.1)" textLength="310">{coverage_percent:.0f}%</text>
        <text x="825" y="140" transform="scale(.1)" textLength="310">{coverage_percent:.0f}%</text>
    </g>
</svg>"""
        
        with open(output_file, 'w') as f:
            f.write(svg_template)
        
        print(f"Coverage badge created: {output_file}")
    
    def compare_coverage(self, previous_coverage_file: str) -> Dict[str, Any]:
        """Compare current coverage with previous results."""
        current = self.parse_coverage_xml()
        
        try:
            with open(previous_coverage_file, 'r') as f:
                previous = json.load(f)
        except Exception as e:
            return {"error": f"Could not load previous coverage data: {str(e)}"}
        
        if "error" in current or "overall" not in previous:
            return {"error": "Invalid coverage data"}
        
        current_overall = current["overall"]
        previous_overall = previous["overall"]
        
        line_change = current_overall["line_rate"] - previous_overall["line_rate"]
        branch_change = current_overall["branch_rate"] - previous_overall["branch_rate"]
        
        # File-level changes
        file_changes = {}
        current_files = current.get("files", {})
        previous_files = previous.get("files", {})
        
        all_files = set(current_files.keys()) | set(previous_files.keys())
        
        for filename in all_files:
            current_rate = current_files.get(filename, {}).get("line_rate", 0)
            previous_rate = previous_files.get(filename, {}).get("line_rate", 0)
            
            change = current_rate - previous_rate
            if abs(change) >= 1.0:  # Only report significant changes
                file_changes[filename] = {
                    "current": current_rate,
                    "previous": previous_rate,
                    "change": change
                }
        
        return {
            "overall_changes": {
                "line_coverage": {
                    "current": current_overall["line_rate"],
                    "previous": previous_overall["line_rate"],
                    "change": line_change,
                    "improved": line_change > 0
                },
                "branch_coverage": {
                    "current": current_overall["branch_rate"],
                    "previous": previous_overall["branch_rate"],
                    "change": branch_change,
                    "improved": branch_change > 0
                }
            },
            "file_changes": file_changes,
            "summary": {
                "files_improved": len([f for f in file_changes.values() if f["change"] > 0]),
                "files_degraded": len([f for f in file_changes.values() if f["change"] < 0]),
                "overall_improved": line_change > 0,
                "significant_change": abs(line_change) >= 1.0
            }
        }
    
    def export_coverage_data(self, output_file: str):
        """Export coverage data for historical tracking."""
        coverage_data = self.parse_coverage_xml()
        
        with open(output_file, 'w') as f:
            json.dump(coverage_data, f, indent=2)
        
        print(f"Coverage data exported to {output_file}")


def main():
    """CLI interface for coverage analysis."""
    import argparse
    
    parser = argparse.ArgumentParser(description='MAOS Coverage Analysis')
    parser.add_argument('--project-root', default='.', help='Project root directory')
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Run coverage
    run_parser = subparsers.add_parser('run', help='Run coverage analysis')
    run_parser.add_argument('paths', nargs='*', help='Test paths')
    
    # Generate report
    report_parser = subparsers.add_parser('report', help='Generate coverage report')
    
    # Create badge
    badge_parser = subparsers.add_parser('badge', help='Create coverage badge')
    badge_parser.add_argument('--output', default='coverage_badge.svg', help='Output file')
    
    # Compare coverage
    compare_parser = subparsers.add_parser('compare', help='Compare with previous coverage')
    compare_parser.add_argument('previous_file', help='Previous coverage JSON file')
    
    # Export data
    export_parser = subparsers.add_parser('export', help='Export coverage data')
    export_parser.add_argument('output_file', help='Output JSON file')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    analyzer = CoverageAnalyzer(args.project_root)
    
    if args.command == 'run':
        result = analyzer.run_coverage(args.paths)
        if result["success"]:
            print("✅ Coverage analysis completed successfully")
        else:
            print("❌ Coverage analysis failed")
            print(result.get("stderr", "Unknown error"))
            sys.exit(result["returncode"])
    
    elif args.command == 'report':
        report = analyzer.generate_coverage_report()
        if "error" in report:
            print(f"❌ Error: {report['error']}")
            sys.exit(1)
        
        overall = report["overall_metrics"]
        print(f"\n📊 Coverage Report")
        print(f"Line Coverage: {overall['line_rate']:.1f}%")
        print(f"Branch Coverage: {overall['branch_rate']:.1f}%")
        print(f"Files Analyzed: {report['file_count']}")
        print(f"Target Met: {'✅' if report['meets_target'] else '❌'}")
        
        if report["recommendations"]:
            print(f"\n💡 Recommendations:")
            for rec in report["recommendations"]:
                print(f"  - {rec}")
        
        print(f"\n📈 Coverage Distribution:")
        for range_name, count in report["coverage_distribution"].items():
            print(f"  {range_name}: {count} files")
    
    elif args.command == 'badge':
        analyzer.create_coverage_badge(args.output)
    
    elif args.command == 'compare':
        comparison = analyzer.compare_coverage(args.previous_file)
        if "error" in comparison:
            print(f"❌ Error: {comparison['error']}")
            sys.exit(1)
        
        overall = comparison["overall_changes"]
        line_cov = overall["line_coverage"]
        branch_cov = overall["branch_coverage"]
        
        print(f"\n📊 Coverage Comparison")
        print(f"Line Coverage: {line_cov['current']:.1f}% ({line_cov['change']:+.1f}%)")
        print(f"Branch Coverage: {branch_cov['current']:.1f}% ({branch_cov['change']:+.1f}%)")
        
        summary = comparison["summary"]
        print(f"\nFiles Improved: {summary['files_improved']}")
        print(f"Files Degraded: {summary['files_degraded']}")
        print(f"Overall Trend: {'📈 Improved' if summary['overall_improved'] else '📉 Degraded'}")
    
    elif args.command == 'export':
        analyzer.export_coverage_data(args.output_file)


if __name__ == '__main__':
    main()