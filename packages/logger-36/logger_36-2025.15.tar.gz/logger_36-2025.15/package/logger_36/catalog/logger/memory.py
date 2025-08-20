"""
Copyright CNRS/Inria/UniCA
Contributor(s): Eric Debreuve (eric.debreuve@cnrs.fr) since 2023
SEE COPYRIGHT NOTICE BELOW
"""

from logger_36.config.memory import LENGTH_100, MAX_N_SAMPLES
from logger_36.constant.memory import storage_units_h
from logger_36.instance.logger import L
from logger_36.task.format.memory import FormattedUsage, UsageBar
from logger_36.task.format.message import MessageWithActualExpected
from logger_36.type.logger import logger_t


def LogMemoryUsages(
    *,
    unit: storage_units_h | None = "a",
    decimals: int = None,
    max_n_samples: int | None = MAX_N_SAMPLES,
    length_100: int = LENGTH_100,
    logger: logger_t = L,
) -> None:
    """"""
    if not logger.any_handler_stores_memory:
        return

    where_s, usages = zip(*logger.memory_usages)

    where, max_usage = logger.max_memory_usage_full
    value, unit = FormattedUsage(max_usage, unit=unit, decimals=decimals)
    title = f"Memory Usage: Max={value}{unit} near {where}\n"

    if isinstance(max_n_samples, int):
        if max_n_samples < 1:
            raise ValueError(
                MessageWithActualExpected(
                    "Invalid maximum number of samples",
                    actual=max_n_samples,
                    expected=1,
                    expected_op=">=",
                )
            )

        where_s = list(where_s)
        usages = list(usages)
        while usages.__len__() > max_n_samples:
            index = usages.index(min(usages))
            del where_s[index]
            del usages[index]

    usages = tuple(round(_elm, 1) for _elm in usages)
    max_usage = max(usages)

    plot = []
    max_where_length = max(map(len, where_s))
    usages_as_str = tuple(map(lambda _elm: f"{_elm:_}", usages))
    max_usage_length = max(map(len, usages_as_str))
    for where, usage, usage_as_str in zip(where_s, usages, usages_as_str):
        bar = UsageBar(usage, max_usage, length_100=length_100)
        plot.append(
            f"{where:{max_where_length}} "
            f"{bar:{length_100}} "
            f"{usage_as_str: >{max_usage_length}}"
        )
    plot = "\n".join(plot)

    logger.info(title + plot)


def LogMaximumMemoryUsage(
    *,
    unit: storage_units_h | None = "a",
    decimals: int | None = None,
    logger: logger_t = L,
) -> None:
    """
    unit: b or None=bytes, k=kilo, m=mega, g=giga, a=auto
    """
    if logger.any_handler_stores_memory:
        where, max_usage = logger.max_memory_usage_full
        value, unit = FormattedUsage(max_usage, unit=unit, decimals=decimals)
        logger.info(f"Max. Memory Usage: {value}{unit} near {where}")


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
