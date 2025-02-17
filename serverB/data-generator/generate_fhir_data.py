import requests
import json
from datetime import datetime, timedelta
import random
import names

BASE_URL = "http://fetal-fhir:8080/fhir"

def create_patient(maternal_id=None):
    """Create a fetus patient record linked to maternal ID"""
    patient_data = {
        "resourceType": "Patient",
        "active": True,
        "name": [
            {
                "use": "official",
                "family": names.get_last_name(),  # Using mother's last name
                "given": ["Fetus"]  # Placeholder name
            }
        ],
        "identifier": [
            {
                "system": "http://example.com/fetal-id",
                "value": f"FET{random.randint(10000, 99999)}"
            }
        ]
    }
    
    # Link to maternal record if provided
    if maternal_id:
        patient_data["link"] = [
            {
                "other": {
                    "reference": f"Patient/{maternal_id}"
                },
                "type": "seealso"
            }
        ]
    
    response = requests.post(
        f"{BASE_URL}/Patient",
        headers={"Content-Type": "application/fhir+json"},
        json=patient_data
    )
    
    if response.status_code == 201:
        return response.json()["id"]
    else:
        raise Exception(f"Failed to create patient: {response.text}")

def create_fetal_measurements(patient_id, gestational_age):
    """Record fetal measurements based on gestational age"""
    
    # Calculate expected measurements based on gestational age
    # These are simplified estimates - in practice, you'd use proper growth charts
    expected_weight = max(0, (gestational_age - 10) * 100)  # Rough estimate in grams
    expected_length = max(0, (gestational_age - 10) * 2)    # Rough estimate in cm
    
    measurements = [
        # Fetal Weight Estimation
        {
            "code": {
                "coding": [
                    {
                        "system": "http://loinc.org",
                        "code": "11727-5",
                        "display": "Fetus Estimated weight"
                    }
                ]
            },
            "valueQuantity": {
                "value": expected_weight + random.uniform(-100, 100),  # Add some variation
                "unit": "g",
                "system": "http://unitsofmeasure.org",
                "code": "g"
            }
        },
        # Crown-Rump Length or Fetal Length
        {
            "code": {
                "coding": [
                    {
                        "system": "http://loinc.org",
                        "code": "11820-8",
                        "display": "Fetus Crown rump length"
                    }
                ]
            },
            "valueQuantity": {
                "value": expected_length + random.uniform(-1, 1),  # Add some variation
                "unit": "cm",
                "system": "http://unitsofmeasure.org",
                "code": "cm"
            }
        }
    ]
    
    success = True
    for measurement in measurements:
        observation = {
            "resourceType": "Observation",
            "status": "final",
            "category": [
                {
                    "coding": [
                        {
                            "system": "http://terminology.hl7.org/CodeSystem/observation-category",
                            "code": "imaging"
                        }
                    ]
                }
            ],
            "subject": {
                "reference": f"Patient/{patient_id}"
            },
            "effectiveDateTime": datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"),
            **measurement
        }
        
        response = requests.post(
            f"{BASE_URL}/Observation",
            headers={"Content-Type": "application/fhir+json"},
            json=observation
        )
        
        if response.status_code != 201:
            success = False
            print(f"Failed to create fetal measurement: {response.text}")
    
    return success

def create_fetal_heart_monitoring(patient_id):
    """Record fetal heart rate monitoring"""
    heart_rate = {
        "resourceType": "Observation",
        "status": "final",
        "category": [
            {
                "coding": [
                    {
                        "system": "http://terminology.hl7.org/CodeSystem/observation-category",
                        "code": "vital-signs"
                    }
                ]
            }
        ],
        "code": {
            "coding": [
                {
                    "system": "http://loinc.org",
                    "code": "55283-6",
                    "display": "Fetal Heart Rate"
                }
            ]
        },
        "subject": {
            "reference": f"Patient/{patient_id}"
        },
        "effectiveDateTime": datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"),
        "valueQuantity": {
            "value": random.randint(120, 160),
            "unit": "beats/minute",
            "system": "http://unitsofmeasure.org",
            "code": "/min"
        }
    }
    
    response = requests.post(
        f"{BASE_URL}/Observation",
        headers={"Content-Type": "application/fhir+json"},
        json=heart_rate
    )
    
    return response.status_code == 201

def create_ultrasound_report(patient_id, gestational_age):
    """Create an ultrasound diagnostic report"""
    
    # Define possible findings based on gestational age
    findings = [
        "Normal fetal position",
        "Normal cardiac activity",
        "Normal amniotic fluid volume",
        "Placenta in normal position"
    ]
    
    diagnostic_report = {
        "resourceType": "DiagnosticReport",
        "status": "final",
        "category": [
            {
                "coding": [
                    {
                        "system": "http://terminology.hl7.org/CodeSystem/v2-0074",
                        "code": "RAD",
                        "display": "Radiology"
                    }
                ]
            }
        ],
        "code": {
            "coding": [
                {
                    "system": "http://loinc.org",
                    "code": "45264-7",
                    "display": "Obstetric ultrasound study"
                }
            ]
        },
        "subject": {
            "reference": f"Patient/{patient_id}"
        },
        "effectiveDateTime": datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"),
        "issued": datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"),
        "conclusion": ". ".join(findings),
        "conclusionCode": [
            {
                "coding": [
                    {
                        "system": "http://snomed.info/sct",
                        "code": "247236001",
                        "display": "Normal ultrasound scan"
                    }
                ]
            }
        ]
    }
    
    response = requests.post(
        f"{BASE_URL}/DiagnosticReport",
        headers={"Content-Type": "application/fhir+json"},
        json=diagnostic_report
    )
    
    return response.status_code == 201

def create_fetal_movement(patient_id):
    """Record fetal movement observation"""
    movement = {
        "resourceType": "Observation",
        "status": "final",
        "category": [
            {
                "coding": [
                    {
                        "system": "http://terminology.hl7.org/CodeSystem/observation-category",
                        "code": "exam"
                    }
                ]
            }
        ],
        "code": {
            "coding": [
                {
                    "system": "http://snomed.info/sct",
                    "code": "364617005",
                    "display": "Fetal movement finding"
                }
            ]
        },
        "subject": {
            "reference": f"Patient/{patient_id}"
        },
        "effectiveDateTime": datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"),
        "valueCodeableConcept": {
            "coding": [
                {
                    "system": "http://snomed.info/sct",
                    "code": "289431008",
                    "display": "Fetal movements present"
                }
            ]
        }
    }
    
    response = requests.post(
        f"{BASE_URL}/Observation",
        headers={"Content-Type": "application/fhir+json"},
        json=movement
    )
    
    return response.status_code == 201

def main():
    """Generate test data for fetal health monitoring"""
    print("Starting fetal health data generation...")
    
    for i in range(5):  # Generate data for 5 fetuses
        try:
            # Create fetal patient record
            patient_id = create_patient()
            print(f"Created fetal patient {i+1}/5 with ID: {patient_id}")
            
            # Simulate random gestational age
            gestational_age = random.randint(12, 40)
            
            # Record fetal measurements
            if create_fetal_measurements(patient_id, gestational_age):
                print(f"Recorded fetal measurements for patient {patient_id}")
            
            # Record fetal heart rate
            if create_fetal_heart_monitoring(patient_id):
                print(f"Recorded fetal heart rate for patient {patient_id}")
            
            # Create ultrasound report
            if create_ultrasound_report(patient_id, gestational_age):
                print(f"Created ultrasound report for patient {patient_id}")
            
            # Record fetal movement
            if create_fetal_movement(patient_id):
                print(f"Recorded fetal movement for patient {patient_id}")
            
            print("---")
            
        except Exception as e:
            print(f"Error processing fetal patient {i+1}: {str(e)}")
    
    print("Fetal health data generation complete!")

if __name__ == "__main__":
    main()