const express = require('express');
const medUtils = require('openhim-mediator-utils');
const axios = require('axios');

const app = express();
const port = 3000;

const FHIR_SERVERS = [
  { name: 'maternal', url: 'http://maternal-fhir:8080/fhir' },
  { name: 'fetal', url: 'http://fetal-fhir:8080/fhir' },
  { name: 'obstetric', url: 'http://obstetric-fhir:8080/fhir' }
];

// Mediator config
const mediatorConfig = {
  urn: 'urn:mediator:fhir-search',
  version: '1.0.0',
  name: 'FHIR Search Mediator',
  description: 'A mediator for searching across multiple FHIR servers',
  defaultConfig: {},
  endpoints: [
    {
      name: 'FHIR Search',
      host: 'fhir-search-mediator',
      port: port,
      path: '/fhir-search',
      type: 'http'
    }
  ]
};

async function searchFHIR(resourceType, searchParams) {
  const results = [];
  
  for (const server of FHIR_SERVERS) {
    try {
      const url = `${server.url}/${resourceType}?${searchParams}`;
      console.log(`Searching ${server.name} at URL: ${url}`);
      
      const response = await axios.get(url);
      
      if (response.data && response.data.entry) {
        response.data.entry.forEach(entry => {
          if (entry.resource) {
            entry.resource.source = server.name;
          }
        });
        results.push(...response.data.entry);
      }
    } catch (error) {
      console.error(`Error searching ${server.name}: ${error.message}`);
    }
  }
  
  return {
    resourceType: 'Bundle',
    type: 'searchset',
    total: results.length,
    entry: results
  };
}

app.get('/fhir-search/:resourceType', async (req, res) => {
  const resourceType = req.params.resourceType;
  const searchParams = new URLSearchParams(req.query).toString();
  
  try {
    const results = await searchFHIR(resourceType, searchParams);
    
    // Build orchestrations
    const orchestrations = FHIR_SERVERS.map(server => ({
      name: `search-${server.name}`,
      request: {
        path: `/${resourceType}?${searchParams}`,
        headers: {},
        querystring: searchParams,
        body: '',
        method: 'GET',
        timestamp: new Date()
      },
      response: {
        status: 200,
        body: JSON.stringify(results),
        timestamp: new Date()
      }
    }));

    // Construct return object
    const returnObject = {
      'x-mediator-urn': mediatorConfig.urn,
      status: 'Successful',
      response: {
        status: 200,
        headers: {
          'content-type': 'application/json'
        },
        body: JSON.stringify(results),
        timestamp: new Date()
      },
      orchestrations: orchestrations
    };

    res.json(returnObject);
  } catch (error) {
    console.error('Search error:', error);
    res.status(500).json({ error: error.message });
  }
});

app.get('/health', (req, res) => {
  res.json({ status: 'healthy' });
});

// Start the server
app.listen(port, () => {
  console.log(`Mediator listening on port ${port}`);
  
  const mediatorRegisterConfig = {
    username: 'root@openhim.org',
    password: 'openhim-password',
    apiURL: 'http://openhim-core:8080',
    trustSelfSigned: true,
    force: true
  };

  // Register mediator
  medUtils.registerMediator(mediatorRegisterConfig, mediatorConfig, (err) => {
    if (err) {
      console.error('Failed to register mediator:', err);
      // Continue running even if registration fails
    } else {
      console.log('Successfully registered mediator!');

      // Setup heartbeat
      const configEmitter = medUtils.activateHeartbeat(mediatorRegisterConfig);
      
      configEmitter.on('config', (newConfig) => {
        console.log('Received updated config:', newConfig);
        // Handle config updates
      });
    }
  });
});