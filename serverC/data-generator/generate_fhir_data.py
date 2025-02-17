import requests
import json
from datetime import datetime, timedelta
import random
import names

BASE_URL = "http://obstetric-fhir:8080/fhir"

def create_patient():
    """Create a patient record for obstetric care"""
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
        "birthDate": (datetime.now() - timedelta(days=random.randint(7300, 10950))).strftime("%Y-%m-%d"),
        "identifier": [
            {
                "system": "http://example.com/obstetric-id",
                "value": f"OBS{random.randint(10000, 99999)}"
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

def create_delivery_plan(patient_id):
    """Create a care plan for delivery"""
    delivery_methods = [
        {"code": "386637004", "display": "Vaginal delivery"},
        {"code": "11466000", "display": "Cesarean section"}
    ]
    selected_method = random.choice(delivery_methods)
    
    care_plan = {
        "resourceType": "CarePlan",
        "status": "active",
        "intent": "plan",
        "subject": {
            "reference": f"Patient/{patient_id}"
        },
        "category": [
            {
                "coding": [
                    {
                        "system": "http://snomed.info/sct",
                        "code": "183460006",
                        "display": "Obstetric care plan"
                    }
                ]
            }
        ],
        "title": f"Delivery Plan - {selected_method['display']}",
        "description": f"Planned {selected_method['display']} with standard monitoring and care protocols",
        "activity": [
            {
                "detail": {
                    "code": {
                        "coding": [
                            {
                                "system": "http://snomed.info/sct",
                                "code": selected_method["code"],
                                "display": selected_method["display"]
                            }
                        ]
                    },
                    "status": "not-started",
                    "scheduledPeriod": {
                        "start": (datetime.now() + timedelta(days=random.randint(30, 90))).strftime("%Y-%m-%d")
                    }
                }
            }
        ]
    }
    
    response = requests.post(
        f"{BASE_URL}/CarePlan",
        headers={"Content-Type": "application/fhir+json"},
        json=care_plan
    )
    
    return response.status_code == 201

def create_risk_assessment(patient_id):
    """Create a risk assessment for pregnancy"""
    risk_factors = [
        {
            "code": "161766001",
            "display": "History of previous cesarean section"
        },
        {
            "code": "199745000",
            "display": "Elderly primigravida"
        },
        {
            "code": "48194001",
            "display": "Pregnancy-induced hypertension"
        }
    ]
    
    selected_risks = random.sample(risk_factors, random.randint(0, 2))
    
    risk_assessment = {
        "resourceType": "RiskAssessment",
        "status": "final",
        "subject": {
            "reference": f"Patient/{patient_id}"
        },
        "occurrenceDateTime": datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"),
        "condition": {
            "coding": [
                {
                    "system": "http://snomed.info/sct",
                    "code": "364320009",
                    "display": "Pregnancy-related risk factor"
                }
            ]
        },
        "prediction": [
            {
                "outcome": {
                    "coding": [
                        {
                            "system": "http://snomed.info/sct",
                            "code": risk["code"],
                            "display": risk["display"]
                        }
                    ]
                },
                "probabilityDecimal": random.uniform(0.1, 0.5)
            } for risk in selected_risks
        ] if selected_risks else []
    }
    
    response = requests.post(
        f"{BASE_URL}/RiskAssessment",
        headers={"Content-Type": "application/fhir+json"},
        json=risk_assessment
    )
    
    return response.status_code == 201

def create_labor_progress(patient_id):
    """Create labor progress observations"""
    cervical_dilation = {
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
                    "system": "http://loinc.org",
                    "code": "11884-4",
                    "display": "Cervix dilation"
                }
            ]
        },
        "subject": {
            "reference": f"Patient/{patient_id}"
        },
        "effectiveDateTime": datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"),
        "valueQuantity": {
            "value": random.randint(1, 10),
            "unit": "cm",
            "system": "http://unitsofmeasure.org",
            "code": "cm"
        }
    }
    
    contraction_monitoring = {
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
                    "code": "364567001",
                    "display": "Uterine contraction monitoring"
                }
            ]
        },
        "subject": {
            "reference": f"Patient/{patient_id}"
        },
        "effectiveDateTime": datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"),
        "component": [
            {
                "code": {
                    "coding": [
                        {
                            "system": "http://snomed.info/sct",
                            "code": "364567001",
                            "display": "Contraction frequency"
                        }
                    ]
                },
                "valueQuantity": {
                    "value": random.randint(2, 5),
                    "unit": "minutes",
                    "system": "http://unitsofmeasure.org",
                    "code": "min"
                }
            }
        ]
    }
    
    success = True
    for observation in [cervical_dilation, contraction_monitoring]:
        response = requests.post(
            f"{BASE_URL}/Observation",
            headers={"Content-Type": "application/fhir+json"},
            json=observation
        )
        if response.status_code != 201:
            success = False
            print(f"Failed to create labor observation: {response.text}")
    
    return success

def create_complications_monitoring(patient_id):
    """Create monitoring for potential complications"""
    complications = [
        {
            "code": "198609003",
            "display": "Pre-eclampsia screening"
        },
        {
            "code": "237228008",
            "display": "Gestational diabetes screening"
        }
    ]
    
    success = True
    for complication in complications:
        observation = {
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
                        "code": complication["code"],
                        "display": complication["display"]
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
                        "code": "260385009",
                        "display": "Negative"
                    }
                ]
            }
        }
        
        response = requests.post(
            f"{BASE_URL}/Observation",
            headers={"Content-Type": "application/fhir+json"},
            json=observation
        )
        
        if response.status_code != 201:
            success = False
            print(f"Failed to create complication monitoring: {response.text}")
    
    return success

def main():
    """Generate test data for obstetric care"""
    print("Starting obstetric care data generation...")
    
    for i in range(5):  # Generate data for 5 patients
        try:
            # Create patient
            patient_id = create_patient()
            print(f"Created obstetric patient {i+1}/5 with ID: {patient_id}")
            
            # Create delivery plan
            if create_delivery_plan(patient_id):
                print(f"Created delivery plan for patient {patient_id}")
            
            # Create risk assessment
            if create_risk_assessment(patient_id):
                print(f"Created risk assessment for patient {patient_id}")
            
            # Create labor progress observations
            if create_labor_progress(patient_id):
                print(f"Recorded labor progress for patient {patient_id}")
            
            # Create complications monitoring
            if create_complications_monitoring(patient_id):
                print(f"Created complications monitoring for patient {patient_id}")
            
            print("---")
            
        except Exception as e:
            print(f"Error processing obstetric patient {i+1}: {str(e)}")
    
    print("Obstetric care data generation complete!")

if __name__ == "__main__":
    main()