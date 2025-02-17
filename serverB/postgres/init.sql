CREATE TABLE IF NOT EXISTS prenatal_observation (
    id SERIAL PRIMARY KEY,
    patient_id VARCHAR(255),
    observation_date TIMESTAMP,
    weight DECIMAL,
    blood_pressure VARCHAR(50),
    fetal_heart_rate INTEGER,
    notes TEXT
);