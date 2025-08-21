import sys, os

sys.path.append(os.path.abspath(os.curdir))
from ablelabs.neon.common.suitable.enums import Axis

DI_COUNT: int = 8
DO_COUNT: int = 8

PIPETTE_COUNT: int = 8
PIPETTE_NUMBERS = [i + 1 for i in range(PIPETTE_COUNT)]

AXIS_YS = [Axis.Y[n] for n in PIPETTE_NUMBERS]
AXIS_ZS = [Axis.Z[n] for n in PIPETTE_NUMBERS]
AXIS_PS = [Axis.P[n] for n in PIPETTE_NUMBERS]

Y_MIN_INTERVAL_MM = 9.0
