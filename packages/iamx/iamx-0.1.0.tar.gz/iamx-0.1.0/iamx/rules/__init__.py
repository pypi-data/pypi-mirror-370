"""IAM Policy Analysis Rules."""

from .base import BaseRule
from .permissions import OverlyPermissiveActionsRule, WildcardActionsRule, AdministrativeActionsRule, DataAccessActionsRule
from .resources import WildcardResourcesRule, MissingResourceRestrictionsRule, CrossAccountResourceRule

__all__ = [
    "BaseRule",
    "OverlyPermissiveActionsRule",
    "WildcardActionsRule", 
    "AdministrativeActionsRule",
    "DataAccessActionsRule",
    "WildcardResourcesRule",
    "MissingResourceRestrictionsRule",
    "CrossAccountResourceRule",
]
