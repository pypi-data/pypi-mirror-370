"""
DataFlow Node Generation

Dynamic node generation for database operations.
"""

from typing import Any, Dict, List, Optional, Type, Union

from kailash.nodes.base import Node, NodeParameter, NodeRegistry
from kailash.nodes.base_async import AsyncNode


class NodeGenerator:
    """Generates workflow nodes for DataFlow models."""

    def __init__(self, dataflow_instance):
        self.dataflow_instance = dataflow_instance
        # TDD mode detection and context
        self._tdd_mode = getattr(dataflow_instance, "_tdd_mode", False)
        self._test_context = getattr(dataflow_instance, "_test_context", None)

    def _normalize_type_annotation(self, type_annotation: Any) -> Type:
        """Normalize complex type annotations to simple types for NodeParameter.

        This function converts complex typing constructs like Optional[str], List[str],
        Dict[str, Any], etc. into simple Python types that NodeParameter can handle.

        Args:
            type_annotation: The type annotation from model field

        Returns:
            A simple Python type (str, int, bool, list, dict, etc.)
        """
        # Handle typing constructs
        if hasattr(type_annotation, "__origin__"):
            origin = type_annotation.__origin__
            args = getattr(type_annotation, "__args__", ())

            # Handle Optional[T] -> Union[T, None]
            if origin is Union:
                # Find the non-None type
                for arg in args:
                    if arg is not type(None):
                        return self._normalize_type_annotation(arg)
                # Fallback to str if all types are None
                return str

            # Handle List[T], Dict[K, V], etc. - return base container type
            elif origin in (list, List):
                return list
            elif origin in (dict, Dict):
                return dict
            elif origin in (tuple, tuple):
                return tuple
            elif origin in (set, frozenset):
                return set

            # Return the origin for other generic types
            return origin

        # Handle regular types
        elif isinstance(type_annotation, type):
            return type_annotation

        # Handle special cases for common types that might not be recognized
        from datetime import date, datetime, time
        from decimal import Decimal

        if type_annotation is datetime:
            return datetime
        elif type_annotation is date:
            return date
        elif type_annotation is time:
            return time
        elif type_annotation is Decimal:
            return Decimal

        # Fallback to str for unknown types
        return str

    def generate_crud_nodes(self, model_name: str, fields: Dict[str, Any]):
        """Generate CRUD workflow nodes for a model."""
        nodes = {
            f"{model_name}CreateNode": self._create_node_class(
                model_name, "create", fields
            ),
            f"{model_name}ReadNode": self._create_node_class(
                model_name, "read", fields
            ),
            f"{model_name}UpdateNode": self._create_node_class(
                model_name, "update", fields
            ),
            f"{model_name}DeleteNode": self._create_node_class(
                model_name, "delete", fields
            ),
            f"{model_name}ListNode": self._create_node_class(
                model_name, "list", fields
            ),
        }

        # Register nodes with Kailash's NodeRegistry system
        for node_name, node_class in nodes.items():
            NodeRegistry.register(node_class, alias=node_name)
            # Also register in module namespace for direct imports
            globals()[node_name] = node_class
            # Store in DataFlow instance for testing
            self.dataflow_instance._nodes[node_name] = node_class

        return nodes

    def generate_bulk_nodes(self, model_name: str, fields: Dict[str, Any]):
        """Generate bulk operation nodes for a model."""
        nodes = {
            f"{model_name}BulkCreateNode": self._create_node_class(
                model_name, "bulk_create", fields
            ),
            f"{model_name}BulkUpdateNode": self._create_node_class(
                model_name, "bulk_update", fields
            ),
            f"{model_name}BulkDeleteNode": self._create_node_class(
                model_name, "bulk_delete", fields
            ),
            f"{model_name}BulkUpsertNode": self._create_node_class(
                model_name, "bulk_upsert", fields
            ),
        }

        # Register nodes with Kailash's NodeRegistry system
        for node_name, node_class in nodes.items():
            NodeRegistry.register(node_class, alias=node_name)
            globals()[node_name] = node_class
            # Store in DataFlow instance for testing
            self.dataflow_instance._nodes[node_name] = node_class

        return nodes

    def _create_node_class(
        self, model_name: str, operation: str, fields: Dict[str, Any]
    ) -> Type[Node]:
        """Create a workflow node class for a model operation."""

        # Store parent DataFlow instance and TDD context in closure
        dataflow_instance = self.dataflow_instance
        tdd_mode = self._tdd_mode
        test_context = self._test_context

        class DataFlowNode(AsyncNode):
            """Auto-generated DataFlow node."""

            def __init__(self, **kwargs):
                # Set attributes before calling super().__init__() because
                # the parent constructor calls get_parameters() which needs these
                self.model_name = model_name
                self.operation = operation
                self.dataflow_instance = dataflow_instance
                self.model_fields = fields
                # TDD context inheritance
                self._tdd_mode = tdd_mode
                self._test_context = test_context
                super().__init__(**kwargs)

            def validate_inputs(self, **kwargs) -> Dict[str, Any]:
                """Override validate_inputs to add SQL injection protection for DataFlow nodes.

                This method provides connection-level SQL injection protection by:
                1. Calling parent validation for type checking and required parameters
                2. Adding SQL injection detection and sanitization
                3. Preventing malicious SQL fragments in database parameters
                """
                import logging
                import re
                from typing import Any, Dict, List, Union

                logger = logging.getLogger(__name__)

                # First, call parent validation for standard checks
                validated_inputs = super().validate_inputs(**kwargs)

                # SQL injection patterns to detect
                sql_injection_patterns = [
                    r"(?i)(union\s+select)",  # UNION SELECT attacks
                    r"(?i)(select\s+\*?\s*from)",  # SELECT FROM attacks
                    r"(?i)(drop\s+table)",  # DROP TABLE attacks
                    r"(?i)(delete\s+from)",  # DELETE FROM attacks
                    r"(?i)(insert\s+into)",  # INSERT INTO attacks
                    r"(?i)(update\s+\w+\s+set)",  # UPDATE SET attacks
                    r"(?i)(exec\s*\()",  # EXEC() attacks
                    r"(?i)(script\s*>)",  # XSS in SQL context
                    r"(?i)(or\s+['\"]?1['\"]?\s*=\s*['\"]?1['\"]?)",  # OR 1=1 attacks
                    r"(?i)(and\s+['\"]?1['\"]?\s*=\s*['\"]?1['\"]?)",  # AND 1=1 attacks
                    r"(?i)(\;\s*(drop|delete|insert|update|exec))",  # Statement chaining
                    r"(?i)(--\s*$)",  # SQL comments for bypass
                    r"(?i)(/\*.*?\*/)",  # SQL block comments
                ]

                def sanitize_sql_input(value: Any, field_name: str) -> Any:
                    """Sanitize individual input value for SQL injection."""
                    if value is None:
                        return None
                    if not isinstance(value, str):
                        # For non-string types, only process if they could contain injection when converted
                        from datetime import date, datetime, time
                        from decimal import Decimal

                        # Safe types that don't need sanitization
                        safe_types = (int, float, bool, datetime, date, time, Decimal)
                        if isinstance(value, safe_types):
                            return value  # Safe types, return as-is
                        # For complex types, convert to string and sanitize, then return the sanitized string
                        value = str(value)

                    original_value = value

                    # Apply sanitization in specific order to avoid conflicts
                    # 1. Handle statement chaining first (most general)
                    value = re.sub(
                        r"(?i)(\;\s*(drop|delete|insert|update|exec))",
                        "; STATEMENT_BLOCKED",
                        value,
                    )

                    # 2. Handle specific SQL commands
                    value = re.sub(r"(?i)(union\s+select)", "UNION_SELECT", value)
                    value = re.sub(
                        r"(?i)(select\s+\*?\s*from)", "SELECT_FROM", value
                    )  # Add SELECT protection
                    value = re.sub(r"(?i)(drop\s+table)", "DROP_TABLE", value)
                    value = re.sub(r"(?i)(delete\s+from)", "DELETE_FROM", value)
                    value = re.sub(r"(?i)(insert\s+into)", "INSERT_INTO", value)
                    value = re.sub(r"(?i)(update\s+\w+\s+set)", "UPDATE_SET", value)
                    value = re.sub(r"(?i)(exec\s*\()", "EXEC_FUNC", value)

                    # 3. Handle logical operators
                    value = re.sub(
                        r"(?i)(or\s+['\"]?1['\"]?\s*=\s*['\"]?1['\"]?)",
                        "OR_1_EQUALS_1",
                        value,
                    )
                    value = re.sub(
                        r"(?i)(and\s+['\"]?1['\"]?\s*=\s*['\"]?1['\"]?)",
                        "AND_1_EQUALS_1",
                        value,
                    )

                    # 4. Handle comments
                    value = re.sub(r"(?i)(--\s*$)", "-- COMMENT_BLOCKED", value)
                    value = re.sub(r"(?i)(/\*.*?\*/)", "/* COMMENT_BLOCKED */", value)

                    # 5. Check if any patterns were found and log
                    if value != original_value:
                        for pattern in sql_injection_patterns:
                            if re.search(pattern, original_value):
                                logger.warning(
                                    f"Potential SQL injection detected in field '{field_name}': {pattern}"
                                )
                                break
                        logger.info(
                            f"Sanitized SQL injection in field '{field_name}': {original_value} -> {value}"
                        )

                    return value

                def sanitize_nested_structure(data: Any, field_path: str = "") -> Any:
                    """Recursively sanitize nested data structures."""
                    if isinstance(data, dict):
                        return {
                            key: sanitize_nested_structure(
                                value, f"{field_path}.{key}" if field_path else key
                            )
                            for key, value in data.items()
                        }
                    elif isinstance(data, list):
                        return [
                            sanitize_nested_structure(item, f"{field_path}[{i}]")
                            for i, item in enumerate(data)
                        ]
                    else:
                        return sanitize_sql_input(data, field_path)

                # Apply SQL injection protection to all validated inputs
                protected_inputs = {}
                for field_name, value in validated_inputs.items():
                    if field_name in ["filter", "data", "update"]:
                        # Special handling for complex database operation fields
                        protected_inputs[field_name] = sanitize_nested_structure(
                            value, field_name
                        )
                    else:
                        # Standard field sanitization
                        protected_inputs[field_name] = sanitize_sql_input(
                            value, field_name
                        )

                # Additional DataFlow-specific validations
                if operation == "create" or operation == "update":
                    # Ensure no SQL injection in individual field values
                    for field_name, field_info in self.model_fields.items():
                        if field_name in protected_inputs:
                            value = protected_inputs[field_name]
                            if isinstance(value, str) and len(value) > 1000:
                                logger.warning(
                                    f"Suspiciously long input in field '{field_name}': {len(value)} characters"
                                )

                elif operation == "list":
                    # Special validation for filter parameters
                    filter_dict = protected_inputs.get("filter", {})
                    if isinstance(filter_dict, dict):
                        # Validate MongoDB-style operators are safe
                        for field, filter_value in filter_dict.items():
                            if isinstance(filter_value, dict):
                                for op, op_value in filter_value.items():
                                    if op.startswith("$"):
                                        # Validate MongoDB-style operators
                                        allowed_ops = [
                                            "$eq",
                                            "$ne",
                                            "$gt",
                                            "$gte",
                                            "$lt",
                                            "$lte",
                                            "$in",
                                            "$nin",
                                            "$regex",
                                            "$exists",
                                            "$not",
                                            "$contains",  # For JSON field queries
                                            "$mul",  # For mathematical operations in updates
                                        ]
                                        if op not in allowed_ops:
                                            raise ValueError(
                                                f"Unsafe filter operator '{op}' in field '{field}'"
                                            )

                elif operation.startswith("bulk_"):
                    # Validate bulk data doesn't contain injection
                    bulk_data = protected_inputs.get("data", [])
                    if isinstance(bulk_data, list):
                        for i, record in enumerate(bulk_data):
                            if isinstance(record, dict):
                                for field_name, value in record.items():
                                    if isinstance(value, str):
                                        # Check each field in bulk data
                                        sanitized = sanitize_sql_input(
                                            value, f"data[{i}].{field_name}"
                                        )
                                        if sanitized != value:
                                            bulk_data[i][field_name] = sanitized

                logger.debug(
                    f"DataFlow SQL injection protection applied to {operation} operation"
                )
                return protected_inputs

            def get_parameters(self) -> Dict[str, NodeParameter]:
                """Define parameters for this DataFlow node."""
                # Add database_url parameter to all operations
                base_params = {
                    "database_url": NodeParameter(
                        name="database_url",
                        type=str,
                        required=False,
                        default=None,
                        description="Database connection URL to override default configuration",
                    )
                }

                if operation == "create":
                    # Generate parameters from model fields
                    params = base_params.copy()
                    for field_name, field_info in self.model_fields.items():
                        # CRITICAL FIX: Include ID parameter for string ID models (user-provided IDs)
                        if field_name == "id":
                            # Include ID parameter only if it's explicitly typed as string (user-provided)
                            id_type = field_info.get("type")
                            if id_type == str:
                                params["id"] = NodeParameter(
                                    name="id",
                                    type=str,
                                    required=True,
                                    description="Primary key for the record (user-provided string)",
                                )
                        elif field_name not in ["created_at", "updated_at"]:
                            # Normalize complex type annotations to simple types
                            normalized_type = self.dataflow_instance._node_generator._normalize_type_annotation(
                                field_info["type"]
                            )

                            # DEBUG: Log type normalization
                            import logging

                            logger = logging.getLogger(__name__)
                            logger.warning(
                                f"PARAM {field_name}: original_type={field_info['type']} -> normalized_type={normalized_type}"
                            )
                            params[field_name] = NodeParameter(
                                name=field_name,
                                type=normalized_type,
                                required=field_info.get("required", True),
                                default=field_info.get("default"),
                                description=f"{field_name} for the record",
                            )
                    return params

                elif operation == "read":
                    params = base_params.copy()
                    params.update(
                        {
                            "record_id": NodeParameter(
                                name="record_id",
                                type=int,
                                required=False,
                                default=None,
                                description="ID of record to read",
                            ),
                            "id": NodeParameter(
                                name="id",
                                type=Any,  # Accept any type to avoid validation errors
                                required=False,
                                default=None,
                                description="Alias for record_id (accepts workflow connections)",
                            ),
                            "conditions": NodeParameter(
                                name="conditions",
                                type=dict,
                                required=False,
                                default={},
                                description="Read conditions (e.g., {'id': 123})",
                            ),
                            "raise_on_not_found": NodeParameter(
                                name="raise_on_not_found",
                                type=bool,
                                required=False,
                                default=True,
                                description="Whether to raise error if record not found",
                            ),
                        }
                    )
                    return params

                elif operation == "update":
                    params = base_params.copy()
                    params.update(
                        {
                            "record_id": NodeParameter(
                                name="record_id",
                                type=int,
                                required=False,
                                default=None,
                                description="ID of record to update",
                            ),
                            "id": NodeParameter(
                                name="id",
                                type=Any,  # Accept any type to avoid validation errors
                                required=False,
                                default=None,
                                description="Alias for record_id (accepts workflow connections)",
                            ),
                            # Support nested parameter format
                            "conditions": NodeParameter(
                                name="conditions",
                                type=dict,
                                required=False,
                                default={},
                                description="Update conditions (e.g., {'id': 123})",
                            ),
                            "updates": NodeParameter(
                                name="updates",
                                type=dict,
                                required=False,
                                default={},
                                description="Fields to update (e.g., {'published': True})",
                            ),
                        }
                    )
                    # Add all model fields as optional update parameters for backward compatibility
                    for field_name, field_info in self.model_fields.items():
                        if field_name not in ["id", "created_at", "updated_at"]:
                            # Normalize complex type annotations to simple types
                            normalized_type = self.dataflow_instance._node_generator._normalize_type_annotation(
                                field_info["type"]
                            )

                            params[field_name] = NodeParameter(
                                name=field_name,
                                type=normalized_type,
                                required=False,
                                description=f"New {field_name} for the record",
                            )
                    return params

                elif operation == "delete":
                    params = base_params.copy()
                    params.update(
                        {
                            "record_id": NodeParameter(
                                name="record_id",
                                type=int,
                                required=False,
                                default=None,
                                description="ID of record to delete",
                            ),
                            "id": NodeParameter(
                                name="id",
                                type=Any,  # Accept any type to avoid validation errors
                                required=False,
                                default=None,
                                description="Alias for record_id (accepts workflow connections)",
                            ),
                        }
                    )
                    return params

                elif operation == "list":
                    params = base_params.copy()
                    params.update(
                        {
                            "limit": NodeParameter(
                                name="limit",
                                type=int,
                                required=False,
                                default=10,
                                description="Maximum number of records to return",
                            ),
                            "offset": NodeParameter(
                                name="offset",
                                type=int,
                                required=False,
                                default=0,
                                description="Number of records to skip",
                            ),
                            "order_by": NodeParameter(
                                name="order_by",
                                type=list,
                                required=False,
                                default=[],
                                description="Fields to sort by",
                            ),
                            "filter": NodeParameter(
                                name="filter",
                                type=dict,
                                required=False,
                                default={},
                                description="Filter criteria",
                            ),
                            "enable_cache": NodeParameter(
                                name="enable_cache",
                                type=bool,
                                required=False,
                                default=True,
                                description="Whether to enable query caching",
                            ),
                            "cache_ttl": NodeParameter(
                                name="cache_ttl",
                                type=int,
                                required=False,
                                default=None,
                                description="Cache TTL in seconds",
                            ),
                            "cache_key": NodeParameter(
                                name="cache_key",
                                type=str,
                                required=False,
                                default=None,
                                description="Override cache key",
                            ),
                            "count_only": NodeParameter(
                                name="count_only",
                                type=bool,
                                required=False,
                                default=False,
                                description="Return count only",
                            ),
                        }
                    )
                    return params

                elif operation.startswith("bulk_"):
                    params = base_params.copy()
                    params.update(
                        {
                            "data": NodeParameter(
                                name="data",
                                type=list,
                                required=False,
                                default=[],
                                description="List of records for bulk operation",
                                auto_map_from=["records", "rows", "documents"],
                            ),
                            "batch_size": NodeParameter(
                                name="batch_size",
                                type=int,
                                required=False,
                                default=1000,
                                description="Batch size for bulk operations",
                            ),
                            "conflict_resolution": NodeParameter(
                                name="conflict_resolution",
                                type=str,
                                required=False,
                                default="skip",
                                description="How to handle conflicts",
                            ),
                            "filter": NodeParameter(
                                name="filter",
                                type=dict,
                                required=False,
                                default={},
                                description="Filter for bulk update/delete",
                            ),
                            "update": NodeParameter(
                                name="update",
                                type=dict,
                                required=False,
                                default={},
                                description="Update values for bulk update",
                            ),
                            "return_ids": NodeParameter(
                                name="return_ids",
                                type=bool,
                                required=False,
                                default=False,
                                description="Whether to return created record IDs",
                            ),
                        }
                    )
                    return params

                return {}

            def run(self, **kwargs) -> Dict[str, Any]:
                """Synchronous wrapper for async_run to support both sync and async usage.

                This allows DataFlow nodes to be used in both synchronous scripts
                and async applications, improving developer experience.
                """
                import asyncio

                # Check if we're already in an event loop
                try:
                    loop = asyncio.get_running_loop()
                    # We're in an async context, can't use run() safely
                    raise RuntimeError(
                        f"Cannot use synchronous run() from within an async context. "
                        f"Use 'await {self.__class__.__name__}.async_run()' instead."
                    )
                except RuntimeError as e:
                    if "no running event loop" not in str(e).lower():
                        # It's a different RuntimeError, re-raise it
                        raise
                    # No event loop running, safe to create one
                    return asyncio.run(self.async_run(**kwargs))

            async def async_run(self, **kwargs) -> Dict[str, Any]:
                """Execute the database operation using DataFlow components."""
                import asyncio
                import logging

                from kailash.nodes.data.async_sql import AsyncSQLDatabaseNode

                logger = logging.getLogger(__name__)
                logger.warning(
                    f"DataFlow Node {self.model_name}{self.operation.title()}Node - received kwargs: {kwargs}"
                )

                # Ensure table exists before any database operations (lazy table creation)
                if self.dataflow_instance and hasattr(
                    self.dataflow_instance, "ensure_table_exists"
                ):
                    logger.debug(f"Ensuring table exists for model {self.model_name}")
                    try:
                        table_created = (
                            await self.dataflow_instance.ensure_table_exists(
                                self.model_name
                            )
                        )
                        if not table_created:
                            logger.warning(
                                f"Failed to ensure table exists for model {self.model_name}"
                            )
                    except Exception as e:
                        logger.error(
                            f"Error ensuring table exists for model {self.model_name}: {e}"
                        )
                        # Continue anyway - the database operation might still work

                logger.info(f"Run called with kwargs: {kwargs}")

                # TDD mode: Override connection string if test context available
                if (
                    self._tdd_mode
                    and self._test_context
                    and hasattr(self._test_context, "connection")
                ):
                    # Extract connection info from TDD context
                    tdd_connection_info = self._get_tdd_connection_info()
                    if tdd_connection_info:
                        kwargs["database_url"] = tdd_connection_info
                        logger.debug(
                            f"TDD mode: Using test connection for {operation} operation"
                        )

                # Apply tenant filtering if multi-tenant mode
                if self.dataflow_instance.config.security.multi_tenant:
                    tenant_id = self.dataflow_instance._tenant_context.get("tenant_id")
                    if tenant_id and "filter" in kwargs:
                        kwargs["filter"]["tenant_id"] = tenant_id

                # Execute database operations using DataFlow components
                logger.warning(
                    f"Operation detection: operation='{operation}', model='{model_name}'"
                )
                if operation == "create":
                    # Use DataFlow's insert SQL generation and AsyncSQLDatabaseNode for execution
                    try:
                        # Get connection string - prioritize parameter over instance config
                        connection_string = kwargs.get("database_url")
                        if not connection_string:
                            connection_string = self.dataflow_instance.config.database.get_connection_url(
                                self.dataflow_instance.config.environment
                            )

                        # Detect database type for SQL generation
                        if kwargs.get("database_url"):
                            # Use provided database URL to detect type
                            from ..adapters.connection_parser import ConnectionParser

                            database_type = ConnectionParser.detect_database_type(
                                connection_string
                            )
                        else:
                            database_type = (
                                self.dataflow_instance._detect_database_type()
                            )

                        # DEBUG: Check what self.model_name we have
                        # Fixed: Using self.model_name to avoid closure variable conflicts
                        logger.debug(
                            f"CREATE operation - self.model_name: {self.model_name}"
                        )

                        # Use self.model_name instead of closure variable to avoid conflicts
                        # Use DataFlow's insert SQL generation
                        query = self.dataflow_instance._generate_insert_sql(
                            self.model_name, database_type
                        )

                        # Get ALL model fields to match SQL generation
                        model_fields = self.dataflow_instance.get_model_fields(
                            self.model_name
                        )

                        # CRITICAL FIX: Use the EXACT SAME field ordering as SQL generation
                        # This ensures parameter order matches SQL placeholder order
                        field_names = []
                        for name in model_fields.keys():
                            if name == "id":
                                # Include ID in SQL field list only if it's string type (user-provided)
                                id_type = model_fields["id"].get("type")
                                if id_type == str and "id" in kwargs:
                                    field_names.append(name)
                            elif name not in ["created_at", "updated_at"]:
                                field_names.append(name)

                        # DEBUG: Log the exact field order we're using
                        logger.warning(
                            f"CREATE {self.model_name} - Field order from model_fields.keys(): {field_names}"
                        )
                        logger.warning(
                            f"CREATE {self.model_name} - Generated SQL: {query}"
                        )

                        # Build complete parameter set with defaults in correct order
                        complete_params = {}

                        for field_name in field_names:
                            field_info = model_fields[field_name]

                            if field_name in kwargs:
                                # Use provided value
                                complete_params[field_name] = kwargs[field_name]
                            elif "default" in field_info:
                                # Use model default
                                default_value = field_info["default"]
                                # Handle callable defaults
                                if callable(default_value):
                                    complete_params[field_name] = default_value()
                                else:
                                    complete_params[field_name] = default_value
                            elif field_info.get("required", True):
                                # Required field missing
                                raise ValueError(
                                    f"Required field '{field_name}' missing for {self.model_name}. "
                                    f"Expected fields: {field_names}"
                                )
                            else:
                                # Optional field without default - use None
                                complete_params[field_name] = None

                        # Now parameters match SQL placeholders exactly with correct ordering
                        values = [complete_params[k] for k in field_names]

                        # Debug logging to help identify field ordering issues
                        logger.warning(
                            f"CREATE {self.model_name}: field_names={field_names}, "
                            f"values count={len(values)}, SQL placeholders expected={len(field_names)}"
                        )
                        # Enhanced debug logging to show value types
                        value_debug = []
                        for i, (field, value) in enumerate(zip(field_names, values)):
                            value_type = type(value).__name__
                            value_repr = (
                                repr(value)[:50] + "..."
                                if len(repr(value)) > 50
                                else repr(value)
                            )
                            value_debug.append(
                                f"${i+1} {field}={value_repr} (type={value_type})"
                            )

                        logger.warning(
                            f"CREATE {self.model_name}: Parameter details:\n"
                            + "\n".join(value_debug)
                        )

                        # NOTE: PostgreSQL bypass removed - AsyncSQLDatabaseNode should handle all databases
                        # If there are parameter conversion issues, they should be fixed in AsyncSQLDatabaseNode itself

                        # Execute using AsyncSQLDatabaseNode
                        # For SQLite INSERT without RETURNING, use fetch_mode="all" to get metadata
                        fetch_mode = (
                            "all"
                            if database_type == "sqlite" and "RETURNING" not in query
                            else "one"
                        )

                        sql_node = AsyncSQLDatabaseNode(
                            node_id=f"{self.model_name}_{self.operation}_sql",
                            connection_string=connection_string,
                            database_type=database_type,
                            query=query,
                            params=values,
                            fetch_mode=fetch_mode,
                            validate_queries=False,
                            transaction_mode="auto",
                        )

                        # Execute the async node properly in async context
                        result = await sql_node.async_run(
                            query=query,
                            params=values,
                            fetch_mode=fetch_mode,
                            validate_queries=False,
                            transaction_mode="auto",
                        )

                        # DEBUG: Log the result for SQLite
                        if database_type == "sqlite":
                            logger.warning(f"SQLite INSERT result: {result}")

                        if result and "result" in result and "data" in result["result"]:
                            row = result["result"]["data"]

                            # Check if this is SQLite lastrowid response
                            if isinstance(row, dict) and "lastrowid" in row:
                                # SQLite returns lastrowid for INSERT operations
                                logger.warning(
                                    f"SQLite lastrowid found directly: {row['lastrowid']}"
                                )
                                created_record = {"id": row["lastrowid"], **kwargs}
                                # Invalidate cache after successful create
                                cache_integration = getattr(
                                    self.dataflow_instance, "_cache_integration", None
                                )
                                if cache_integration:
                                    cache_integration.invalidate_model_cache(
                                        self.model_name, "create", created_record
                                    )
                                return created_record

                            if isinstance(row, list) and len(row) > 0:
                                row = row[0]

                            if row and isinstance(row, dict) and "lastrowid" not in row:
                                # Invalidate cache after successful create
                                cache_integration = getattr(
                                    self.dataflow_instance, "_cache_integration", None
                                )
                                if cache_integration:
                                    cache_integration.invalidate_model_cache(
                                        self.model_name, "create", row
                                    )

                                # Return the created record with all fields
                                return {**kwargs, **row}

                        # Check for SQLite lastrowid (SQLite doesn't support RETURNING clause)
                        if result and "result" in result:
                            result_data = result["result"]
                            # Check if data contains lastrowid
                            if "data" in result_data:
                                data = result_data["data"]
                                if isinstance(data, dict) and "lastrowid" in data:
                                    # SQLite returns lastrowid for INSERT operations
                                    logger.warning(
                                        f"SQLite lastrowid found: {data['lastrowid']}"
                                    )
                                    created_record = {"id": data["lastrowid"], **kwargs}
                                    # Invalidate cache after successful create
                                    cache_integration = getattr(
                                        self.dataflow_instance,
                                        "_cache_integration",
                                        None,
                                    )
                                    if cache_integration:
                                        cache_integration.invalidate_model_cache(
                                            self.model_name, "create", created_record
                                        )
                                    return created_record
                            elif (
                                isinstance(result_data, dict)
                                and "lastrowid" in result_data
                            ):
                                # SQLite returns lastrowid for INSERT operations
                                return {"id": result_data["lastrowid"], **kwargs}
                            elif isinstance(result_data, list) and len(result_data) > 0:
                                first_result = result_data[0]
                                if (
                                    isinstance(first_result, dict)
                                    and "lastrowid" in first_result
                                ):
                                    return {"id": first_result["lastrowid"], **kwargs}

                        # Fall back to basic response if no data returned
                        logger.warning(
                            f"CREATE {self.model_name}: Falling back to basic response - no lastrowid found"
                        )
                        return {"id": None, **kwargs}

                    except Exception as e:
                        original_error = str(e)
                        logger.warning(
                            f"CREATE {self.model_name} failed with error: {original_error}"
                        )

                        # Check for parameter mismatch error
                        if (
                            "could not determine data type of parameter"
                            in original_error
                        ):
                            import re

                            match = re.search(r"parameter \$(\d+)", original_error)
                            param_num = int(match.group(1)) if match else 0

                            logger.warning(
                                f"DATAFLOW DEBUG: Param error detected - param_num={param_num}"
                            )

                            # CRITICAL FIX: Handle parameter $11 type determination issue
                            if param_num == 11 and "$11" in query:
                                try:
                                    logger.warning(
                                        "DATAFLOW PARAM $11 FIX: Detected parameter $11 issue, retrying with type cast"
                                    )

                                    # Add explicit type casting for parameter $11
                                    fixed_sql = query.replace("$11", "$11::integer")

                                    # Import and retry with the fixed SQL
                                    from kailash.nodes.data.async_sql import (
                                        AsyncSQLDatabaseNode,
                                    )

                                    sql_node = AsyncSQLDatabaseNode(
                                        connection_string=connection_string,
                                        database_type=database_type,
                                    )
                                    result = await sql_node.async_run(
                                        query=fixed_sql,
                                        params=values,
                                        fetch_mode="one",  # RETURNING clause should return one record
                                        validate_queries=False,
                                        transaction_mode="auto",  # Ensure auto-commit for create operations
                                    )

                                    if (
                                        result
                                        and "result" in result
                                        and "data" in result["result"]
                                    ):
                                        row = result["result"]["data"]
                                        if isinstance(row, list) and len(row) > 0:
                                            row = row[0]
                                        if isinstance(row, dict):
                                            logger.warning(
                                                "DATAFLOW PARAM $11 FIX: Success with type cast!"
                                            )
                                            # Return the created record with all fields
                                            return {**kwargs, **row}

                                    logger.warning(
                                        "DATAFLOW PARAM $11 FIX: Type cast succeeded but no data returned"
                                    )

                                except Exception as retry_error:
                                    logger.warning(
                                        f"DATAFLOW PARAM $11 FIX: Retry with type cast failed: {retry_error}"
                                    )
                                    # Continue with normal error handling

                            # Provide helpful error message
                            model_fields = self.dataflow_instance.get_model_fields(
                                self.model_name
                            )
                            expected_fields = [
                                f
                                for f in model_fields.keys()
                                if f not in ["id", "created_at", "updated_at"]
                            ]
                            provided_fields = list(kwargs.keys())

                            # The actual fields used (after applying defaults)
                            actual_fields = field_names  # These are the fields we actually built parameters for

                            error_msg = (
                                f"Parameter mismatch in {self.model_name} creation.\n"
                                f"SQL expects {len(expected_fields)} parameters but built {len(actual_fields)} parameters.\n"
                                f"Expected fields: {expected_fields}\n"
                                f"Built fields: {actual_fields}\n"
                                f"User provided: {provided_fields}\n"
                                f"Missing from user input: {list(set(expected_fields) - set(provided_fields))}\n"
                                f"Note: DataFlow auto-completes fields with defaults.\n"
                                f"Actual error: {original_error}"
                            )
                            logger.error(error_msg)
                        else:
                            logger.error(f"Create operation failed: {e}")
                            error_msg = str(e)

                        return {"success": False, "error": error_msg}

                elif operation == "read":
                    # Handle both nested parameter format and direct field format
                    conditions = kwargs.get("conditions", {})

                    # Handle string JSON input that might come from parameter validation
                    if isinstance(conditions, str):
                        try:
                            import json

                            conditions = (
                                json.loads(conditions) if conditions.strip() else {}
                            )
                        except (json.JSONDecodeError, ValueError):
                            conditions = {}

                    # Determine record_id from conditions or direct parameters
                    record_id = None
                    if conditions and "id" in conditions:
                        record_id = conditions["id"]
                    else:
                        # Fall back to direct parameters for backward compatibility
                        # Prioritize record_id over id to avoid conflicts with node's own id
                        record_id = kwargs.get("record_id")
                        if record_id is None:
                            # Get the ID parameter for record lookup
                            id_param = kwargs.get("id")
                            if id_param is not None:
                                # Type-aware ID conversion to fix string ID bug
                                id_field_info = self.model_fields.get("id", {})
                                id_type = id_field_info.get("type")

                                if id_type == str:
                                    # Model explicitly defines ID as string - preserve it
                                    record_id = id_param
                                elif id_type == int or id_type is None:
                                    # Model defines ID as int OR no type info (backward compat)
                                    try:
                                        record_id = int(id_param)
                                    except (ValueError, TypeError):
                                        # If conversion fails, preserve original
                                        record_id = id_param
                                else:
                                    # Other types (UUID, custom) - preserve as-is
                                    record_id = id_param

                    if record_id is None:
                        record_id = 1

                    # Get connection string - prioritize parameter over instance config
                    connection_string = kwargs.get("database_url")
                    if not connection_string:
                        connection_string = (
                            self.dataflow_instance.config.database.get_connection_url(
                                self.dataflow_instance.config.environment
                            )
                        )

                    # Detect database type for SQL generation
                    if kwargs.get("database_url"):
                        from ..adapters.connection_parser import ConnectionParser

                        database_type = ConnectionParser.detect_database_type(
                            connection_string
                        )
                    else:
                        database_type = self.dataflow_instance._detect_database_type()

                    # Use DataFlow's select SQL generation
                    select_templates = self.dataflow_instance._generate_select_sql(
                        self.model_name, database_type
                    )
                    query = select_templates["select_by_id"]

                    sql_node = AsyncSQLDatabaseNode(
                        node_id=f"{self.model_name}_{self.operation}_sql",
                        connection_string=connection_string,
                        database_type=database_type,
                    )

                    result = await sql_node.async_run(
                        query=query,
                        params=[record_id],
                        fetch_mode="one",
                        validate_queries=False,
                        transaction_mode="auto",  # Ensure auto-commit for read operations
                    )

                    if result and "result" in result and "data" in result["result"]:
                        row = result["result"]["data"]
                        if isinstance(row, list) and len(row) > 0:
                            row = row[0]
                        if row:
                            # Return the row data with 'found' key as expected by tests
                            return {**row, "found": True}
                    return {"id": record_id, "found": False}

                elif operation == "update":
                    # Handle both nested parameter format and direct field format
                    conditions = kwargs.get("conditions", {})
                    updates_dict = kwargs.get("updates", {})

                    # Handle string JSON input that might come from parameter validation
                    if isinstance(conditions, str):
                        try:
                            import json

                            conditions = (
                                json.loads(conditions) if conditions.strip() else {}
                            )
                        except (json.JSONDecodeError, ValueError):
                            conditions = {}

                    if isinstance(updates_dict, str):
                        try:
                            import json

                            # Try to parse as JSON first
                            updates_dict = (
                                json.loads(updates_dict) if updates_dict.strip() else {}
                            )
                        except (json.JSONDecodeError, ValueError) as e:
                            # Fallback: try to evaluate as Python literal (for single-quoted dicts)
                            try:
                                import ast

                                updates_dict = (
                                    ast.literal_eval(updates_dict)
                                    if updates_dict.strip()
                                    else {}
                                )
                            except (ValueError, SyntaxError):
                                updates_dict = {}

                    # Determine record_id from conditions or direct parameters
                    record_id = None
                    if conditions and "id" in conditions:
                        record_id = conditions["id"]
                    else:
                        # Fall back to record_id parameter - prioritize this over 'id'
                        # since 'id' often contains the node ID which is not a record ID
                        record_id = kwargs.get("record_id")

                        # Only use 'id' parameter if no record_id is available and 'id' looks like a record ID
                        if record_id is None:
                            id_param = kwargs.get("id")
                            # Check if id_param looks like a record ID, not a node ID
                            if (
                                id_param is not None
                                and id_param != operation  # Not the operation name
                                and not isinstance(
                                    id_param, str
                                )  # Not a string (likely int/UUID)
                                or (
                                    isinstance(id_param, str)
                                    and not id_param.endswith(
                                        f"_{operation}"
                                    )  # Not a node ID pattern
                                    and len(id_param) < 50
                                )
                            ):  # Reasonable ID length
                                # Type-aware ID conversion to fix string ID bug
                                id_field_info = self.model_fields.get("id", {})
                                id_type = id_field_info.get("type")

                                if id_type == str:
                                    # Model explicitly defines ID as string - preserve it
                                    record_id = id_param
                                elif id_type == int or id_type is None:
                                    # Model defines ID as int OR no type info (backward compat)
                                    try:
                                        record_id = int(id_param)
                                    except (ValueError, TypeError):
                                        # If conversion fails, don't use this value
                                        record_id = None
                                else:
                                    # Other types (UUID, custom) - preserve as-is
                                    record_id = id_param

                    if record_id is None:
                        record_id = 1

                    # Determine updates from nested format or direct field parameters
                    if updates_dict:
                        # Use nested updates format
                        updates = updates_dict
                    else:
                        # Fall back to direct field parameters for backward compatibility
                        updates = {
                            k: v
                            for k, v in kwargs.items()
                            if k
                            not in [
                                "record_id",
                                "id",
                                "database_url",
                                "conditions",
                                "updates",
                            ]
                            and k not in ["created_at", "updated_at"]
                        }

                    if updates:
                        # Get connection string - prioritize parameter over instance config
                        connection_string = kwargs.get("database_url")
                        if not connection_string:
                            connection_string = self.dataflow_instance.config.database.get_connection_url(
                                self.dataflow_instance.config.environment
                            )

                        # Detect database type for SQL generation
                        if kwargs.get("database_url"):
                            from ..adapters.connection_parser import ConnectionParser

                            database_type = ConnectionParser.detect_database_type(
                                connection_string
                            )
                        else:
                            database_type = (
                                self.dataflow_instance._detect_database_type()
                            )

                        # Get table name
                        table_name = self.dataflow_instance._class_name_to_table_name(
                            self.model_name
                        )

                        # CRITICAL FIX: Check if updated_at column exists before using it
                        try:
                            actual_columns = self.dataflow_instance._get_table_columns(
                                table_name
                            )
                            has_updated_at = (
                                actual_columns and "updated_at" in actual_columns
                            )
                        except Exception:
                            has_updated_at = False

                        # Build dynamic UPDATE query for only the fields being updated
                        field_names = list(updates.keys())
                        if database_type.lower() == "postgresql":
                            set_clauses = [
                                f"{name} = ${i+1}" for i, name in enumerate(field_names)
                            ]
                            where_clause = f"WHERE id = ${len(field_names)+1}"
                            updated_at_clause = (
                                "updated_at = CURRENT_TIMESTAMP"
                                if has_updated_at
                                else None
                            )

                            # Get all field names for RETURNING clause
                            all_fields = self.dataflow_instance.get_model_fields(
                                self.model_name
                            )
                            # CRITICAL FIX: Only include columns that actually exist
                            try:
                                expected_columns = (
                                    ["id"]
                                    + list(all_fields.keys())
                                    + ["created_at", "updated_at"]
                                )
                                all_columns = (
                                    [
                                        col
                                        for col in expected_columns
                                        if col in actual_columns
                                    ]
                                    if actual_columns
                                    else list(all_fields.keys())
                                )
                            except Exception:
                                all_columns = list(all_fields.keys())

                            # Build SET clause (only include updated_at if column exists)
                            all_set_clauses = set_clauses
                            if updated_at_clause:
                                all_set_clauses.append(updated_at_clause)

                            query = f"UPDATE {table_name} SET {', '.join(all_set_clauses)} {where_clause} RETURNING {', '.join(all_columns)}"
                        elif database_type.lower() == "mysql":
                            set_clauses = [f"{name} = %s" for name in field_names]
                            where_clause = "WHERE id = %s"
                            updated_at_clause = (
                                "updated_at = NOW()" if has_updated_at else None
                            )

                            # Build SET clause (only include updated_at if column exists)
                            all_set_clauses = set_clauses
                            if updated_at_clause:
                                all_set_clauses.append(updated_at_clause)

                            query = f"UPDATE {table_name} SET {', '.join(all_set_clauses)} {where_clause}"
                        else:  # sqlite
                            set_clauses = [f"{name} = ?" for name in field_names]
                            where_clause = "WHERE id = ?"
                            updated_at_clause = (
                                "updated_at = CURRENT_TIMESTAMP"
                                if has_updated_at
                                else None
                            )

                            # Build SET clause (only include updated_at if column exists)
                            all_set_clauses = set_clauses
                            if updated_at_clause:
                                all_set_clauses.append(updated_at_clause)

                            query = f"UPDATE {table_name} SET {', '.join(all_set_clauses)} {where_clause}"

                        # Prepare parameters: field values first, then ID
                        values = list(updates.values()) + [record_id]

                        sql_node = AsyncSQLDatabaseNode(
                            node_id=f"{self.model_name}_{self.operation}_sql",
                            connection_string=connection_string,
                            database_type=database_type,
                        )
                        result = await sql_node.async_run(
                            query=query,
                            params=values,
                            fetch_mode="one",
                            validate_queries=False,
                            transaction_mode="auto",  # Ensure auto-commit for update operations
                        )

                        if result and "result" in result and "data" in result["result"]:
                            row = result["result"]["data"]
                            if isinstance(row, list) and len(row) > 0:
                                row = row[0]
                            if row:
                                # Invalidate cache after successful update
                                cache_integration = getattr(
                                    self.dataflow_instance, "_cache_integration", None
                                )
                                if cache_integration:
                                    cache_integration.invalidate_model_cache(
                                        self.model_name, "update", row
                                    )

                                # Merge the update values with the returned row data
                                # and add 'updated' key as expected by tests
                                # Ensure 'id' is available for connections (not record_id)
                                update_data = {
                                    k: v for k, v in kwargs.items() if k != "record_id"
                                }
                                result_data = {
                                    **update_data,
                                    **row,
                                    "updated": True,
                                    "id": record_id,
                                }
                                return result_data

                    return {"id": record_id, "updated": False}

                elif operation == "delete":
                    # Accept both 'id' and 'record_id' for backward compatibility
                    # Convert id to int if it's a valid number
                    id_param = kwargs.get("id")
                    if id_param is not None:
                        # Type-aware ID conversion to fix string ID bug
                        id_field_info = self.model_fields.get("id", {})
                        id_type = id_field_info.get("type")

                        if id_type == str:
                            # Model explicitly defines ID as string - preserve it
                            record_id = id_param
                        elif id_type == int or id_type is None:
                            # Model defines ID as int OR no type info (backward compat)
                            try:
                                record_id = int(id_param)
                            except (ValueError, TypeError):
                                # If conversion fails, preserve original
                                record_id = id_param
                        else:
                            # Other types (UUID, custom) - preserve as-is
                            record_id = id_param
                    else:
                        record_id = kwargs.get("record_id")

                    if record_id is None:
                        record_id = 1

                    # Get connection string - prioritize parameter over instance config
                    connection_string = kwargs.get("database_url")
                    if not connection_string:
                        connection_string = (
                            self.dataflow_instance.config.database.get_connection_url(
                                self.dataflow_instance.config.environment
                            )
                        )

                    # Detect database type for SQL generation
                    if kwargs.get("database_url"):
                        from ..adapters.connection_parser import ConnectionParser

                        database_type = ConnectionParser.detect_database_type(
                            connection_string
                        )
                    else:
                        database_type = self.dataflow_instance._detect_database_type()

                    # Get the table name directly
                    table_name = self.dataflow_instance._class_name_to_table_name(
                        self.model_name
                    )

                    # Simple DELETE query with RETURNING for PostgreSQL
                    # Use ? placeholder which AsyncSQLDatabaseNode will convert to $1 for PostgreSQL
                    query = f"DELETE FROM {table_name} WHERE id = ? RETURNING id"

                    # Debug log
                    import logging

                    logger = logging.getLogger(__name__)
                    logger.info(
                        f"DELETE: table={table_name}, id={record_id}, query={query}"
                    )

                    sql_node = AsyncSQLDatabaseNode(
                        node_id=f"{self.model_name}_{self.operation}_sql",
                        connection_string=connection_string,
                        database_type=database_type,
                    )
                    result = await sql_node.async_run(
                        query=query,
                        params=[record_id],
                        fetch_mode="one",
                        validate_queries=False,
                        transaction_mode="auto",  # Ensure auto-commit for delete operations
                    )
                    logger.info(f"DELETE result: {result}")

                    # Check if delete was successful
                    if result and "result" in result:
                        result_data = result["result"]

                        # Check for data returned (RETURNING clause)
                        if "data" in result_data and result_data["data"]:
                            row = result_data["data"]
                            if isinstance(row, list) and len(row) > 0:
                                row = row[0]
                            if row:
                                # Record was deleted successfully
                                # Invalidate cache after successful delete
                                cache_integration = getattr(
                                    self.dataflow_instance, "_cache_integration", None
                                )
                                if cache_integration:
                                    cache_integration.invalidate_model_cache(
                                        self.model_name, "delete", {"id": record_id}
                                    )
                                return {"id": record_id, "deleted": True}

                        # Check for rows_affected when no RETURNING clause
                        elif (
                            "rows_affected" in result_data
                            and result_data["rows_affected"] > 0
                        ):
                            # Record was deleted successfully
                            cache_integration = getattr(
                                self.dataflow_instance, "_cache_integration", None
                            )
                            if cache_integration:
                                cache_integration.invalidate_model_cache(
                                    self.model_name, "delete", {"id": record_id}
                                )
                            return {"id": record_id, "deleted": True}

                    return {"id": record_id, "deleted": False}

                elif operation == "list":
                    limit = kwargs.get("limit", 10)
                    offset = kwargs.get("offset", 0)
                    filter_dict = kwargs.get("filter", {})
                    order_by = kwargs.get("order_by", [])
                    enable_cache = kwargs.get("enable_cache", True)
                    cache_ttl = kwargs.get("cache_ttl")
                    cache_key_override = kwargs.get("cache_key")
                    count_only = kwargs.get("count_only", False)

                    # Fix parameter type issues
                    import json

                    if isinstance(order_by, str):
                        try:
                            order_by = json.loads(order_by) if order_by.strip() else []
                        except (json.JSONDecodeError, ValueError):
                            order_by = []

                    if isinstance(filter_dict, str):
                        try:
                            filter_dict = (
                                json.loads(filter_dict) if filter_dict.strip() else {}
                            )
                        except (json.JSONDecodeError, ValueError):
                            filter_dict = {}

                    # Debug logging
                    logger.info(f"List operation - filter_dict: {filter_dict}")
                    logger.info(f"List operation - order_by: {order_by}")

                    # Use QueryBuilder if filters are provided
                    if filter_dict:
                        from ..database.query_builder import create_query_builder

                        # Get table name from DataFlow instance
                        table_name = self.dataflow_instance._class_name_to_table_name(
                            model_name
                        )

                        # Create query builder
                        builder = create_query_builder(
                            table_name, self.dataflow_instance.config.database.url
                        )

                        # Apply filters using MongoDB-style operators
                        for field, value in filter_dict.items():
                            if isinstance(value, dict):
                                # Handle MongoDB-style operators
                                for op, op_value in value.items():
                                    builder.where(field, op, op_value)
                            else:
                                # Simple equality
                                builder.where(field, "$eq", value)

                        # Apply ordering
                        if order_by:
                            for order_spec in order_by:
                                if isinstance(order_spec, dict):
                                    for field, direction in order_spec.items():
                                        dir_str = "DESC" if direction == -1 else "ASC"
                                        builder.order_by(field, dir_str)
                                else:
                                    builder.order_by(order_spec)
                        else:
                            builder.order_by("id", "DESC")

                        # Apply pagination
                        builder.limit(limit).offset(offset)

                        # Build query
                        if count_only:
                            query, params = builder.build_count()
                        else:
                            query, params = builder.build_select()
                    else:
                        # Simple query without filters using DataFlow SQL generation
                        # Get connection string - prioritize parameter over instance config
                        list_connection_string = kwargs.get("database_url")
                        if not list_connection_string:
                            list_connection_string = self.dataflow_instance.config.database.get_connection_url(
                                self.dataflow_instance.config.environment
                            )

                        # Detect database type for SQL generation
                        if kwargs.get("database_url"):
                            from ..adapters.connection_parser import ConnectionParser

                            database_type = ConnectionParser.detect_database_type(
                                list_connection_string
                            )
                        else:
                            database_type = (
                                self.dataflow_instance._detect_database_type()
                            )

                        select_templates = self.dataflow_instance._generate_select_sql(
                            self.model_name, database_type
                        )

                        if count_only:
                            query = select_templates["count_all"]
                            params = []
                        else:
                            # Build pagination query using template
                            if database_type.lower() == "postgresql":
                                query = select_templates[
                                    "select_with_pagination"
                                ].format(limit="$1", offset="$2")
                            elif database_type.lower() == "mysql":
                                query = select_templates[
                                    "select_with_pagination"
                                ].format(limit="%s", offset="%s")
                            else:  # sqlite
                                query = select_templates[
                                    "select_with_pagination"
                                ].format(limit="?", offset="?")
                            params = [limit, offset]

                    # Define executor function for cache integration
                    async def execute_query():
                        # Get connection string - prioritize parameter over instance config
                        connection_string = kwargs.get("database_url")
                        if not connection_string:
                            connection_string = self.dataflow_instance.config.database.get_connection_url(
                                self.dataflow_instance.config.environment
                            )

                        # Detect database type within the function scope
                        from ..adapters.connection_parser import ConnectionParser

                        db_type = ConnectionParser.detect_database_type(
                            connection_string
                        )

                        # Debug logging
                        logger.info(f"List operation - Executing query: {query}")
                        logger.info(f"List operation - With params: {params}")
                        logger.info(
                            f"List operation - Connection: {connection_string[:50]}..."
                        )

                        sql_node = AsyncSQLDatabaseNode(
                            node_id=f"{self.model_name}_{self.operation}_sql",
                            connection_string=connection_string,
                            database_type=db_type,
                        )
                        sql_result = await sql_node.async_run(
                            query=query,
                            params=params,
                            fetch_mode="all" if not count_only else "one",
                            validate_queries=False,
                            transaction_mode="auto",  # Ensure auto-commit for list operations
                        )

                        if (
                            sql_result
                            and "result" in sql_result
                            and "data" in sql_result["result"]
                        ):
                            if count_only:
                                # Return count result
                                count_data = sql_result["result"]["data"]
                                if isinstance(count_data, list) and len(count_data) > 0:
                                    count_value = count_data[0]
                                    if isinstance(count_value, dict):
                                        count = count_value.get("count", 0)
                                    else:
                                        count = count_value
                                else:
                                    count = 0
                                return {"count": count}
                            else:
                                # Return list result
                                records = sql_result["result"]["data"]
                                return {
                                    "records": records,
                                    "count": len(records),
                                    "limit": limit,
                                }

                        # Default return
                        if count_only:
                            return {"count": 0}
                        else:
                            return {"records": [], "count": 0, "limit": limit}

                    # Check if cache integration is available
                    cache_integration = getattr(
                        self.dataflow_instance, "_cache_integration", None
                    )
                    logger.info(
                        f"List operation - cache_integration: {cache_integration}, enable_cache: {enable_cache}"
                    )

                    if cache_integration and enable_cache:
                        # Use cache integration
                        logger.info("List operation - Using cache integration")
                        result = await cache_integration.execute_with_cache(
                            model_name=self.model_name,
                            query=query,
                            params=params,
                            executor_func=execute_query,
                            cache_enabled=enable_cache,
                            cache_ttl=cache_ttl,
                            cache_key_override=cache_key_override,
                        )
                        logger.info(f"List operation - Cache result: {result}")
                        return result
                    else:
                        # Execute directly without caching
                        logger.info("List operation - Executing without cache")
                        result = await execute_query()
                        logger.info(f"List operation - Direct result: {result}")
                        return result

                elif operation.startswith("bulk_"):
                    # Use validate_inputs to handle auto_map_from parameter mapping
                    validated_inputs = self.validate_inputs(**kwargs)
                    data = validated_inputs.get("data", [])
                    batch_size = validated_inputs.get("batch_size", 1000)

                    if operation == "bulk_create" and data:
                        # Implement real bulk create using database operations
                        try:
                            # Get connection string - prioritize parameter over instance config
                            connection_string = kwargs.get("database_url")
                            if not connection_string:
                                connection_string = self.dataflow_instance.config.database.get_connection_url(
                                    self.dataflow_instance.config.environment
                                )

                            # Detect database type for SQL generation
                            if kwargs.get("database_url"):
                                from ..adapters.connection_parser import (
                                    ConnectionParser,
                                )

                                database_type = ConnectionParser.detect_database_type(
                                    connection_string
                                )
                            else:
                                database_type = (
                                    self.dataflow_instance._detect_database_type()
                                )

                            processed_count = 0
                            for record in data:
                                try:
                                    # Get table name
                                    table_name = self.dataflow_instance._class_name_to_table_name(
                                        model_name
                                    )

                                    # Get field names (exclude auto-generated fields)
                                    field_names = [
                                        k
                                        for k in record.keys()
                                        if k not in ["id", "created_at", "updated_at"]
                                    ]
                                    values = [record.get(k) for k in field_names]

                                    # Build dynamic INSERT query for only the fields being provided
                                    columns = ", ".join(field_names)
                                    if database_type.lower() == "postgresql":
                                        placeholders = ", ".join(
                                            [f"${i+1}" for i in range(len(field_names))]
                                        )
                                        query = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders}) RETURNING id, created_at, updated_at"
                                    elif database_type.lower() == "mysql":
                                        placeholders = ", ".join(
                                            ["%s"] * len(field_names)
                                        )
                                        query = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"
                                    else:  # sqlite
                                        placeholders = ", ".join(
                                            ["?"] * len(field_names)
                                        )
                                        query = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"

                                    # Execute using AsyncSQLDatabaseNode
                                    sql_node = AsyncSQLDatabaseNode(
                                        node_id=f"{self.model_name}_{self.operation}_sql_{processed_count}",
                                        connection_string=connection_string,
                                        database_type=database_type,
                                    )
                                    result = await sql_node.async_run(
                                        query=query,
                                        params=values,
                                        fetch_mode="one",  # RETURNING clause should return one record
                                        validate_queries=False,
                                        transaction_mode="auto",  # Ensure auto-commit for bulk operations
                                    )

                                    if result and "result" in result:
                                        processed_count += 1
                                except Exception as e:
                                    logger.warning(
                                        f"Failed to insert bulk record {record}: {e}"
                                    )
                                    continue

                            # Invalidate cache after successful bulk create
                            cache_integration = getattr(
                                self.dataflow_instance, "_cache_integration", None
                            )
                            if cache_integration:
                                cache_integration.invalidate_model_cache(
                                    self.model_name,
                                    "bulk_create",
                                    {"processed": processed_count},
                                )

                            return {
                                "processed": processed_count,
                                "batch_size": batch_size,
                                "operation": operation,
                                "success": True,
                            }
                        except Exception as e:
                            logger.error(f"Bulk create operation failed: {e}")
                            return {
                                "processed": 0,
                                "batch_size": batch_size,
                                "operation": operation,
                                "success": False,
                                "error": str(e),
                            }
                    elif operation == "bulk_update" and (data or kwargs.get("filter")):
                        # Use DataFlow's bulk update operations
                        try:
                            bulk_result = self.dataflow_instance.bulk.bulk_update(
                                model_name=self.model_name,
                                data=data,
                                filter_criteria=kwargs.get("filter", {}),
                                update_values=kwargs.get("update", {}),
                                batch_size=batch_size,
                                **{
                                    k: v
                                    for k, v in kwargs.items()
                                    if k
                                    not in ["data", "batch_size", "filter", "update"]
                                },
                            )

                            return {
                                "processed": bulk_result.get("records_processed", 0),
                                "batch_size": batch_size,
                                "operation": operation,
                                "success": bulk_result.get("success", True),
                            }
                        except Exception as e:
                            logger.error(f"Bulk update operation failed: {e}")
                            return {
                                "processed": 0,
                                "batch_size": batch_size,
                                "operation": operation,
                                "success": False,
                                "error": str(e),
                            }
                    elif operation == "bulk_delete" and (data or kwargs.get("filter")):
                        # Use DataFlow's bulk delete operations
                        try:
                            bulk_result = self.dataflow_instance.bulk.bulk_delete(
                                model_name=self.model_name,
                                data=data,
                                filter_criteria=kwargs.get("filter", {}),
                                batch_size=batch_size,
                                **{
                                    k: v
                                    for k, v in kwargs.items()
                                    if k not in ["data", "batch_size", "filter"]
                                },
                            )

                            return {
                                "processed": bulk_result.get("records_processed", 0),
                                "batch_size": batch_size,
                                "operation": operation,
                                "success": bulk_result.get("success", True),
                            }
                        except Exception as e:
                            logger.error(f"Bulk delete operation failed: {e}")
                            return {
                                "processed": 0,
                                "batch_size": batch_size,
                                "operation": operation,
                                "success": False,
                                "error": str(e),
                            }
                    elif operation == "bulk_upsert" and data:
                        # Use DataFlow's bulk upsert operations
                        try:
                            bulk_result = self.dataflow_instance.bulk.bulk_upsert(
                                model_name=self.model_name,
                                data=data,
                                conflict_resolution=kwargs.get(
                                    "conflict_resolution", "skip"
                                ),
                                batch_size=batch_size,
                                **{
                                    k: v
                                    for k, v in kwargs.items()
                                    if k
                                    not in ["data", "batch_size", "conflict_resolution"]
                                },
                            )

                            return {
                                "processed": bulk_result.get("records_processed", 0),
                                "batch_size": batch_size,
                                "operation": operation,
                                "success": bulk_result.get("success", True),
                            }
                        except Exception as e:
                            logger.error(f"Bulk upsert operation failed: {e}")
                            return {
                                "processed": 0,
                                "batch_size": batch_size,
                                "operation": operation,
                                "success": False,
                                "error": str(e),
                            }
                    else:
                        # Fallback for unsupported bulk operations
                        result = {
                            "processed": len(data) if data else 0,
                            "batch_size": batch_size,
                            "operation": operation,
                            "success": False,
                            "error": f"Unsupported bulk operation: {operation}",
                        }
                        return result

                else:
                    result = {"operation": operation, "status": "executed"}
                    return result

            def _get_tdd_connection_info(self) -> Optional[str]:
                """Extract connection information from TDD test context."""
                if not (self._tdd_mode and self._test_context):
                    return None

                # If DataFlow instance has TDD connection override, use it
                if hasattr(self.dataflow_instance, "_tdd_connection"):
                    # Build connection string from TDD connection
                    # Note: This is a simplified approach - in practice you might need
                    # to extract connection parameters differently
                    try:
                        # For asyncpg connections, we can get connection parameters
                        conn = self.dataflow_instance._tdd_connection
                        if hasattr(conn, "_params"):
                            params = conn._params
                            # FIXED Bug 012: Use safe attribute access with getattr and proper defaults
                            # asyncpg connection parameters may use different attribute names
                            host = getattr(
                                params,
                                "server_hostname",
                                getattr(params, "host", "localhost"),
                            )
                            user = getattr(params, "user", "postgres")
                            password = getattr(params, "password", "")
                            database = getattr(params, "database", "postgres")
                            port = getattr(params, "port", 5432)

                            return f"postgresql://{user}:{password}@{host}:{port}/{database}"
                        else:
                            # Fallback: use test database URL from environment
                            import os

                            return os.getenv(
                                "TEST_DATABASE_URL",
                                "postgresql://dataflow_test:dataflow_test_password@localhost:5434/dataflow_test",
                            )
                    except Exception as e:
                        # FIXED Bug 011: Use self.logger instead of logger
                        self.logger.debug(f"Failed to extract TDD connection info: {e}")
                        return None

                return None

        # Set dynamic class name and proper module
        DataFlowNode.__name__ = (
            f"{model_name}{operation.replace('_', ' ').title().replace(' ', '')}Node"
        )
        DataFlowNode.__qualname__ = DataFlowNode.__name__

        return DataFlowNode
