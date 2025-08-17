import numpy as np
import pandas as pd 
import pytest

from KAN_synth.models import (
    KAN_CTGAN,
    HYBRID_KAN_CTGAN,
    Disc_KAN_CTGAN,
    Gen_KAN_CTGAN,
    KAN_TVAE,
    HYBRID_KAN_TVAE,
)

@pytest.fixture
def dummy_data():
    return pd.DataFrame({
        "A": np.random.randint(0, 3, 100),
        "B": np.random.randn(100),
        "C": np.random.choice(["X", "Y", "Z"], 100)
    })

@pytest.mark.parametrize("model_class", [
    KAN_CTGAN, HYBRID_KAN_CTGAN, Disc_KAN_CTGAN, Gen_KAN_CTGAN,
    KAN_TVAE, HYBRID_KAN_TVAE,
])
def test_model_fit_and_sample(model_class, dummy_data):
    model = model_class(epochs=2, verbose=True)
    model.fit(dummy_data, discrete_columns=["A", "C"])
    sampled = model.sample(10)
    assert isinstance(sampled, pd.DataFrame)
    assert sampled.shape[0] == 10

print("TEST PASSED")