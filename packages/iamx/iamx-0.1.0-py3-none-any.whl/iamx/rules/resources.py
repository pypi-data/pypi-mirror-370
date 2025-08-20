"""Resource-related analysis rules."""

from typing import Any, Dict, List

from .base import BaseRule
from ..core.models import Finding, Severity


class WildcardResourcesRule(BaseRule):
    """Detects wildcard resources in IAM policies."""
    
    title = "Wildcard Resources"
    description = "Detects wildcard resources that may be too permissive"
    severity = Severity.HIGH
    category = "resources"
    
    def analyze_statement(self, statement: Dict[str, Any], statement_index: int) -> List[Finding]:
        """Analyze statement for wildcard resources."""
        findings = []
        
        # Only analyze Allow statements
        if statement.get("Effect") != "Allow":
            return findings
        
        # Get resources from the statement
        resources = []
        for resource_field in ["Resource", "NotResource"]:
            if resource_field in statement:
                resource_value = statement[resource_field]
                if isinstance(resource_value, str):
                    resources.append(resource_value)
                elif isinstance(resource_value, list):
                    resources.extend(resource_value)
        
        # Check for wildcard resources
        wildcard_resources = []
        for resource in resources:
            if self._is_wildcard_resource(resource):
                wildcard_resources.append(resource)
        
        if wildcard_resources:
            resource_list = ", ".join(wildcard_resources)
            findings.append(
                self.create_finding(
                    title="Wildcard Resources Detected",
                    description=(
                        f"The policy contains wildcard resources: {resource_list}. "
                        "Wildcard resources grant access to all resources of that type and should be reviewed carefully."
                    ),
                    severity=self.severity,
                    statement_index=statement_index,
                    resource_pattern=resource_list,
                    recommendation=(
                        "Review wildcard resources and replace with specific resource ARNs where possible. "
                        "Consider using resource tags or conditions to limit access scope."
                    ),
                    examples=[
                        "Replace '*' with specific ARNs like 'arn:aws:s3:::my-bucket/*'",
                        "Use resource tags to limit access: 'arn:aws:s3:::my-bucket/*' with tag conditions",
                        "Implement least-privilege access by specifying exact resources needed"
                    ],
                    references=[
                        "https://docs.aws.amazon.com/IAM/latest/UserGuide/best-practices.html#grant-least-privilege",
                        "https://docs.aws.amazon.com/IAM/latest/UserGuide/access_policies.html#access_policies-json"
                    ]
                )
            )
        
        return findings
    
    def _is_wildcard_resource(self, resource: str) -> bool:
        """Check if a resource is a wildcard."""
        # Only flag simple wildcards or overly broad patterns
        if resource == "*":
            return True
            
        # Don't flag legitimate ARN patterns with wildcards
        if resource.startswith("arn:aws:"):
            # Don't flag cross-account bucket patterns
            if "arn:aws:s3:::" in resource and resource.count(":") >= 5:
                return False
                
            # Don't flag legitimate ARN patterns with wildcards at the end
            # e.g., "arn:aws:ec2:*:*:instance/*" is a legitimate pattern
            if resource.endswith("/*"):
                parts = resource.split(":")
                if len(parts) >= 6:  # Proper ARN format
                    return False
                    
            # Don't flag legitimate ARN patterns with region/account wildcards
            # e.g., "arn:aws:cloudwatch:*:*:metric/my-metric" is legitimate
            if "*:*:" in resource and not resource.endswith("*"):
                return False
                
        # Only flag simple wildcards or overly broad patterns
        return "*" in resource and (resource == "*" or resource.count("*") > 1)


class MissingResourceRestrictionsRule(BaseRule):
    """Detects missing resource restrictions for sensitive actions."""
    
    title = "Missing Resource Restrictions"
    description = "Detects actions that should have resource restrictions"
    severity = Severity.MEDIUM
    category = "resources"
    
    def analyze_statement(self, statement: Dict[str, Any], statement_index: int) -> List[Finding]:
        """Analyze statement for missing resource restrictions."""
        findings = []
        
        # Only analyze Allow statements
        if statement.get("Effect") != "Allow":
            return findings
        
        # Get actions and resources
        actions = []
        for action_field in ["Action", "NotAction"]:
            if action_field in statement:
                action_value = statement[action_field]
                if isinstance(action_value, str):
                    actions.append(action_value)
                elif isinstance(action_value, list):
                    actions.extend(action_value)
        
        resources = []
        for resource_field in ["Resource", "NotResource"]:
            if resource_field in statement:
                resource_value = statement[resource_field]
                if isinstance(resource_value, str):
                    resources.append(resource_value)
                elif isinstance(resource_value, list):
                    resources.extend(resource_value)
        
        # Check for sensitive actions without proper resource restrictions
        sensitive_actions = []
        for action in actions:
            if self._is_sensitive_action(action) and self._has_wildcard_resources(resources):
                sensitive_actions.append(action)
        
        if sensitive_actions:
            action_list = ", ".join(sensitive_actions)
            findings.append(
                self.create_finding(
                    title="Sensitive Actions Without Resource Restrictions",
                    description=(
                        f"The policy grants sensitive actions without proper resource restrictions: {action_list}. "
                        "These actions can access or modify data across all resources."
                    ),
                    severity=self.severity,
                    statement_index=statement_index,
                    action_pattern=action_list,
                    recommendation=(
                        "Add specific resource ARN restrictions for sensitive actions. "
                        "Consider using bucket policies, object-level permissions, or resource tags."
                    ),
                    examples=[
                        "Add resource restrictions: 'arn:aws:s3:::my-bucket/*' for S3 actions",
                        "Use bucket policies for S3 access control",
                        "Implement object-level permissions for sensitive data"
                    ],
                    references=[
                        "https://docs.aws.amazon.com/AmazonS3/latest/userguide/using-with-s3-actions.html",
                        "https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/access-control-identity-based.html"
                    ]
                )
            )
        
        return findings
    
    def _is_sensitive_action(self, action: str) -> bool:
        """Check if an action is sensitive and requires resource restrictions."""
        sensitive_actions = {
            # S3 data access
            "s3:GetObject", "s3:PutObject", "s3:DeleteObject", "s3:GetObjectAcl", "s3:PutObjectAcl",
            # DynamoDB data access
            "dynamodb:GetItem", "dynamodb:PutItem", "dynamodb:DeleteItem", "dynamodb:UpdateItem",
            "dynamodb:Query", "dynamodb:Scan",
            # KMS operations
            "kms:Decrypt", "kms:Encrypt", "kms:GenerateDataKey", "kms:ReEncrypt",
            # Secrets Manager
            "secretsmanager:GetSecretValue", "secretsmanager:PutSecretValue",
            # Systems Manager
            "ssm:GetParameter", "ssm:PutParameter", "ssm:DeleteParameter",
            # Lambda
            "lambda:InvokeFunction", "lambda:UpdateFunctionCode",
            # RDS
            "rds:CreateDBInstance", "rds:DeleteDBInstance", "rds:ModifyDBInstance",
        }
        return action in sensitive_actions
    
    def _has_wildcard_resources(self, resources: List[str]) -> bool:
        """Check if resources contain wildcards."""
        return any(self._is_wildcard_resource(resource) for resource in resources)
    
    def _is_wildcard_resource(self, resource: str) -> bool:
        """Check if a resource is a wildcard."""
        return resource == "*" or "*" in resource


class CrossAccountResourceRule(BaseRule):
    """Detects cross-account resource access."""
    
    title = "Cross-Account Resource Access"
    description = "Detects access to resources in other AWS accounts (may be legitimate)"
    severity = Severity.LOW
    category = "resources"
    
    def analyze_statement(self, statement: Dict[str, Any], statement_index: int) -> List[Finding]:
        """Analyze statement for cross-account resource access."""
        findings = []
        
        # Only analyze Allow statements
        if statement.get("Effect") != "Allow":
            return findings
        
        # Get resources
        resources = []
        for resource_field in ["Resource", "NotResource"]:
            if resource_field in statement:
                resource_value = statement[resource_field]
                if isinstance(resource_value, str):
                    resources.append(resource_value)
                elif isinstance(resource_value, list):
                    resources.extend(resource_value)
        
        # Check for cross-account resources
        cross_account_resources = []
        for resource in resources:
            if self._is_cross_account_resource(resource):
                cross_account_resources.append(resource)
        
        if cross_account_resources:
            resource_list = ", ".join(cross_account_resources)
            findings.append(
                self.create_finding(
                    title="Cross-Account Resource Access",
                    description=(
                        f"The policy grants access to resources in other AWS accounts: {resource_list}. "
                        "Cross-account access is common in AWS but should be reviewed to ensure it's legitimate."
                    ),
                    severity=self.severity,
                    statement_index=statement_index,
                    resource_pattern=resource_list,
                    recommendation=(
                        "Verify this cross-account access is legitimate and necessary. "
                        "Common legitimate uses: shared data lakes, centralized logging, AWS Organizations."
                    ),
                    examples=[
                        "Use AWS Organizations for centralized account management",
                        "Implement cross-account roles with limited permissions",
                        "Use AWS Resource Access Manager (RAM) for resource sharing"
                    ],
                    references=[
                        "https://docs.aws.amazon.com/organizations/latest/userguide/orgs_introduction.html",
                        "https://docs.aws.amazon.com/IAM/latest/UserGuide/tutorial_cross-account-with-roles.html",
                        "https://docs.aws.amazon.com/ram/latest/userguide/what-is.html"
                    ]
                )
            )
        
        return findings
    
    def _is_cross_account_resource(self, resource: str) -> bool:
        """Check if a resource is in a different AWS account."""
        # This is a simplified check - in a real implementation, you'd compare against the current account ID
        # For now, we'll look for patterns that suggest cross-account access
        if "arn:aws:" in resource:
            # Look for account IDs that are not the current account
            # This is a placeholder - you'd need to implement account ID detection
            return "*" in resource or "arn:aws:iam::*:role/*" in resource
        return False
