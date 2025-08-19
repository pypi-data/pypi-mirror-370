from typing import Literal

NoiseModel = Literal[
    "bit_flip",
    "depolarize",
    "phase_flip",
    "phase_damp",
    "amplitude_damp"
    # "asymmetric_depolarization"
]
