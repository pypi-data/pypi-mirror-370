"""
Copyright CNRS/Inria/UniCA
Contributor(s): Eric Debreuve (eric.debreuve@cnrs.fr) since 2023
SEE COPYRIGHT NOTICE BELOW
"""

import logging as l
from io import IOBase as io_base_t
from pathlib import Path as path_t

from logger_36.constant.html import BODY_PLACEHOLDER, MINIMAL_HTML, TITLE_PLACEHOLDER
from logger_36.instance.logger import L


def SaveLOGasHTML(path: str | path_t | io_base_t | None = None) -> None:
    """
    From first console handler found.
    """
    cannot_save = "Cannot save logging record as HTML"

    if path is None:
        for handler in L.handlers:
            if isinstance(handler, l.FileHandler):
                path = path_t(handler.baseFilename).with_suffix(".htm")
                break
        else:
            L.warning(f"{cannot_save}: No file handler to build a filename from.")
            return

        if path.exists():
            L.warning(
                f'{cannot_save}: Automatically generated path "{path}" already exists.'
            )
            return
    elif isinstance(path, str):
        path = path_t(path)

    actual_file = isinstance(path, path_t)

    if actual_file and path.exists():
        L.warning(f'{cannot_save}: File "{path}" already exists.')
        return

    body = "\n".join(map(_HighlightedEvent, L.recorded))
    html = MINIMAL_HTML.replace(TITLE_PLACEHOLDER, L.name).replace(
        BODY_PLACEHOLDER, body
    )
    if actual_file:
        with open(path, "w") as accessor:
            accessor.write(html)
    else:
        path.write(html)


def _HighlightedEvent(event: tuple[int, str], /) -> str:
    """"""
    level, message = event
    if level == l.DEBUG:
        color = "BlueViolet"
    elif level == l.INFO:
        color = "black"
    elif level == l.WARNING:
        color = "gold"
    elif level == l.ERROR:
        color = "orange"
    elif level == l.CRITICAL:
        color = "red"
    else:
        color = "black"

    return f'<span style="color:{color}">{message}</span>'


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
