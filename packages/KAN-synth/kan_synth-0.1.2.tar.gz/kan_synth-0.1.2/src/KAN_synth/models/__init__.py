"""
Model subpackage for KAN_synth.

Includes:
- KAN-enhanced CTGAN and TVAE
- Core KAN layers
"""


# CTGAN-Based models with KAN 
from .KAN_CTGAN_code import KAN_CTGAN
from .Hybrid_CTGAN_code import HYBRID_KAN_CTGAN
from .Gen_KAN_CTGAN_code import Gen_KAN_CTGAN
from .Disc_KAN_CTGAN_code import Disc_KAN_CTGAN

# TVAE-Based models with KAN
from .KAN_TVAE_code import KAN_TVAE
from .Hybrid_TVAE_code import HYBRID_KAN_TVAE

from .KAN_code import KANLinear