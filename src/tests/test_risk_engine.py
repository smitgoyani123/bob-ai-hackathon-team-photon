import numpy as np
import pandas as pd

from src.weather_risk import calculate_weather_risk


def test_weather_risk_handles_constant_observations():
    model_input = pd.DataFrame({
        "weather_rainfall": [10.0, 10.0],
        "weather_wind": [5.0, 5.0],
        "weather_temperature": [25.0, 25.0],
        "weather_storm": [0.0, 0.0],
        "weather_flood_risk": [0.0, 0.0],
    })

    result = calculate_weather_risk(model_input)

    assert result.name == "weather_risk"
    assert np.isfinite(result).all()
    assert ((result >= 0) & (result <= 100)).all()
