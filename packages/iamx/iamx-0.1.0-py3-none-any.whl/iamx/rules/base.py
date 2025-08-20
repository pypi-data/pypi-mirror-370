"""Base rule class for IAM policy analysis."""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

from ..core.models import Finding, Severity


class BaseRule(ABC):
    """Base class for all IAM policy analysis rules."""
    
    def __init__(self):
        self.id = self.__class__.__name__
        self.title = getattr(self, 'title', self.__class__.__name__)
        self.description = getattr(self, 'description', '')
        self.severity = getattr(self, 'severity', Severity.MEDIUM)
        self.category = getattr(self, 'category', 'general')
    
    @abstractmethod
    def analyze_statement(self, statement: Dict[str, Any], statement_index: int) -> List[Finding]:
        """Analyze a single policy statement and return findings."""
        pass
    
    def create_finding(
        self,
        title: str,
        description: str,
        severity: Severity,
        statement_index: Optional[int] = None,
        action_pattern: Optional[str] = None,
        resource_pattern: Optional[str] = None,
        condition_pattern: Optional[str] = None,
        recommendation: str = "",
        examples: Optional[List[str]] = None,
        references: Optional[List[str]] = None,
    ) -> Finding:
        """Create a finding with the given parameters."""
        return Finding(
            id=f"{self.id}_{statement_index or 'general'}",
            title=title,
            description=description,
            severity=severity,
            category=self.category,
            statement_index=statement_index,
            action_pattern=action_pattern,
            resource_pattern=resource_pattern,
            condition_pattern=condition_pattern,
            recommendation=recommendation,
            examples=examples or [],
            references=references or [],
        )
    
    def has_wildcard_actions(self, actions: List[str]) -> bool:
        """Check if actions contain wildcards."""
        return any("*" in action for action in actions)
    
    def has_wildcard_resources(self, resources: List[str]) -> bool:
        """Check if resources contain wildcards."""
        return any("*" in resource for resource in resources)
    
    def get_service_from_action(self, action: str) -> str:
        """Extract service name from an action."""
        if ":" in action:
            return action.split(":")[0]
        return ""
    
    def get_action_name(self, action: str) -> str:
        """Extract action name from a full action string."""
        if ":" in action:
            return action.split(":")[1]
        return action
    
    def is_administrative_action(self, action: str) -> bool:
        """Check if an action is administrative in nature."""
        admin_actions = {
            "iam:CreateUser",
            "iam:DeleteUser", 
            "iam:AttachUserPolicy",
            "iam:DetachUserPolicy",
            "iam:CreateRole",
            "iam:DeleteRole",
            "iam:AttachRolePolicy",
            "iam:DetachRolePolicy",
            "iam:CreatePolicy",
            "iam:DeletePolicy",
            "iam:AttachPolicy",
            "iam:DetachPolicy",
            "iam:CreateAccessKey",
            "iam:DeleteAccessKey",
            "iam:UpdateAccessKey",
            "iam:CreateLoginProfile",
            "iam:DeleteLoginProfile",
            "iam:UpdateLoginProfile",
            "iam:AddUserToGroup",
            "iam:RemoveUserFromGroup",
            "iam:CreateGroup",
            "iam:DeleteGroup",
            "iam:AttachGroupPolicy",
            "iam:DetachGroupPolicy",
            "iam:CreateServiceLinkedRole",
            "iam:DeleteServiceLinkedRole",
            "iam:PassRole",
            "iam:AssumeRole",
            "iam:AssumeRolePolicy",
            "iam:UpdateAssumeRolePolicy",
            "iam:TagRole",
            "iam:UntagRole",
            "iam:TagUser",
            "iam:UntagUser",
            "iam:TagPolicy",
            "iam:UntagPolicy",
            "iam:TagGroup",
            "iam:UntagGroup",
            "iam:CreateInstanceProfile",
            "iam:DeleteInstanceProfile",
            "iam:AddRoleToInstanceProfile",
            "iam:RemoveRoleFromInstanceProfile",
            "iam:CreateSAMLProvider",
            "iam:DeleteSAMLProvider",
            "iam:UpdateSAMLProvider",
            "iam:CreateOpenIDConnectProvider",
            "iam:DeleteOpenIDConnectProvider",
            "iam:UpdateOpenIDConnectProviderThumbprint",
            "iam:CreateVirtualMFADevice",
            "iam:DeleteVirtualMFADevice",
            "iam:EnableMFADevice",
            "iam:DeactivateMFADevice",
            "iam:ResyncMFADevice",
            "iam:CreateAccountAlias",
            "iam:DeleteAccountAlias",
            "iam:UpdateAccountPasswordPolicy",
            "iam:UpdateAccountEmailAddress",
            "iam:UpdateAccountName",
            "iam:UpdateAccountDescription",
            "iam:UpdateAccountPasswordPolicy",
            "iam:UpdateAccountEmailAddress",
            "iam:UpdateAccountName",
            "iam:UpdateAccountDescription",
        }
        return action in admin_actions
    
    def is_data_access_action(self, action: str) -> bool:
        """Check if an action provides data access."""
        data_actions = {
            "s3:GetObject",
            "s3:GetObjectVersion",
            "s3:GetObjectAcl",
            "s3:GetObjectVersionAcl",
            "s3:GetObjectTagging",
            "s3:GetObjectVersionTagging",
            "s3:GetObjectTorrent",
            "s3:GetObjectVersionTorrent",
            "s3:GetObjectRetention",
            "s3:GetObjectLegalHold",
            "s3:GetObjectVersionRetention",
            "s3:GetObjectVersionLegalHold",
            "s3:GetObjectLockConfiguration",
            "s3:GetObjectLockRetention",
            "s3:GetObjectLockLegalHold",
            "s3:GetObjectVersionLockRetention",
            "s3:GetObjectVersionLockLegalHold",
            "dynamodb:GetItem",
            "dynamodb:BatchGetItem",
            "dynamodb:Query",
            "dynamodb:Scan",
            "dynamodb:DescribeTable",
            "dynamodb:ListTables",
            "dynamodb:DescribeBackup",
            "dynamodb:ListBackups",
            "dynamodb:DescribeContinuousBackups",
            "dynamodb:DescribeGlobalTable",
            "dynamodb:ListGlobalTables",
            "dynamodb:DescribeLimits",
            "dynamodb:DescribeTimeToLive",
            "dynamodb:ListTagsOfResource",
            "dynamodb:DescribeContributorInsights",
            "dynamodb:DescribeEndpoints",
            "dynamodb:DescribeExport",
            "dynamodb:ListExports",
            "dynamodb:DescribeKinesisStreamingDestination",
            "dynamodb:DescribeTableReplicaAutoScaling",
            "dynamodb:DescribeGlobalTableSettings",
            "dynamodb:DescribeReplicaAutoScaling",
            "dynamodb:DescribeTableRestoreInProgress",
            "dynamodb:DescribeImport",
            "dynamodb:ListImports",
            "dynamodb:DescribeTableReplicaAutoScaling",
            "dynamodb:DescribeGlobalTableSettings",
            "dynamodb:DescribeReplicaAutoScaling",
            "dynamodb:DescribeTableRestoreInProgress",
            "dynamodb:DescribeImport",
            "dynamodb:ListImports",
        }
        return action in data_actions
    
    def is_write_action(self, action: str) -> bool:
        """Check if an action allows writing/modifying resources."""
        write_actions = {
            "s3:PutObject",
            "s3:PutObjectAcl",
            "s3:PutObjectTagging",
            "s3:PutObjectVersionTagging",
            "s3:PutObjectRetention",
            "s3:PutObjectLegalHold",
            "s3:PutObjectVersionRetention",
            "s3:PutObjectVersionLegalHold",
            "s3:PutObjectLockConfiguration",
            "s3:PutObjectLockRetention",
            "s3:PutObjectLockLegalHold",
            "s3:PutObjectVersionLockRetention",
            "s3:PutObjectVersionLockLegalHold",
            "s3:DeleteObject",
            "s3:DeleteObjectVersion",
            "s3:DeleteObjectTagging",
            "s3:DeleteObjectVersionTagging",
            "s3:DeleteObjectRetention",
            "s3:DeleteObjectLegalHold",
            "s3:DeleteObjectVersionRetention",
            "s3:DeleteObjectVersionLegalHold",
            "s3:DeleteObjectLockRetention",
            "s3:DeleteObjectLockLegalHold",
            "s3:DeleteObjectVersionLockRetention",
            "s3:DeleteObjectVersionLockLegalHold",
            "dynamodb:PutItem",
            "dynamodb:BatchWriteItem",
            "dynamodb:UpdateItem",
            "dynamodb:DeleteItem",
            "dynamodb:CreateTable",
            "dynamodb:DeleteTable",
            "dynamodb:UpdateTable",
            "dynamodb:CreateBackup",
            "dynamodb:DeleteBackup",
            "dynamodb:UpdateContinuousBackups",
            "dynamodb:CreateGlobalTable",
            "dynamodb:DeleteGlobalTable",
            "dynamodb:UpdateGlobalTable",
            "dynamodb:UpdateGlobalTableSettings",
            "dynamodb:UpdateTimeToLive",
            "dynamodb:TagResource",
            "dynamodb:UntagResource",
            "dynamodb:UpdateContributorInsights",
            "dynamodb:UpdateTableReplicaAutoScaling",
            "dynamodb:UpdateGlobalTableSettings",
            "dynamodb:UpdateReplicaAutoScaling",
            "dynamodb:RestoreTableFromBackup",
            "dynamodb:RestoreTableToPointInTime",
            "dynamodb:CreateTableReplicaAutoScaling",
            "dynamodb:DeleteTableReplicaAutoScaling",
            "dynamodb:CreateGlobalTableSettings",
            "dynamodb:DeleteGlobalTableSettings",
            "dynamodb:CreateReplicaAutoScaling",
            "dynamodb:DeleteReplicaAutoScaling",
            "dynamodb:CreateTableRestoreInProgress",
            "dynamodb:DeleteTableRestoreInProgress",
            "dynamodb:CreateImport",
            "dynamodb:DeleteImport",
            "dynamodb:CreateTableReplicaAutoScaling",
            "dynamodb:DeleteTableReplicaAutoScaling",
            "dynamodb:CreateGlobalTableSettings",
            "dynamodb:DeleteGlobalTableSettings",
            "dynamodb:CreateReplicaAutoScaling",
            "dynamodb:DeleteReplicaAutoScaling",
            "dynamodb:CreateTableRestoreInProgress",
            "dynamodb:DeleteTableRestoreInProgress",
            "dynamodb:CreateImport",
            "dynamodb:DeleteImport",
        }
        return action in write_actions
