import requests
import json
from datetime import datetime, timedelta
import random
import names

BASE_URL = "http://maternal-fhir:8080/fhir"

def create_patient():
    """Create a pregnant patient and return their ID"""
    patient_data = {
        "resourceType": "Patient",
        "active": True,
        "name": [
            {
                "use": "official",
                "family": names.get_last_name(),
                "given": [names.get_first_name(gender='female')]
            }
        ],
        "gender": "female",
        "birthDate": (datetime.now() - timedelta(days=random.randint(7300, 10950))).strftime("%Y-%m-%d"),  # Age between 20-30
        "identifier": [
            {
                "system": "http://example.com/maternal-id",
                "value": f"MAT{random.randint(10000, 99999)}"
            }
        ]
    }
    
    response = requests.post(
        f"{BASE_URL}/Patient",
        headers={"Content-Type": "application/fhir+json"},
        json=patient_data
    )
    
    if response.status_code == 201:
        return response.json()["id"]
    else:
        raise Exception(f"Failed to create patient: {response.text}")

def create_pregnancy_observation(patient_id):
    """Record pregnancy status and gestational age"""
    gestational_weeks = random.randint(8, 40)
    pregnancy_data = {
        "resourceType": "Observation",
        "status": "final",
        "code": {
            "coding": [
                {
                    "system": "http://loinc.org",
                    "code": "82810-3",
                    "display": "Pregnancy status"
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
                    "code": "77386006",
                    "display": "Pregnant"
                }
            ]
        },
        "component": [
            {
                "code": {
                    "coding": [
                        {
                            "system": "http://loinc.org",
                            "code": "49052-4",
                            "display": "Gestational age"
                        }
                    ]
                },
                "valueQuantity": {
                    "value": gestational_weeks,
                    "unit": "weeks",
                    "system": "http://unitsofmeasure.org",
                    "code": "wk"
                }
            }
        ]
    }
    
    response = requests.post(
        f"{BASE_URL}/Observation",
        headers={"Content-Type": "application/fhir+json"},
        json=pregnancy_data
    )
    
    return response.status_code == 201

def create_vital_signs(patient_id):
    """Record maternal vital signs"""
    vitals = [
        # Blood Pressure
        {
            "code": {
                "coding": [
                    {
                        "system": "http://loinc.org",
                        "code": "85354-9",
                        "display": "Blood pressure panel"
                    }
                ]
            },
            "component": [
                {
                    "code": {
                        "coding": [
                            {
                                "system": "http://loinc.org",
                                "code": "8480-6",
                                "display": "Systolic blood pressure"
                            }
                        ]
                    },
                    "valueQuantity": {
                        "value": random.randint(100, 140),
                        "unit": "mmHg",
                        "system": "http://unitsofmeasure.org",
                        "code": "mm[Hg]"
                    }
                },
                {
                    "code": {
                        "coding": [
                            {
                                "system": "http://loinc.org",
                                "code": "8462-4",
                                "display": "Diastolic blood pressure"
                            }
                        ]
                    },
                    "valueQuantity": {
                        "value": random.randint(60, 90),
                        "unit": "mmHg",
                        "system": "http://unitsofmeasure.org",
                        "code": "mm[Hg]"
                    }
                }
            ]
        },
        # Weight
        {
            "code": {
                "coding": [
                    {
                        "system": "http://loinc.org",
                        "code": "29463-7",
                        "display": "Body weight"
                    }
                ]
            },
            "valueQuantity": {
                "value": random.uniform(50.0, 85.0),
                "unit": "kg",
                "system": "http://unitsofmeasure.org",
                "code": "kg"
            }
        },
        # Heart Rate
        {
            "code": {
                "coding": [
                    {
                        "system": "http://loinc.org",
                        "code": "8867-4",
                        "display": "Heart rate"
                    }
                ]
            },
            "valueQuantity": {
                "value": random.randint(60, 100),
                "unit": "beats/minute",
                "system": "http://unitsofmeasure.org",
                "code": "/min"
            }
        }
    ]
    
    success = True
    for vital in vitals:
        observation = {
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
            "subject": {
                "reference": f"Patient/{patient_id}"
            },
            "effectiveDateTime": datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"),
            **vital
        }
        
        response = requests.post(
            f"{BASE_URL}/Observation",
            headers={"Content-Type": "application/fhir+json"},
            json=observation
        )
        
        if response.status_code != 201:
            success = False
            print(f"Failed to create vital sign: {response.text}")
    
    return success

def create_lab_results(patient_id):
    """Record maternal lab results"""
    lab_tests = [
        # Hemoglobin
        {
            "code": {
                "coding": [
                    {
                        "system": "http://loinc.org",
                        "code": "718-7",
                        "display": "Hemoglobin [Mass/volume] in Blood"
                    }
                ]
            },
            "valueQuantity": {
                "value": random.uniform(11.0, 15.0),
                "unit": "g/dL",
                "system": "http://unitsofmeasure.org",
                "code": "g/dL"
            }
        },
        # Blood Glucose
        {
            "code": {
                "coding": [
                    {
                        "system": "http://loinc.org",
                        "code": "2339-0",
                        "display": "Glucose [Mass/volume] in Blood"
                    }
                ]
            },
            "valueQuantity": {
                "value": random.uniform(70.0, 130.0),
                "unit": "mg/dL",
                "system": "http://unitsofmeasure.org",
                "code": "mg/dL"
            }
        }
    ]
    
    success = True
    for lab_test in lab_tests:
        observation = {
            "resourceType": "Observation",
            "status": "final",
            "category": [
                {
                    "coding": [
                        {
                            "system": "http://terminology.hl7.org/CodeSystem/observation-category",
                            "code": "laboratory"
                        }
                    ]
                }
            ],
            "subject": {
                "reference": f"Patient/{patient_id}"
            },
            "effectiveDateTime": datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"),
            **lab_test
        }
        
        response = requests.post(
            f"{BASE_URL}/Observation",
            headers={"Content-Type": "application/fhir+json"},
            json=observation
        )
        
        if response.status_code != 201:
            success = False
            print(f"Failed to create lab result: {response.text}")
    
    return success

def create_medication_statement(patient_id):
    """Record maternal medications"""
    medications = [
        {
            "code": {
                "coding": [
                    {
                        "system": "http://www.nlm.nih.gov/research/umls/rxnorm",
                        "code": "2278",
                        "display": "Folic Acid"
                    }
                ]
            },
            "dosage": "1 mg daily"
        },
        {
            "code": {
                "coding": [
                    {
                        "system": "http://www.nlm.nih.gov/research/umls/rxnorm",
                        "code": "40790",
                        "display": "Prenatal Vitamins"
                    }
                ]
            },
            "dosage": "1 tablet daily"
        }
    ]
    
    success = True
    for medication in medications:
        med_statement = {
            "resourceType": "MedicationStatement",
            "status": "active",
            "subject": {
                "reference": f"Patient/{patient_id}"
            },
            "medicationCodeableConcept": medication["code"],
            "effectiveDateTime": datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"),
            "dosage": [
                {
                    "text": medication["dosage"]
                }
            ]
        }
        
        response = requests.post(
            f"{BASE_URL}/MedicationStatement",
            headers={"Content-Type": "application/fhir+json"},
            json=med_statement
        )
        
        if response.status_code != 201:
            success = False
            print(f"Failed to create medication statement: {response.text}")
    
    return success

def main():
    """Generate test data for maternal health monitoring"""
    print("Starting maternal health data generation...")
    
    for i in range(5):  # Generate data for 5 patients
        try:
            # Create patient
            patient_id = create_patient()
            print(f"Created patient {i+1}/5 with ID: {patient_id}")
            
            # Record pregnancy status
            if create_pregnancy_observation(patient_id):
                print(f"Recorded pregnancy status for patient {patient_id}")
            
            # Record vital signs
            if create_vital_signs(patient_id):
                print(f"Recorded vital signs for patient {patient_id}")
            
            # Record lab results
            if create_lab_results(patient_id):
                print(f"Recorded lab results for patient {patient_id}")
            
            # Record medications
            if create_medication_statement(patient_id):
                print(f"Recorded medications for patient {patient_id}")
            
            print("---")
            
        except Exception as e:
            print(f"Error processing patient {i+1}: {str(e)}")
    
    print("Maternal health data generation complete!")

if __name__ == "__main__":
    main()