import logging
from pathlib import Path
from typing import Any

from lsprotocol.types import (
    InitializeParams,
    Registration,
    RegistrationParams,
    INITIALIZE,
    TEXT_DOCUMENT_DID_OPEN,
    TEXT_DOCUMENT_DID_CLOSE,
    LanguageKind,
    Diagnostic,
    DiagnosticSeverity,
    DidOpenTextDocumentParams,
    DidCloseTextDocumentParams,
    NotebookDocumentSyncOptions,
    TextDocumentSyncKind,
)

from pygls.lsp.server import LanguageServer

from databricks.labs.bladebridge.helpers import map_dialect_to_source_tech, full_range
from databricks.labs.bladebridge.lsp_extension import (
    TRANSPILE_TO_DATABRICKS_CAPABILITY,
    TranspileDocumentParams,
    TranspileDocumentResult,
    TRANSPILE_TO_DATABRICKS_METHOD,
)
from databricks.labs.bladebridge.transpiler import Transpiler
from databricks.labs.bladebridge.__about__ import __version__

logging.basicConfig(filename="lsp-server.log", filemode="w", level=logging.DEBUG)

logger = logging.getLogger(__name__)


class Server(LanguageServer):

    def __init__(
        self,
        name: str,
        version: str,
        *args,
        text_document_sync_kind: TextDocumentSyncKind = TextDocumentSyncKind.Incremental,
        notebook_document_sync: NotebookDocumentSyncOptions | None = None,
        **kwargs,
    ):
        super().__init__(
            name,
            version,
            *args,
            text_document_sync_kind,
            notebook_document_sync,
            **kwargs,
        )
        self._transpiler: Transpiler | None = None

    async def did_initialize(self, init_params: InitializeParams) -> None:
        registrations = [
            Registration(
                id=TRANSPILE_TO_DATABRICKS_CAPABILITY["id"],
                method=TRANSPILE_TO_DATABRICKS_CAPABILITY["method"],
            )
        ]
        init_options: dict[str, Any] = init_params.initialization_options or {}
        morph: dict[str, Any] = init_options.get("remorph", {})
        dialect = morph.get("source-dialect", "ansi")
        source_tech = map_dialect_to_source_tech(dialect)
        options: dict[str, Any] = init_options.get("options") or {}
        overrides_file: str | None = options.get("overrides-file")
        target_tech: str = options.get("target-tech", "SQL")
        self._transpiler = Transpiler(source_tech, target_tech, overrides_file)
        register_params = RegistrationParams(registrations)
        await self.client_register_capability_async(register_params)

    def transpile_to_databricks(
        self, params: TranspileDocumentParams
    ) -> TranspileDocumentResult:
        source_sql = self.workspace.get_text_document(params.uri).source
        if self._transpiler:
            changes, diagnostics = self._transpiler.transpile(
                Path(params.uri).name, source_sql
            )
            return TranspileDocumentResult(
                uri=params.uri,
                language_id=LanguageKind.Sql,
                changes=changes,
                diagnostics=diagnostics,
            )
        diagnostic = Diagnostic(
            range=full_range(source_sql),
            message="Transpiler is not initialized",
            severity=DiagnosticSeverity.Error,
        )
        return TranspileDocumentResult(
            uri=params.uri,
            language_id=LanguageKind.Sql,
            changes=[],
            diagnostics=[diagnostic],
        )


server = Server("bladebridge-transpiler", __version__)


@server.feature(INITIALIZE)
async def lsp_did_initialize(params: InitializeParams) -> None:
    await server.did_initialize(params)


@server.feature(TEXT_DOCUMENT_DID_OPEN)
async def lsp_text_document_did_open(params: DidOpenTextDocumentParams) -> None:
    logger.debug(f"open-document-uri={params.text_document.uri}")


@server.feature(TEXT_DOCUMENT_DID_CLOSE)
async def lsp_text_document_did_close(params: DidCloseTextDocumentParams) -> None:
    logger.debug(f"close-document-uri={params.text_document.uri}")


@server.feature(TRANSPILE_TO_DATABRICKS_METHOD)
def transpile_to_databricks(params: TranspileDocumentParams) -> TranspileDocumentResult:
    return server.transpile_to_databricks(params)


if __name__ == "__main__":
    server.start_io()
