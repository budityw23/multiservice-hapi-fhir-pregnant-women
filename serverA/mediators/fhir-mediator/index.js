const express = require('express');
const axios = require('axios');
const app = express();
const port = 3000;

// Middleware to parse JSON bodies
app.use(express.json());

// Forward all FHIR requests to the HAPI FHIR server
app.all('/fhir/*', async (req, res) => {
  try {
    const fhirResponse = await axios({
      method: req.method,
      url: `http://maternal-fhir:8080${req.url}`,
      data: req.body,
      headers: req.headers,
      validateStatus: false
    });

    res.status(fhirResponse.status).send(fhirResponse.data);
  } catch (error) {
    console.error('Error forwarding request:', error);
    res.status(500).send({ error: 'Internal Server Error' });
  }
});

app.listen(port, () => {
  console.log(`FHIR Mediator listening at http://localhost:${port}`);
}); 