"""IAM Policy Parser - Handles parsing and validation of IAM policies."""

import json
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from rich.console import Console

from .models import PolicyMetadata


class PolicyParseError(Exception):
    """Raised when there's an error parsing an IAM policy."""
    pass


class PolicyParser:
    """Parser for IAM policy documents."""
    
    def __init__(self):
        self.required_fields = ["Version", "Statement"]
        self.valid_versions = ["2012-10-17", "2008-10-17"]
        self.valid_effects = ["Allow", "Deny"]
        
    def parse_file(self, file_path: Union[str, Path]) -> Dict[str, Any]:
        """Parse an IAM policy from a file."""
        try:
            file_path = Path(file_path)
            if not file_path.exists():
                raise PolicyParseError(f"Policy file not found: {file_path}")
            
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            return self.parse_string(content, filename=file_path.name)
        except (IOError, OSError) as e:
            raise PolicyParseError(f"Error reading policy file {file_path}: {e}")
    
    def parse_string(self, content: str, filename: Optional[str] = None) -> Dict[str, Any]:
        """Parse an IAM policy from a string."""
        try:
            # Try to parse as JSON
            policy = json.loads(content)
        except json.JSONDecodeError as e:
            raise PolicyParseError(f"Invalid JSON in policy: {e}")
        
        # Validate the policy structure
        self._validate_policy(policy)
        
        # Add filename if provided
        if filename:
            policy['_filename'] = filename
        
        return policy
    
    def _validate_policy(self, policy: Dict[str, Any]) -> None:
        """Validate the structure of an IAM policy."""
        if not isinstance(policy, dict):
            raise PolicyParseError("Policy must be a JSON object")
        
        # Check required fields
        for field in self.required_fields:
            if field not in policy:
                raise PolicyParseError(f"Missing required field: {field}")
        
        # Validate Version
        version = policy.get("Version")
        if version not in self.valid_versions:
            raise PolicyParseError(
                f"Invalid Version: {version}. Must be one of: {self.valid_versions}"
            )
        
        # Validate Statement
        statements = policy.get("Statement")
        if not isinstance(statements, list):
            raise PolicyParseError("Statement must be an array")
        
        if not statements:
            # Allow empty statements but warn
            Console().print("[yellow]Warning: Policy contains no statements[/yellow]")
            return
        
        # Validate each statement
        for i, statement in enumerate(statements):
            self._validate_statement(statement, i)
    
    def _validate_statement(self, statement: Dict[str, Any], index: int) -> None:
        """Validate a single policy statement."""
        if not isinstance(statement, dict):
            raise PolicyParseError(f"Statement {index} must be a JSON object")
        
        # Check required statement fields
        if "Effect" not in statement:
            raise PolicyParseError(f"Statement {index} missing required field: Effect")
        
        effect = statement.get("Effect")
        if effect not in self.valid_effects:
            raise PolicyParseError(
                f"Statement {index} has invalid Effect: {effect}. Must be one of: {self.valid_effects}"
            )
        
        # Check for at least one of Action/NotAction
        has_action = "Action" in statement or "NotAction" in statement
        if not has_action:
            raise PolicyParseError(f"Statement {index} must contain either Action or NotAction")
        
        # Check for at least one of Resource/NotResource
        has_resource = "Resource" in statement or "NotResource" in statement
        if not has_resource:
            # Allow missing Resource for some edge cases but warn
            Console().print(f"[yellow]Warning: Statement {index} missing Resource/NotResource field[/yellow]")
            # Don't raise error, just continue
        
        # Validate Principal (only for resource-based policies)
        if "Principal" in statement:
            self._validate_principal(statement["Principal"], index)
        
        # Validate Condition
        if "Condition" in statement:
            self._validate_condition(statement["Condition"], index)
    
    def _validate_principal(self, principal: Any, statement_index: int) -> None:
        """Validate the Principal field in a statement."""
        if isinstance(principal, dict):
            # Principal can be a map of service/account/user
            for key, value in principal.items():
                if not isinstance(value, (str, list)):
                    raise PolicyParseError(
                        f"Statement {statement_index} Principal value must be string or array"
                    )
        elif principal != "*":
            raise PolicyParseError(
                f"Statement {statement_index} Principal must be '*' or a map"
            )
    
    def _validate_condition(self, condition: Any, statement_index: int) -> None:
        """Validate the Condition field in a statement."""
        if not isinstance(condition, dict):
            raise PolicyParseError(f"Statement {statement_index} Condition must be a map")
        
        for operator, conditions in condition.items():
            if not isinstance(conditions, dict):
                raise PolicyParseError(
                    f"Statement {statement_index} Condition operator must be a map"
                )
            
            for key, value in conditions.items():
                if not isinstance(value, (str, list, bool, int, float)):
                    raise PolicyParseError(
                        f"Statement {statement_index} Condition value must be primitive type"
                    )
    
    def extract_metadata(self, policy: Dict[str, Any]) -> PolicyMetadata:
        """Extract metadata from a parsed policy."""
        statements = policy.get("Statement", [])
        
        # Count actions and resources
        action_count = 0
        resource_count = 0
        
        for statement in statements:
            # Count actions
            for action_field in ["Action", "NotAction"]:
                if action_field in statement:
                    actions = statement[action_field]
                    if isinstance(actions, str):
                        action_count += 1
                    elif isinstance(actions, list):
                        action_count += len(actions)
            
            # Count resources
            for resource_field in ["Resource", "NotResource"]:
                if resource_field in statement:
                    resources = statement[resource_field]
                    if isinstance(resources, str):
                        resource_count += 1
                    elif isinstance(resources, list):
                        resource_count += len(resources)
        
        return PolicyMetadata(
            filename=policy.get("_filename"),
            policy_name=policy.get("PolicyName"),
            policy_id=policy.get("PolicyId"),
            version=policy.get("Version"),
            statement_count=len(statements),
            action_count=action_count,
            resource_count=resource_count,
        )
    
    def normalize_actions(self, actions: Union[str, List[str]]) -> List[str]:
        """Normalize action patterns to a list of individual actions."""
        if isinstance(actions, str):
            actions = [actions]
        
        normalized = []
        for action in actions:
            if "*" in action:
                # Handle wildcard actions (this is a simplified version)
                # In a real implementation, you'd want to expand these based on AWS service APIs
                normalized.append(action)
            else:
                normalized.append(action)
        
        return normalized
    
    def normalize_resources(self, resources: Union[str, List[str]]) -> List[str]:
        """Normalize resource patterns to a list of individual resources."""
        if isinstance(resources, str):
            resources = [resources]
        
        return list(resources)
    
    def extract_statement_patterns(self, statement: Dict[str, Any]) -> Dict[str, Any]:
        """Extract patterns from a policy statement for analysis."""
        patterns = {
            "effect": statement.get("Effect"),
            "actions": [],
            "resources": [],
            "conditions": statement.get("Condition", {}),
            "principal": statement.get("Principal"),
        }
        
        # Extract actions
        for action_field in ["Action", "NotAction"]:
            if action_field in statement:
                actions = self.normalize_actions(statement[action_field])
                patterns["actions"].extend(actions)
        
        # Extract resources
        for resource_field in ["Resource", "NotResource"]:
            if resource_field in statement:
                resources = self.normalize_resources(statement[resource_field])
                patterns["resources"].extend(resources)
        
        return patterns
