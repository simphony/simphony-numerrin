""" Provisional CUBA keywords specific for this revision

"""

from enum import IntEnum, unique


@unique
class CUBAExt(IntEnum):

    INCOMPRESSIBLE = 1
    COMPRESSIBLE = 2
    VOF_MODEL = 3
    LAMINAR_MODEL = 4
    GE = 5
    PATCH_TYPE = 6
    PHASE_LIST = 7
    MAX_COURANT_NUMBER = 8
    SURFACE_TENSION = 9
    NUMBER_OF_CORES = 10
    MIXTURE_MODEL = 11
    RELATIVE_VELOCITY_MODEL = 12
    RELATIVE_VELOCITY_MODEL_COEFFS = 13
    STRESS_MODEL = 14
    EXTERNAL_BODY_FORCE_MODEL = 15
    EXTERNAL_BODY_FORCE_MODEL_COEFFS = 16
