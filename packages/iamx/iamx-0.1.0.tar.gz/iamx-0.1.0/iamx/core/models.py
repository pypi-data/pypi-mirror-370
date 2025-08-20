"""Core data models for IAM policy analysis."""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field


class Severity(str, Enum):
    """Severity levels for policy findings."""
    
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class Finding(BaseModel):
    """Represents a single finding in an IAM policy analysis."""
    
    id: str = Field(..., description="Unique identifier for the finding")
    title: str = Field(..., description="Short title describing the finding")
    description: str = Field(..., description="Detailed description of the finding")
    severity: Severity = Field(..., description="Severity level of the finding")
    category: str = Field(..., description="Category of the finding (e.g., 'permissions', 'resources')")
    statement_index: Optional[int] = Field(None, description="Index of the policy statement where finding was found")
    action_pattern: Optional[str] = Field(None, description="Pattern of actions that triggered the finding")
    resource_pattern: Optional[str] = Field(None, description="Pattern of resources that triggered the finding")
    condition_pattern: Optional[str] = Field(None, description="Pattern of conditions that triggered the finding")
    recommendation: str = Field(..., description="Recommended fix for the finding")
    examples: List[str] = Field(default_factory=list, description="Example fixes for the finding")
    references: List[str] = Field(default_factory=list, description="Reference links for more information")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="When the finding was created")


class PolicyMetadata(BaseModel):
    """Metadata about an analyzed IAM policy."""
    
    filename: Optional[str] = Field(None, description="Name of the policy file")
    policy_name: Optional[str] = Field(None, description="Name of the policy")
    policy_id: Optional[str] = Field(None, description="ID of the policy")
    version: Optional[str] = Field(None, description="Version of the policy")
    statement_count: int = Field(..., description="Number of statements in the policy")
    action_count: int = Field(..., description="Total number of actions across all statements")
    resource_count: int = Field(..., description="Total number of resources across all statements")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="When the analysis was performed")


class AnalysisResult(BaseModel):
    """Result of analyzing an IAM policy."""
    
    metadata: PolicyMetadata = Field(..., description="Metadata about the analyzed policy")
    findings: List[Finding] = Field(default_factory=list, description="List of findings from the analysis")
    summary: Dict[str, int] = Field(default_factory=dict, description="Summary of findings by severity")
    risk_score: float = Field(..., description="Overall risk score (0.0 to 10.0)")
    passed: bool = Field(..., description="Whether the policy passed the analysis threshold")
    raw_policy: Dict[str, Any] = Field(..., description="The original policy document")
    analyzed_at: datetime = Field(default_factory=datetime.utcnow, description="When the analysis was performed")

    def __init__(self, **data):
        super().__init__(**data)
        # Calculate summary
        self.summary = {}
        for severity in Severity:
            count = len([f for f in self.findings if f.severity == severity])
            if count > 0:
                self.summary[severity.value] = count

    @property
    def critical_count(self) -> int:
        """Number of critical findings."""
        return self.summary.get(Severity.CRITICAL.value, 0)

    @property
    def high_count(self) -> int:
        """Number of high severity findings."""
        return self.summary.get(Severity.HIGH.value, 0)

    @property
    def medium_count(self) -> int:
        """Number of medium severity findings."""
        return self.summary.get(Severity.MEDIUM.value, 0)

    @property
    def low_count(self) -> int:
        """Number of low severity findings."""
        return self.summary.get(Severity.LOW.value, 0)

    @property
    def total_findings(self) -> int:
        """Total number of findings."""
        return len(self.findings)


class AnalysisConfig(BaseModel):
    """Configuration for policy analysis."""
    
    fail_on_severity: Severity = Field(
        default=Severity.CRITICAL, 
        description="Minimum severity level that causes analysis to fail"
    )
    include_info: bool = Field(
        default=True, 
        description="Whether to include informational findings"
    )
    max_findings_per_category: int = Field(
        default=10, 
        description="Maximum number of findings to report per category"
    )
    enable_ai_summaries: bool = Field(
        default=False, 
        description="Whether to enable AI-powered summaries (requires API key)"
    )
    custom_rules: List[str] = Field(
        default_factory=list, 
        description="Paths to custom rule files"
    )


class BulkAnalysisResult(BaseModel):
    """Result of analyzing multiple IAM policies."""
    
    results: List[AnalysisResult] = Field(..., description="Results for each analyzed policy")
    summary: Dict[str, int] = Field(default_factory=dict, description="Overall summary across all policies")
    total_policies: int = Field(..., description="Total number of policies analyzed")
    failed_policies: int = Field(default=0, description="Number of policies that failed analysis")
    overall_risk_score: float = Field(default=0.0, description="Average risk score across all policies")
    analyzed_at: datetime = Field(default_factory=datetime.utcnow, description="When the bulk analysis was performed")

    def __init__(self, **data):
        super().__init__(**data)
        # Calculate overall summary
        self.summary = {}
        for severity in Severity:
            count = sum(r.summary.get(severity.value, 0) for r in self.results)
            if count > 0:
                self.summary[severity.value] = count
        
        # Calculate failed policies
        self.failed_policies = len([r for r in self.results if not r.passed])
        
        # Calculate overall risk score
        if self.results:
            self.overall_risk_score = sum(r.risk_score for r in self.results) / len(self.results)
        else:
            self.overall_risk_score = 0.0
