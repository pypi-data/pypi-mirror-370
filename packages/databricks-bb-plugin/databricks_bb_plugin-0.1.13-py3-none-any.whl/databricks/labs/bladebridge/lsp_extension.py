"""
This file enhances LSP with the "document/transpileToDatabricks".
This enhancement is independent from pygls.
"""

from collections.abc import Sequence
from typing import Literal
from uuid import uuid4

import attrs
from lsprotocol import types as lsp_types_module
from lsprotocol.types import LanguageKind, TextEdit, Diagnostic, METHOD_TO_TYPES

TRANSPILE_TO_DATABRICKS_METHOD = "document/transpileToDatabricks"
TRANSPILE_TO_DATABRICKS_CAPABILITY = {
    "id": str(uuid4()),
    "method": TRANSPILE_TO_DATABRICKS_METHOD,
}


@attrs.define
class TranspileDocumentParams:
    uri: str = attrs.field()
    language_id: LanguageKind | str = attrs.field()


@attrs.define
class TranspileDocumentRequest:
    # 'id' is mandated by LSP
    # pylint: disable=invalid-name
    id: int | str = attrs.field()
    params: TranspileDocumentParams = attrs.field()
    method: Literal["document/transpileToDatabricks"] = "document/transpileToDatabricks"
    jsonrpc: str = attrs.field(default="2.0")


@attrs.define
class TranspileDocumentResult:
    uri: str = attrs.field()
    language_id: LanguageKind | str = attrs.field()
    changes: Sequence[TextEdit] = attrs.field()
    diagnostics: Sequence[Diagnostic] = attrs.field()


@attrs.define
class TranspileDocumentResponse:
    # 'id' is mandated by LSP
    # pylint: disable=invalid-name
    id: int | str = attrs.field()
    result: TranspileDocumentResult = attrs.field()
    jsonrpc: str = attrs.field(default="2.0")


METHOD_TO_TYPES[TRANSPILE_TO_DATABRICKS_METHOD] = (
    TranspileDocumentRequest,
    TranspileDocumentResponse,
    TranspileDocumentParams,
    None,
)


# ensure proper serialization of TranspileDocumentRequest
def install_special_properties():
    is_special_property = getattr(lsp_types_module, "is_special_property")

    def customized(cls: type, property_name: str) -> bool:
        if cls is TranspileDocumentRequest and property_name in {"method", "jsonrpc"}:
            return True
        return is_special_property(cls, property_name)

    setattr(lsp_types_module, "is_special_property", customized)


install_special_properties()
