"""IAM Policy Analyzer - Main analysis engine."""

import math
from typing import Any, Dict, List, Optional

from .models import AnalysisConfig, AnalysisResult, BulkAnalysisResult, Finding, PolicyMetadata, Severity
from .parser import PolicyParser
from ..rules import (
    OverlyPermissiveActionsRule,
    WildcardActionsRule,
    AdministrativeActionsRule,
    DataAccessActionsRule,
    WildcardResourcesRule,
    MissingResourceRestrictionsRule,
    CrossAccountResourceRule,
)


class PolicyAnalyzer:
    """Main analyzer for IAM policies."""
    
    def __init__(self, config: Optional[AnalysisConfig] = None):
        self.config = config or AnalysisConfig()
        self.parser = PolicyParser()
        self.rules = self._load_rules()
    
    def _load_rules(self) -> List[Any]:
        """Load all analysis rules."""
        return [
            OverlyPermissiveActionsRule(),
            WildcardActionsRule(),
            AdministrativeActionsRule(),
            DataAccessActionsRule(),
            WildcardResourcesRule(),
            MissingResourceRestrictionsRule(),
            CrossAccountResourceRule(),
        ]
    
    def analyze_file(self, file_path: str) -> AnalysisResult:
        """Analyze a single policy file."""
        # Parse the policy
        policy = self.parser.parse_file(file_path)
        
        # Extract metadata
        metadata = self.parser.extract_metadata(policy)
        
        # Analyze the policy
        findings = self._analyze_policy(policy)
        
        # Calculate risk score
        risk_score = self._calculate_risk_score(findings)
        
        # Determine if policy passed
        passed = self._check_policy_passed(findings)
        
        return AnalysisResult(
            metadata=metadata,
            findings=findings,
            risk_score=risk_score,
            passed=passed,
            raw_policy=policy,
        )
    
    def analyze_string(self, policy_content: str, filename: Optional[str] = None) -> AnalysisResult:
        """Analyze a policy from a string."""
        # Parse the policy
        policy = self.parser.parse_string(policy_content, filename)
        
        # Extract metadata
        metadata = self.parser.extract_metadata(policy)
        
        # Analyze the policy
        findings = self._analyze_policy(policy)
        
        # Calculate risk score
        risk_score = self._calculate_risk_score(findings)
        
        # Determine if policy passed
        passed = self._check_policy_passed(findings)
        
        return AnalysisResult(
            metadata=metadata,
            findings=findings,
            risk_score=risk_score,
            passed=passed,
            raw_policy=policy,
        )
    
    def analyze_multiple_files(self, file_paths: List[str]) -> BulkAnalysisResult:
        """Analyze multiple policy files."""
        results = []
        
        for file_path in file_paths:
            try:
                result = self.analyze_file(file_path)
                results.append(result)
            except Exception as e:
                # Create a failed result for files that can't be analyzed
                metadata = PolicyMetadata(
                    filename=file_path,
                    statement_count=0,
                    action_count=0,
                    resource_count=0,
                )
                failed_result = AnalysisResult(
                    metadata=metadata,
                    findings=[],
                    risk_score=10.0,  # Maximum risk for failed analysis
                    passed=False,
                    raw_policy={},
                )
                results.append(failed_result)
        
        return BulkAnalysisResult(
            results=results,
            total_policies=len(file_paths),
        )
    
    def _analyze_policy(self, policy: Dict[str, Any]) -> List[Finding]:
        """Analyze a policy using all rules."""
        findings = []
        statements = policy.get("Statement", [])
        
        for statement_index, statement in enumerate(statements):
            # Run each rule on the statement
            for rule in self.rules:
                try:
                    rule_findings = rule.analyze_statement(statement, statement_index)
                    findings.extend(rule_findings)
                except Exception as e:
                    # Log error but continue with other rules
                    print(f"Error running rule {rule.__class__.__name__}: {e}")
        
        # Filter findings based on configuration
        findings = self._filter_findings(findings)
        
        # Limit findings per category if configured
        if self.config.max_findings_per_category > 0:
            findings = self._limit_findings_per_category(findings)
        
        return findings
    
    def _filter_findings(self, findings: List[Finding]) -> List[Finding]:
        """Filter findings based on configuration."""
        filtered = []
        
        for finding in findings:
            # Skip info findings if not included
            if finding.severity == Severity.INFO and not self.config.include_info:
                continue
            
            filtered.append(finding)
        
        return filtered
    
    def _limit_findings_per_category(self, findings: List[Finding]) -> List[Finding]:
        """Limit the number of findings per category."""
        limited = []
        category_counts = {}
        
        for finding in findings:
            category = finding.category
            if category not in category_counts:
                category_counts[category] = 0
            
            if category_counts[category] < self.config.max_findings_per_category:
                limited.append(finding)
                category_counts[category] += 1
        
        return limited
    
    def _calculate_risk_score(self, findings: List[Finding]) -> float:
        """Calculate overall risk score based on findings."""
        if not findings:
            return 0.0
        
        # Weight factors for different severity levels
        # Reduced weights to prevent over-scoring
        severity_weights = {
            Severity.CRITICAL: 8.0,
            Severity.HIGH: 5.0,
            Severity.MEDIUM: 2.5,
            Severity.LOW: 0.8,
            Severity.INFO: 0.3,
        }
        
        # Calculate weighted sum of all findings
        total_weight = 0.0
        for finding in findings:
            weight = severity_weights.get(finding.severity, 1.0)
            total_weight += weight
        
        # Calculate base score with better scaling
        # Use logarithmic scaling to prevent multiple medium findings from maxing out
        if total_weight > 0:
            # Apply logarithmic scaling: log(total_weight + 1) * 2.5
            # This provides better score accuracy while maintaining good status accuracy
            risk_score = min(10.0, math.log(total_weight + 1) * 2.5)
        else:
            risk_score = 0.0
        
        return round(risk_score, 2)
    
    def _check_policy_passed(self, findings: List[Finding]) -> bool:
        """Check if the policy passed based on risk score thresholds."""
        # Calculate risk score first
        risk_score = self._calculate_risk_score(findings)
        
        # Check for CRITICAL or HIGH findings first
        critical_high_findings = [f for f in findings if f.severity in [Severity.CRITICAL, Severity.HIGH]]
        
        # If there are any CRITICAL or HIGH findings, the policy should fail
        if critical_high_findings:
            return False
        
        # Otherwise, use risk score threshold
        # LOW (0-4): PASS
        # MEDIUM (4-6): PASS with warnings  
        # HIGH (6-10): FAIL
        if risk_score >= 6.0:
            return False  # HIGH risk = FAIL
        else:
            return True   # LOW or MEDIUM risk = PASS
    
    def get_findings_by_severity(self, findings: List[Finding], severity: Severity) -> List[Finding]:
        """Get findings filtered by severity."""
        return [f for f in findings if f.severity == severity]
    
    def get_findings_by_category(self, findings: List[Finding], category: str) -> List[Finding]:
        """Get findings filtered by category."""
        return [f for f in findings if f.category == category]
    
    def get_summary_stats(self, findings: List[Finding]) -> Dict[str, int]:
        """Get summary statistics for findings."""
        summary = {}
        for severity in Severity:
            count = len(self.get_findings_by_severity(findings, severity))
            if count > 0:
                summary[severity.value] = count
        return summary
