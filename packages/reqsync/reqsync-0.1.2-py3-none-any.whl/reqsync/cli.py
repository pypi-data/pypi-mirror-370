# src/reqsync/cli.py
from __future__ import annotations

from enum import Enum
from pathlib import Path
from typing import Any, Optional

import typer
from click.core import ParameterSource

from ._logging import setup_logging
from ._types import ExitCode, Options
from .config import load_project_config, merge_options
from .core import sync


class PolicyEnum(str, Enum):
    LOWER_BOUND = "lower-bound"
    FLOOR_ONLY = "floor-only"
    FLOOR_AND_CAP = "floor-and-cap"
    UPDATE_IN_PLACE = "update-in-place"


app = typer.Typer(
    add_completion=False,
    no_args_is_help=True,
    help="Synchronize requirements.txt to match installed versions safely.",
)


# This aligns with the test runner's expectation and eliminates the "unexpected argument" error.
@app.callback(invoke_without_command=True)
def main_cli(
    ctx: typer.Context,
    path: Path = typer.Option(
        Path("requirements.txt"),
        "--path",
        help="Path to requirements.txt",
        dir_okay=False,
    ),
    follow_includes: bool = typer.Option(True, help="Follow -r includes recursively"),
    update_constraints: bool = typer.Option(False, help="Allow updating constraint files"),
    policy: PolicyEnum = typer.Option(
        PolicyEnum.LOWER_BOUND,
        help="Policy: lower-bound | floor-only | floor-and-cap | update-in-place",
    ),
    allow_prerelease: bool = typer.Option(False, help="Adopt pre/dev versions"),
    keep_local: bool = typer.Option(False, help="Keep local version suffixes (+local)"),
    no_upgrade: bool = typer.Option(False, help="Do not run pip upgrade; just rewrite to current env"),
    pip_timeout_sec: int = typer.Option(900, help="Timeout for pip upgrade in seconds"),
    pip_args: str = typer.Option("", help="Allowlisted pip args to pass through"),
    only: Optional[str] = typer.Option(None, help="Comma-separated package globs to include"),
    exclude: Optional[str] = typer.Option(None, help="Comma-separated package globs to exclude"),
    check: bool = typer.Option(False, help="Exit nonzero if changes would be made"),
    dry_run: bool = typer.Option(False, help="Preview changes without writing"),
    show_diff: bool = typer.Option(False, help="Show unified diff"),
    json_report: Optional[Path] = typer.Option(None, help="Write JSON report to this path"),
    backup_suffix: str = typer.Option(".bak", help="Backup suffix"),
    timestamped_backups: bool = typer.Option(True, help="Use timestamped backups"),
    log_file: Optional[Path] = typer.Option(None, help="Optional log file path"),
    verbosity: int = typer.Option(0, "--verbose", "-v", count=True, help="Increase logging verbosity"),
    quiet: bool = typer.Option(False, "--quiet", "-q", help="Reduce logging"),
    system_ok: bool = typer.Option(False, help="Allow running outside a venv"),
    allow_hashes: bool = typer.Option(False, help="Skip hashed stanzas instead of refusing"),
    allow_dirty: bool = typer.Option(True, help="Allow running with dirty git repo"),
    last_wins: bool = typer.Option(False, help="If duplicates across includes, last definition wins"),
    use_config: bool = typer.Option(True, help="Load reqsync.toml or [tool.reqsync] from pyproject"),
) -> None:
    """
    Upgrade env and rewrite requirements to match installed versions while preserving formatting.
    """
    setup_logging(verbosity=verbosity, quiet=quiet, log_file=log_file)
    opts = Options(path=Path("requirements.txt"))
    if use_config:
        config_from_file = load_project_config(Path(".").resolve())
        opts = merge_options(opts, config_from_file)
    cli_overrides: dict[str, Any] = {
        k: v for k, v in ctx.params.items() if ctx.get_parameter_source(k) is not ParameterSource.DEFAULT
    }
    opts = merge_options(opts, cli_overrides)
    try:
        result = sync(opts)
    except FileNotFoundError:
        typer.secho(f"Requirements file not found: {opts.path}", fg=typer.colors.RED, err=True)
        raise typer.Exit(ExitCode.MISSING_FILE) from None
    except RuntimeError as err:
        msg = str(err)
        if "hash pins" in msg:
            code = ExitCode.HASHES_PRESENT
        elif "Refusing to run outside a virtualenv" in msg:
            code = ExitCode.SYSTEM_PYTHON_BLOCKED
        elif "pip install -U failed" in msg:
            code = ExitCode.PIP_FAILED
        elif "Write failed and backups restored" in msg:
            code = ExitCode.WRITE_FAILED_ROLLED_BACK
        else:
            code = ExitCode.GENERIC_ERROR
        typer.secho(msg, fg=typer.colors.RED, err=True)
        raise typer.Exit(code) from err

    if opts.json_report:
        from .report import to_json_report, write_json_report

        write_json_report(to_json_report(result.files), str(opts.json_report))

    if result.changed:
        if opts.show_diff or opts.dry_run:
            typer.echo(result.diff or "")
        if opts.check:
            raise typer.Exit(ExitCode.CHANGES_WOULD_BE_MADE) from None

    raise typer.Exit(ExitCode.OK) from None


def main() -> None:
    app()


if __name__ == "__main__":
    main()
