from datetime import timedelta
from sklearn.linear_model import Ridge
import pandas as pd

def generate_predictions():
    # Load and process weather data
    weather = pd.read_csv(r'weather_dataset.csv')  # Update with your file path
    weather.index = pd.to_datetime(weather.index)
    predictors = ['tmax', 'tmin']
    weather['tavg'] = (weather['tmax'] + weather['tmin']) / 2
    weather = weather.dropna(subset=predictors + ['tavg'])

    # Train model
    model = Ridge(alpha=1.0)
    model.fit(weather[predictors], weather['tavg'])

    # Generate predictions
    last_date = weather.index.max()
    prediction = pd.DataFrame({
        'date': [last_date + timedelta(days=i) for i in range(1, 8)],
        'tmax': weather['tmax'].iloc[-7:].values,
        'tmin': weather['tmin'].iloc[-7:].values
    })
    prediction['tavg_prediction'] = model.predict(prediction[predictors])

    # Convert Fahrenheit to Celsius
    def fahrenheit_to_celsius(fahrenheit):
        return (fahrenheit - 32) * 5 / 9

    prediction['tmax'] = prediction['tmax'].apply(fahrenheit_to_celsius)
    prediction['tmin'] = prediction['tmin'].apply(fahrenheit_to_celsius)
    prediction['tavg_prediction'] = prediction['tavg_prediction'].apply(fahrenheit_to_celsius)

    # Convert DataFrame to list of dictionaries for Flask
    return prediction[['date', 'tmax', 'tmin', 'tavg_prediction']].to_dict(orient='records')
