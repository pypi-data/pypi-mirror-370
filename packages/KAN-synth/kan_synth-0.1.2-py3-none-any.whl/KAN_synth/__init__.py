"""
KAN_synth: KAN-based synthetic tabular data generation package.

This package includes hybrid models combining CTGAN/TVAE with Kolmogorov–Arnold Networks (KANs),
as well as benchmarking utilities and evaluation tools.
"""
# CTGAN-Based models with KAN 
from .models.KAN_CTGAN_code import KAN_CTGAN
from .models.Hybrid_CTGAN_code import HYBRID_KAN_CTGAN
from .models.Gen_KAN_CTGAN_code import Gen_KAN_CTGAN
from .models.Disc_KAN_CTGAN_code import Disc_KAN_CTGAN

# TVAE-Based models with KAN
from .models.KAN_TVAE_code import KAN_TVAE
from .models.Hybrid_TVAE_code import HYBRID_KAN_TVAE

# Utilities
from .utilities.Utilities import overall_similarity, evaluate_all_models, evaluate_all_models_classification, visualize_class_score, visualize_reg_score
