# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing_extensions import Literal, TypeAlias

__all__ = ["BatchStatus"]

BatchStatus: TypeAlias = Literal["created", "processing", "completed", "failed", "partially_failed"]
