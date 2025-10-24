#!/usr/bin/env python3
"""
Workflow Change Impact Analyzer

Analyzes the impact of workflow changes on CI/CD pipeline performance,
security, and reliability. Provides detailed impact assessment and
recommendations for workflow modifications.

Requirements addressed:
- 10.4: Implement workflow change impact analysis
"""

import argparse
import json
import os
import re
import subprocess
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Set, Tuple
import yaml


class WorkflowImpactAnalyzer:
    """Comprehensive workflow change impact analyzer."""
    
    def __init__(self, repo_root: Optional[Path] = None):
        """Initialize the impact analyzer.
        
        Args:
            repo_root: Path to repository root. If None, auto-detect.
        """
        self.repo_root = repo_root or self._find_repo_root()
        self.workflows_dir = self.repo_root / ".github" / "workflows"
        
        # Impact categories and weights
        self.impact_weights = {
            "security": 1.0,      # Highest priority
            "performance": 0.8,   # High priority
            "reliability": 0.9,   # Very high priority
            "maintainability": 0.6, # Medium priority
            "compatibility": 0.7   # Medium-high priority
        }
        
        # Critical workflow patterns
        self.critical_patterns = {
            "permissions": {"weight": 1.0, "category": "security"},
            "secrets": {"weight": 1.0, "category": "security"},
            "runs-on": {"weight": 0.8, "category": "performance"},
            "timeout-minutes": {"weight": 0.7, "category": "reliability"},
            "needs": {"weight": 0.9, "category": "reliability"},
            "strategy": {"weight": 0.6, "category": "performance"},
            "matrix": {"weight": 0.6, "category": "performance"},
            "uses:": {"weight": 0.8, "category": "compatibility"},
            "if:": {"weight": 0.7, "category": "reliability"}
        }
    
    def _find_repo_root(self) -> Path:
        """Find repository root by looking for .git directory."""
        current = Path.cwd()
        while current != current.parent:
            if (current / ".git").exists():
                return current
            current = current.parent
        raise ValueError("Could not find repository root (.git directory)")
    
    def analyze_changes(self, base_ref: str = "main", target_ref: str = "HEAD") -> Dict[str, Any]:
        """Analyze workflow changes between two references.
        
        Args:
            base_ref: Base reference (e.g., 'main', 'origin/main')
            target_ref: Target reference (e.g., 'HEAD', branch name)
            
        Returns:
            Comprehensive impact analysis results.
        """
        print(f"🔍 Analyzing workflow changes: {base_ref}...{target_ref}")
        
        analysis = {
            "metadata": {
                "base_ref": base_ref,
                "target_ref": target_ref,
                "analysis_time": datetime.now().isoformat(),
                "analyzer_version": "1.0.0"
            },
            "summary": {
                "overall_risk": "low",
                "impact_score": 0.0,
                "changed_workflows": 0,
                "new_workflows": 0,
                "deleted_workflows": 0,
                "modified_workflows": 0
            },
            "changes": {
                "files": [],
                "impact_categories": {
                    "security": {"score": 0.0, "changes": []},
                    "performance": {"score": 0.0, "changes": []},
                    "reliability": {"score": 0.0, "changes": []},
                    "maintainability": {"score": 0.0, "changes": []},
                    "compatibility": {"score": 0.0, "changes": []}
                }
            },
            "recommendations": [],
            "testing_strategy": {},
            "rollback_plan": {}
        }
        
        try:
            # Get changed workflow files
            changed_files = self._get_changed_workflow_files(base_ref, target_ref)
            
            if not changed_files:
                analysis["summary"]["overall_risk"] = "none"
                analysis["recommendations"].append("No workflow changes detected - no impact expected")
                return analysis
            
            print(f"Found {len(changed_files)} changed workflow files")
            
            # Analyze each changed file
            for file_info in changed_files:
                file_analysis = self._analyze_file_change(file_info, base_ref, target_ref)
                analysis["changes"]["files"].append(file_analysis)
                
                # Update summary counts
                if file_info["status"] == "added":
                    analysis["summary"]["new_workflows"] += 1
                elif file_info["status"] == "deleted":
                    analysis["summary"]["deleted_workflows"] += 1
                elif file_info["status"] == "modified":
                    analysis["summary"]["modified_workflows"] += 1
                
                # Aggregate impact scores
                for category, category_data in file_analysis["impact_categories"].items():
                    analysis["changes"]["impact_categories"][category]["score"] += category_data["score"]
                    analysis["changes"]["impact_categories"][category]["changes"].extend(category_data["changes"])
            
            analysis["summary"]["changed_workflows"] = len(changed_files)
            
            # Calculate overall impact
            analysis = self._calculate_overall_impact(analysis)
            
            # Generate recommendations
            analysis["recommendations"] = self._generate_recommendations(analysis)
            
            # Create testing strategy
            analysis["testing_strategy"] = self._create_testing_strategy(analysis)
            
            # Create rollback plan
            analysis["rollback_plan"] = self._create_rollback_plan(analysis)
            
        except subprocess.CalledProcessError as e:
            analysis["error"] = f"Git command failed: {e}"
            analysis["summary"]["overall_risk"] = "unknown"
        except Exception as e:
            analysis["error"] = f"Analysis failed: {e}"
            analysis["summary"]["overall_risk"] = "unknown"
        
        return analysis
    
    def _get_changed_workflow_files(self, base_ref: str, target_ref: str) -> List[Dict[str, Any]]:
        """Get list of changed workflow files with their status."""
        # Get changed files with status
        result = subprocess.run(
            ["git", "diff", "--name-status", f"{base_ref}...{target_ref}", ".github/workflows/"],
            cwd=self.repo_root,
            capture_output=True,
            text=True,
            check=True
        )
        
        changed_files = []
        for line in result.stdout.strip().split('\n'):
            if not line:
                continue
            
            parts = line.split('\t')
            if len(parts) >= 2:
                status_code = parts[0]
                file_path = parts[1]
                
                # Only include YAML workflow files
                if not (file_path.endswith('.yml') or file_path.endswith('.yaml')):
                    continue
                
                # Map git status codes
                status_map = {
                    'A': 'added',
                    'M': 'modified',
                    'D': 'deleted',
                    'R': 'renamed',
                    'C': 'copied'
                }
                
                status = status_map.get(status_code[0], 'modified')
                
                changed_files.append({
                    "path": file_path,
                    "status": status,
                    "git_status": status_code
                })
        
        return changed_files
    
    def _analyze_file_change(self, file_info: Dict[str, Any], base_ref: str, target_ref: str) -> Dict[str, Any]:
        """Analyze changes in a specific workflow file."""
        file_path = file_info["path"]
        status = file_info["status"]
        
        analysis = {
            "file": file_path,
            "status": status,
            "risk_level": "low",
            "impact_score": 0.0,
            "impact_categories": {
                "security": {"score": 0.0, "changes": []},
                "performance": {"score": 0.0, "changes": []},
                "reliability": {"score": 0.0, "changes": []},
                "maintainability": {"score": 0.0, "changes": []},
                "compatibility": {"score": 0.0, "changes": []}
            },
            "change_details": {
                "lines_added": 0,
                "lines_removed": 0,
                "sections_modified": [],
                "critical_changes": []
            }
        }
        
        try:
            if status == "added":
                analysis = self._analyze_new_workflow(file_path, analysis)
            elif status == "deleted":
                analysis = self._analyze_deleted_workflow(file_path, analysis)
            elif status == "modified":
                analysis = self._analyze_modified_workflow(file_path, base_ref, target_ref, analysis)
            
            # Calculate file-level impact score
            total_score = sum(
                cat_data["score"] * self.impact_weights[category]
                for category, cat_data in analysis["impact_categories"].items()
            )
            analysis["impact_score"] = total_score
            
            # Determine risk level
            if total_score >= 0.8:
                analysis["risk_level"] = "high"
            elif total_score >= 0.4:
                analysis["risk_level"] = "medium"
            else:
                analysis["risk_level"] = "low"
                
        except Exception as e:
            analysis["error"] = str(e)
            analysis["risk_level"] = "unknown"
        
        return analysis
    
    def _analyze_new_workflow(self, file_path: str, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze a newly added workflow."""
        full_path = self.repo_root / file_path
        
        if not full_path.exists():
            analysis["impact_categories"]["reliability"]["changes"].append({
                "type": "new_workflow_missing",
                "description": "New workflow file not found in working directory",
                "impact": "File may not be properly committed"
            })
            analysis["impact_categories"]["reliability"]["score"] = 0.3
            return analysis
        
        try:
            with open(full_path, 'r', encoding='utf-8') as f:
                content = f.read()
                workflow_data = yaml.safe_load(content)
            
            # Analyze new workflow for potential issues
            analysis["impact_categories"]["maintainability"]["changes"].append({
                "type": "new_workflow",
                "description": f"New workflow added: {Path(file_path).stem}",
                "impact": "Increases CI/CD complexity and maintenance burden"
            })
            analysis["impact_categories"]["maintainability"]["score"] = 0.3
            
            # Check for high-risk patterns in new workflow
            if self._has_security_sensitive_content(content):
                analysis["impact_categories"]["security"]["changes"].append({
                    "type": "new_security_sensitive",
                    "description": "New workflow contains security-sensitive configurations",
                    "impact": "Requires security review"
                })
                analysis["impact_categories"]["security"]["score"] = 0.6
            
            # Check for performance impact
            if self._has_performance_impact(workflow_data):
                analysis["impact_categories"]["performance"]["changes"].append({
                    "type": "new_performance_impact",
                    "description": "New workflow may impact CI/CD performance",
                    "impact": "May increase overall execution time"
                })
                analysis["impact_categories"]["performance"]["score"] = 0.4
                
        except Exception as e:
            analysis["impact_categories"]["reliability"]["changes"].append({
                "type": "new_workflow_error",
                "description": f"Error analyzing new workflow: {e}",
                "impact": "Workflow may have syntax or configuration issues"
            })
            analysis["impact_categories"]["reliability"]["score"] = 0.7
        
        return analysis
    
    def _analyze_deleted_workflow(self, file_path: str, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze a deleted workflow."""
        analysis["impact_categories"]["reliability"]["changes"].append({
            "type": "workflow_deleted",
            "description": f"Workflow deleted: {Path(file_path).stem}",
            "impact": "CI/CD functionality may be lost"
        })
        analysis["impact_categories"]["reliability"]["score"] = 0.8
        
        # Check if this was a critical workflow
        workflow_name = Path(file_path).stem.lower()
        if any(critical in workflow_name for critical in ["security", "test", "build", "deploy"]):
            analysis["impact_categories"]["reliability"]["score"] = 1.0
            analysis["change_details"]["critical_changes"].append(
                f"Critical workflow deleted: {workflow_name}"
            )
        
        return analysis
    
    def _analyze_modified_workflow(self, file_path: str, base_ref: str, target_ref: str, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze a modified workflow."""
        try:
            # Get the diff for this file
            result = subprocess.run(
                ["git", "diff", f"{base_ref}...{target_ref}", "--", file_path],
                cwd=self.repo_root,
                capture_output=True,
                text=True,
                check=True
            )
            
            diff_content = result.stdout
            
            # Parse diff statistics
            added_lines = len([line for line in diff_content.split('\n') if line.startswith('+')])
            removed_lines = len([line for line in diff_content.split('\n') if line.startswith('-')])
            
            analysis["change_details"]["lines_added"] = added_lines
            analysis["change_details"]["lines_removed"] = removed_lines
            
            # Analyze specific change patterns
            analysis = self._analyze_diff_patterns(diff_content, analysis)
            
            # Check for breaking changes
            if removed_lines > added_lines * 2:  # Significant removal
                analysis["impact_categories"]["reliability"]["changes"].append({
                    "type": "significant_removal",
                    "description": f"Significant content removal ({removed_lines} lines removed vs {added_lines} added)",
                    "impact": "May break existing functionality"
                })
                analysis["impact_categories"]["reliability"]["score"] += 0.6
            
            # Check change magnitude
            total_changes = added_lines + removed_lines
            if total_changes > 50:  # Large change
                analysis["impact_categories"]["maintainability"]["changes"].append({
                    "type": "large_change",
                    "description": f"Large workflow modification ({total_changes} total line changes)",
                    "impact": "Requires thorough review and testing"
                })
                analysis["impact_categories"]["maintainability"]["score"] += 0.4
                
        except subprocess.CalledProcessError as e:
            analysis["impact_categories"]["reliability"]["changes"].append({
                "type": "diff_analysis_error",
                "description": f"Could not analyze workflow diff: {e}",
                "impact": "Unable to assess change impact"
            })
            analysis["impact_categories"]["reliability"]["score"] = 0.5
        
        return analysis
    
    def _analyze_diff_patterns(self, diff_content: str, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze specific patterns in the diff content."""
        
        # Define critical change patterns
        critical_patterns = [
            (r'[+-]\s*permissions:', "permissions", "security", 0.9),
            (r'[+-].*secrets\.|[+-].*\$\{\{\s*secrets\.', "secrets", "security", 1.0),
            (r'[+-]\s*runs-on:', "runner", "performance", 0.7),
            (r'[+-].*uses:\s*.*@', "action_version", "compatibility", 0.6),
            (r'[+-]\s*needs:', "dependencies", "reliability", 0.8),
            (r'[+-]\s*timeout-minutes:', "timeout", "reliability", 0.5),
            (r'[+-]\s*strategy:', "strategy", "performance", 0.5),
            (r'[+-]\s*matrix:', "matrix", "performance", 0.5),
            (r'[+-]\s*if:', "conditions", "reliability", 0.6),
            (r'[+-].*env:', "environment", "maintainability", 0.4)
        ]
        
        for pattern, change_type, category, impact_score in critical_patterns:
            matches = re.findall(pattern, diff_content, re.IGNORECASE | re.MULTILINE)
            
            if matches:
                analysis["impact_categories"][category]["changes"].append({
                    "type": f"{change_type}_change",
                    "description": f"{change_type.replace('_', ' ').title()} configuration modified",
                    "impact": f"May affect workflow {category}",
                    "occurrences": len(matches)
                })
                
                # Add to impact score (scaled by number of occurrences)
                score_addition = min(impact_score * len(matches) * 0.1, impact_score)
                analysis["impact_categories"][category]["score"] += score_addition
                
                # Track critical changes
                if impact_score >= 0.8:
                    analysis["change_details"]["critical_changes"].append(
                        f"{change_type.replace('_', ' ').title()} modified ({len(matches)} occurrences)"
                    )
                
                # Track modified sections
                if change_type not in analysis["change_details"]["sections_modified"]:
                    analysis["change_details"]["sections_modified"].append(change_type)
        
        return analysis
    
    def _has_security_sensitive_content(self, content: str) -> bool:
        """Check if content has security-sensitive configurations."""
        security_patterns = [
            r'permissions:\s*write-all',
            r'permissions:.*write',
            r'secrets\.',
            r'token\s*:',
            r'password\s*:',
            r'api[_-]?key\s*:'
        ]
        
        return any(re.search(pattern, content, re.IGNORECASE) for pattern in security_patterns)
    
    def _has_performance_impact(self, workflow_data: Dict) -> bool:
        """Check if workflow has potential performance impact."""
        if not isinstance(workflow_data, dict):
            return False
        
        jobs = workflow_data.get("jobs", {})
        
        # Check for performance indicators
        job_count = len(jobs)
        has_matrix = any("strategy" in job.get("strategy", {}) for job in jobs.values() if isinstance(job, dict))
        has_long_timeout = any(
            job.get("timeout-minutes", 0) > 30 
            for job in jobs.values() 
            if isinstance(job, dict)
        )
        
        return job_count > 5 or has_matrix or has_long_timeout
    
    def _calculate_overall_impact(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate overall impact score and risk level."""
        
        # Calculate weighted impact score
        total_weighted_score = 0.0
        total_weight = 0.0
        
        for category, weight in self.impact_weights.items():
            category_score = analysis["changes"]["impact_categories"][category]["score"]
            total_weighted_score += category_score * weight
            total_weight += weight
        
        overall_score = total_weighted_score / total_weight if total_weight > 0 else 0.0
        analysis["summary"]["impact_score"] = round(overall_score, 3)
        
        # Determine overall risk level
        if overall_score >= 0.8:
            analysis["summary"]["overall_risk"] = "high"
        elif overall_score >= 0.4:
            analysis["summary"]["overall_risk"] = "medium"
        elif overall_score > 0:
            analysis["summary"]["overall_risk"] = "low"
        else:
            analysis["summary"]["overall_risk"] = "minimal"
        
        return analysis
    
    def _generate_recommendations(self, analysis: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on impact analysis."""
        recommendations = []
        
        risk_level = analysis["summary"]["overall_risk"]
        impact_score = analysis["summary"]["impact_score"]
        
        # Risk-based recommendations
        if risk_level == "high":
            recommendations.extend([
                "🚨 HIGH RISK: Implement comprehensive testing before deployment",
                "🔒 Security review required for permission and secret changes",
                "🧪 Test workflows in isolated environment using 'act' or feature branch",
                "📋 Create detailed rollback plan before deployment",
                "👥 Require additional reviewer approval for these changes"
            ])
        elif risk_level == "medium":
            recommendations.extend([
                "⚠️ MEDIUM RISK: Thorough testing recommended",
                "🧪 Test critical workflows in development environment",
                "📊 Monitor workflow performance after deployment",
                "🔄 Prepare rollback procedures"
            ])
        elif risk_level == "low":
            recommendations.extend([
                "✅ LOW RISK: Standard review and testing sufficient",
                "📝 Document changes for future reference"
            ])
        
        # Category-specific recommendations
        categories = analysis["changes"]["impact_categories"]
        
        if categories["security"]["score"] > 0.5:
            recommendations.append("🔐 Security impact detected - review permissions and secret handling")
        
        if categories["performance"]["score"] > 0.5:
            recommendations.append("⚡ Performance impact detected - benchmark execution times")
        
        if categories["reliability"]["score"] > 0.5:
            recommendations.append("🛡️ Reliability impact detected - test error handling and recovery")
        
        if categories["compatibility"]["score"] > 0.5:
            recommendations.append("🔄 Compatibility impact detected - verify action version compatibility")
        
        # Change-specific recommendations
        if analysis["summary"]["new_workflows"] > 0:
            recommendations.append("📁 New workflows added - ensure proper integration with existing CI/CD")
        
        if analysis["summary"]["deleted_workflows"] > 0:
            recommendations.append("🗑️ Workflows deleted - verify no critical functionality is lost")
        
        # File-specific recommendations
        for file_analysis in analysis["changes"]["files"]:
            if file_analysis["risk_level"] == "high":
                recommendations.append(f"⚠️ High-risk changes in {file_analysis['file']} - prioritize testing")
        
        return recommendations
    
    def _create_testing_strategy(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Create a testing strategy based on impact analysis."""
        
        risk_level = analysis["summary"]["overall_risk"]
        
        strategy = {
            "approach": "standard",
            "priority": "medium",
            "test_phases": [],
            "tools": [],
            "environments": ["development"],
            "validation_criteria": []
        }
        
        # Adjust strategy based on risk level
        if risk_level == "high":
            strategy.update({
                "approach": "comprehensive",
                "priority": "high",
                "environments": ["development", "staging", "isolated"],
                "test_phases": [
                    "syntax_validation",
                    "isolated_testing",
                    "integration_testing",
                    "performance_testing",
                    "security_validation"
                ]
            })
        elif risk_level == "medium":
            strategy.update({
                "approach": "thorough",
                "priority": "medium",
                "environments": ["development", "staging"],
                "test_phases": [
                    "syntax_validation",
                    "integration_testing",
                    "performance_testing"
                ]
            })
        else:
            strategy.update({
                "test_phases": [
                    "syntax_validation",
                    "basic_testing"
                ]
            })
        
        # Add tools based on detected changes
        categories = analysis["changes"]["impact_categories"]
        
        if categories["security"]["score"] > 0.3:
            strategy["tools"].append("security_scanner")
            strategy["validation_criteria"].append("Security scan passes")
        
        if categories["performance"]["score"] > 0.3:
            strategy["tools"].append("performance_monitor")
            strategy["validation_criteria"].append("Performance within acceptable limits")
        
        if any(file_info["status"] in ["added", "modified"] for file_info in analysis["changes"]["files"]):
            strategy["tools"].append("act")  # For local workflow testing
            strategy["validation_criteria"].append("Workflow executes successfully in isolation")
        
        # Add validation criteria
        strategy["validation_criteria"].extend([
            "All workflows pass syntax validation",
            "No breaking changes in existing functionality",
            "Documentation updated if needed"
        ])
        
        return strategy
    
    def _create_rollback_plan(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Create a rollback plan for the changes."""
        
        risk_level = analysis["summary"]["overall_risk"]
        
        plan = {
            "complexity": "simple",
            "estimated_time": "5 minutes",
            "steps": [],
            "prerequisites": [],
            "validation": []
        }
        
        # Adjust plan based on risk and changes
        if risk_level == "high":
            plan.update({
                "complexity": "complex",
                "estimated_time": "15-30 minutes"
            })
        elif risk_level == "medium":
            plan.update({
                "complexity": "moderate",
                "estimated_time": "10-15 minutes"
            })
        
        # Add rollback steps
        plan["steps"] = [
            "1. Identify failing workflows or issues",
            "2. Revert workflow changes using git",
            "3. Verify workflows return to previous state",
            "4. Test critical workflows",
            "5. Monitor for stability"
        ]
        
        # Add prerequisites
        plan["prerequisites"] = [
            "Access to repository with write permissions",
            "Knowledge of git revert/reset commands",
            "Backup of current workflow state"
        ]
        
        # Add validation steps
        plan["validation"] = [
            "All workflows return to previous working state",
            "No new errors introduced by rollback",
            "Critical CI/CD functionality restored"
        ]
        
        # Add specific rollback commands
        if analysis["changes"]["files"]:
            file_paths = [f["file"] for f in analysis["changes"]["files"]]
            plan["commands"] = [
                f"git checkout HEAD~1 -- {' '.join(file_paths)}",
                "git commit -m 'Rollback workflow changes'",
                "git push origin main"
            ]
        
        return plan
    
    def generate_report(self, analysis: Dict[str, Any], format: str = "text") -> str:
        """Generate a formatted report of the impact analysis."""
        
        if format == "json":
            return json.dumps(analysis, indent=2)
        
        # Generate text report
        report_lines = []
        
        # Header
        report_lines.extend([
            "🔍 Workflow Change Impact Analysis Report",
            "=" * 50,
            f"Analysis Time: {analysis['metadata']['analysis_time']}",
            f"Base Reference: {analysis['metadata']['base_ref']}",
            f"Target Reference: {analysis['metadata']['target_ref']}",
            ""
        ])
        
        # Summary
        summary = analysis["summary"]
        risk_icon = {"high": "🔴", "medium": "🟡", "low": "🟢", "minimal": "⚪", "none": "⚫"}.get(summary["overall_risk"], "❓")
        
        report_lines.extend([
            "📊 Impact Summary",
            "-" * 20,
            f"{risk_icon} Overall Risk: {summary['overall_risk'].upper()}",
            f"📈 Impact Score: {summary['impact_score']:.3f}",
            f"📁 Changed Workflows: {summary['changed_workflows']}",
            f"  ➕ New: {summary['new_workflows']}",
            f"  ✏️ Modified: {summary['modified_workflows']}",
            f"  ➖ Deleted: {summary['deleted_workflows']}",
            ""
        ])
        
        # Impact Categories
        if any(cat["score"] > 0 for cat in analysis["changes"]["impact_categories"].values()):
            report_lines.extend([
                "🎯 Impact Categories",
                "-" * 20
            ])
            
            for category, data in analysis["changes"]["impact_categories"].items():
                if data["score"] > 0:
                    score_bar = "█" * int(data["score"] * 10) + "░" * (10 - int(data["score"] * 10))
                    report_lines.append(f"{category.title()}: {data['score']:.2f} [{score_bar}]")
                    
                    for change in data["changes"][:3]:  # Show top 3 changes
                        report_lines.append(f"  • {change['description']}")
            
            report_lines.append("")
        
        # File Changes
        if analysis["changes"]["files"]:
            report_lines.extend([
                "📋 File Changes",
                "-" * 20
            ])
            
            for file_info in analysis["changes"]["files"]:
                status_icon = {"added": "➕", "modified": "✏️", "deleted": "➖"}.get(file_info["status"], "❓")
                risk_icon = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(file_info["risk_level"], "❓")
                
                report_lines.append(f"{status_icon} {file_info['file']} ({risk_icon} {file_info['risk_level']} risk)")
                
                if file_info["change_details"]["critical_changes"]:
                    for critical in file_info["change_details"]["critical_changes"]:
                        report_lines.append(f"    ⚠️ {critical}")
            
            report_lines.append("")
        
        # Recommendations
        if analysis["recommendations"]:
            report_lines.extend([
                "💡 Recommendations",
                "-" * 20
            ])
            
            for rec in analysis["recommendations"]:
                report_lines.append(f"• {rec}")
            
            report_lines.append("")
        
        # Testing Strategy
        testing = analysis["testing_strategy"]
        if testing:
            report_lines.extend([
                "🧪 Testing Strategy",
                "-" * 20,
                f"Approach: {testing['approach'].title()}",
                f"Priority: {testing['priority'].title()}",
                f"Environments: {', '.join(testing['environments'])}",
                ""
            ])
            
            if testing["test_phases"]:
                report_lines.append("Test Phases:")
                for phase in testing["test_phases"]:
                    report_lines.append(f"  • {phase.replace('_', ' ').title()}")
                report_lines.append("")
        
        # Rollback Plan
        rollback = analysis["rollback_plan"]
        if rollback:
            report_lines.extend([
                "🔄 Rollback Plan",
                "-" * 20,
                f"Complexity: {rollback['complexity'].title()}",
                f"Estimated Time: {rollback['estimated_time']}",
                ""
            ])
            
            if rollback.get("commands"):
                report_lines.append("Quick Rollback Commands:")
                for cmd in rollback["commands"]:
                    report_lines.append(f"  $ {cmd}")
                report_lines.append("")
        
        return "\n".join(report_lines)


def main():
    """Main entry point for the workflow impact analyzer."""
    parser = argparse.ArgumentParser(
        description="Analyze workflow change impact",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                                    # Analyze changes against main
  %(prog)s --base origin/main --target HEAD  # Specify references
  %(prog)s --output json                     # JSON output
  %(prog)s --report-file impact-report.txt   # Save report to file
        """
    )
    
    parser.add_argument(
        "--base",
        type=str,
        default="main",
        help="Base reference for comparison (default: main)"
    )
    
    parser.add_argument(
        "--target",
        type=str,
        default="HEAD",
        help="Target reference for comparison (default: HEAD)"
    )
    
    parser.add_argument(
        "--output",
        choices=["text", "json"],
        default="text",
        help="Output format (default: text)"
    )
    
    parser.add_argument(
        "--report-file",
        type=str,
        help="Save report to file"
    )
    
    parser.add_argument(
        "--repo-root",
        type=Path,
        help="Repository root path (auto-detected if not specified)"
    )
    
    args = parser.parse_args()
    
    try:
        analyzer = WorkflowImpactAnalyzer(args.repo_root)
        analysis = analyzer.analyze_changes(args.base, args.target)
        
        # Generate report
        report = analyzer.generate_report(analysis, args.output)
        
        # Output report
        if args.report_file:
            with open(args.report_file, 'w', encoding='utf-8') as f:
                f.write(report)
            print(f"📄 Report saved to: {args.report_file}")
        else:
            print(report)
        
        # Exit with appropriate code
        risk_level = analysis["summary"]["overall_risk"]
        if risk_level == "high":
            sys.exit(2)  # High risk
        elif risk_level == "medium":
            sys.exit(1)  # Medium risk
        else:
            sys.exit(0)  # Low/minimal/no risk
            
    except Exception as e:
        print(f"❌ Analysis error: {e}")
        sys.exit(3)


if __name__ == "__main__":
    main()