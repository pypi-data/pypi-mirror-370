"""This module provides a model for the OpenAPI specification."""

import json
import logging
import re
from decimal import Decimal
from enum import Enum
from pathlib import Path
from typing import Annotated, Any, Dict, List, Tuple, Type, Union

from pydantic import BaseModel, ConfigDict, Field, create_model

from axmp_openapi_helper.openapi.fastapi.openapi_models import (
    OpenAPI,
    Operation,
    Parameter,
    ParameterInType,
    PathItem,
    Reference,
    Schema,
    SchemaOrBool,
)

logger = logging.getLogger(__name__)

SUPPORTED_METHODS: list[str] = [
    "get",
    "put",
    "post",
    "delete",
    "options",
    "head",
    "patch",
    "trace",
]


class SchemaType(Enum):
    """SchemaType is an enum for the schema type."""

    STRING = "string"
    NUMBER = "number"
    INTEGER = "integer"
    BOOLEAN = "boolean"
    OBJECT = "object"
    ARRAY = "array"
    NULL = "null"


class AxmpOpenAPI(OpenAPI):
    """AxmpOpenAPI is a subclass of OpenAPI."""

    @classmethod
    def from_spec_file(cls, file_path: str | Path):
        """Load OpenAPI from file.

        Args:
            file_path (str | Path): File path.

        Returns:
            AxmpOpenAPI: AxmpOpenAPI instance.
        """
        with open(file_path) as file:
            openapi = cls.model_validate_json(file.read())

            # convert paths to PathItem enforced
            if openapi.paths:
                converted_paths = {}
                for path, path_item in openapi.paths.items():
                    if isinstance(path_item, dict):
                        converted_paths[path] = PathItem.model_validate(path_item)
                    else:
                        converted_paths[path] = path_item
                openapi.paths.update(converted_paths)

            return openapi

    @classmethod
    def from_spec_string(cls, spec_string: str):
        """Load OpenAPI from specification string.

        Args:
            spec_string (str): OpenAPI specification string.

        Returns:
            AxmpOpenAPI: AxmpOpenAPI instance.
        """
        openapi = cls.model_validate_json(spec_string)
        # convert paths to PathItem enforced
        if openapi.paths:
            converted_paths = {}
            for path, path_item in openapi.paths.items():
                if isinstance(path_item, dict):
                    converted_paths[path] = PathItem.model_validate(path_item)
                else:
                    converted_paths[path] = path_item
            openapi.paths.update(converted_paths)

        return openapi

    @classmethod
    def from_spec_dict(cls, data: dict):
        """Load OpenAPI from specification dictionary.

        Args:
            spec_dict (dict): OpenAPI specification dictionary.
        """
        openapi = cls.model_validate_json(json.dumps(data, ensure_ascii=False))
        # convert paths to PathItem enforced
        if openapi.paths:
            converted_paths = {}
            for path, path_item in openapi.paths.items():
                if isinstance(path_item, dict):
                    converted_paths[path] = PathItem.model_validate(path_item)
                else:
                    converted_paths[path] = path_item
            openapi.paths.update(converted_paths)

        return openapi

    # NOTE: @deprecated, use from_spec_file or from_spec_string instead
    @classmethod
    def from_openapi(cls, openapi: OpenAPI):
        """Load OpenAPI from OpenAPI.

        Args:
            openapi (OpenAPI): OpenAPI.

        Returns:
            AxmpOpenAPI: AxmpOpenAPI instance.
        """
        openapi = cls.model_validate_json(openapi.model_dump_json())  # type: ignore
        # convert paths to PathItem enforced
        if openapi.paths:
            converted_paths = {}
            for path, path_item in openapi.paths.items():
                if isinstance(path_item, dict):
                    converted_paths[path] = PathItem.model_validate(path_item)
                else:
                    converted_paths[path] = path_item
            openapi.paths.update(converted_paths)

        return openapi

    def generate_models_by_path_and_method(
        self,
        *,
        path: str,
        method: str,
    ) -> Tuple[BaseModel | None, BaseModel | None, BaseModel | None]:
        """Generate parameter and request body models from operation and component schema.

        Returns:
            Tuple[BaseModel, BaseModel, BaseModel]: Tuple of parameter and request body models.
                First element is query parameter model.
                Second element is path parameter model.
                Third element is request body model.
        """
        operation = self.get_operation_by_path_method(path=path, method=method)

        query_parameter_model = None
        path_parameter_model = None
        request_body_model = None

        query_parameters = []
        path_parameters = []

        if operation.parameters:
            for parameter in operation.parameters:
                if parameter.in_ is ParameterInType.query:
                    query_parameters.append(parameter)
                elif parameter.in_ is ParameterInType.path:
                    path_parameters.append(parameter)

        if len(query_parameters) > 0:
            query_parameter_model = self._generate_model_from_parameters(
                path=path,
                method=method,
                parameters=query_parameters,
                parameter_in_type=ParameterInType.query,
            )
        else:
            query_parameter_model = None

        if len(path_parameters) > 0:
            path_parameter_model = self._generate_model_from_parameters(
                path=path,
                method=method,
                parameters=path_parameters,
                parameter_in_type=ParameterInType.path,
            )
        else:
            path_parameter_model = None

        if operation.requestBody:
            # Handle both RequestBody and Reference types
            request_body = operation.requestBody
            
            # If requestBody is a Reference, resolve it
            if hasattr(request_body, 'ref') and request_body.ref:
                # This is a Reference type, need to resolve it
                ref = request_body.ref
                class_name, component = self._get_component_schema_by_ref(ref=ref)
                if component and hasattr(component, 'content'):
                    # The component is a RequestBody with content
                    content_ = component.content
                else:
                    logger.warning(f"Reference not found or invalid: {ref}")
                    request_body_model = None
            else:
                # This is a direct RequestBody type
                content_ = request_body.content
            
            if content_:
                schema_ = None
                # Process only the first type in the content array and ignore subsequent types.
                for i, (_, media_type) in enumerate(content_.items()):
                    if i == 0:
                        schema_ = media_type.schema_
                        break
                if schema_:
                    if schema_.title is None:
                        schema_.title = path+"-"+method
                    request_body_model = self._generate_model_from_request_body_schema(
                        schema_=schema_
                    )
                else:
                    logger.warning("Schema is not found for content type")
                    request_body_model = None
            else:
                request_body_model = None
        else:
            request_body_model = None

        return query_parameter_model, path_parameter_model, request_body_model

    def get_operation_by_path_method(self, *, path: str, method: str) -> Operation:
        """Get operation from path.

        Args:
            path (str): Path.

        Returns:
            Operation: Operation.
        """
        method = method.lower()

        logger.debug(f"path: {path}, method: {method}")
        path_item = self.paths[path]

        if path_item is None:
            raise ValueError(f"Path {path} not found")

        logger.debug(
            f"path_item ::\n{path}: {path_item.model_dump_json(indent=4, exclude_none=True)}"
        )

        operation = None
        if isinstance(path_item, PathItem):
            if hasattr(path_item, method):
                operation = getattr(path_item, method)
                if operation is None:
                    raise ValueError(f"Method {method} not found in path {path}")
            else:
                raise ValueError(f"Method {method} not found in path {path}")
        else:
            raise ValueError(f"Path item {path_item} is not a PathItem")

        logger.debug(
            f"operation ::\n{method}: {operation.model_dump_json(indent=4, exclude_none=True)}"
        )

        return operation

    # get all tags of the operation of the pathitem of the paths of openapi spec
    def get_tags(self) -> list[str]:
        """Get all tags of the operation of the pathitem of the paths of openapi spec."""
        tags = []
        for path, path_item in self.paths.items():
            for method in SUPPORTED_METHODS:
                if hasattr(path_item, method):
                    operation: Operation = getattr(path_item, method)  # type: ignore
                    if operation:
                        if operation.tags:
                            tags.extend(operation.tags)

        return list(set(tags))

    # get operations by tag
    def get_operations_by_tag(self, *, tag: str) -> list[tuple[str, str, Operation]]:
        """Get operations by tag.

        Args:
            tag (str): Tag.

        Returns:
            list[tuple[str, str, Operation]]: List of operations.
                First element is path.
                Second element is method.
                Third element is operation.
        """
        logger.debug(f"tag: {tag}")
        if not tag:
            return []

        operations: list[tuple[str, str, Operation]] = []
        for path, path_item in self.paths.items():
            for method in SUPPORTED_METHODS:
                if hasattr(path_item, method):
                    operation: Operation = getattr(path_item, method)  # type: ignore
                    if operation:
                        if operation.tags:
                            if tag in operation.tags:
                                operations.append((path, method, operation))  # type: ignore
        return operations

    # get operations by path regular expression
    def get_operations_by_path_pattern(
        self, *, regex: str
    ) -> list[tuple[str, str, Operation]]:
        """Get operations by path regular expression.

        Args:
            regex (str): Regular expression.

        Returns:
            list[tuple[str, str, Operation]]: List of operations.
                First element is path.
                Second element is method.
                Third element is operation.
        """
        logger.debug(f"regex: {regex}")
        if not regex:
            return []

        operations: list[tuple[str, str, Operation]] = []
        for path, path_item in self.paths.items():
            if re.match(regex, path):
                for method in SUPPORTED_METHODS:
                    if hasattr(path_item, method):
                        operation: Operation = getattr(path_item, method)  # type: ignore
                        if operation:
                            operations.append((path, method, operation))  # type: ignore
        return operations

    # get operations by method
    def get_operations_by_method(
        self, *, method: str
    ) -> list[tuple[str, str, Operation]]:
        """Get operations by method.

        Args:
            method (str): Method.

        Returns:
            list[tuple[str, str, Operation]]: List of operations.
                First element is path.
                Second element is method.
                Third element is operation.
        """
        logger.debug(f"method: {method}")
        if not method:
            return []
        
        # Convert method to lowercase if it's uppercase
        method = method.lower()
        
        operations: list[tuple[str, str, Operation]] = []
        for path, path_item in self.paths.items():
            if hasattr(path_item, method):
                operation: Operation = getattr(path_item, method)  # type: ignore
                if operation:
                    operations.append((path, method, operation))  # type: ignore
        return operations

    def get_operations_by_tag_method_pattern(
        self, *, tags: list[str], methods: list[str], regex: str
    ) -> list[tuple[str, str, Operation]]:
        """Get operations by path and method.

        Args:
            tags (list[str]): Tags.
            methods (list[str]): Methods.
            regex (str): Regular expression.

        Returns:
            list[tuple[str, str, Operation]]: List of operations.
                First element is path.
                Second element is method.
                Third element is operation.
        """
        logger.debug(f"tags: {tags}, methods: {methods}, regex: {regex}")
        common_operations: list[tuple[str, str, Operation]] = []

        tag_matched_operations: list[tuple[str, str, Operation]] = []
        if tags:
            for tag in tags:
                tag_matched_operations.extend(self.get_operations_by_tag(tag=tag))

        method_matched_operations: list[tuple[str, str, Operation]] = []
        if methods:
            for method in methods:
                method_matched_operations.extend(
                    self.get_operations_by_method(method=method)
                )

        pattern_matched_operations: list[tuple[str, str, Operation]] = (
            self.get_operations_by_path_pattern(regex=regex)
        )

        if pattern_matched_operations and len(pattern_matched_operations) > 0:
            if tag_matched_operations and len(tag_matched_operations) > 0:
                if method_matched_operations and len(method_matched_operations) > 0:
                    for path, method, operation in pattern_matched_operations:
                        if (path, method) in [
                            (path, method) for path, method, _ in tag_matched_operations
                        ] and (path, method) in [
                            (path, method)
                            for path, method, _ in method_matched_operations
                        ]:
                            # check the duplicate operations by path and method of the common_operations
                            if (path, method, operation) not in common_operations:
                                common_operations.append((path, method, operation))
                else:
                    for path, method, operation in pattern_matched_operations:
                        if (path, method) in [
                            (path, method) for path, method, _ in tag_matched_operations
                        ]:
                            # check the duplicate operations by path and method of the common_operations
                            if (path, method, operation) not in common_operations:
                                common_operations.append((path, method, operation))
            else:
                if method_matched_operations and len(method_matched_operations) > 0:
                    for path, method, operation in pattern_matched_operations:
                        if (path, method) in [
                            (path, method)
                            for path, method, _ in method_matched_operations
                        ]:
                            # check the duplicate operations by path and method of the common_operations
                            if (path, method, operation) not in common_operations:
                                common_operations.append((path, method, operation))
                else:
                    for path, method, operation in pattern_matched_operations:
                        # check the duplicate operations by path and method of the common_operations
                        if (path, method, operation) not in common_operations:
                            common_operations.append((path, method, operation))
        else:
            if tag_matched_operations and len(tag_matched_operations) > 0:
                if method_matched_operations and len(method_matched_operations) > 0:
                    for path, method, operation in tag_matched_operations:
                        if (path, method) in [
                            (path, method)
                            for path, method, _ in method_matched_operations
                        ]:
                            # check the duplicate operations by path and method of the common_operations
                            if (path, method, operation) not in common_operations:
                                common_operations.append((path, method, operation))
                else:
                    for path, method, operation in tag_matched_operations:
                        # check the duplicate operations by path and method of the common_operations
                        if (path, method, operation) not in common_operations:
                            common_operations.append((path, method, operation))
            else:
                if method_matched_operations and len(method_matched_operations) > 0:
                    for path, method, operation in method_matched_operations:
                        # check the duplicate operations by path and method of the common_operations
                        if (path, method, operation) not in common_operations:
                            common_operations.append((path, method, operation))
                else:
                    # NOTE: if all the *_matched_operations are empty, we should raise an error
                    logger.warning(
                        f"All the *_matched_operations are empty for tags: {tags}, methods: {methods}, regex: {regex}"
                    )
                    return []

        return common_operations

    def _generate_model_from_request_body_schema(
        self, *, schema_: Schema
    ) -> BaseModel | None:
        """Generate model from request body schema.

        Args:
            schema_ (Schema): Schema.

        Returns:
            Optional[BaseModel]: Model.
        """
        model_ = None
        if schema_.type:
            if schema_.type == SchemaType.ARRAY.value:
                ref = schema_.items.ref
                if ref:
                    field_type = self._get_field_type_from_schema(schema_=schema_)

                    # @TODO: enhance field definition
                    fields = {}
                    fields[schema_.title.lower()] = Annotated[
                        field_type, Field(default=...)
                    ]

                    logger.info(
                        f"Model for request body(array): {schema_.title} will be created"
                        f". field_type: {field_type}"
                    )

                    model_ = create_model(
                        schema_.title,
                        **fields,
                        __config__=ConfigDict(use_enum_values=True),
                    )
        else:
            ref = schema_.ref
            if ref:
                class_name, component_schema = self._get_component_schema_by_ref(
                    ref=ref
                )
                model_ = self._generate_model_from_component_schema(
                    class_name=class_name, schema_=component_schema
                )
            else:
                logger.warning(f"Ref is not found: {schema_.ref}")
                raise ValueError(f"Ref is not found: {schema_.ref}")

        return model_

    def _generate_model_from_parameters(
        self,
        *,
        path: str,
        method: str,
        parameter_in_type: ParameterInType,
        parameters: List[Parameter | Reference] | None,
    ) -> Type[BaseModel] | None:
        """Generate model from parameters.

        Args:
            operation_id (str): Operation ID.
            parameter_in_type (ParameterInType): Parameter in type.
                Can be query, path, header, cookie.
            parameters (Optional[List[Union[Parameter, Reference]]]): Parameters.

        Returns:
            Type[BaseModel]: Generated model.
                If parameter_in_type is query, the model is query parameter model.
                If parameter_in_type is path, the model is path parameter model.
        """
        if parameters is None:
            return None

        if len(parameters) == 0:
            return None

        fields = {}
        for parameter in parameters:
            logger.debug(
                f"parameter: {parameter.model_dump_json(indent=4, exclude_none=True)}"
            )

            if isinstance(parameter, Reference):
                ...  # don't support reference
            else:
                field_name = parameter.name
                # @TODO: enhance field definition
                field_type, field = self._make_field_from_parameter(parameter=parameter)
                fields[field_name] = Annotated[field_type, field]

                logger.debug(f"field_name: {field_name}")
                logger.debug(f"field: {fields[field_name]}")

        replaced_path = re.sub(r"[/{}_]", "-", path)  # remove path params brackets
        model_name = "".join(word.capitalize() for word in replaced_path.split("-"))
        model_name = f"{model_name}{parameter_in_type.value.capitalize()}Parameters"

        log_str = (
            f"Model for {parameter_in_type.value} parameters: {model_name} will be created\n"
            f"Fields: {len(fields)}\n"
        )
        for field_name, field_info in fields.items():
            log_str += f"  - {field_name}: {field_info}\n"

        logger.info(log_str)

        return create_model(
            model_name, **fields, __config__=ConfigDict(use_enum_values=True)
        )

    def _make_field_from_parameter(
        self,
        *,
        parameter: Parameter,
    ) -> Tuple[Type[Any], Field]:
        """Make field from parameter.

        Args:
            parameter_in_type (ParameterInType): Parameter in type.
            parameter (Parameter): Parameter.

        Returns:
            Tuple[Any, Field]: Tuple of field type and field.
        """
        logger.debug(f"parameter: {parameter}")

        # This schema is the schema of the parameter
        field_schema: Schema = parameter.schema_

        # NOTE: append parameter description and name into the field description and title
        # because the enum type description is retouched by the _get_field_type_from_schema
        # so we need to append it before call _get_field_type_from_schema
        # Issue: https://github.com/cloudz-mp/zmp-zcp-toolkit/issues/11
        if (field_schema.description is None) and (parameter.description is not None):
            field_schema.description = parameter.description
        if (field_schema.title is None) and (parameter.name is not None):
            field_schema.title = parameter.name

        field_type = self._get_field_type_from_schema(schema_=field_schema)

        field = self._make_field_from_schema(
            schema_=field_schema, required=parameter.required
        )

        logger.debug(f"field_type: {field_type}")
        logger.debug(f"field: {field}")

        return (field_type, field)

    def _get_field_type_from_schema(
        self,
        *,
        schema_: Schema,
    ) -> Type[Any]:
        """Get field type from schema.

        Args:
            schema_ (Schema): Schema.

        Returns:
            Type[Any]: Field type.
        """
        logger.debug(f"schema_.type: {schema_.type}")

        field_type = None
        if schema_.type == SchemaType.STRING.value:
            field_type = str
        elif schema_.type == SchemaType.NUMBER.value:
            # NOTE: llm needs float for int when validate because of the max_digit
            field_type = Decimal
        elif schema_.type == SchemaType.INTEGER.value:
            # NOTE: llm needs float for int when validate because of the multipleOf,
            # maximum, minimum, exclusiveMaximum, exclusiveMinimum instead of int
            field_type = Decimal
        elif schema_.type == SchemaType.BOOLEAN.value:
            field_type = bool
        elif schema_.type == SchemaType.OBJECT.value:
            if schema_.additionalProperties:
                if isinstance(schema_.additionalProperties, Schema):
                    if schema_.additionalProperties.type:
                        field_type = dict[
                            str,
                            str
                            if schema_.additionalProperties.type
                            == SchemaType.STRING.value
                            else schema_.additionalProperties.type,
                        ]
                    else:
                        field_type = dict
                elif isinstance(schema_.additionalProperties, dict):
                    field_type = dict[
                        str,
                        str
                        if schema_.additionalProperties["type"]
                        == SchemaType.STRING.value
                        else schema_.additionalProperties["type"],
                    ]
                else:
                    field_type = dict
            else:
                field_type = dict
        elif schema_.type == SchemaType.ARRAY.value:
            if schema_.items:
                if isinstance(schema_.items, Schema):
                    if schema_.items.type:
                        if schema_.items.type == SchemaType.STRING.value:
                            field_type = list[str]
                        elif schema_.items.type == SchemaType.INTEGER.value:
                            # NOTE: llm needs float for int when validate because of the multipleOf,
                            # maximum, minimum, exclusiveMaximum, exclusiveMinimum instead of int
                            field_type = list[Decimal]
                        elif schema_.items.type == SchemaType.NUMBER.value:
                            # NOTE: llm needs float for int when validate because of the max_digit
                            field_type = list[Decimal]
                        elif schema_.items.type == SchemaType.BOOLEAN.value:
                            field_type = list[bool]
                        elif schema_.items.type == SchemaType.OBJECT.value:
                            # TODO: check if the additionalProperties is exist or not
                            field_type = list[dict]
                        else:
                            raise ValueError(
                                f"Unsupported array item type: {schema_.items.type}"
                            )
                    else:
                        if schema_.items.ref:
                            class_name, component_schema = (
                                self._get_component_schema_by_ref(ref=schema_.items.ref)
                            )
                            model_ = self._generate_model_from_component_schema(
                                class_name=class_name, schema_=component_schema
                            )

                            logger.debug(f"model_: {model_}")
                            logger.debug(f"type(model_): {type(model_)}")

                            field_type = list[model_]

                            # Append enum items into the description for LLM
                            # TODO: refactor this in another function
                            if isinstance(model_, type(Enum)):
                                schema_.description = (
                                    f"{schema_.description + '.' if schema_.description else ''}"
                                    f"Values are {', '.join(v.value for v in model_)}"
                                )
                        elif schema_.items.oneOf:
                            one_of = schema_.items.oneOf
                            types = []
                            for item in one_of:
                                if item.ref:
                                    class_name, component_schema = (
                                        self._get_component_schema_by_ref(ref=item.ref)
                                    )
                                    model_ = self._generate_model_from_component_schema(
                                        class_name=class_name, schema_=component_schema
                                    )
                                    types.append(model_)
                                else:
                                    logger.warning(
                                        f"Unsupported array item type because of ref is not found: {item}"
                                    )
                                    raise ValueError(
                                        f"Unsupported array item type because of ref is not found: {item}"
                                    )
                            if len(types) == 0:
                                field_type = Any
                            elif len(types) == 1:
                                field_type = list[types[0]]
                            else:
                                field_type = list[Union[tuple(types)]]
                        else:
                            logger.warning(
                                f"Unsupported array type because of ref is not found: {schema_.items}"
                            )
                            field_type = Any
                elif isinstance(schema_.items, dict):
                    field_type = list[dict]
            else:
                logger.warning(f"Type is array but items is not found: {schema_.items}")
                field_type = Any
        else:
            field_type = self._get_field_type_from_none_type_schema(schema_=schema_)

        return field_type

    def _get_field_type_from_none_type_schema(
        self,
        *,
        schema_: Schema,
    ) -> Type[Any]:
        """Get field type from none schema.

        Args:
            schema_ (Schema): Schema.

        Returns:
            Type[Any]: Field type.
        """
        if schema_.type is not None:
            if schema_.type != "null":
                # raise ValueError(f"Schema has type: {schema_.type}")
                logger.warning(f"Schema has type: {schema_.type}")

        all_of: List[SchemaOrBool] = schema_.allOf
        one_of: List[SchemaOrBool] = schema_.oneOf
        any_of: List[SchemaOrBool] = schema_.anyOf
        ref: str = schema_.ref

        if any_of:
            types = []
            for f_schema in any_of:
                # This is the schema of the parameter's schema (anyOf)
                if isinstance(f_schema, Schema):
                    f_type = self._get_field_type_from_schema(schema_=f_schema)
                    types.append(f_type)

                    # Extract other properties from f_schema and send to parent schema
                    # format, maxLength, minLength, pattern, etc.
                    for field_name, field_value in f_schema.model_dump(
                        exclude_none=True
                    ).items():
                        setattr(schema_, field_name, field_value)

            if len(types) == 0:
                field_type = Any
            elif len(types) == 1:
                field_type = types[0]
            else:
                field_type = Union[tuple(types)]
        elif one_of:
            # TODO: support oneOf, check using the real example
            ...
        elif all_of:
            types = []
            for f_schema in all_of:
                # This is the schema of the parameter's schema (allOf)
                if isinstance(f_schema, Schema):
                    if f_schema.type is not None:
                        raise ValueError(f"Schema has type: {f_schema.type}")
                    else:
                        class_name, component_schema = (
                            self._get_component_schema_by_ref(ref=f_schema.ref)
                        )
                        model_ = self._generate_model_from_component_schema(
                            class_name=class_name, schema_=component_schema
                        )

                        logger.debug(f"model_: {model_}")
                        logger.debug(f"type(model_): {type(model_)}")

                        types.append(model_)

                        # Append enum items into the description for LLM
                        if isinstance(model_, type(Enum)):
                            schema_.description = (
                                f"{schema_.description + '.' if schema_.description else ''}"
                                f"Values are {', '.join(v.value for v in model_)}"
                            )
                else:
                    raise ValueError(f"Unsupported schema type: {type(f_schema)}")

            if len(types) == 0:
                field_type = Any
            elif len(types) == 1:
                field_type = types[0]
            else:
                field_type = Union[tuple(types)]
        elif ref:
            class_name, component_schema = self._get_component_schema_by_ref(ref=ref)
            model_ = self._generate_model_from_component_schema(
                class_name=class_name, schema_=component_schema
            )

            logger.debug(f"model_: {model_}")
            logger.debug(f"type(model_): {type(model_)}")

            # Append enum items into the description for LLM
            if isinstance(model_, type(Enum)):
                schema_.description = (
                    f"{schema_.description + '.' if schema_.description else ''}"
                    f"Values are {', '.join(v.value for v in model_)}"
                )

            field_type = model_
        else:
            field_type = None

        return field_type

    def _make_field_from_schema(
        self,
        *,
        schema_: Schema,
        required: bool,
    ) -> Field:
        """Make field from schema.

        Args:
            schema_ (Schema): Schema.
            required (bool): Required.

        Returns:
            Field: Field of pydantic.
        """
        field = Field(
            default=schema_.default if not required else ...,
            title=schema_.title,
            description=schema_.description,
            min_length=schema_.minLength,
            max_length=schema_.maxLength,
            pattern=schema_.pattern,
            max_digits=int(schema_.maximum) if schema_.maximum is not None else None,
            lt=int(schema_.exclusiveMaximum)
            if schema_.exclusiveMaximum is not None
            else None,
            lte=int(schema_.maximum) if schema_.maximum is not None else None,
            gt=int(schema_.exclusiveMinimum)
            if schema_.exclusiveMinimum is not None
            else None,
            gte=int(schema_.minimum) if schema_.minimum is not None else None,
        )

        logger.debug(f"field from schema: {field}")

        return field

    def _get_component_schema_by_ref(
        self, *, ref: str
    ) -> Tuple[str | None, Any | None]:
        """Get component from reference.

        Args:
            ref (str): Reference.

        Returns:
            Tuple[str | None, Any | None]: Component name and component object.
        """
        # Handle different types of references
        if ref.startswith("#/components/schemas/"):
            ref = ref.replace("#/components/schemas/", "")
            if ref in self.components.schemas:
                return ref, self.components.schemas[ref]
        elif ref.startswith("#/components/requestBodies/"):
            ref = ref.replace("#/components/requestBodies/", "")
            if hasattr(self.components, 'requestBodies') and ref in self.components.requestBodies:
                return ref, self.components.requestBodies[ref]
        elif ref.startswith("#/components/responses/"):
            ref = ref.replace("#/components/responses/", "")
            if hasattr(self.components, 'responses') and ref in self.components.responses:
                return ref, self.components.responses[ref]
        elif ref.startswith("#/components/parameters/"):
            ref = ref.replace("#/components/parameters/", "")
            if hasattr(self.components, 'parameters') and ref in self.components.parameters:
                return ref, self.components.parameters[ref]
        
        logger.warning(f"Component not found: {ref}")
        return None, None

    def _generate_model_from_component_schema(
        self,
        *,
        class_name: str,
        schema_: Schema,
    ) -> Type[Enum] | Type[BaseModel] | None:
        """Generate model from component schema.

        Args:
            schema_ (Schema): Component schema.

        Raises:
            ValueError: Unsupported schema type.

        Returns:
            Type[BaseModel]: Generated model.
        """
        type_ = schema_.type

        if type_ == SchemaType.STRING.value:
            # for enum
            enum_: List[str] = schema_.enum
            if len(enum_) > 0:
                return Enum(schema_.title, {v: v for v in enum_})
            else:
                raise ValueError(f"Enum is not found: {schema_.title}")
        elif type_ == SchemaType.OBJECT.value:
            # for object
            if schema_.properties:
                return self._generate_model_from_properties(
                    class_name=class_name,
                    required_fields=schema_.required,
                    properties=schema_.properties,
                )
            elif schema_.allOf:
                models: list[Type[Enum] | Type[BaseModel] | None] = []
                for item in schema_.allOf:
                    if isinstance(item, Schema):
                        if item.ref:
                            ref_class_name, component_schema = (
                                self._get_component_schema_by_ref(ref=item.ref)
                            )
                            if isinstance(component_schema, Schema):
                                model_ = self._generate_model_from_component_schema(
                                    class_name=ref_class_name, schema_=component_schema
                                )
                            else:
                                logger.warning(f"Component schema is not a Schema type: {ref_class_name}")
                                model_ = None
                        else:
                            model_ = self._generate_model_from_component_schema(
                                class_name=f"{class_name}_TemporaryClass",  # It's a temporary class name
                                schema_=item,
                            )

                    models.append(model_)

                if len(models) == 0:
                    raise ValueError(f"AllOf items is not found: {schema_.allOf}")
                else:
                    merged_fields = {}
                    for model in models:
                        if model:
                            for field_name, field_info in model.model_fields.items():
                                # @TODO: enhance field definition
                                merged_fields[field_name] = Annotated[
                                    field_info.annotation, field_info
                                ]

                    log_str = (
                        f"Model for request body: {class_name} will be created\n"
                        f"Fields: {len(merged_fields)}\n"
                    )
                    for field_name, field_info in merged_fields.items():
                        log_str += f"  - {field_name}: {field_info}\n"

                    logger.info(log_str)

                    return create_model(
                        f"{class_name}",
                        **merged_fields,
                        __config__=ConfigDict(use_enum_values=True),
                    )
            else:
                raise ValueError(f"Properties is not found: {schema_}")
        else:
            raise ValueError(f"Unsupported schema type: {type_}")

    def _generate_model_from_properties(
        self,
        *,
        class_name: str,
        required_fields: List[str],
        properties: Dict[str, Tuple[Type[Any], Field]],
    ) -> Type[BaseModel]:
        """Generate model from properties.

        Args:
            properties (Dict[str, Tuple[Type[Any], Field]]): Properties.

        Returns:
            Type[BaseModel]: Generated model.
        """
        logger.info(f"class_name: {class_name}")
        logger.info(f"required_fields: {required_fields}")
        # logger.debug(f"properties: {properties}")

        fields = {}
        for field_name, field_schema in properties.items():
            if isinstance(field_schema, Schema):
                field_type = self._get_field_type_from_schema(schema_=field_schema)

                required = (
                    True if required_fields and field_name in required_fields else False
                )

                field = self._make_field_from_schema(
                    schema_=field_schema, required=required
                )

                logger.debug(f"field_type: {field_type}")
                logger.debug(f"field: {field}")

                # @TODO: enhance field definition
                fields[field_name] = Annotated[field_type, field]
            else:
                raise ValueError(f"Unsupported schema type: {type(field_schema)}")

        log_str = (
            f"Model for request body: {class_name} will be created\n"
            f"Fields: {len(fields)}\n"
        )
        for field_name, field_info in fields.items():
            log_str += f"  - {field_name}: {field_info}\n"

        logger.info(log_str)

        return create_model(
            f"{class_name}", **fields, __config__=ConfigDict(use_enum_values=True)
        )
