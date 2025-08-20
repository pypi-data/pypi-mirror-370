"""
Copyright CNRS/Inria/UniCA
Contributor(s): Eric Debreuve (eric.debreuve@cnrs.fr) since 2023
SEE COPYRIGHT NOTICE BELOW
"""

from logger_36.constant.memory import STORAGE_UNITS, storage_units_h
from logger_36.task.format.message import MessageWithActualExpected

_KILO_UNIT = 1000.0
_MEGA_UNIT = _KILO_UNIT * 1000.0
_GIGA_UNIT = _MEGA_UNIT * 1000.0

_BLOCKS_PARTIAL = ("", "▏", "▎", "▍", "▌", "▋", "▊")
_BLOCK_FULL = "▉"


def FormattedUsage(
    usage: int, /, *, unit: storage_units_h | None = "a", decimals: int | None = None
) -> tuple[int | float, str]:
    """
    unit: b or None=bytes, k=kilo, m=mega, g=giga, a=auto
    """
    if (unit is None) or (unit == "b"):
        value = usage
        unit = "B"
    elif unit == "k":
        value = _Rounded(usage / _KILO_UNIT, decimals)
        unit = "KB"
    elif unit == "m":
        value = _Rounded(usage / _MEGA_UNIT, decimals)
        unit = "MB"
    elif unit == "g":
        value = _Rounded(usage / _GIGA_UNIT, decimals)
        unit = "GB"
    elif unit == "a":
        value, unit = FormattedUsageWithAutoUnit(usage, decimals)
    else:
        raise ValueError(
            MessageWithActualExpected(
                "Invalid unit", actual=unit, expected=str(STORAGE_UNITS)[1:-1]
            )
        )

    return value, unit


def FormattedUsageWithAutoUnit(
    usage: int, decimals: int | None, /
) -> tuple[int | float, str]:
    """"""
    if usage > _GIGA_UNIT:
        return _Rounded(usage / _GIGA_UNIT, decimals), "GB"

    if usage > _MEGA_UNIT:
        return _Rounded(usage / _MEGA_UNIT, decimals), "MB"

    if usage > _KILO_UNIT:
        return _Rounded(usage / _KILO_UNIT, decimals), "KB"

    return usage, "B"


def UsageBar(
    usage: int | float, max_usage: int | float, /, *, length_100: int = 10
) -> str:
    """"""
    length = (usage / max_usage) * length_100
    n_full_s = int(length)
    return (
        n_full_s * _BLOCK_FULL
        + _BLOCKS_PARTIAL[int((2.0 / 3.0) * int(10 * (length - n_full_s)))]
    )


def _Rounded(value: float, decimals: int | None, /) -> int | float:
    """"""
    if decimals == 0:
        decimals = None

    return round(value, ndigits=decimals)


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
