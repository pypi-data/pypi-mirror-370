"""
EspoCRM Pydantic modelleri

API istekleri ve yanıtları için type-safe veri modelleri:
- Base model sınıfları
- Entity modelleri
- Arama parametreleri
- API yanıt modelleri
- API istek modelleri
"""

from .base import EspoCRMBaseModel, EspoCRMListResponse, ModelType
from .search import (
    SearchParams, WhereClause, OrderDirection, WhereOperator,
    create_search_params, equals, not_equals, greater_than, less_than,
    in_list, not_in_list, contains, starts_with, ends_with,
    is_null, is_not_null, between, today, past, future
)
from .entities import (
    EntityRecord, EntityType, Account, Contact, Lead, Opportunity, Document, Note, create_entity
)
from .requests import (
    RelationshipRequest, LinkRequest, UnlinkRequest, RelationshipListRequest,
    create_link_request, create_unlink_request, create_relationship_list_request
)
from .responses import (
    APIResponse, ErrorResponse, EntityResponse, ListResponse, BulkOperationResult,
    parse_entity_response, parse_list_response, parse_error_response
)

__all__ = [
    # Base models
    "EspoCRMBaseModel",
    "EspoCRMListResponse",
    "ModelType",
    
    # Search models
    "SearchParams",
    "WhereClause",
    "OrderDirection",
    "WhereOperator",
    
    # Search convenience functions
    "create_search_params",
    "equals",
    "not_equals",
    "greater_than",
    "less_than",
    "in_list",
    "not_in_list",
    "contains",
    "starts_with",
    "ends_with",
    "is_null",
    "is_not_null",
    "between",
    "today",
    "past",
    "future",
    
    # Entity models
    "EntityRecord",
    "EntityType",
    "Account",
    "Contact",
    "Lead",
    "Opportunity",
    "Document",
    "Note",
    "create_entity",
    
    # Request models
    "RelationshipRequest",
    "LinkRequest",
    "UnlinkRequest",
    "RelationshipListRequest",
    "create_link_request",
    "create_unlink_request",
    "create_relationship_list_request",
    
    # Response models
    "APIResponse",
    "ErrorResponse",
    "EntityResponse",
    "ListResponse",
    "BulkOperationResult",
    "parse_entity_response",
    "parse_list_response",
    "parse_error_response",
]
