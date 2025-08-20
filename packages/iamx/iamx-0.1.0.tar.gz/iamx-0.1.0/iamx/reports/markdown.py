"""Markdown report generator for IAM policy analysis."""

from datetime import datetime
from typing import Any, Union

from ..core.models import AnalysisResult, BulkAnalysisResult, Finding, Severity


class MarkdownReporter:
    """Generates Markdown reports for IAM policy analysis."""
    
    def generate_report(self, result: Union[AnalysisResult, BulkAnalysisResult]) -> str:
        """Generate a Markdown report from analysis results."""
        if hasattr(result, 'passed'):
            return self._generate_single_report(result)
        else:
            return self._generate_bulk_report(result)
    
    def _generate_single_report(self, result: AnalysisResult) -> str:
        """Generate a Markdown report for a single policy analysis."""
        lines = []
        
        # Header
        filename = result.metadata.filename or "Policy"
        lines.append(f"# IAM Policy Analysis Report: {filename}")
        lines.append("")
        lines.append(f"**Generated:** {result.analyzed_at.strftime('%Y-%m-%d %H:%M:%S UTC')}")
        lines.append("")
        
        # Executive Summary
        lines.append("## Executive Summary")
        lines.append("")
        
        status_emoji = "✅" if result.passed else "❌"
        status_text = "PASSED" if result.passed else "FAILED"
        lines.append(f"- **Status:** {status_emoji} {status_text}")
        lines.append(f"- **Risk Score:** {result.risk_score}/10.0")
        lines.append(f"- **Total Findings:** {result.total_findings}")
        lines.append(f"- **Policy Statements:** {result.metadata.statement_count}")
        lines.append(f"- **Total Actions:** {result.metadata.action_count}")
        lines.append(f"- **Total Resources:** {result.metadata.resource_count}")
        lines.append("")
        
        # Policy Metadata
        lines.append("## Policy Information")
        lines.append("")
        if result.metadata.policy_name:
            lines.append(f"- **Policy Name:** {result.metadata.policy_name}")
        if result.metadata.policy_id:
            lines.append(f"- **Policy ID:** {result.metadata.policy_id}")
        if result.metadata.version:
            lines.append(f"- **Version:** {result.metadata.version}")
        lines.append("")
        
        # Findings Summary
        if result.findings:
            lines.append("## Findings Summary")
            lines.append("")
            
            severity_counts = {}
            for severity in Severity:
                count = len([f for f in result.findings if f.severity == severity])
                if count > 0:
                    severity_counts[severity] = count
            
            for severity in [Severity.CRITICAL, Severity.HIGH, Severity.MEDIUM, Severity.LOW, Severity.INFO]:
                if severity in severity_counts:
                    emoji = self._get_severity_emoji(severity)
                    lines.append(f"- {emoji} **{severity.value.title()}:** {severity_counts[severity]} findings")
            lines.append("")
        
        # Detailed Findings
        if result.findings:
            lines.append("## Detailed Findings")
            lines.append("")
            
            for severity in [Severity.CRITICAL, Severity.HIGH, Severity.MEDIUM, Severity.LOW, Severity.INFO]:
                severity_findings = [f for f in result.findings if f.severity == severity]
                if severity_findings:
                    emoji = self._get_severity_emoji(severity)
                    lines.append(f"### {emoji} {severity.value.title()} Severity")
                    lines.append("")
                    
                    for finding in severity_findings:
                        lines.extend(self._format_finding(finding))
                        lines.append("")
        else:
            lines.append("## Detailed Findings")
            lines.append("")
            lines.append("✅ **No security issues found!**")
            lines.append("")
        
        # Recommendations
        if result.findings:
            lines.append("## Recommendations")
            lines.append("")
            lines.append("Based on the analysis, consider the following recommendations:")
            lines.append("")
            
            # Group recommendations by category
            recommendations_by_category = {}
            for finding in result.findings:
                category = finding.category
                if category not in recommendations_by_category:
                    recommendations_by_category[category] = []
                recommendations_by_category[category].append(finding.recommendation)
            
            for category, recommendations in recommendations_by_category.items():
                lines.append(f"### {category.title()}")
                lines.append("")
                for recommendation in recommendations:
                    lines.append(f"- {recommendation}")
                lines.append("")
        
        return "\n".join(lines)
    
    def _generate_bulk_report(self, result: BulkAnalysisResult) -> str:
        """Generate a Markdown report for bulk policy analysis."""
        lines = []
        
        # Header
        lines.append("# IAM Policy Bulk Analysis Report")
        lines.append("")
        lines.append(f"**Generated:** {result.analyzed_at.strftime('%Y-%m-%d %H:%M:%S UTC')}")
        lines.append("")
        
        # Executive Summary
        lines.append("## Executive Summary")
        lines.append("")
        lines.append(f"- **Total Policies Analyzed:** {result.total_policies}")
        lines.append(f"- **Failed Policies:** {result.failed_policies}")
        lines.append(f"- **Overall Risk Score:** {result.overall_risk_score}/10.0")
        lines.append("")
        
        # Overall Findings Summary
        if result.summary:
            lines.append("## Overall Findings Summary")
            lines.append("")
            
            for severity in [Severity.CRITICAL, Severity.HIGH, Severity.MEDIUM, Severity.LOW, Severity.INFO]:
                count = result.summary.get(severity.value, 0)
                if count > 0:
                    emoji = self._get_severity_emoji(severity)
                    lines.append(f"- {emoji} **{severity.value.title()}:** {count} findings")
            lines.append("")
        
        # Individual Policy Results
        lines.append("## Individual Policy Results")
        lines.append("")
        
        for policy_result in result.results:
            filename = policy_result.metadata.filename or "Unknown"
            status_emoji = "✅" if policy_result.passed else "❌"
            status_text = "PASSED" if policy_result.passed else "FAILED"
            
            lines.append(f"### {filename}")
            lines.append("")
            lines.append(f"- **Status:** {status_emoji} {status_text}")
            lines.append(f"- **Risk Score:** {policy_result.risk_score}/10.0")
            lines.append(f"- **Findings:** {policy_result.total_findings}")
            lines.append(f"- **Statements:** {policy_result.metadata.statement_count}")
            lines.append("")
            
            # Show findings summary for this policy
            if policy_result.findings:
                severity_counts = {}
                for severity in Severity:
                    count = len([f for f in policy_result.findings if f.severity == severity])
                    if count > 0:
                        severity_counts[severity] = count
                
                for severity in [Severity.CRITICAL, Severity.HIGH, Severity.MEDIUM, Severity.LOW, Severity.INFO]:
                    if severity in severity_counts:
                        emoji = self._get_severity_emoji(severity)
                        lines.append(f"  - {emoji} {severity.value.title()}: {severity_counts[severity]}")
                lines.append("")
        
        return "\n".join(lines)
    
    def _format_finding(self, finding: Finding) -> list:
        """Format a single finding for Markdown."""
        lines = []
        
        # Finding header
        lines.append(f"#### {finding.title}")
        lines.append("")
        
        # Description
        lines.append(f"**Description:** {finding.description}")
        lines.append("")
        
        # Statement info
        if finding.statement_index is not None:
            lines.append(f"**Statement:** {finding.statement_index}")
            lines.append("")
        
        # Patterns
        if finding.action_pattern:
            lines.append(f"**Actions:** `{finding.action_pattern}`")
            lines.append("")
        if finding.resource_pattern:
            lines.append(f"**Resources:** `{finding.resource_pattern}`")
            lines.append("")
        if finding.condition_pattern:
            lines.append(f"**Conditions:** `{finding.condition_pattern}`")
            lines.append("")
        
        # Recommendation
        if finding.recommendation:
            lines.append("**Recommendation:**")
            lines.append("")
            lines.append(f"{finding.recommendation}")
            lines.append("")
        
        # Examples
        if finding.examples:
            lines.append("**Examples:**")
            lines.append("")
            for example in finding.examples:
                lines.append(f"- {example}")
            lines.append("")
        
        # References
        if finding.references:
            lines.append("**References:**")
            lines.append("")
            for i, ref in enumerate(finding.references, 1):
                lines.append(f"{i}. {ref}")
            lines.append("")
        
        return lines
    
    def _get_severity_emoji(self, severity: Severity) -> str:
        """Get emoji for severity level."""
        emoji_map = {
            Severity.CRITICAL: "❌",
            Severity.HIGH: "⚠️",
            Severity.MEDIUM: "🔶",
            Severity.LOW: "ℹ️",
            Severity.INFO: "✅",
        }
        return emoji_map.get(severity, "•")
