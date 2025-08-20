from __future__ import annotations
import io
import logging
import random
import os
from pathlib import Path
import textwrap
from typing import Any, Callable, TypedDict

from pandas import DataFrame
import pytest

import rich
from rich.syntax import Syntax

import relationalai as rai
from relationalai.clients import config as cfg
from relationalai import debugging
from relationalai.debugging import logger
from relationalai.errors import RAIException
from relationalai.metamodel import Task

################################################################################
# Parameterize tests over all files in a directory
################################################################################

def path_to_slug(path: Path, base_path:str|Path):
    return str(path.relative_to(base_path)).replace("/", "__").replace(".py", "")

def all_files_in_dir(test_case_dir: Path, *, pattern = "*.py"):
    "Decorator to parameterize a pytest over files in the given directory."
    test_case_files = [path for path in test_case_dir.rglob(pattern)]
    return pytest.mark.parametrize(
        "file_path", test_case_files, ids=lambda path: path_to_slug(path, test_case_dir)
    )

################################################################################
# Tap block info out of the debug log
################################################################################

class ISourceInfo(TypedDict):
    file: str
    line: int
    block: str

class IPassInfo(TypedDict):
    name: str
    task: str
    elapsed: float

class ISampledResults(TypedDict):
    values: DataFrame
    count: int

class Block(TypedDict):
    task: Task
    source: ISourceInfo
    passes: list[IPassInfo]
    emitted: str
    emit_time: float
    results: ISampledResults|None
    alt_format_results: Any|None
    elapsed: float|None

class QueryTextLogger(logging.Handler):
    def __init__(self):
        super().__init__()
        # compilation events that get 'results' added to them
        self.blocks: list[Block] = []

    def emit(self, record):
        d = record.msg
        if isinstance(d, dict):
            if d["event"] == "compilation":
                self.blocks.append({
                    "task": d["task"],
                    "source": d["source"],
                    "passes": d["passes"],
                    "emitted": d["emitted"],
                    "emit_time": d["emit_time"],
                    "results": None,
                    "alt_format_results": None,
                    "elapsed": None
                })
            elif d["event"] == "time" and d["type"] == "query" and not d.get("internal"):
                last = self.blocks[-1]
                last["results"] = d["results"]
                last["alt_format_results"] = d.get("alt_format_results")
                last["elapsed"] = d["elapsed"]

################################################################################
# Snapshot validation
################################################################################

class SnapshotError(Exception):
    def __init__(self, file_path: Path, code: str, task: Task, header: str|None = None, footer: str|None = None):
        self.file_path = file_path
        self.source_code = code
        self.task = task
        self.header = header
        self.footer = footer

    def __str__(self):
        file_path = self.file_path

        with io.StringIO() as buf:
            console = rich.console.Console(file=buf, force_terminal=True)
            if self.header:
                console.print(self.header)

            source_info = debugging.get_source(self.task)
            assert source_info and source_info.line is not None
            source = debugging.find_block_in(self.source_code, source_info.line, str(file_path))

            base = os.getcwd()
            console.print("\nIn", f"./{file_path.relative_to(base)}" if file_path.is_relative_to(base) else file_path)
            if source.source:
                console.print(Syntax(source.source, "python", dedent=True, line_numbers=True, start_line=source.line, padding=1))

            if self.footer:
                console.print("\n" + self.footer)
            v = buf.getvalue()
        return v

    def __repr__(self):
        return self.__str__()

class ChangedSnapshotError(SnapshotError):
    def __init__(self, file_path: Path, code: str, task: Task, snap_file: str, diff: str):
        header = f"The value for the following block no longer matches its snapshot ({snap_file}):"
        footer = f"[bold]Diff[/bold]\n{diff}\n\n" + \
        "[yellow]If this change is expected, you can update the snapshot by running pytest with [bold]--snapshot-update[/bold][/yellow]"
        super().__init__(file_path, code, task, header, footer)

class NewSnapshotError(SnapshotError):
    def __init__(self, file_path: Path, code: str, task: Task, value: str|None):
        header = "No snapshot exists for the following block:"
        footer = textwrap.dedent(f"""
        Got:
        {value}
        [yellow]To save the current result as a snapshot, run pytest with [bold]--snapshot-update[/bold][/yellow]
        """)
        super().__init__(file_path, code, task, header, footer)


def exec_traced(code: str, model_kwargs:dict|None = None, file_path: str|None = None) -> list[Block]:
    # install logger to capture Rel compilation
    query_logger = QueryTextLogger()
    logger.addHandler(query_logger)


    model_kwargs = model_kwargs or {}
    if file_path:
        # ensure that the exec knows what file is being run
        model_kwargs["__file__"] = str(file_path)

    try:
        if file_path:
            code_object = compile(code, file_path, 'exec')
            exec(code_object, model_kwargs)
        else:
            exec(code, model_kwargs)
    except RAIException as err:
        err.pprint() # @FIXME: Is this still needed?
        raise err
    finally:
        logger.removeHandler(query_logger)

    return query_logger.blocks

def validate_block_snapshots(
        file_path: Path,
        snapshot,
        get_snapshot_str: Callable, # given a block, return the snapshot string
        snapshot_prefix:str,
        model_kwargs:dict|None = None
    ):
    """Execute the program at `file_path`, applying `get_snapshot_str` to all
    blocks and ensuring the result has not changed since the last run."""
    with open(file_path, "r") as file:
        code = file.read()
        # @TODO: Consider suppressing stdout

        blocks = exec_traced(code, model_kwargs, str(file_path))
        block_index = 0
        for block in blocks:
            snapshot_path = f"{snapshot_prefix}{block_index}.txt"
            cmp_string = None
            try:
                cmp_string = get_snapshot_str(block)
                if cmp_string is not None:
                    snapshot.assert_match(cmp_string, snapshot_path)
                    # only counting blocks that actually assert something
                    block_index += 1
            except RAIException as err:
                err.pprint()
                raise err from None
            except AssertionError as err:
                lines = str(err).splitlines()
                if "doesn't exist" in lines[0]:
                    raise NewSnapshotError(file_path, code, block["task"], cmp_string) from None

                if len(lines) >= 3 and "does not match" in lines[0]:
                    diff = '\n'.join(lines[3:])
                    raise ChangedSnapshotError(file_path, code, block["task"], snapshot_path, diff) from None

                raise


def randomize(name: str) -> str:
    return f"{name}_{random.randint(1000000000, 9999999999)}"

def do_snapshot_test(
        snapshot,
        file_path: Path,
        config: cfg.Config|None = None,
        engine_size: str|None = None,
        runs: int = 1,
        outer_span_type: str = "test",
        create_db: bool = True,
    ):
    """Execute the program at `file_path`, validating that query results
    have not changed since the last run. Uses the given `config` and
    `engine_size` if provided, or the ambient config if not."""
    test_name = file_path.stem

    provider = rai.Resources(config=config)
    config = provider.config

    def get_results(event: Block):
        if event["alt_format_results"]:
            return str(event["alt_format_results"].to_pandas())
        if event["results"]:
            return str(event["results"]["values"])

    with debugging.span(outer_span_type, name=test_name, engine_size=engine_size):
        for i in range(runs):
            with debugging.span("run", idx=i):
                program_span = debugging.get_program_span()
                db_name = randomize(test_name)
                validate_block_snapshots(file_path, snapshot, get_results, "query", {
                    "name": db_name,
                    "config": config,
                    "span": program_span,
                })
                # Some tests always use the same DB, never creating a DB named `db_name`,
                # so we don't need to delete it.
                if create_db:
                    try:
                        provider.delete_graph(db_name)
                    except Exception as e:
                        print(f"Failed to delete graph {db_name}: {e}")
