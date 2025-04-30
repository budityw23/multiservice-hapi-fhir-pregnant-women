from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import requests
from datetime import datetime
import concurrent.futures
import logging

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO)

# Database configuration for module-checker connection
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://admin:admin@checklist-db:5432/checklist'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# FHIR servers configuration
FHIR_SERVERS = {
    'serverA': 'http://maternal-fhir:8080/fhir',
    'serverB': 'http://fetal-fhir:8080/fhir',
    'serverC': 'http://obstetric-fhir:8080/fhir'
}

db = SQLAlchemy(app)

# Import models from module-checker
class Module(db.Model):
    __tablename__ = 'modules'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.Text)
    items = db.relationship('ChecklistItem', backref='module', lazy=True)

class ChecklistItem(db.Model):
    __tablename__ = 'checklist_items'
    id = db.Column(db.Integer, primary_key=True)
    module_id = db.Column(db.Integer, db.ForeignKey('modules.id'), nullable=False)
    code = db.Column(db.String(50), nullable=False)
    display = db.Column(db.String(200), nullable=False)
    system = db.Column(db.String(200), default='http://loinc.org')
    required = db.Column(db.Boolean, default=False)

def get_patient_id(server_url, patient_identifier):
    """Get patient ID from identifier"""
    try:
        response = requests.get(
            f"{server_url}/Patient",
            params={'identifier': patient_identifier},
            headers={'Accept': 'application/fhir+json'}
        )
        
        if response.status_code == 200:
            bundle = response.json()
            if bundle.get('total', 0) > 0:
                return bundle['entry'][0]['resource']['id']
        return None
    except Exception as e:
        print(f"Error looking up patient in {server_url}: {str(e)}")
        return None

def search_fhir_server(server_url, patient_identifier, encounter_id=None, codes=None):
    """Search for observations in a FHIR server"""
    try:
        # First get the patient ID for this server
        patient_id = get_patient_id(server_url, patient_identifier)
        if not patient_id:
            return []

        # Then search for observations
        params = {
            'patient': patient_id,
            'code': ','.join(codes) if codes else None,
            'encounter': encounter_id if encounter_id else None
        }
        
        response = requests.get(
            f"{server_url}/Observation",
            params={k: v for k, v in params.items() if v is not None},
            headers={'Accept': 'application/fhir+json'}
        )
        
        if response.status_code == 200:
            return response.json().get('entry', [])
        return []
    except Exception as e:
        print(f"Error querying {server_url}: {str(e)}")
        return []

def post_observation_to_serverA(observation, patient_identifier, encounter_id=None):
    """Post an observation from serverB/C to serverA"""
    try:
        # First get or create patient in serverA
        patient_id = get_patient_id(FHIR_SERVERS['serverA'], patient_identifier)
        if not patient_id:
            logging.error(f"Patient {patient_identifier} not found in serverA")
            return False

        # Prepare the observation for posting
        new_observation = observation['resource'].copy()
        new_observation.pop('id', None)  # Remove existing ID
        new_observation['subject'] = {'reference': f'Patient/{patient_id}'}
        new_observation.pop('performer', None)  # Remove performer if it exists
        
        if encounter_id:
            new_observation['encounter'] = {'reference': f'Encounter/{encounter_id}'}

        logging.info(f"Posting observation to serverA: {new_observation}")

        # Post the observation to serverA
        response = requests.post(
            f"{FHIR_SERVERS['serverA']}/Observation",
            json=new_observation,
            headers={'Content-Type': 'application/fhir+json'}
        )
        
        if response.status_code not in [200, 201]:
            logging.error(f"Failed to post observation to serverA: {response.status_code} - {response.text}")
        
        return response.status_code in [200, 201]
    except Exception as e:
        logging.error(f"Error posting observation to serverA: {str(e)}")
        return False

@app.route('/')
def index():
    # Get all modules for the dropdown
    modules = Module.query.all()
    return render_template('index.html', modules=modules)

@app.route('/check', methods=['POST'])
def check_completeness():
    patient_identifier = request.form.get('patient_identifier')
    encounter_id = request.form.get('encounter_id')
    module_id = request.form.get('module_id')

    if not all([patient_identifier, module_id]):
        return jsonify({'error': 'Missing required parameters'}), 400

    # Get module checklist
    module = Module.query.get_or_404(module_id)
    checklist_items = {item.code: item for item in module.items}
    codes = list(checklist_items.keys())

    # Initialize results
    results = {code: {
        'code': code,
        'display': checklist_items[code].display,
        'required': checklist_items[code].required,
        'found': False,
        'value': None,
        'source': None
    } for code in codes}

    # Search serverA first (with encounter filter)
    observations = search_fhir_server(FHIR_SERVERS['serverA'], patient_identifier, encounter_id, codes)
    for obs in observations:
        code = obs['resource']['code']['coding'][0]['code']
        if code in results and not results[code]['found']:
            results[code].update({
                'found': True,
                'value': obs['resource'].get('valueQuantity', {}).get('value') or
                         obs['resource'].get('valueCodeableConcept', {}).get('display', 'N/A'),
                'source': 'serverA'
            })

    # For missing codes, search other servers in parallel
    missing_codes = [code for code in codes if not results[code]['found']]
    if missing_codes:
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
            future_to_server = {
                executor.submit(search_fhir_server, FHIR_SERVERS['serverB'], patient_identifier, None, missing_codes): 'serverB',
                executor.submit(search_fhir_server, FHIR_SERVERS['serverC'], patient_identifier, None, missing_codes): 'serverC'
            }

            for future in concurrent.futures.as_completed(future_to_server):
                server_name = future_to_server[future]
                observations = future.result()
                
                for obs in observations:
                    code = obs['resource']['code']['coding'][0]['code']
                    if code in results and not results[code]['found']:
                        results[code].update({
                            'found': True,
                            'value': obs['resource'].get('valueQuantity', {}).get('value') or
                                     obs['resource'].get('valueCodeableConcept', {}).get('display', 'N/A'),
                            'source': server_name
                        })

    return render_template(
        'results.html',
        results=results.values(),
        patient_identifier=patient_identifier,
        encounter_id=encounter_id,
        module=module
    )

@app.route('/sync', methods=['POST'])
def sync_data():
    patient_identifier = request.form.get('patient_identifier')
    encounter_id = request.form.get('encounter_id')
    module_id = request.form.get('module_id')

    if not all([patient_identifier, module_id]):
        return jsonify({'error': 'Missing required parameters'}), 400

    # Get module checklist
    module = Module.query.get_or_404(module_id)
    checklist_items = {item.code: item for item in module.items}
    codes = list(checklist_items.keys())

    # Initialize results
    results = {code: {
        'code': code,
        'display': checklist_items[code].display,
        'required': checklist_items[code].required,
        'found': False,
        'value': None,
        'source': None,
        'synced': False
    } for code in codes}

    # First check serverA
    observations = search_fhir_server(FHIR_SERVERS['serverA'], patient_identifier, encounter_id, codes)
    for obs in observations:
        code = obs['resource']['code']['coding'][0]['code']
        if code in results:
            results[code].update({
                'found': True,
                'value': obs['resource'].get('valueQuantity', {}).get('value') or
                         obs['resource'].get('valueCodeableConcept', {}).get('display', 'N/A'),
                'source': 'serverA'
            })

    # For missing codes, search and sync from other servers
    missing_codes = [code for code in codes if not results[code]['found']]
    if missing_codes:
        # Search serverB and serverC in parallel
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
            future_to_server = {
                executor.submit(search_fhir_server, FHIR_SERVERS['serverB'], patient_identifier, None, missing_codes): 'serverB',
                executor.submit(search_fhir_server, FHIR_SERVERS['serverC'], patient_identifier, None, missing_codes): 'serverC'
            }

            for future in concurrent.futures.as_completed(future_to_server):
                server_name = future_to_server[future]
                observations = future.result()
                
                for obs in observations:
                    code = obs['resource']['code']['coding'][0]['code']
                    if code in results and not results[code]['found']:
                        # Try to sync to serverA
                        synced = post_observation_to_serverA(obs, patient_identifier, encounter_id)
                        
                        results[code].update({
                            'found': True,
                            'value': obs['resource'].get('valueQuantity', {}).get('value') or
                                    obs['resource'].get('valueCodeableConcept', {}).get('display', 'N/A'),
                            'source': f"{server_name} → serverA" if synced else server_name,
                            'synced': synced
                        })

    return render_template(
        'sync_results.html',
        results=results.values(),
        patient_identifier=patient_identifier,
        encounter_id=encounter_id,
        module=module
    )

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8002) 