"""
Copyright CNRS/Inria/UniCA
Contributor(s): Eric Debreuve (eric.debreuve@cnrs.fr) since 2023
SEE COPYRIGHT NOTICE BELOW
"""

import dataclasses as d
import logging as l
import sys as s
import textwrap as text
import traceback as tcbk
import types as t
import typing as h
from datetime import date as date_t
from datetime import datetime as date_time_t
from os import sep as FOLDER_SEPARATOR
from pathlib import Path as path_t
from traceback import TracebackException as traceback_t

from logger_36.catalog.config.optional import MISSING_RICH_MESSAGE, RICH_IS_AVAILABLE
from logger_36.catalog.handler.console import console_handler_t
from logger_36.catalog.handler.file import file_handler_t
from logger_36.config.issue import ISSUE_CONTEXT_END, ISSUE_CONTEXT_SEPARATOR
from logger_36.config.message import (
    DATE_FORMAT,
    ELAPSED_TIME_SEPARATOR,
    LONG_ENOUGH,
    TIME_FORMAT,
)
from logger_36.constant.generic import NOT_PASSED
from logger_36.constant.handler import ANONYMOUS, HANDLER_KINDS, handler_codes_h
from logger_36.constant.issue import ISSUE_LEVEL_SEPARATOR, ORDER, order_h
from logger_36.constant.logger import (
    LOGGER_NAME,
    WARNING_LOGGER_NAME,
    WARNING_TYPE_COMPILED_PATTERN,
)
from logger_36.constant.memory import UNKNOWN_MEMORY_USAGE
from logger_36.constant.message import LINE_INDENT, TIME_LENGTH_m_1, expected_op_h
from logger_36.constant.path import PROJECT_FILE_RELATIVE
from logger_36.constant.record import (
    HIDE_WHERE_ATTR,
    SHOW_W_RULE_ATTR,
    STORE_MEMORY_ATTR,
)
from logger_36.extension.exception import OverrideExceptionFormat
from logger_36.task.format.message import MessageFromRecord, MessageWithActualExpected
from logger_36.task.format.rule import RuleAsText
from logger_36.task.measure.chronos import ElapsedTime
from logger_36.task.measure.memory import CurrentUsage as CurrentMemoryUsage
from logger_36.type.handler import any_handler_t as base_handler_t
from logger_36.type.issue import NewIssue, issue_t

if RICH_IS_AVAILABLE:
    from logger_36.catalog.handler.console_rich import console_rich_handler_t
else:
    from logger_36.catalog.handler.console import (
        console_handler_t as console_rich_handler_t,
    )

base_t = l.Logger

logger_handle_raw_h = h.Callable[[l.LogRecord], None]
logger_handle_with_self_h = h.Callable[[l.Logger, l.LogRecord], None]
logger_handle_h = logger_handle_raw_h | logger_handle_with_self_h

_DATE_TIME_ORIGIN = date_time_t.fromtimestamp(1970, None)
_DATE_ORIGIN = _DATE_TIME_ORIGIN.date()


@d.dataclass(slots=True, repr=False, eq=False)
class logger_t(base_t):
    """
    intercepted_wrn_handle: When warning interception is on, this stores the original
        "handle" method of the Python warning logger.

    _should_activate_log_interceptions: Loggers instantiated after a logger_t logger will
    be missed by an early call of ToggleLogInterceptions. Therefore, passing True for
    activate_log_interceptions only sets _should_activate_log_interceptions to True,
    which is later checked in AddHandler to effectively call ToggleLogInterceptions if
    _should_hold_messages is False (which normally indicates that the handler about to be
    added is the last one).

    _should_hold_messages: Must not be False until at least one handler has been added.
    """

    should_record_messages: bool = False
    exit_on_error: bool = False  # Implies exit_on_critical.
    exit_on_critical: bool = False

    events: dict[int, int] = d.field(init=False, default_factory=dict)
    recorded: list[tuple[int, str]] = d.field(init=False, default_factory=list)

    last_message_now: date_time_t = d.field(init=False, default=_DATE_TIME_ORIGIN)
    last_message_date: date_t = d.field(init=False, default=_DATE_ORIGIN)
    any_handler_stores_memory: bool = d.field(init=False, default=False)
    memory_usages: list[tuple[str, int]] = d.field(init=False, default_factory=list)
    context_levels: list[str] = d.field(init=False, default_factory=list)
    staged_issues: list[issue_t] = d.field(init=False, default_factory=list)
    intercepted_wrn_handle: logger_handle_h | None = d.field(init=False, default=None)
    intercepted_log_handles: dict[str, logger_handle_h] = d.field(
        init=False, default_factory=dict
    )
    _on_hold: list[l.LogRecord] = d.field(init=False, default_factory=list)
    _should_hold_messages: bool = d.field(init=False, default=True)
    _should_activate_log_interceptions: bool = d.field(init=False, default=False)

    name_: d.InitVar[str] = LOGGER_NAME
    level_: d.InitVar[int] = l.NOTSET
    activate_wrn_interceptions: d.InitVar[bool] = True
    activate_log_interceptions: d.InitVar[bool] = True

    @property
    def intercepts_warnings(self) -> bool:
        """"""
        return self.intercepted_wrn_handle is not None

    @property
    def intercepts_logs(self) -> bool:
        """"""
        return self.intercepted_log_handles.__len__() > 0

    @property
    def has_staged_issues(self) -> bool:
        """"""
        return self.staged_issues.__len__() > 0

    @property
    def n_staged_issues(self) -> int:
        """"""
        return self.staged_issues.__len__()

    @property
    def max_memory_usage(self) -> int:
        """"""
        if self.memory_usages.__len__() > 0:
            return max(tuple(zip(*self.memory_usages))[1])
        return UNKNOWN_MEMORY_USAGE

    @property
    def max_memory_usage_full(self) -> tuple[str, int]:
        """"""
        if self.memory_usages.__len__() > 0:
            where_s, usages = zip(*self.memory_usages)
            max_usage = max(usages)

            return where_s[usages.index(max_usage)], max_usage

        return "?", UNKNOWN_MEMORY_USAGE

    def __post_init__(
        self,
        name_: str,
        level_: int,
        activate_wrn_interceptions: bool,
        activate_log_interceptions: bool,
    ) -> None:
        """"""
        base_t.__init__(self, name_)
        self.setLevel(level_)
        self.propagate = False  # Part of base_t.

        for level in l.getLevelNamesMapping().values():
            self.events[level] = 0

        self.info(f'New logger "{self.name}" for "{PROJECT_FILE_RELATIVE}"')

        if activate_wrn_interceptions:
            self.ToggleWarningInterceptions(True)
        if activate_log_interceptions:
            self._should_activate_log_interceptions = True

        if self.exit_on_error:
            self.exit_on_critical = True

    def handle(self, record: l.LogRecord, /) -> None:
        """"""
        elapsed_time, now = ElapsedTime(should_return_now=True)

        if (self._on_hold.__len__() > 0) and not self._should_hold_messages:
            for held in self._on_hold:
                if self.should_record_messages:
                    self.recorded.append(
                        (held.levelno, MessageFromRecord(held, RuleAsText)[0])
                    )
                base_t.handle(self, held)
            self._on_hold.clear()

        if (date := now.date()) != self.last_message_date:
            self.last_message_date = date
            # levelno: Added for management by logging.Logger.handle.
            date_record = l.makeLogRecord(
                {
                    "name": self.name,
                    "levelno": l.INFO,
                    "msg": f"DATE: {date.strftime(DATE_FORMAT)}",
                    SHOW_W_RULE_ATTR: True,
                }
            )
            if self._should_hold_messages:
                self._on_hold.append(date_record)
            else:
                if self.should_record_messages:
                    self.recorded.append(
                        (
                            date_record.levelno,
                            MessageFromRecord(date_record, RuleAsText)[0],
                        )
                    )
                base_t.handle(self, date_record)

        # When.
        if now - self.last_message_now > LONG_ENOUGH:
            record.when_or_elapsed = now.strftime(TIME_FORMAT)
        else:
            record.when_or_elapsed = (
                f"{ELAPSED_TIME_SEPARATOR}{elapsed_time:.<{TIME_LENGTH_m_1}}"
            )
        self.last_message_now = now

        # Where.
        # Memory usage is also stored if there are no handlers yet, just in case.
        should_store_where = self.any_handler_stores_memory or not self.hasHandlers()
        should_show_where = (record.levelno != l.INFO) and not hasattr(
            record, HIDE_WHERE_ATTR
        )
        if should_store_where or should_show_where:
            module = path_t(record.pathname)
            for path in s.path:
                if module.is_relative_to(path):
                    module = module.relative_to(path).with_suffix("")
                    module = str(module).replace(FOLDER_SEPARATOR, ".")
                    break
            else:
                module = record.module
            where = f"{module}:{record.funcName}:{record.lineno}"
            if should_show_where:
                record.where = where
        else:
            where = None

        # How.
        record.level_first_letter = record.levelname[0]

        # What.
        if not isinstance(record.msg, str):
            record.msg = str(record.msg)

        if self._should_hold_messages:
            self._on_hold.append(record)
        else:
            if self.should_record_messages:
                self.recorded.append(
                    (record.levelno, MessageFromRecord(record, RuleAsText)[0])
                )
            base_t.handle(self, record)

        if (self.exit_on_critical and (record.levelno is l.CRITICAL)) or (
            self.exit_on_error and (record.levelno is l.ERROR)
        ):
            # Also works if self.exit_on_error and record.levelno is l.CRITICAL since
            # __post_init__ set self.exit_on_critical if self.exit_on_error.
            s.exit(1)

        self.events[record.levelno] += 1

        if should_store_where:
            self.memory_usages.append((where, CurrentMemoryUsage()))

    def SetLevel(self, level: int, /, *, which: handler_codes_h | str = "a") -> None:
        """
        Set level of handlers, but the logger level is not modified.

        which: if not a handler_codes_h, then it corresponds to a handler name.
        """
        found = False
        for handler in self.handlers:
            if (
                (which == "a")
                or ((which in "cfg") and (getattr(handler, "kind", None) == which))
                or (which == handler.name)
            ):
                handler.setLevel(level)
                if which not in HANDLER_KINDS:
                    return
                found = True

        if not found:
            raise ValueError(
                MessageWithActualExpected(
                    "Handler not found",
                    actual=which,
                    expected=f"{str(HANDLER_KINDS)[1:-1]}, or a handler name",
                )
            )

    def MakeMonochrome(self) -> None:
        """"""
        OverrideExceptionFormat()
        self.AddHandler(console_handler_t)

    def MakeRich(self, *, alternating_logs: int = 0) -> None:
        """"""
        if MISSING_RICH_MESSAGE is not None:
            s.__stderr__.write(MISSING_RICH_MESSAGE + "\n")

        OverrideExceptionFormat()
        if console_rich_handler_t is console_handler_t:
            handler_kwargs = {}
        else:
            handler_kwargs = {"alternating_logs": alternating_logs}
        self.AddHandler(console_rich_handler_t, **handler_kwargs)

    def MakePermanent(self, path: str | path_t, /) -> None:
        """"""
        OverrideExceptionFormat()
        self.AddHandler(file_handler_t, path=path)

    def ResetEventCounts(self) -> None:
        """"""
        for level in self.events:
            self.events[level] = 0

    def ToggleWarningInterceptions(self, state: bool, /) -> None:
        """"""
        if state:
            if self.intercepts_warnings:
                return

            logger = l.getLogger(WARNING_LOGGER_NAME)
            self.intercepted_wrn_handle = logger.handle
            logger.handle = t.MethodType(_HandleForWarnings(self), logger)

            l.captureWarnings(True)
            self.info("Warning Interception: ON")
        else:
            if not self.intercepts_warnings:
                return

            logger = l.getLogger(WARNING_LOGGER_NAME)
            logger.handle = self.intercepted_wrn_handle
            self.intercepted_wrn_handle = None

            l.captureWarnings(False)
            self.info("Warning Interception: OFF")

    def ToggleLogInterceptions(self, state: bool, /) -> None:
        """"""
        if state:
            if self.intercepts_logs:
                return

            # Note: Alternative to self.manager is logging.root.manager.
            all_loggers_names_but_root = self.manager.loggerDict.keys()
            all_loggers = [l.getLogger()] + [
                l.getLogger(_nme)
                for _nme in all_loggers_names_but_root
                if _nme not in (self.name, WARNING_LOGGER_NAME)
            ]
            for logger in all_loggers:
                self.intercepted_log_handles[logger.name] = logger.handle
                logger.handle = t.MethodType(
                    _HandleForInterceptions(logger, self), logger
                )

            intercepted = sorted(self.intercepted_log_handles.keys())
            if intercepted.__len__() > 0:
                as_str = ", ".join(intercepted)
                self.info(f"Now Intercepting LOGs from: {as_str}")
        else:
            if not self.intercepts_logs:
                return

            for name, handle in self.intercepted_log_handles.items():
                logger = l.getLogger(name)
                logger.handle = handle
            self.intercepted_log_handles.clear()
            self.info("Log Interception: OFF")

    def AddHandler(
        self,
        handler_t: type[base_handler_t],
        /,
        *,
        name: str | None = None,
        level: int = l.INFO,
        should_store_memory_usage: bool = False,
        message_width: int = -1,
        formatter: l.Formatter | None = None,
        should_still_hold_messages: bool = False,
        **kwargs,
    ) -> None:
        """"""
        if (not should_still_hold_messages) and self._should_activate_log_interceptions:
            self.ToggleLogInterceptions(True)
            self._should_activate_log_interceptions = False

        self._should_hold_messages = should_still_hold_messages
        handler = handler_t.New(
            name=name,
            should_store_memory_usage=should_store_memory_usage,
            message_width=message_width,
            level=level,
            formatter=formatter,
            **kwargs,
        )
        base_t.addHandler(self, handler)

        extension = getattr(handler, "extension", None)
        if extension is None:
            name = handler.name
            if (name is None) or (name.__len__() == 0):
                name = ANONYMOUS
        else:
            name = getattr(extension, "name", ANONYMOUS)
            if getattr(extension, STORE_MEMORY_ATTR, False):
                self.any_handler_stores_memory = True

        path = getattr(handler, "baseFilename", "")
        if isinstance(path, path_t) or (path.__len__() > 0):
            path = f"\nPath: {path}"

        self.info(
            f'New handler "{name}" of type "{type(handler).__name__}" and '
            f"level {handler.level}={l.getLevelName(handler.level)}{path}"
        )

    def __call__(self, *args, **kwargs) -> None:
        """
        For a print-like calling.
        """
        separator = kwargs.get("separator", " ")
        self.info(separator.join(map(str, args)))

    def Log(
        self,
        message: str,
        /,
        *,
        level: int | str = l.ERROR,
        actual: h.Any = NOT_PASSED,
        expected: h.Any | None = None,
        expected_is_choices: bool = False,
        expected_op: expected_op_h = "=",
        with_final_dot: bool = True,
    ) -> None:
        """"""
        if isinstance(level, str):
            level = l.getLevelNamesMapping()[level.upper()]
        message = MessageWithActualExpected(
            message,
            actual=actual,
            expected=expected,
            expected_is_choices=expected_is_choices,
            expected_op=expected_op,
            with_final_dot=with_final_dot,
        )
        self.log(level, message)

    def LogException(
        self,
        exception: Exception,
        /,
        *,
        level: int | str = l.ERROR,
        should_remove_caller: bool = False,
    ) -> None:
        """"""
        if isinstance(level, str):
            level = l.getLevelNamesMapping()[level.upper()]
        lines = tcbk.format_exception(exception)
        if should_remove_caller:
            message = "\n".join(lines[:1] + lines[2:])
        else:
            # TODO: Explain:
            #     - Why it's not: "\n".join(lines)?
            #     - Why adding exception name here and not when removing caller?
            formatted = "".join(lines)
            message = f"{type(exception).__name__}:\n{formatted}"
        self.log(level, message)

    def LogAsIs(self, message: str, /, *, indented: bool = False) -> None:
        """"""
        if indented:
            message = text.indent(message, LINE_INDENT)

        for handler in self.handlers:
            if (LogAsIs := getattr(handler, "LogAsIs", None)) is None:
                self.info(message)
            else:
                LogAsIs(message)

    info_raw = LogAsIs  # To follow the convention of the logging methods info, error...

    def DisplayRule(
        self, /, *, message: str | None = None, color: str = "white"
    ) -> None:
        """"""
        for handler in self.handlers:
            if (DisplayRule := getattr(handler, "DisplayRule", None)) is None:
                self.info(RuleAsText(message, None))
            else:
                DisplayRule(text=message, color=color)

    def AddContextLevel(self, new_level: str, /) -> None:
        """"""
        self.context_levels.append(new_level)

    def AddedContextLevel(self, new_level: str, /) -> h.Self:
        """
        Meant to be used as:
        with self.AddedContextLevel("new level"):
            ...
        """
        self.AddContextLevel(new_level)
        return self

    def StageIssue(
        self,
        message: str,
        /,
        *,
        level: int = l.ERROR,
        actual: h.Any = NOT_PASSED,
        expected: h.Any | None = None,
        expected_is_choices: bool = False,
        expected_op: expected_op_h = "=",
        with_final_dot: bool = False,
    ) -> None:
        """"""
        context = ISSUE_CONTEXT_SEPARATOR.join(self.context_levels)
        issue = NewIssue(
            context,
            ISSUE_CONTEXT_END,
            message,
            level=level,
            actual=actual,
            expected=expected,
            expected_is_choices=expected_is_choices,
            expected_op=expected_op,
            with_final_dot=with_final_dot,
        )
        self.staged_issues.append(issue)

    def PopIssues(self, /, *, should_remove_context: bool = False) -> list[str]:
        """"""
        if not self.has_staged_issues:
            return []

        output = []

        if should_remove_context:
            separator = ISSUE_CONTEXT_END
        else:
            separator = ISSUE_LEVEL_SEPARATOR
        separator_length = separator.__len__()
        for issue in self.staged_issues:
            start_idx = issue.find(separator)
            issue = issue[(start_idx + separator_length) :]
            output.append(issue)

        self.staged_issues.clear()

        return output

    def CommitIssues(
        self, /, *, order: order_h = "when", unified: bool = False
    ) -> None:
        """
        Note that issues after an issue with a level triggering process exit will not be
        logged.
        """
        if not self.has_staged_issues:
            return

        if order not in ORDER:
            raise ValueError(
                MessageWithActualExpected(
                    "Invalid commit order",
                    actual=order,
                    expected=f"One of {str(ORDER)[1:-1]}",
                )
            )

        if order == "when":
            issues = self.staged_issues
        else:  # order == "context"
            issues = sorted(self.staged_issues, key=lambda _: _.context)
        """
        Format issues as an exception:
        try:
            raise ValueError("\n" + "\n".join(issues))
        except ValueError as exception:
            lines = ["Traceback (most recent call last):"] + tcbk.format_stack()[:-1]
            lines[-1] = lines[-1][:-1]
            lines.extend(tcbk.format_exception_only(exception))
            formatted = "\n".join(lines)
        """

        hide_where = {HIDE_WHERE_ATTR: None}
        if unified:
            level, _ = issues[0].split(ISSUE_LEVEL_SEPARATOR, maxsplit=1)
            wo_level = []
            for issue in issues:
                _, issue = issue.split(ISSUE_LEVEL_SEPARATOR, maxsplit=1)
                wo_level.append(issue)
            self.log(int(level), "\n".join(wo_level), stacklevel=2, extra=hide_where)
        else:
            for issue in issues:
                level, issue = issue.split(ISSUE_LEVEL_SEPARATOR, maxsplit=1)
                self.log(int(level), issue, stacklevel=2, extra=hide_where)
        self.staged_issues.clear()

    def __enter__(self) -> None:
        """"""
        pass

    def __exit__(
        self,
        exc_type: Exception | None,
        exc_value: str | None,
        traceback: traceback_t | None,
        /,
    ) -> bool:
        """"""
        _ = self.context_levels.pop()
        return False


def _HandleForWarnings(interceptor: base_t, /) -> logger_handle_h:
    """"""

    def handle_p(_: base_t, record: l.LogRecord, /) -> None:
        pieces = WARNING_TYPE_COMPILED_PATTERN.match(record.msg)
        if pieces is None:
            # The warning message does not follow the default format.
            interceptor.handle(record)
            return

        GetPiece = pieces.group
        path = GetPiece(1)
        line = GetPiece(2)
        kind = GetPiece(3)
        message = GetPiece(4)

        path_as_t = path_t(path)
        line = int(line)
        line_content = path_as_t.read_text().splitlines()[line - 1]
        message = message.replace(line_content.strip(), "").strip()

        duplicate = l.makeLogRecord(record.__dict__)
        duplicate.msg = f"{kind}: {message}"
        duplicate.pathname = path
        duplicate.module = path_as_t.stem
        duplicate.funcName = "<function>"
        duplicate.lineno = line

        interceptor.handle(duplicate)

    return handle_p


def _HandleForInterceptions(
    intercepted: base_t, interceptor: base_t, /
) -> logger_handle_h:
    """"""

    def handle_p(_: base_t, record: l.LogRecord, /) -> None:
        duplicate = l.makeLogRecord(record.__dict__)
        duplicate.msg = f"{record.msg} :{intercepted.name}:"
        interceptor.handle(duplicate)

    return handle_p


"""
COPYRIGHT NOTICE

This software is governed by the CeCILL  license under French law and
abiding by the rules of distribution of free software.  You can  use,
modify and/ or redistribute the software under the terms of the CeCILL
license as circulated by CEA, CNRS and INRIA at the following URL
"http://www.cecill.info".

As a counterpart to the access to the source code and  rights to copy,
modify and redistribute granted by the license, users are provided only
with a limited warranty  and the software's author,  the holder of the
economic rights,  and the successive licensors  have only  limited
liability.

In this respect, the user's attention is drawn to the risks associated
with loading,  using,  modifying and/or developing or reproducing the
software by the user in light of its specific status of free software,
that may mean  that it is complicated to manipulate,  and  that  also
therefore means  that it is reserved for developers  and  experienced
professionals having in-depth computer knowledge. Users are therefore
encouraged to load and test the software's suitability as regards their
requirements in conditions enabling the security of their systems and/or
data to be ensured and,  more generally, to use and operate it in the
same conditions as regards security.

The fact that you are presently reading this means that you have had
knowledge of the CeCILL license and that you accept its terms.

SEE LICENCE NOTICE: file README-LICENCE-utf8.txt at project source root.

This software is being developed by Eric Debreuve, a CNRS employee and
member of team Morpheme.
Team Morpheme is a joint team between Inria, CNRS, and UniCA.
It is hosted by the Centre Inria d'Université Côte d'Azur, Laboratory
I3S, and Laboratory iBV.

CNRS: https://www.cnrs.fr/index.php/en
Inria: https://www.inria.fr/en/
UniCA: https://univ-cotedazur.eu/
Centre Inria d'Université Côte d'Azur: https://www.inria.fr/en/centre/sophia/
I3S: https://www.i3s.unice.fr/en/
iBV: http://ibv.unice.fr/
Team Morpheme: https://team.inria.fr/morpheme/
"""
