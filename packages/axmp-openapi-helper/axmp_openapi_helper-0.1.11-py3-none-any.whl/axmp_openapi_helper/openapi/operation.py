"""This module provides a model for the API operation."""

from __future__ import annotations

import logging
from typing import Type

from pydantic import BaseModel, ConfigDict, create_model

logger = logging.getLogger(__name__)


class AxmpAPIOperation(BaseModel):
    """A model for the API operation."""

    server_name: str
    name: str
    description: str
    path: str
    method: str
    path_params: Type[BaseModel] | None = None
    query_params: Type[BaseModel] | None = None
    request_body: Type[BaseModel] | None = None

    @property
    def args_schema(self) -> Type[BaseModel]:
        """Create the arguments schema for the API operation."""
        model_name = "".join(word.capitalize() for word in self.name.split("_"))
        return self._create_args_schema(
            model_name=f"{model_name}ArgsSchema",
            models=[self.path_params, self.query_params, self.request_body],
        )

    def _create_args_schema(
        self,
        *,
        model_name: str,
        models: list[Type[BaseModel] | None],
    ) -> Type[BaseModel]:
        merged_fields = {}
        for model in models:
            if model:
                for field_name, field_info in model.model_fields.items():
                    merged_fields[field_name] = (field_info.annotation, field_info)

        return create_model(
            model_name, **merged_fields, __config__=ConfigDict(use_enum_values=True)
        )
