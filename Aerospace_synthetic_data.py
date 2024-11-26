import pandas as pd
import numpy as np

df = pd.DataFrame({
    'aircraft_id': pd.Series(np.random.choice(['N' + str(i).zfill(4) + chr(np.random.randint(65, 91)) + chr(np.random.randint(65, 91)) for i in range(100, 999)], size=200, replace=False)),
    'flight_number': pd.Series(['AA' + str(np.random.randint(100, 999)) for _ in range(200)]),
    'timestamp': pd.to_datetime(np.random.rand(200) * (pd.Timestamp('2023-12-31').value - pd.Timestamp('2023-01-01').value) + pd.Timestamp('2023-01-01').value, unit='ns'),
    'latitude': np.random.uniform(-90, 90, 200),
    'longitude': np.random.uniform(-180, 180, 200),
    'altitude': np.random.randint(0, 70000, 200),
    'airspeed': np.random.randint(0, 600, 200),
    'heading': np.random.randint(0, 360, 200),
    'fuel_consumption': np.random.uniform(0, 10000, 200),
    'engine_temperature': np.random.randint(0, 1200, 200),
    'vibration_level': np.random.uniform(0, 5, 200),
    'weather_conditions': np.random.choice(['Sunny', 'Cloudy', 'Rainy', 'Snowy', 'Foggy', 'Stormy'], size=200),
    'maintenance_status': np.random.choice(['Operational', 'Scheduled Maintenance', 'Unscheduled Maintenance', 'Grounded'], size=200),
    'part_number': pd.Series(['ABC' + str(i).zfill(6) for i in range(100000, 999999)], size=200),
    'part_name': pd.Series(['Part ' + str(i) for i in range(1, 201)]),
    'manufacturing_date': pd.to_datetime(np.random.rand(200) * (pd.Timestamp('2023-12-31').value - pd.Timestamp('2018-01-01').value) + pd.Timestamp('2018-01-01').value, unit='ns'),
    'installation_date': pd.to_datetime(np.random.rand(200) * (pd.Timestamp('2023-12-31').value - pd.Timestamp('2018-01-01').value) + pd.Timestamp('2018-01-01').value, unit='ns'),
    'failure_reason': np.random.choice(['Wear and Tear', 'Corrosion', 'Manufacturing Defect', 'Foreign Object Damage', 'Other', 'Unknown'], size=200)
})

print(df)