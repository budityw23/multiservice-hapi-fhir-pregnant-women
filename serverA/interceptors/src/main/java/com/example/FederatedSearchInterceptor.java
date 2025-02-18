package com.example;

import ca.uhn.fhir.context.FhirContext;
import ca.uhn.fhir.interceptor.api.Hook;
import ca.uhn.fhir.interceptor.api.Interceptor;
import ca.uhn.fhir.interceptor.api.Pointcut;
import ca.uhn.fhir.rest.api.server.RequestDetails;
import ca.uhn.fhir.rest.client.api.IGenericClient;
import ca.uhn.fhir.rest.gclient.StringClientParam;
import org.hl7.fhir.r4.model.Bundle;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import jakarta.annotation.PostConstruct;

@Interceptor
public class FederatedSearchInterceptor {
    private static final Logger logger = LoggerFactory.getLogger(FederatedSearchInterceptor.class);
    private static final FhirContext ctx = FhirContext.forR4();

    @PostConstruct
    public void initialize() {
        logger.info("FederatedSearchInterceptor is being initialized");
    }

    @Hook(Pointcut.SERVER_INCOMING_REQUEST_PRE_HANDLED)
    public boolean preHandleResource(RequestDetails requestDetails) {
        logger.info("Intercepting request: {} {}", requestDetails.getRequestType(), requestDetails.getRequestPath());
        
        if (!"Patient".equals(requestDetails.getResourceName()) || 
            !"GET".equals(requestDetails.getRequestType()) || 
            !requestDetails.getRequestPath().startsWith("/Patient")) {
            return true;
        }

        try {
            // Create FHIR clients
            IGenericClient clientB = ctx.newRestfulGenericClient("http://fetal-fhir:8080/fhir");
            IGenericClient clientC = ctx.newRestfulGenericClient("http://obstetric-fhir:8080/fhir");

            logger.info("Created FHIR clients for Server B and C");

            // Get search parameters
            String[] nameParams = requestDetails.getParameters().get("name");
            if (nameParams != null && nameParams.length > 0) {
                String nameParam = nameParams[0];
                logger.info("Searching for name: {}", nameParam);

                // Search Server B
                Bundle resultB = clientB.search()
                    .forResource("Patient")
                    .where(new StringClientParam("name").matches().value(nameParam))
                    .returnBundle(Bundle.class)
                    .execute();

                logger.info("Server B results: {}", resultB.getTotal());

                // Search Server C
                Bundle resultC = clientC.search()
                    .forResource("Patient")
                    .where(new StringClientParam("name").matches().value(nameParam))
                    .returnBundle(Bundle.class)
                    .execute();

                logger.info("Server C results: {}", resultC.getTotal());

                // Store results for response phase
                requestDetails.setAttribute("server_b_results", resultB);
                requestDetails.setAttribute("server_c_results", resultC);
            }

        } catch (Exception e) {
            logger.error("Error in federated search: ", e);
        }

        return true;
    }

    @Hook(Pointcut.SERVER_OUTGOING_RESPONSE)
    public void processResponse(RequestDetails requestDetails, ca.uhn.fhir.rest.api.server.ResponseDetails responseDetails) {
        if (!"Patient".equals(requestDetails.getResourceName()) || 
            !"GET".equals(requestDetails.getRequestType())) {
            return;
        }

        try {
            Bundle responseBundle = (Bundle) responseDetails.getResponseResource();
            Bundle serverBResults = (Bundle) requestDetails.getAttribute("server_b_results");
            Bundle serverCResults = (Bundle) requestDetails.getAttribute("server_c_results");

            if (responseBundle != null) {
                Bundle combinedBundle = new Bundle();
                combinedBundle.setType(Bundle.BundleType.SEARCHSET);

                // Add local results
                if (responseBundle.getEntry() != null) {
                    combinedBundle.getEntry().addAll(responseBundle.getEntry());
                }

                // Add Server B results
                if (serverBResults != null && serverBResults.getEntry() != null) {
                    combinedBundle.getEntry().addAll(serverBResults.getEntry());
                }

                // Add Server C results
                if (serverCResults != null && serverCResults.getEntry() != null) {
                    combinedBundle.getEntry().addAll(serverCResults.getEntry());
                }

                combinedBundle.setTotal(combinedBundle.getEntry().size());
                responseDetails.setResponseResource(combinedBundle);

                logger.info("Combined results total: {}", combinedBundle.getTotal());
            }
        } catch (Exception e) {
            logger.error("Error combining results: ", e);
        }
    }
}