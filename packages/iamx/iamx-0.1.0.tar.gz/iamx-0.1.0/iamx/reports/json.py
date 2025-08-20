"""JSON report generator for IAM policy analysis."""

import json
from typing import Any, Dict, Union

from ..core.models import AnalysisResult, BulkAnalysisResult, Finding, Severity


class JsonReporter:
    """Generates JSON reports for IAM policy analysis."""
    
    def generate_report(self, result: Union[AnalysisResult, BulkAnalysisResult]) -> str:
        """Generate a JSON report from analysis results."""
        if hasattr(result, 'passed'):
            return self._generate_single_report(result)
        else:
            return self._generate_bulk_report(result)
    
    def _generate_single_report(self, result: AnalysisResult) -> str:
        """Generate a JSON report for a single policy analysis."""
        report = {
            "metadata": {
                "tool": "iamx",
                "version": "0.1.0",
                "generated_at": result.analyzed_at.isoformat(),
                "analysis_type": "single_policy",
            },
            "policy": {
                "filename": result.metadata.filename,
                "policy_name": result.metadata.policy_name,
                "policy_id": result.metadata.policy_id,
                "version": result.metadata.version,
                "statement_count": result.metadata.statement_count,
                "action_count": result.metadata.action_count,
                "resource_count": result.metadata.resource_count,
            },
            "results": {
                "passed": result.passed,
                "risk_score": result.risk_score,
                "total_findings": result.total_findings,
                "summary": result.summary,
            },
            "findings": [self._serialize_finding(finding) for finding in result.findings],
        }
        
        return json.dumps(report, indent=2, default=str)
    
    def _generate_bulk_report(self, result: BulkAnalysisResult) -> str:
        """Generate a JSON report for bulk policy analysis."""
        report = {
            "metadata": {
                "tool": "iamx",
                "version": "0.1.0",
                "generated_at": result.analyzed_at.isoformat(),
                "analysis_type": "bulk_policies",
            },
            "summary": {
                "total_policies": result.total_policies,
                "failed_policies": result.failed_policies,
                "overall_risk_score": result.overall_risk_score,
                "findings_summary": result.summary,
            },
            "policies": [
                {
                    "filename": policy_result.metadata.filename,
                    "policy_name": policy_result.metadata.policy_name,
                    "policy_id": policy_result.metadata.policy_id,
                    "version": policy_result.metadata.version,
                    "statement_count": policy_result.metadata.statement_count,
                    "action_count": policy_result.metadata.action_count,
                    "resource_count": policy_result.metadata.resource_count,
                    "results": {
                        "passed": policy_result.passed,
                        "risk_score": policy_result.risk_score,
                        "total_findings": policy_result.total_findings,
                        "summary": policy_result.summary,
                    },
                    "findings": [self._serialize_finding(finding) for finding in policy_result.findings],
                }
                for policy_result in result.results
            ],
        }
        
        return json.dumps(report, indent=2, default=str)
    
    def _serialize_finding(self, finding: Finding) -> Dict[str, Any]:
        """Serialize a finding to a dictionary."""
        return {
            "id": finding.id,
            "title": finding.title,
            "description": finding.description,
            "severity": finding.severity.value,
            "category": finding.category,
            "statement_index": finding.statement_index,
            "action_pattern": finding.action_pattern,
            "resource_pattern": finding.resource_pattern,
            "condition_pattern": finding.condition_pattern,
            "recommendation": finding.recommendation,
            "examples": finding.examples,
            "references": finding.references,
            "created_at": finding.created_at.isoformat(),
        }
