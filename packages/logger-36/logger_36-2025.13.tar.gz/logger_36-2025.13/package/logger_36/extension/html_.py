"""
Copyright CNRS/Inria/UniCA
Contributor(s): Eric Debreuve (eric.debreuve@cnrs.fr) since 2023
SEE COPYRIGHT NOTICE BELOW
"""

import dataclasses as d
import re as r
from html.parser import HTMLParser as base_t

_BODY_END_PATTERN = r"</[bB][oO][dD][yY]>(.|\n)*$"


@d.dataclass(slots=True, repr=False, eq=False)
class html_content_t(base_t):
    source: str = ""
    inside_body: bool = d.field(init=False, default=False)
    body_position_start: tuple[int, int] = d.field(init=False, default=(-1, -1))
    body_position_end: tuple[int, int] = d.field(init=False, default=(-1, -1))
    pieces: list[str] = d.field(init=False, default_factory=list)

    @property
    def body(self) -> str:
        """"""
        output = self.source.splitlines()
        output = "\n".join(
            output[self.body_position_start[0] : (self.body_position_end[0] + 1)]
        )
        output = output[self.body_position_start[1] :]
        output = r.sub(_BODY_END_PATTERN, "", output, count=1)

        return output.strip()

    @property
    def body_as_text(self) -> str:
        """"""
        return "".join(self.pieces).strip()

    def __post_init__(self) -> None:
        """"""
        base_t.__init__(self)
        self.source = self.source.strip()
        self.feed(self.source)

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]], /) -> None:
        """"""
        if tag == "body":
            self.body_position_start = self.getpos()
            self.inside_body = True

    def handle_endtag(self, tag: str, /) -> None:
        """"""
        if tag == "body":
            self.body_position_end = self.getpos()
            self.inside_body = False

    def handle_data(self, data: str, /) -> None:
        """"""
        if self.inside_body:
            self.pieces.append(data)


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
