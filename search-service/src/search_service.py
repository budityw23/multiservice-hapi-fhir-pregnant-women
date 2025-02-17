from fastapi import FastAPI, HTTPException, Request
from typing import Optional, Dict, Any
import requests
from config import FHIR_SERVERS
from urllib.parse import urlencode

app = FastAPI()

async def search_with_params(resource_type: str, search_params: Dict[str, str]) -> Optional[Dict[Any, Any]]:
    """
    Search for resources across all FHIR servers using search parameters
    """
    for server in sorted(FHIR_SERVERS, key=lambda x: x['priority']):
        try:
            # Construct the search URL with parameters
            base_url = f"{server['url']}/{resource_type}"
            if search_params:
                query_string = urlencode(search_params)
                url = f"{base_url}?{query_string}"
            else:
                url = base_url

            response = requests.get(
                url,
                headers={"Accept": "application/fhir+json"}
            )
            
            if response.status_code == 200:
                result = response.json()
                # Check if we got any matches
                if result.get('total', 0) > 0:
                    # Add source server information
                    for entry in result.get('entry', []):
                        if 'resource' in entry:
                            entry['resource']['meta'] = entry['resource'].get('meta', {})
                            entry['resource']['meta']['source'] = server['name']
                    return result
                
        except requests.RequestException as e:
            print(f"Error querying {server['name']}: {str(e)}")
            continue
            
    return None

@app.get("/fhir/{resource_type}")
async def search_resources(request: Request, resource_type: str):
    """
    Endpoint to search for resources with parameters across all FHIR servers
    """
    # Get all query parameters from the request
    search_params = dict(request.query_params)
    
    result = await search_with_params(resource_type, search_params)
    
    if result and result.get('total', 0) > 0:
        return result
    else:
        raise HTTPException(
            status_code=404,
            detail=f"No {resource_type} resources found matching the criteria"
        )

@app.get("/fhir/{resource_type}/{id}")
async def get_resource(resource_type: str, id: str):
    """
    Endpoint to search for a specific resource by ID across all FHIR servers
    """
    result = await search_with_params(resource_type, {'_id': id})
    
    if result and result.get('total', 0) > 0:
        return result
    else:
        raise HTTPException(
            status_code=404,
            detail=f"Resource {resource_type}/{id} not found in any server"
        )

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}