import sys, os

sys.path.append(os.path.abspath(os.curdir))
from ablelabs.neon.common.suitable.enums import Axis

PIPETTE_COUNT: int = 2
DECK_COUNT: int = 12

PIPETTE_NUMBERS = [i + 1 for i in range(PIPETTE_COUNT)]
DECK_NUMBERS = [i + 1 for i in range(DECK_COUNT)]

AXIS_ZS = [Axis.Z[n] for n in PIPETTE_NUMBERS]
AXIS_PS = [Axis.P[n] for n in PIPETTE_NUMBERS]
