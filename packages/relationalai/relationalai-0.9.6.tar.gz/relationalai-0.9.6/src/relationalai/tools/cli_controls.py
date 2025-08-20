#pyright: reportPrivateImportUsage=false
from __future__ import annotations
import io
import os
from typing import Callable, Sequence, TextIO, cast, Any, List
from pathlib import Path
from InquirerPy.base.complex import FakeDocument
from prompt_toolkit.key_binding import KeyPressEvent
from prompt_toolkit.validation import ValidationError
import rich
from rich.console import Console
from rich.color import Color
import sys
from InquirerPy import inquirer, utils as inquirer_utils
from InquirerPy.base.control import Choice
import time
import threading
import itertools
import shutil
from wcwidth import wcwidth

from relationalai import debugging

from ..environments import runtime_env, NotebookRuntimeEnvironment, SnowbookEnvironment, HexEnvironment, JupyterEnvironment

#--------------------------------------------------
# Constants
#--------------------------------------------------

REFETCH = "[REFETCH LIST]"
MANUAL_ENTRY = "[MANUAL ENTRY]"

#--------------------------------------------------
# Style
#--------------------------------------------------

STYLE = inquirer_utils.get_style({
    "fuzzy_prompt": "#e5c07b"
}, False)

#--------------------------------------------------
# Helpers
#--------------------------------------------------

def rich_str(string:str, style:str|None = None) -> str:
    output = io.StringIO()
    console = Console(file=output, force_terminal=True)
    console.print(string, style=style)
    return output.getvalue()

def nat_path(path: Path, base: Path):
    resolved_path = path.resolve()
    resolved_base = base.resolve()
    if resolved_base in resolved_path.parents or resolved_path == resolved_base:
        return resolved_path.relative_to(resolved_base)
    else:
        return resolved_path.absolute()

def get_default(value:str|None, list_of_values:Sequence[str]):
    if value is None:
        return None
    list_of_values_lower = [v.lower() for v in list_of_values]
    value_lower = value.lower()
    if value_lower in list_of_values_lower:
        return value

#--------------------------------------------------
# Dividers
#--------------------------------------------------

def divider(console=None, flush=False):
    div = "\n[dim]---------------------------------------------------\n "
    if console is None:
        rich.print(div)
    else:
        console.print(div)
    if flush:
        sys.stdout.flush()

def abort():
    rich.print()
    rich.print("[yellow]Aborted")
    divider()
    sys.exit(1)

#--------------------------------------------------
# Prompts
#--------------------------------------------------

default_bindings = cast(Any, {
    "interrupt": [
        {"key": "escape"},
        {"key": "c-c"},
        {"key": "c-d"}
    ],
    "skip": [
        {"key": "c-s"}
    ]
})

def prompt(message:str, value:str|None, newline=False, validator:Callable|None = None, invalid_message:str|None = None) -> str:
    if value:
        return value
    if invalid_message is None:
        invalid_message = "Invalid input"
    try:
        result:str = inquirer.text(
            message,
            validate=validator,
            invalid_message=invalid_message,
            keybindings=default_bindings,
        ).execute()
    except KeyboardInterrupt:
        abort()
        raise Exception("Unreachable")
    if newline:
        rich.print("")
    return result

def select(message:str, choices:List[str|Choice], value:str|None, newline=False, **kwargs) -> str|Any:
    if value:
        return value
    try:
        result:str = inquirer.select(message, choices, keybindings=default_bindings, **kwargs).execute()
    except KeyboardInterrupt:
        abort()
        raise Exception("Unreachable")
    if newline:
        rich.print("")
    return result

def _enumerate_static_choices(choices: inquirer_utils.InquirerPyChoice) -> inquirer_utils.InquirerPyChoice:
    return [{"name": f"{i+1} {choice}", "value": choice} for i, choice in enumerate(choices)]

def _enumerate_choices(choices: inquirer_utils.InquirerPyListChoices) -> inquirer_utils.InquirerPyListChoices:
    if callable(choices):
        return lambda session: _enumerate_static_choices(choices(session))
    else:
        return _enumerate_static_choices(choices)

def _fuzzy(message:str, choices:inquirer_utils.InquirerPyListChoices, default:str|None = None, multiselect=False, show_index=False, **kwargs) -> str|list[str]:
    if show_index:
        choices = _enumerate_choices(choices)    

    try:
        kwargs["keybindings"] = default_bindings
        if multiselect:
            kwargs["keybindings"] = { # pylint: disable=assignment-from-no-return
                "toggle": [
                    {"key": "tab"},   # toggle choices
                ],
                "toggle-down": [
                    {"key": "tab", "filter":False},
                ],
            }.update(default_bindings)
            kwargs["multiselect"] = True

        # NOTE: Using the builtin `default` kwarg to do this also filters
        #       results which is undesirable and confusing for pre-filled
        #       fields, so we move the cursor ourselves using the internals :(
        prompt = inquirer.fuzzy(message, choices=choices, max_height=8, border=True, style=STYLE, **kwargs)
        prompt._content_control._get_choices(prompt._content_control.choices, default)

        return prompt.execute()
    except KeyboardInterrupt:
        return abort()

def fuzzy(message:str, choices:inquirer_utils.InquirerPyListChoices, default:str|None = None, show_index=False, **kwargs) -> str:
    return cast(str, _fuzzy(message, choices, default=default, show_index=show_index, **kwargs))

def fuzzy_multiselect(message:str, choices:inquirer_utils.InquirerPyListChoices, default:str|None = None, show_index=False, **kwargs) -> list[str]:
    return cast(list[str], _fuzzy(message, choices, default=default, show_index=show_index, multiselect=True, **kwargs))

def fuzzy_with_refetch(prompt: str, type: str, fn: Callable, *args, **kwargs):
    exception = None
    auto_select = kwargs.get("auto_select", None)
    not_found_message = kwargs.get("not_found_message", None)
    manual_entry = kwargs.get("manual_entry", None)
    items = []
    with Spinner(f"Fetching {type}", f"Fetched {type}"):
        try:
            items = fn(*args)
        except Exception as e:
            exception = e
    if exception is not None:
        rich.print(f"\n[red]Error fetching {type}: {exception}\n")
        return exception
    if len(items) == 0:
        if not_found_message:
            rich.print(f"\n[yellow]{not_found_message}\n")
        else:
            rich.print(f"\n[yellow]No valid {type} found\n")
        return None

    if auto_select and len(items) == 1 and items[0].lower() == auto_select.lower():
        return auto_select

    if manual_entry:
        items.insert(0, MANUAL_ENTRY)
    items.insert(0, REFETCH)

    passed_default = kwargs.get("default", None)
    passed_mandatory = kwargs.get("mandatory", False)

    rich.print("")
    result = fuzzy(
        prompt,
        items,
        default=get_default(passed_default, items),
        mandatory=passed_mandatory
    )
    rich.print("")

    while result == REFETCH:
        result = fuzzy_with_refetch(prompt, type, fn, *args, **kwargs)
    return result

def confirm(message:str, default:bool = False) -> bool:
    try:
        return inquirer.confirm(message, default=default, keybindings=default_bindings).execute()
    except KeyboardInterrupt:
        return abort()

def text(message:str, default:str|None = None, validator:Callable|None = None, invalid_message:str|None = None, **kwargs) -> str:
    if not invalid_message:
        invalid_message = "Invalid input"
    try:
        return inquirer.text(
            message,
            default=default or "",
            keybindings=default_bindings,
            validate=validator,
            invalid_message=invalid_message,
            **kwargs
        ).execute()
    except KeyboardInterrupt:
        return abort()

def password(message:str, default:str|None = None, validator:Callable|None = None, invalid_message:str|None = None) -> str:
    if invalid_message is None:
        invalid_message = "Invalid input"
    try:
        return inquirer.secret(
            message,
            default=default or "",
            keybindings=default_bindings,
            validate=validator,
            invalid_message=invalid_message
        ).execute()
    except KeyboardInterrupt:
        return abort()

def file(message: str, start_path:Path|None = None, allow_freeform=False, **kwargs) -> str|None:
    try:
        return FuzzyFile(message, start_path, allow_freeform=allow_freeform, max_height=8, border=True, style=STYLE, **kwargs).execute()
    except KeyboardInterrupt:
        return abort()

class FuzzyFile(inquirer.fuzzy):
    def __init__(self, message: str, initial_path: Path|None = None, allow_freeform = False,  *args, **kwargs):
        self.initial_path = initial_path or Path()
        self.current_path = Path(self.initial_path)
        self.allow_freeform = allow_freeform

        kwargs["keybindings"] = {
            **default_bindings,
            "answer": [
                {"key": os.sep},
                {"key": "enter"},
                {"key": "tab"},
                {"key": "right"}
            ],
            **kwargs.get("keybindings", {})
        }

        super().__init__(message, *args, **kwargs, choices=self._get_choices)

    def _get_prompt_message(self) -> List[tuple[str, str]]:
        pre_answer = ("class:instruction", f" {self.instruction} " if self.instruction else " ")
        result = str(nat_path(self.current_path, self.initial_path))

        if result:
            sep = " " if self._amark else ""
            return [
                ("class:answermark", self._amark),
                ("class:answered_question", f"{sep}{self._message} "),
                ("class:answer", f"{result}{os.sep if not self.status['answered'] else ''}"),
            ]
        else:
            sep = " " if self._qmark else ""
            return [
                ("class:answermark", self._amark),
                ("class:questionmark", self._qmark),
                ("class:question", f"{sep}{self._message}"),
                pre_answer
            ]

    def _handle_enter(self, event: KeyPressEvent) -> None:
        try:
            fake_document = FakeDocument(self.result_value)
            self._validator.validate(fake_document)  # type: ignore
            cc = self.content_control
            if self._multiselect:
                self.status["answered"] = True
                if not self.selected_choices:
                    self.status["result"] = [cc.selection["name"]]
                    event.app.exit(result=[cc.selection["value"]])
                else:
                    self.status["result"] = self.result_name
                    event.app.exit(result=self.result_value)
            else:
                res_value = cc.selection["value"]
                self.current_path /= res_value
                if self.current_path.is_dir():
                    self._update_choices()
                else:
                    self.status["answered"] = True
                    self.status["result"] = cc.selection["name"]
                    event.app.exit(result=str(nat_path(self.current_path, self.initial_path)))
        except ValidationError as e:
            self._set_error(str(e))
        except IndexError:
            self.status["answered"] = True
            res = self._get_current_text() if self.allow_freeform else None
            if self._multiselect:
                res = [res] if res is not None else []
            self.status["result"] = res
            event.app.exit(result=res)

    def _get_choices(self, _ = None):
        choices = os.listdir(self.current_path)
        choices.append("..")
        return choices

    def _update_choices(self):
        raw_choices = self._get_choices()
        cc = self.content_control
        cc.selected_choice_index = 0
        cc._raw_choices = raw_choices
        cc.choices = cc._get_choices(raw_choices, None)
        cc._safety_check()
        cc._format_choices()
        self._buffer.reset()

#--------------------------------------------------
# Spinner
#--------------------------------------------------

class Spinner:
    """Shows a spinner control while a task is running.
    The finished_message will not be printed if there was an exception and the failed_message is provided.
    """
    busy = False

    def __init__(
        self,
        message="",
        finished_message: str = "",
        failed_message=None,
        delay=None,
        leading_newline=False,
        trailing_newline=False,
    ):
        self.message = message
        self.finished_message = finished_message
        self.failed_message = failed_message
        self.spinner_generator = itertools.cycle(["▰▱▱▱", "▰▰▱▱", "▰▰▰▱", "▰▰▰▰", "▱▰▰▰", "▱▱▰▰", "▱▱▱▰", "▱▱▱▱"])
        self.is_snowflake_notebook = isinstance(runtime_env, SnowbookEnvironment)
        self.is_hex = isinstance(runtime_env, HexEnvironment)
        self.is_jupyter = isinstance(runtime_env, JupyterEnvironment)
        self.in_notebook = isinstance(runtime_env, NotebookRuntimeEnvironment)
        self.is_tty = sys.stdout.isatty()

        self._set_delay(delay)
        self.leading_newline = leading_newline
        self.trailing_newline = trailing_newline
        self.last_message = ""
        self.display = None

    def _set_delay(self, delay: float|int|None) -> None:
        """Set appropriate delay based on environment and user input."""
        # If delay value is provided, validate and use it
        if delay:
            if isinstance(delay, (int, float)) and delay > 0:
                self.delay = float(delay)
                return
            else:
                raise ValueError(f"Invalid delay value: {delay}")
        # Otherwise, set delay based on environment
        elif self.is_hex:
            self.delay = 0 # Hex tries to append a new block each frame
        elif self.is_snowflake_notebook:
                self.delay = 0.5 # SF notebooks get bogged down
        elif self.in_notebook or self.is_tty:
            # Fast refresh for other notebooks or terminals with good printing support
            self.delay = 0.1
        else:
            # Otherwise disable the spinner animation entirely
            # for non-interactive environments.
            self.delay = 0

    def get_message(self, starting=False):
        max_width = shutil.get_terminal_size().columns
        spinner = "⏳⏳⏳⏳" if not self.is_tty and starting else next(self.spinner_generator)
        full_message = f"{spinner} {self.message}"
        if len(full_message) > max_width:
            return full_message[:max_width - 3] + "..."
        else:
            return full_message

    def update(self, message:str|None=None, color:str|None=None, file:TextIO|None=None, starting=False):
        if message is None:
            message = self.get_message(starting=starting)
        if self.is_jupyter:
            # @NOTE: IPython isn't available in CI. This won't ever get invoked w/out IPython available though.
            from IPython.display import HTML, display # pyright: ignore[reportMissingImports]
            color_string = ""
            if color:
                color_value = Color.parse(color)
                rgb_tuple = color_value.get_truecolor()
                rgb_hex = f"#{rgb_tuple[0]:02X}{rgb_tuple[1]:02X}{rgb_tuple[2]:02X}"
                color_string = f"color: {rgb_hex};" if color is not None else ""
            content = HTML(f"<span style='font-family: monospace;{color_string}'>{message}</span>")
            if self.display is not None:
                self.display.update(content)
            else:
                self.display = display(content, display_id=True)
        else:
            if self.can_use_terminal_colors() and color is not None:
                rich_message = f"[{color}]{message}"
            else:
                rich_message = message
            rich_string = rich_str(rich_message)
            def width(word):
                return sum(wcwidth(c) for c in word)
            diff = width(self.last_message) - width(rich_string)
            self.reset_cursor()
            rich.print(rich_message + (" " * diff), file=file, end="")
            if (file or sys.stdout).isatty() or self.in_notebook:
                (file or sys.stdout).flush()
            self.last_message = rich_string
    
    def can_use_terminal_colors(self):
        return not self.is_snowflake_notebook

    def update_messages(self, updater: dict[str, str]):
        if "message" in updater:
            self.message = updater["message"]
        if "finished_message" in updater:
            self.finished_message = updater["finished_message"]
        if "failed_message" in updater:
            self.failed_message = updater["failed_message"]
        self.update()

    def spinner_task(self):
        while self.busy and self.delay:
            self.update(color="magenta")
            time.sleep(self.delay) #type: ignore[union-attr] | we only call spinner_task if delay is not None anyway
            self.reset_cursor()

    def reset_cursor(self):
        if not self.is_jupyter:
            sys.stdout.write("\r")

    def __enter__(self):
        if self.leading_newline:
            rich.print()
        self.update(color="magenta", starting=True)
        # return control to the event loop briefly so stdout can be sure to flush:
        if self.delay:
            time.sleep(0.25)
        self.reset_cursor()
        if not self.delay:
            return self
        self.busy = True
        threading.Thread(target=self.spinner_task).start()
        return self

    def __exit__(self, exception, value, _):
        self.busy = False
        if exception is not None:
            if self.failed_message is not None:
                self.update(f"{self.failed_message} {value}", color="yellow", file=sys.stderr)
                rich.print()
                return True
            return False
        if self.delay: # will be None for non-interactive environments
            time.sleep(self.delay)
        self.reset_cursor()
        if self.finished_message != "":
            final_message = f"▰▰▰▰ {self.finished_message}"
            self.update(final_message, color="green")
            rich.print()
        elif self.finished_message == "":
            self.update("")
            self.reset_cursor()
        if self.trailing_newline:
            rich.print()

class SpanSpinner(Spinner):
    span: debugging.Span
    def __init__(self, span_type: str, *spinner_args, **spinner_kwargs):
        super().__init__(*spinner_args, **spinner_kwargs)
        self.span_type = span_type
        self.span_attrs = {}

    def attrs(self, **kwargs):
        self.span_attrs = kwargs
        return self

    def __enter__(self):
        self.span = debugging.span_start(self.span_type, **self.span_attrs)
        return super().__enter__()

    def __exit__(self, exc_type, exc_val, exc_tb):
        super().__exit__(exc_type, exc_val, exc_tb)
        debugging.span_end(self.span)
