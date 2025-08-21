"""
Copyright CNRS/Inria/UniCA
Contributor(s): Eric Debreuve (eric.debreuve@cnrs.fr) since 2023
SEE COPYRIGHT NOTICE BELOW
"""

import logging as l
import sys as s
import typing as h
from pathlib import Path as path_t

from logger_36.config.message import FALLBACK_MESSAGE_WIDTH
from logger_36.constant.handler import HANDLER_KINDS
from logger_36.task.format.message import MessageFromRecord, MessageWithActualExpected
from logger_36.task.format.rule import RuleAsText
from logger_36.task.measure.chronos import TimeStamp
from logger_36.type.message import MessageFromRecord_h, RuleWithText_h


class _base_t:
    kind: h.ClassVar[str] = ""  # See logger_36.constant.handler.handler_codes_h.

    def __init__(self, name: str | None, message_width: int) -> None:
        """"""
        if name is None:
            name = f"{type(self).__name__}:{id(self)}"

        self.name = name
        self.message_width = message_width
        #
        self.MessageFromRecord: MessageFromRecord_h | None = None

        self.__post_init__()

    def __post_init__(self) -> None:
        """"""
        if self.name in HANDLER_KINDS:
            raise ValueError(
                MessageWithActualExpected(
                    "Invalid handler name",
                    actual=self.name,
                    expected=f"a name not in {str(HANDLER_KINDS)[1:-1]}",
                )
            )

        if self.name is None:
            self.name = TimeStamp()

        if 0 < self.message_width < FALLBACK_MESSAGE_WIDTH:
            self.message_width = FALLBACK_MESSAGE_WIDTH

    @classmethod
    def New(cls, **kwargs) -> h.Self:
        """
        Interest: default arguments, no prescribed argument order, variable argument list.
        """
        raise NotImplementedError

    def LogAsIs(self, message: str, /) -> None:
        """
        See documentation of
        logger_36.catalog.handler.generic.generic_handler_t.LogAsIs.
        """
        s.__stdout__.write(message + "\n")

    def DisplayRule(self, /, *, text: str | None = None, color: str = "black") -> None:
        """"""
        self.LogAsIs(RuleAsText(text, None))


class handler_t(l.Handler, _base_t):
    def __init__(
        self,
        name: str | None,
        message_width: int,
        level: int,
        formatter: l.Formatter | None,
        *_,
    ) -> None:
        """"""
        l.Handler.__init__(self)
        _base_t.__init__(self, name, message_width)
        __post_init__(self, level, formatter)


class file_handler_t(l.FileHandler, _base_t):
    def __init__(
        self,
        name: str | None,
        message_width: int,
        level: int,
        formatter: l.Formatter | None,
        path: str | path_t | None,
        *_,
    ) -> None:
        """"""
        if path is None:
            raise ValueError("Missing file or folder.")
        if isinstance(path, str):
            path = path_t(path)
        if path.exists():
            raise ValueError(f"File or folder already exists: {path}.")

        l.FileHandler.__init__(self, path)
        _base_t.__init__(self, name, message_width)
        __post_init__(self, level, formatter)


any_handler_t = handler_t | file_handler_t


def __post_init__(
    handler: any_handler_t, level: int, formatter: l.Formatter | None
) -> None:
    """"""
    handler.setLevel(level)

    if formatter is None:
        handler.MessageFromRecord = MessageFromRecord
    else:
        handler.setFormatter(formatter)
        _MessageFromRecordRaw = handler.formatter.format

        def _MessageFromRecord(
            record: l.LogRecord,
            _: RuleWithText_h,
            /,
            *,
            line_width: int = 0,
            PreProcessed: h.Callable[[str], str] | None = None,
        ) -> tuple[str, bool]:
            #
            return _MessageFromRecordRaw(record), False

        handler.MessageFromRecord = _MessageFromRecord


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
