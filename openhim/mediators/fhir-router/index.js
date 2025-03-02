const express = require('express');
const axios = require('axios');
const app = express();
const port = 3000;

// Middleware to parse JSON bodies
app.use(express.json());

// Configuration for FHIR servers
const fhirServers = {
  maternal: 'http://maternal-fhir:8080/fhir',
  fetal: 'http://fetal-fhir:8080/fhir',
  obstetric: 'http://obstetric-fhir:8080/fhir'
};

// Route handler for all FHIR requests
app.all('/:server/*', async (req, res) => {
  const server = req.params.server;
  const baseUrl = fhirServers[server];
  
  if (!baseUrl) {
    return res.status(404).json({ error: 'Server not found' });
  }

  const path = req.params[0];
  const url = `${baseUrl}/${path}`;

  try {
    const response = await axios({
      method: req.method,
      url: url,
      data: req.body,
      headers: {
        'Content-Type': 'application/fhir+json',
        ...req.headers
      },
      validateStatus: false
    });

    res.status(response.status).send(response.data);
  } catch (error) {
    console.error('Error forwarding request:', error);
    res.status(500).json({ error: 'Internal Server Error' });
  }
});

app.listen(port, () => {
  console.log(`FHIR Router Mediator listening at http://localhost:${port}`);
}); 