"""Permission-related analysis rules."""

from typing import Any, Dict, List

from .base import BaseRule
from ..core.models import Finding, Severity


class OverlyPermissiveActionsRule(BaseRule):
    """Detects overly permissive actions in IAM policies."""
    
    title = "Overly Permissive Actions"
    description = "Detects actions that grant overly broad permissions"
    severity = Severity.CRITICAL
    category = "permissions"
    
    def analyze_statement(self, statement: Dict[str, Any], statement_index: int) -> List[Finding]:
        """Analyze statement for overly permissive actions."""
        findings = []
        
        # Only analyze Allow statements
        if statement.get("Effect") != "Allow":
            return findings
        
        # Get actions from the statement
        actions = []
        for action_field in ["Action", "NotAction"]:
            if action_field in statement:
                action_value = statement[action_field]
                if isinstance(action_value, str):
                    actions.append(action_value)
                elif isinstance(action_value, list):
                    actions.extend(action_value)
        
        # Check for overly permissive actions
        overly_permissive = []
        for action in actions:
            if self._is_overly_permissive(action):
                overly_permissive.append(action)
        
        if overly_permissive:
            action_list = ", ".join(overly_permissive)
            findings.append(
                self.create_finding(
                    title="Overly Permissive Actions Detected",
                    description=(
                        f"The policy grants overly permissive actions: {action_list}. "
                        "These actions provide broad access that could lead to security risks."
                    ),
                    severity=self.severity,
                    statement_index=statement_index,
                    action_pattern=action_list,
                    recommendation=(
                        "Replace overly permissive actions with specific, least-privilege actions. "
                        "Consider using AWS managed policies or creating custom policies with minimal required permissions."
                    ),
                    examples=[
                        "Replace 's3:*' with specific actions like 's3:GetObject', 's3:PutObject'",
                        "Replace 'ec2:*' with specific actions like 'ec2:DescribeInstances', 'ec2:StartInstances'",
                        "Replace 'iam:*' with specific actions like 'iam:GetUser', 'iam:ListUsers'"
                    ],
                    references=[
                        "https://docs.aws.amazon.com/IAM/latest/UserGuide/best-practices.html#grant-least-privilege",
                        "https://docs.aws.amazon.com/IAM/latest/UserGuide/access_policies_managed-vs-inline.html"
                    ]
                )
            )
        
        return findings
    
    def _is_overly_permissive(self, action: str) -> bool:
        """Check if an action is overly permissive."""
        # Service-level wildcards
        if action == "*":
            return True
        
        # Service-level permissions (e.g., "s3:*", "ec2:*")
        if action.endswith(":*"):
            service = action[:-2]
            # Some services are more critical than others
            critical_services = {
                "iam", "organizations", "billing", "budgets", "cloudtrail", 
                "config", "guardduty", "securityhub", "macie", "inspector"
            }
            return service in critical_services
        
        # Specific overly permissive actions
        overly_permissive_actions = {
            "iam:*",
            "organizations:*",
            "billing:*",
            "budgets:*",
            "cloudtrail:*",
            "config:*",
            "guardduty:*",
            "securityhub:*",
            "macie:*",
            "inspector:*",
            "s3:*",
            "ec2:*",
            "rds:*",
            "lambda:*",
            "cloudformation:*",
            "cloudwatch:*",
            "logs:*",
            "kms:*",
            "secretsmanager:*",
            "ssm:*",
            "sts:*",
        }
        
        return action in overly_permissive_actions


class WildcardActionsRule(BaseRule):
    """Detects wildcard actions in IAM policies."""
    
    title = "Wildcard Actions"
    description = "Detects wildcard actions that may be too permissive"
    severity = Severity.HIGH
    category = "permissions"
    
    def analyze_statement(self, statement: Dict[str, Any], statement_index: int) -> List[Finding]:
        """Analyze statement for wildcard actions."""
        findings = []
        
        # Only analyze Allow statements
        if statement.get("Effect") != "Allow":
            return findings
        
        # Get actions from the statement
        actions = []
        for action_field in ["Action", "NotAction"]:
            if action_field in statement:
                action_value = statement[action_field]
                if isinstance(action_value, str):
                    actions.append(action_value)
                elif isinstance(action_value, list):
                    actions.extend(action_value)
        
        # Check for wildcard actions
        wildcard_actions = []
        for action in actions:
            if "*" in action:
                wildcard_actions.append(action)
        
        if wildcard_actions:
            action_list = ", ".join(wildcard_actions)
            findings.append(
                self.create_finding(
                    title="Wildcard Actions Detected",
                    description=(
                        f"The policy contains wildcard actions: {action_list}. "
                        "Wildcard actions grant broad permissions and should be reviewed carefully."
                    ),
                    severity=self.severity,
                    statement_index=statement_index,
                    action_pattern=action_list,
                    recommendation=(
                        "Review wildcard actions and replace with specific actions where possible. "
                        "Consider the principle of least privilege and only grant necessary permissions."
                    ),
                    examples=[
                        "Replace 's3:Get*' with specific actions like 's3:GetObject', 's3:GetObjectAcl'",
                        "Replace 'ec2:Describe*' with specific actions like 'ec2:DescribeInstances', 'ec2:DescribeSecurityGroups'",
                        "Use AWS managed policies when possible instead of wildcard actions"
                    ],
                    references=[
                        "https://docs.aws.amazon.com/IAM/latest/UserGuide/best-practices.html#grant-least-privilege",
                        "https://docs.aws.amazon.com/IAM/latest/UserGuide/access_policies_managed-vs-inline.html"
                    ]
                )
            )
        
        return findings


class AdministrativeActionsRule(BaseRule):
    """Detects administrative actions that require special attention."""
    
    title = "Administrative Actions"
    description = "Detects administrative actions that should be carefully controlled"
    severity = Severity.HIGH
    category = "permissions"
    
    def analyze_statement(self, statement: Dict[str, Any], statement_index: int) -> List[Finding]:
        """Analyze statement for administrative actions."""
        findings = []
        
        # Only analyze Allow statements
        if statement.get("Effect") != "Allow":
            return findings
        
        # Get actions from the statement
        actions = []
        for action_field in ["Action", "NotAction"]:
            if action_field in statement:
                action_value = statement[action_field]
                if isinstance(action_value, str):
                    actions.append(action_value)
                elif isinstance(action_value, list):
                    actions.extend(action_value)
        
        # Check for administrative actions
        admin_actions = []
        for action in actions:
            if self.is_administrative_action(action):
                admin_actions.append(action)
        
        if admin_actions:
            action_list = ", ".join(admin_actions)
            findings.append(
                self.create_finding(
                    title="Administrative Actions Detected",
                    description=(
                        f"The policy grants administrative actions: {action_list}. "
                        "These actions can modify IAM users, roles, and policies and should be carefully controlled."
                    ),
                    severity=self.severity,
                    statement_index=statement_index,
                    action_pattern=action_list,
                    recommendation=(
                        "Review administrative actions and ensure they are necessary. "
                        "Consider using temporary credentials, MFA, and additional conditions for these actions."
                    ),
                    examples=[
                        "Add MFA conditions for administrative actions",
                        "Use temporary credentials instead of long-term access keys",
                        "Implement just-in-time access for administrative functions",
                        "Use AWS Organizations SCPs to restrict administrative actions"
                    ],
                    references=[
                        "https://docs.aws.amazon.com/IAM/latest/UserGuide/best-practices.html#use-iam-roles",
                        "https://docs.aws.amazon.com/IAM/latest/UserGuide/best-practices.html#require-mfa",
                        "https://docs.aws.amazon.com/organizations/latest/userguide/orgs_manage_policies_scps.html"
                    ]
                )
            )
        
        return findings


class DataAccessActionsRule(BaseRule):
    """Detects data access actions that may expose sensitive information."""
    
    title = "Data Access Actions"
    description = "Detects actions that provide access to data and should be carefully controlled"
    severity = Severity.MEDIUM
    category = "permissions"
    
    def analyze_statement(self, statement: Dict[str, Any], statement_index: int) -> List[Finding]:
        """Analyze statement for data access actions."""
        findings = []
        
        # Only analyze Allow statements
        if statement.get("Effect") != "Allow":
            return findings
        
        # Get actions from the statement
        actions = []
        for action_field in ["Action", "NotAction"]:
            if action_field in statement:
                action_value = statement[action_field]
                if isinstance(action_value, str):
                    actions.append(action_value)
                elif isinstance(action_value, list):
                    actions.extend(action_value)
        
        # Check for data access actions
        data_actions = []
        for action in actions:
            if self.is_data_access_action(action):
                data_actions.append(action)
        
        if data_actions:
            action_list = ", ".join(data_actions)
            findings.append(
                self.create_finding(
                    title="Data Access Actions Detected",
                    description=(
                        f"The policy grants data access actions: {action_list}. "
                        "These actions can access sensitive data and should be properly restricted."
                    ),
                    severity=self.severity,
                    statement_index=statement_index,
                    action_pattern=action_list,
                    recommendation=(
                        "Review data access actions and ensure proper resource restrictions are in place. "
                        "Consider implementing data classification and access controls."
                    ),
                    examples=[
                        "Add resource ARN restrictions to limit data access",
                        "Use bucket policies and object-level permissions for S3",
                        "Implement encryption at rest and in transit",
                        "Use AWS KMS for encryption key management"
                    ],
                    references=[
                        "https://docs.aws.amazon.com/AmazonS3/latest/userguide/using-with-s3-actions.html",
                        "https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/access-control-identity-based.html",
                        "https://docs.aws.amazon.com/kms/latest/developerguide/overview.html"
                    ]
                )
            )
        
        return findings
