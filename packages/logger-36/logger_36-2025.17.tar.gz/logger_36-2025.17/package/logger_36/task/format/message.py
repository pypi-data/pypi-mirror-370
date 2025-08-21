"""
Copyright CNRS/Inria/UniCA
Contributor(s): Eric Debreuve (eric.debreuve@cnrs.fr) since 2023
SEE COPYRIGHT NOTICE BELOW
"""

import difflib as diff
import logging as l
import typing as h

from logger_36.config.message import (
    LEVEL_CLOSING,
    LEVEL_OPENING,
    MESSAGE_MARKER,
    WHERE_SEPARATOR,
)
from logger_36.constant.generic import NOT_PASSED
from logger_36.constant.message import NEXT_LINE_PROLOGUE, expected_op_h
from logger_36.constant.record import SHOW_W_RULE_ATTR
from logger_36.extension.line import WrappedLines
from logger_36.type.message import RuleWithText_h


def MessageFromRecord(
    record: l.LogRecord,
    RuleWithText: RuleWithText_h,
    /,
    *,
    line_width: int = 0,
    color: str | None = None,
    PreProcessed: h.Callable[[str], str] | None = None,
) -> tuple[str, bool]:
    """
    See logger_36.catalog.handler.README.txt.

    The second returned value is is_not_a_rule.
    """
    message = record.msg

    if hasattr(record, SHOW_W_RULE_ATTR):
        return RuleWithText(message, color), False

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
        return message, True

    level_first_letter = getattr(record, "level_first_letter", "")

    if (where := getattr(record, "where", None)) is None:
        where = ""
    else:
        where = f"{NEXT_LINE_PROLOGUE}{WHERE_SEPARATOR} {where}"

    return (
        f"{when_or_elapsed}"
        f"{LEVEL_OPENING}{level_first_letter}{LEVEL_CLOSING} "
        f"{MESSAGE_MARKER} {message}{where}"
    ), True


def MessageWithActualExpected(
    message: str,
    /,
    *,
    actual: h.Any = NOT_PASSED,
    expected: h.Any | None = None,
    expected_is_choices: bool = False,
    expected_op: expected_op_h = "=",
    with_final_dot: bool = True,
) -> str:
    """"""
    if actual is NOT_PASSED:
        if with_final_dot:
            if message[-1] != ".":
                message += "."
        elif message[-1] == ".":
            message = message[:-1]

        return message

    if message[-1] == ".":
        message = message[:-1]
    expected = _FormattedExpected(expected_op, expected, expected_is_choices, actual)
    if with_final_dot:
        dot = "."
    else:
        dot = ""

    if isinstance(actual, type):
        actual = actual.__name__
    else:
        actual = f"{actual}:{type(actual).__name__}"

    return f"{message}: Actual={actual}; {expected}{dot}"


def _FormattedExpected(
    operator: str, expected: h.Any, expected_is_choices: bool, actual: h.Any, /
) -> str:
    """"""
    if isinstance(expected, h.Sequence) and expected_is_choices:
        close_matches = diff.get_close_matches(actual, expected)
        if close_matches.__len__() > 0:
            close_matches = ", ".join(close_matches)
            return f"Close matche(s): {close_matches}"
        else:
            expected = ", ".join(map(str, expected))
            return f"Valid values: {expected}"

    if isinstance(expected, type):
        return f"Expected{operator}{expected.__name__}"

    if operator == "=":
        stripe = f":{type(expected).__name__}"
    else:
        stripe = ""
        if operator == ":":
            operator = ": "
    return f"Expected{operator}{expected}{stripe}"


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
