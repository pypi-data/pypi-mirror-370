import logging
import os
import subprocess
import sys
from collections.abc import Sequence
from copy import deepcopy
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any, cast

from lsprotocol.types import Diagnostic, TextEdit, DiagnosticSeverity

from .aggregator import Aggregator
from .helpers import full_range, JSONReader
from .hasher import compute_hash

logger = logging.getLogger(__name__)


def print_tree(
    start_path: Path, prefix: str = "", lines: list[str] | None = None
) -> list[str]:
    lines = lines if lines is not None else []
    children = sorted(start_path.iterdir())
    for idx, child in enumerate(children):
        connector = "└── " if idx == len(children) - 1 else "├── "
        lines.append(f"{prefix}{connector}{child.name}")
        if child.is_dir():
            extension = "    " if idx == len(children) - 1 else "│   "
            lines = print_tree(child, prefix + extension, lines)
    return lines


class Transpiler:

    def __init__(
        self, source_tech: str, target_tech: str, overrides_file: str | None = None
    ):
        self._license_file = self._locate_license()
        self._binary = self._locate_binary()
        self._source_tech = source_tech
        mappings = self.load_config_mappings()
        self._source_type = self._get_source_type(mappings, source_tech)
        self._config_file = self._locate_config(mappings, source_tech, target_tech)
        self._overrides_file = Path(overrides_file) if overrides_file else None
        suffix = f" with overrides file '{overrides_file}'" if overrides_file else ""
        logger.info(f"Using config file '{self._config_file}'{suffix}")

    def transpile(
        self, file_name: str, source_code: str
    ) -> tuple[Sequence[TextEdit], Sequence[Diagnostic]]:
        with TemporaryDirectory(prefix="bladerunner_") as tempdir:
            return self._transpile(tempdir, file_name, source_code)

    def _transpile(
        self, tempdir: str, file_name: str, source_code: str
    ) -> tuple[Sequence[TextEdit], Sequence[Diagnostic]]:
        # prepare fs
        workdir = Path(tempdir)
        originals_dir = workdir / "originals"
        originals_dir.mkdir(parents=True, exist_ok=True)

        original_file = originals_dir / file_name
        original_file.parent.mkdir(parents=True, exist_ok=True)
        transpiled_dir = workdir / "transpiled"
        transpiled_dir.mkdir(parents=True, exist_ok=True)
        self._store_source(original_file, source_code)
        error = self._run_binary(workdir, transpiled_dir, original_file)
        if error:
            diagnostic = Diagnostic(
                range=full_range(source_code),
                message=error,
                severity=DiagnosticSeverity.Error,
                code="PARSING-FAILURE",
            )
            return [], [diagnostic]
        aggregator = Aggregator(transpiled_dir)
        try:
            transpiled = aggregator.aggregate()
        except FileNotFoundError:
            tree = "\n".join(print_tree(transpiled_dir))
            error_msg = f"Error transpiling file: {file_name}:\n{tree}"
            logger.error(error_msg)
            diagnostic = Diagnostic(
                range=full_range(source_code),
                message=error_msg,
                severity=DiagnosticSeverity.Error,
                code="CONVERSION-FAILURE",
            )
            return [], [diagnostic]

        edits = [TextEdit(range=full_range(source_code), new_text=transpiled)]
        return edits, []

    def _locate_binary(self) -> Path:
        if "darwin" in sys.platform:
            tool = "MacOS/dbxconv"
        elif "win" in sys.platform:
            tool = "Windows/dbxconv.exe"
        elif "linux" in sys.platform:
            tool = "Linux/dbxconv"
        else:
            raise ValueError(f"Unsupported platform: {sys.platform}")
        return Path(__file__).parent / "Converter" / "bin" / tool

    def _locate_license(self):
        return Path(__file__).parent / "Converter" / "bin" / "converter_key.txt"

    def _get_source_type(
        self, mappings: dict[str, dict[str, Any]], source_tech: str
    ) -> str:
        if source_tech not in mappings.keys():
            raise ValueError(f"No mapping for source tech {source_tech}")
        mapping = mappings[source_tech]
        return mapping["source-type"]

    def _locate_config(
        self, mappings: dict[str, dict[str, Any]], source_tech: str, target_tech: str
    ) -> Path:
        if source_tech not in mappings.keys():
            raise ValueError(f"No mapping for source tech {source_tech}")
        mapping = mappings[source_tech]
        targets: dict[str, str] = mapping.get("targets") or {}
        if target_tech not in targets.keys():
            raise ValueError(
                f"No mapping for source tech {source_tech} and target tech {target_tech}"
            )
        config_file_name = cast(str, targets.get(target_tech))
        all_folders = os.listdir(self.configs_folder())
        names = list(filter(lambda cfg: cfg.upper() == source_tech, all_folders))
        if len(names) != 1:
            raise ValueError(
                f"Could not locate config folder for source tech {source_tech}"
            )
        config_path = self.configs_folder() / names[0] / config_file_name
        if not config_path.exists():
            msg = (
                f"Could not locate config file {config_file_name} "
                f"for source tech {source_tech} and target tech {target_tech}"
            )
            raise ValueError(msg)
        return config_path

    @classmethod
    def configs_folder(cls) -> Path:
        return Path(__file__).parent / "Converter" / "Configs"

    @classmethod
    def load_config_mappings(cls) -> dict[str, Any]:
        config_path = (
            Path(__file__).parent / "Converter" / "Configs" / "tech_mapper_main.json"
        )
        return JSONReader.load(config_path)

    def _store_source(self, file_path: Path, source_code: str) -> None:
        file_path.write_text(source_code, encoding="utf-8")

    def _run_binary(
        self, workdir: Path, transpiled_dir: Path, source: Path
    ) -> str | None:
        cwd = os.getcwd()
        try:
            os.chdir(workdir)
            return self._run_binary_in_workdir(workdir, transpiled_dir, source)
        finally:
            os.chdir(cwd)

    def _run_binary_in_workdir(
        self, workdir: Path, transpiled_dir: Path, source: Path
    ) -> str | None:
        try:
            config_names = [self._config_file.name]
            if self._overrides_file:
                config_names = [str(self._overrides_file)]
            args = [
                str(self._binary),
                self._source_type,
                "-u",
                ",".join(config_names),
                "-n",
                str(transpiled_dir.relative_to(workdir)),
                "-i",
                str(source.relative_to(workdir)),
            ]
            if self._source_type == "SQL":
                args.extend(["-s", self._source_tech])
            hashed = compute_hash(args)
            args.extend(["-H", hashed])
            env = deepcopy(os.environ)
            # converter needs access to included configs
            env["BB_CONFIG_CONVERTER_DIR"] = str(self._config_file.parent.parent)
            env["UTF8_NOT_SUPPORTED"] = str(1)
            completed = subprocess.run(
                args,
                cwd=str(workdir),
                env=env,
                capture_output=True,
                text=True,
                check=False,
            )
            # capture output before managing return code
            if completed.stdout:
                for line in completed.stdout.split("\n"):
                    logger.info(line)
            if completed.stderr:
                for line in completed.stderr.split("\n"):
                    logger.error(line)
            # manage return code
            completed.check_returncode()
            return None
        # it is good practice to catch broad exceptions raised by launching a child process
        except Exception as e:  # pylint: disable=broad-exception-caught
            logger.error("Conversion failed", exc_info=e)
            return str(e)
