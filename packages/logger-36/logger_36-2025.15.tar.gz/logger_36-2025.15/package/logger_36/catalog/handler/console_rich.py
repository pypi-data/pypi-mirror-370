"""
Copyright CNRS/Inria/UniCA
Contributor(s): Eric Debreuve (eric.debreuve@cnrs.fr) since 2023
SEE COPYRIGHT NOTICE BELOW
"""

import logging as l
import typing as h

from rich.console import Console as console_t  # noqa
from rich.console import RenderableType as renderable_t  # noqa
from rich.markup import escape as EscapedVersion  # noqa
from rich.text import Text as text_t  # noqa
from rich.traceback import install as InstallTracebackHandler  # noqa

from logger_36.catalog.config.console_rich import (
    ACTUAL_COLOR,
    ALTERNATIVE_BACKGROUND_FOR_DARK,
    ALTERNATIVE_BACKGROUND_FOR_LIGHT,
    DATE_TIME_COLOR,
    EXPECTED_COLOR,
    GRAY_COLOR,
    LEVEL_COLOR,
    WHITE_COLOR,
)
from logger_36.config.message import ACTUAL_PATTERNS, EXPECTED_PATTERNS, WHERE_SEPARATOR
from logger_36.constant.message import CONTEXT_LENGTH
from logger_36.task.format.rule import Rule
from logger_36.type.handler import handler_t as base_t

_COMMON_TRACEBACK_ARGUMENTS = ("theme", "width")
_EXCLUSIVE_TRACEBACK_ARGUMENTS = (
    "extra_lines",
    "indent_guides",
    "locals_hide_dunder",
    "locals_hide_sunder",
    "locals_max_length",
    "locals_max_string",
    "max_framesshow_locals",
    "suppress",
    "word_wrap",
)


class console_rich_handler_t(base_t):
    """
    alternating_logs:
    - 0: disabled
    - 1: enabled for dark background
    - 2: enabled for light background
    """

    kind: h.ClassVar[str] = "c"

    def __init__(
        self,
        name: str | None,
        should_store_memory_usage: bool,
        message_width: int,
        level: int,
        formatter: l.Formatter | None,
        kwargs,
    ) -> None:
        """"""
        alternating_logs = kwargs.pop("alternating_logs", 0)
        should_install_traceback = kwargs.pop("should_install_traceback", False)

        assert alternating_logs in (0, 1, 2)

        base_t.__init__(
            self,
            name,
            should_store_memory_usage,
            message_width,
            level,
            formatter,
            kwargs,
        )

        self.console = None  # console_t | None.
        self.alternating_logs = alternating_logs
        self._log_parity = False

        self.__post_init_local__(should_install_traceback, **kwargs)

    def __post_init_local__(self, should_install_traceback: bool, **kwargs) -> None:
        """"""
        traceback_kwargs = {}
        if should_install_traceback:
            for key in kwargs:
                if key in _COMMON_TRACEBACK_ARGUMENTS:
                    traceback_kwargs[key] = kwargs[key]
                elif key in _EXCLUSIVE_TRACEBACK_ARGUMENTS:
                    traceback_kwargs[key] = kwargs.pop(key)

        self.console = console_t(highlight=False, force_terminal=True, **kwargs)

        if should_install_traceback:
            traceback_kwargs["console"] = self.console
            InstallTracebackHandler(**traceback_kwargs)

    @classmethod
    def New(
        cls,
        /,
        *,
        name: str | None = None,
        should_store_memory_usage: bool = False,
        message_width: int = -1,
        level: int = l.NOTSET,
        formatter: l.Formatter | None = None,
        **kwargs,
    ) -> h.Self:
        """"""
        return cls(
            name, should_store_memory_usage, message_width, level, formatter, kwargs
        )

    def emit(self, record: l.LogRecord, /) -> None:
        """"""
        message, is_not_a_rule = self.MessageFromRecord(
            record,
            Rule,
            line_width=self.message_width,
            color=DATE_TIME_COLOR,
            PreProcessed=EscapedVersion,
        )
        if is_not_a_rule:
            message = HighlightedVersion(
                self.console,
                message,
                record.levelno,
                self.alternating_logs,
                self._log_parity,
            )
        self.console.print(message, crop=False, overflow="ignore")
        self._log_parity = not self._log_parity

    def LogAsIs(self, message: str | renderable_t, /) -> None:
        """"""
        self.console.print(message, crop=False, overflow="ignore")

    def DisplayRule(self, /, *, text: str | None = None, color: str = "black") -> None:
        """"""
        self.LogAsIs(Rule(text, color))


def HighlightedVersion(
    _: console_t,
    message: str,
    log_level: int,
    alternating_logs: int,
    should_tint_background: bool,
    /,
) -> renderable_t:
    """"""
    output = text_t(message, WHITE_COLOR)

    output.stylize(LEVEL_COLOR[log_level], end=CONTEXT_LENGTH)
    where = message.rfind(WHERE_SEPARATOR)
    if (where >= 0) and ("\n" not in message[where:]):
        output.stylize(GRAY_COLOR, start=where)
    _ = output.highlight_words(ACTUAL_PATTERNS, style=ACTUAL_COLOR)
    _ = output.highlight_regex(EXPECTED_PATTERNS, style=EXPECTED_COLOR)

    if should_tint_background and (alternating_logs > 0):
        if alternating_logs == 1:
            style = ALTERNATIVE_BACKGROUND_FOR_DARK
        else:
            style = ALTERNATIVE_BACKGROUND_FOR_LIGHT
        output.stylize(style)

    return output


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
