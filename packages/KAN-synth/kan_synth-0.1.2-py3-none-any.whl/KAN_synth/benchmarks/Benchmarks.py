"""
Benchmarks.py

This module defines and registers a variety of synthetic data generators—including
original and KAN-based variants of CTGAN and TVAE—for evaluation using the SDGym
`benchmark_single_table` API.

Each synthesizer is wrapped using `create_single_table_synthesizer`, with appropriate
training and sampling logic for integration into SDGym's benchmarking suite. Models
included in this script are:

- ORIGINAL-CTGAN and ORIGINAL-TVAE (baseline models from the CTGAN library)
- KAN-CTGAN and KAN-TVAE (custom KAN-augmented versions)
- Disc_KAN_CTGAN and Gen_KAN_CTGAN (KAN in discriminator or generator only)
- HYBRID_KAN_CTGAN and HYBRID_KAN_TVAE (mixed KAN-MLP architectures)

The final benchmarking call executes the comparison and stores the results in CSV format.

NOTE:
- The file assumes prior availability of KAN-based model implementations.
- Uses only the single-table evaluation mode from SDGym.
- Output file path should be customized for local or cluster usage.

"""

import sdgym
from sdgym import create_single_table_synthesizer
from KAN_synth.models.KAN_CTGAN_code import KAN_CTGAN
from KAN_synth.models.KAN_TVAE_code import KAN_TVAE
from KAN_synth.models.Hybrid_CTGAN_code import HYBRID_KAN_CTGAN
from KAN_synth.models.Hybrid_TVAE_code import HYBRID_KAN_TVAE
from KAN_synth.models.Disc_KAN_CTGAN_code import Disc_KAN_CTGAN
from KAN_synth.models.Gen_KAN_CTGAN_code import Gen_KAN_CTGAN
from ctgan import CTGAN, TVAE

# Models to test
synthetizers = ["GaussianCopulaSynthesizer", "CTGANSynthesizer", "TVAESynthesizer"]

# ORIGINAL MODELS BUT MANUALLY IMPORTED
def get_trained_synthesizer_ORIGINAL_CTGAN(data, metadata):
    discrete = [
        col_name
        for col_name, col_info in metadata["columns"].items()
        if col_info["sdtype"] == "categorical"
    ]

    # Initialize the KAN_CTGAN model
    synth = CTGAN()

    # Train on the provided testing datasets
    synth.fit(data, discrete_columns=discrete)

    return synth

def sample_from_synthesizer_ORIGINAL_CTGAN(synthesizer, n_rows):
    return synthesizer.sample(n_rows)

ORIGINAL_CTGAN_synth = create_single_table_synthesizer(
    get_trained_synthesizer_fn=get_trained_synthesizer_ORIGINAL_CTGAN,
    sample_from_synthesizer_fn=sample_from_synthesizer_ORIGINAL_CTGAN,
    display_name="ORIGINAL-CTGAN"
)

print("ORIGINAL-CTGAN CREATED")

# TVAE ORIGINAL
def get_trained_synthesizer_ORIGINAL_TVAE(data, metadata):
    discrete = [
        col_name
        for col_name, col_info in metadata["columns"].items()
        if col_info["sdtype"] == "categorical"
    ]

    # Initialize the KAN_CTGAN model
    synth = TVAE()

    # Train on the provided testing datasets
    synth.fit(data, discrete_columns=discrete)

    return synth

def sample_from_synthesizer_ORIGINAL_TVAE(synthesizer, n_rows):
    return synthesizer.sample(n_rows)

ORIGINAL_TVAE_synth = create_single_table_synthesizer(
    get_trained_synthesizer_fn=get_trained_synthesizer_ORIGINAL_TVAE,
    sample_from_synthesizer_fn=sample_from_synthesizer_ORIGINAL_TVAE,
    display_name="ORIGINAL-TVAE"
)

print("ORIGINAL-TVAE CREATED")

# Create Custom Synthesizer: KAN_CTGAN
def get_trained_synthesizer_KAN_CTGAN(data, metadata):
    print("METADATA KEYS:", metadata)
    discrete = [
        col_name
        for col_name, col_info in metadata["columns"].items()
        if col_info["sdtype"] == "categorical"
    ]

    # Initialize the KAN_CTGAN model
    synth = KAN_CTGAN()

    # Train on the provided testing datasets
    synth.fit(data, discrete_columns=discrete)

    return synth

def sample_from_synthesizer_KAN_CTGAN(synthesizer, n_rows):
    return synthesizer.sample(n_rows)

KAN_CTGAN_synth = create_single_table_synthesizer(
    get_trained_synthesizer_fn=get_trained_synthesizer_KAN_CTGAN,
    sample_from_synthesizer_fn=sample_from_synthesizer_KAN_CTGAN,
    display_name="KAN-CTGAN"
)

print("KAN-CTGAN CREATED")

# Create Custom Synthesizer: Disc KAN CTGAN
def get_trained_synthesizer_Disc_KAN_CTGAN(data, metadata):
    
    discrete = [
        col_name
        for col_name, col_info in metadata["columns"].items()
        if col_info["sdtype"] == "categorical"
    ]

    # Initialize Hybrid_CTGAN
    synth = Disc_KAN_CTGAN()

    # Training
    synth.fit(data, discrete_columns=discrete)

    return synth

def sample_from_synthesizer_Disc_KAN_CTGAN(synthesizer, n_rows):
    return synthesizer.sample(n_rows)

KAN_Disc_CTGAN_synth = create_single_table_synthesizer(
    get_trained_synthesizer_fn=get_trained_synthesizer_Disc_KAN_CTGAN,
    sample_from_synthesizer_fn=sample_from_synthesizer_Disc_KAN_CTGAN,
    display_name="Disc_KAN_CTGAN"
)

print("Disc-KAN-CTGAN CREATED")

# Create Custom Synthesizer: Gen_KAN_CTGAN
def get_trained_synthesizer_Gen_KAN_CTGAN(data, metadata):

    discrete = [
        col_name
        for col_name, col_info in metadata["columns"].items()
        if col_info["sdtype"] == "categorical"
    ]

    # Initialize Hybrid_CTGAN
    synth = Gen_KAN_CTGAN()

    # Training
    synth.fit(data, discrete_columns=discrete)

    return synth

def sample_from_synthesizer_Gen_KAN_CTGAN(synthesizer, n_rows):
    return synthesizer.sample(n_rows)

KAN_Gen_CTGAN_synth = create_single_table_synthesizer(
    get_trained_synthesizer_fn=get_trained_synthesizer_Gen_KAN_CTGAN,
    sample_from_synthesizer_fn=sample_from_synthesizer_Gen_KAN_CTGAN,
    display_name="Gen_KAN_CTGAN"
)

print("Gen-KAN-CTGAN CREATED")


# Create Custom Synthesizer: Hybrid_CTGAN
def get_trained_synthesizer_Hybrid_CTGAN(data, metadata):
    
    discrete = [
        col_name
        for col_name, col_info in metadata["columns"].items()
        if col_info["sdtype"] == "categorical"
    ]

    # Initialize Hybrid_CTGAN
    synth = HYBRID_KAN_CTGAN()

    # Training
    synth.fit(data, discrete_columns=discrete)

    return synth

def sample_from_synthesizer_Hybrid_CTGAN(synthesizer, n_rows):
    return synthesizer.sample(n_rows)

KAN_HYBRID_CTGAN_synth = create_single_table_synthesizer(
    get_trained_synthesizer_fn=get_trained_synthesizer_Hybrid_CTGAN,
    sample_from_synthesizer_fn=sample_from_synthesizer_Hybrid_CTGAN,
    display_name="KAN_HYBRID_CTGAN"
)

print("HYBRID-KAN-CTGAN CREATED")


# Create Custom Synthesizer: KAN_TAVE
def get_trained_synthesizer_KAN_TVAE(data, metadata):
    
    discrete = [
        col_name
        for col_name, col_info in metadata["columns"].items()
        if col_info["sdtype"] == "categorical"
    ]

    # Initialize KAN_TVAE
    synth = KAN_TVAE()

    # Training
    synth.fit(data, discrete_columns=discrete)

    return synth

def sample_from_synthesizer_KAN_TVAE(synthesizer, n_rows):
    return synthesizer.sample(n_rows)

KAN_TVAE_synth = create_single_table_synthesizer(
    get_trained_synthesizer_fn=get_trained_synthesizer_KAN_TVAE,
    sample_from_synthesizer_fn=sample_from_synthesizer_KAN_TVAE,
    display_name="KAN_TVAE"
)

print("KAN-TVAE CREATED")

# Create Custom Synthesizer: Hybrid_TVAE
def get_trained_synthesizer_Hybrid_TVAE(data, metadata):
    print("METADATA KEYS:", metadata)
    discrete = [
        col_name
        for col_name, col_info in metadata["columns"].items()
        if col_info["sdtype"] == "categorical"
    ]

    # Initialize the KAN_CTGAN model
    synth = HYBRID_KAN_TVAE()

    # Train on the provided testing datasets
    synth.fit(data, discrete_columns=discrete)

    return synth

def sample_from_synthesizer_Hybrid_TVAE(synthesizer, n_rows):
    return synthesizer.sample(n_rows)

Hybrid_TVAE_synth = create_single_table_synthesizer(
    get_trained_synthesizer_fn=get_trained_synthesizer_Hybrid_TVAE,
    sample_from_synthesizer_fn=sample_from_synthesizer_Hybrid_TVAE,
    display_name="Hybrid_TVAE"
)

print("Hybrid-TVAE CREATED")

# Output file path
# Output file path for cluster
output_filepath = "/scrfs/storage/delgobbo/home/Thesis/Benchmarks/SDGym_comparison_Final.csv"


results = sdgym.benchmark_single_table(
    synthesizers=synthetizers,
    custom_synthesizers=[ORIGINAL_CTGAN_synth, ORIGINAL_TVAE_synth, KAN_CTGAN_synth, KAN_TVAE_synth, KAN_HYBRID_CTGAN_synth, KAN_Disc_CTGAN_synth, KAN_Gen_CTGAN_synth, Hybrid_TVAE_synth],
    output_filepath=output_filepath,
    limit_dataset_size=True,
    show_progress=True
)
