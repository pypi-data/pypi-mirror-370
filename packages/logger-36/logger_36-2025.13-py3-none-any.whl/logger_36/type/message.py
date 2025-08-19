"""
Copyright CNRS/Inria/UniCA
Contributor(s): Eric Debreuve (eric.debreuve@cnrs.fr) since 2023
SEE COPYRIGHT NOTICE BELOW
"""

import logging as l
import typing as h

from logger_36.config.message import (
    LEVEL_CLOSING,
    LEVEL_OPENING,
    MESSAGE_MARKER,
    WHERE_SEPARATOR,
)
from logger_36.constant.message import NEXT_LINE_PROLOGUE
from logger_36.extension.line import WrappedLines


@h.runtime_checkable
class _MessageFromRecordPreprocessed_p(h.Protocol):
    def __call__(
        self,
        record: l.LogRecord,
        /,
        *,
        line_width: int = 0,
        PreProcessed: h.Callable[[str], str] | None = None,
    ) -> str: ...


MessageFromRecord_h = _MessageFromRecordPreprocessed_p


def MessageFromRecord(
    record: l.LogRecord,
    /,
    *,
    line_width: int = 0,
    PreProcessed: h.Callable[[str], str] | None = None,
) -> str:
    """
    See logger_36.catalog.handler.README.txt.
    """
    message = record.msg

    if PreProcessed is not None:
        message = PreProcessed(message)
    if (line_width <= 0) or (message.__len__() <= line_width):
        if "\n" in message:
            message = NEXT_LINE_PROLOGUE.join(message.splitlines())
    else:
        if "\n" in message:
            lines = WrappedLines(message.splitlines(), line_width)
        else:
            lines = WrappedLines([message], line_width)
        message = NEXT_LINE_PROLOGUE.join(lines)

    when_or_elapsed = getattr(record, "when_or_elapsed", None)
    if when_or_elapsed is None:
        return message

    level_first_letter = getattr(record, "level_first_letter", "")

    if (where := getattr(record, "where", None)) is None:
        where = ""
    else:
        where = f"{NEXT_LINE_PROLOGUE}{WHERE_SEPARATOR} {where}"

    return (
        f"{when_or_elapsed}"
        f"{LEVEL_OPENING}{level_first_letter}{LEVEL_CLOSING} "
        f"{MESSAGE_MARKER} {message}{where}"
    )


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
