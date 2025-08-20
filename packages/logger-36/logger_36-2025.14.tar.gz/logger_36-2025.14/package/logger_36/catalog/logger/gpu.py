"""
Copyright CNRS/Inria/UniCA
Contributor(s): Eric Debreuve (eric.debreuve@cnrs.fr) since 2023
SEE COPYRIGHT NOTICE BELOW
"""

import sys as s

from logger_36.constant.error import GPU_LOGGING_ERROR
from logger_36.instance.logger import L
from logger_36.type.logger import logger_t

try:
    import tensorflow as tsfl  # noqa
    import tensorrt as tsrt  # noqa
except ModuleNotFoundError:
    tsfl = tsrt = None
    _GPU_LOGGING_ERROR = GPU_LOGGING_ERROR
else:
    _GPU_LOGGING_ERROR = None


def LogGPURelatedDetails(*, logger: logger_t = L) -> None:
    """"""
    global _GPU_LOGGING_ERROR

    if None in (tsfl, tsrt):
        if _GPU_LOGGING_ERROR is not None:
            s.__stderr__.write(_GPU_LOGGING_ERROR + "\n")
            _GPU_LOGGING_ERROR = None
        return

    system_details = tsfl.sysconfig.get_build_info()
    logger.info(
        f"GPU-RELATED DETAILS\n"
        f"                GPUs: {tsfl.config.list_physical_devices('GPU')}\n"
        f"                CPUs: {tsfl.config.list_physical_devices('CPU')}\n"
        f"                Cuda: {system_details['cuda_version']}\n"
        f"               CuDNN: {system_details['cudnn_version']}\n"
        f"          Tensorflow: {tsfl.version.VERSION}\n"
        f"    Tensorflow Build: {tsfl.sysconfig.get_build_info()}\n"
        f"            TensorRT: {tsrt.__version__}"
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
