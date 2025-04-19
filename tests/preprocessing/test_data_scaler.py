import pytest
import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler, StandardScaler
from src.preprocessing.data_scaler import DataScaler

@pytest.fixture
def sample_data():
    return pd.DataFrame({
        "feature1": [1, 2, 3, 4, 5],
        "feature2": [10, 20, 30, 40, 50],
        "feature3": [100, 200, 300, 400, 500]
    })

def test_init():
    scaler = DataScaler(scaling_methods={"feature1": "minmax"}, columns=["feature1"])
    assert scaler.columns == ["feature1"]
    assert scaler.scaling_methods["feature1"] == "minmax"
    assert scaler.scalers == {}
    assert scaler.minmax_scalers == {}

def test_fit_minmax(sample_data):
    scaler = DataScaler(scaling_methods={"feature1": "minmax"}, columns=["feature1"])
    scaler.fit(sample_data)
    assert "feature1" in scaler.scalers
    assert isinstance(scaler.scalers["feature1"], MinMaxScaler)

def test_fit_standard(sample_data):
    scaler = DataScaler(scaling_methods={"feature2": "standard"}, columns=["feature2"])
    scaler.fit(sample_data)
    assert isinstance(scaler.scalers["feature2"], StandardScaler)

def test_fit_log(sample_data):
    scaler = DataScaler(scaling_methods={"feature3": "log"}, columns=["feature3"])
    scaler.fit(sample_data)
    assert scaler.scalers["feature3"] == "log"

def test_fit_unknown_method(sample_data):
    scaler = DataScaler(scaling_methods={"feature1": "unknown"}, columns=["feature1"])
    with pytest.raises(ValueError, match="Unknown scaling method for feature1: unknown"):
        scaler.fit(sample_data)

def test_transform_minmax(sample_data):
    scaler = DataScaler(scaling_methods={"feature1": "minmax"}, columns=["feature1"])
    scaler.fit(sample_data)
    transformed = scaler.transform(sample_data)
    assert transformed.shape == sample_data.shape
    assert np.allclose(transformed["feature1"].min(), 0)
    assert np.allclose(transformed["feature1"].max(), 1)

def test_transform_standard(sample_data):
    scaler = DataScaler(scaling_methods={"feature2": "standard"}, columns=["feature2"])
    scaler.fit(sample_data)
    transformed = scaler.transform(sample_data)
    assert transformed.shape == sample_data.shape
    assert np.allclose(transformed["feature2"].min(), 0)
    assert np.allclose(transformed["feature2"].max(), 1)

def test_transform_log(sample_data):
    scaler = DataScaler(scaling_methods={"feature3": "log"}, columns=["feature3"])
    scaler.fit(sample_data)
    transformed = scaler.transform(sample_data)
    assert transformed.shape == sample_data.shape
    assert np.allclose(transformed["feature3"].min(), 0)
    assert np.allclose(transformed["feature3"].max(), 1)

def test_inverse_transform_log(sample_data):
    scaler = DataScaler(scaling_methods={"feature3": "log"}, columns=["feature3"])
    scaler.fit(sample_data)
    transformed = scaler.transform(sample_data)
    inversed = scaler.inverse_transform(transformed)
    assert np.allclose(sample_data["feature3"], inversed["feature3"], rtol=1e-2)

def test_inverse_transform_standard(sample_data):
    scaler = DataScaler(scaling_methods={"feature2": "standard"}, columns=["feature2"])
    scaler.fit(sample_data)
    transformed = scaler.transform(sample_data)
    inversed = scaler.inverse_transform(transformed)
    assert np.allclose(sample_data["feature2"], inversed["feature2"], rtol=1e-2)

def test_inverse_transform_minmax(sample_data):
    scaler = DataScaler(scaling_methods={"feature1": "minmax"}, columns=["feature1"])
    scaler.fit(sample_data)
    transformed = scaler.transform(sample_data)
    inversed = scaler.inverse_transform(transformed)
    assert np.allclose(sample_data["feature1"], inversed["feature1"], rtol=1e-2)

def test_missing_column_handling(sample_data):
    df = sample_data.drop(columns=["feature1"])
    scaler = DataScaler(scaling_methods={"feature1": "minmax"}, columns=["feature1"])
    scaler.fit(df)
    assert "feature1" not in scaler.scalers

def test_apply_transformation_invalid():
    df = pd.DataFrame({"x": [1, 2, 3]})
    with pytest.raises(ValueError, match="Unknown scaling method: unknown"):
        DataScaler._apply_transformation(df, None, "unknown")

def test_reverse_transformation_invalid():
    df = pd.DataFrame({"x": [1, 2, 3]})
    with pytest.raises(ValueError, match="Unknown scaling method: unknown"):
        DataScaler._reverse_transformation(df, None, "unknown")
