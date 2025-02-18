package com.example;

import ca.uhn.fhir.interceptor.api.Hook;
import ca.uhn.fhir.interceptor.api.Interceptor;
import ca.uhn.fhir.interceptor.api.Pointcut;
import ca.uhn.fhir.rest.api.server.RequestDetails;
import ca.uhn.fhir.rest.client.api.IGenericClient;
import ca.uhn.fhir.context.FhirContext;
import ca.uhn.fhir.rest.gclient.ICriterion;
import ca.uhn.fhir.rest.gclient.StringClientParam;

import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;

import org.hl7.fhir.r4.model.Bundle;
import org.apache.commons.lang3.StringUtils;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.concurrent.CompletableFuture;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;

@Interceptor
public class FederatedSearchInterceptor {
    private static final Logger logger = LoggerFactory.getLogger(FederatedSearchInterceptor.class);
    private static final FhirContext ctx = FhirContext.forR4();
    private final ExecutorService executorService = Executors.newFixedThreadPool(2);
    
    private static final String SERVER_B_URL = "http://fetal-fhir:8080/fhir";
    private static final String SERVER_C_URL = "http://obstetric-fhir:8080/fhir";

    @Hook(Pointcut.SERVER_INCOMING_REQUEST_POST_PROCESSED)
    public boolean interceptSearch(RequestDetails requestDetails, HttpServletRequest servletRequest, HttpServletResponse servletResponse) {
        String resourceType = requestDetails.getResourceName();
        
        // Only intercept search operations
        if (!"GET".equals(requestDetails.getRequestType()) || 
            StringUtils.isEmpty(resourceType) || 
            requestDetails.getRequestPath().contains("_history")) {
            return true;
        }

        try {
            // Get search parameters
            Map<String, String[]> searchParams = requestDetails.getParameters();
            
            // Create FHIR clients for other servers
            IGenericClient clientB = ctx.newRestfulGenericClient(SERVER_B_URL);
            IGenericClient clientC = ctx.newRestfulGenericClient(SERVER_C_URL);

            // Execute searches in parallel
            CompletableFuture<Bundle> searchB = CompletableFuture.supplyAsync(() -> 
                executeSearch(clientB, resourceType, searchParams), executorService);
            
            CompletableFuture<Bundle> searchC = CompletableFuture.supplyAsync(() -> 
                executeSearch(clientC, resourceType, searchParams), executorService);

            // Wait for all searches to complete
            CompletableFuture.allOf(searchB, searchC).join();

            // Combine results
            Bundle localBundle = (Bundle) requestDetails.getUserData().get("bundle");
            Bundle combinedBundle = combineResults(localBundle, searchB.get(), searchC.get());

            // Set the combined results
            requestDetails.getUserData().put("bundle", combinedBundle);

            return true;
        } catch (Exception e) {
            logger.error("Error in federated search: ", e);
            return true; // Continue with local results only
        }
    }

    private Bundle executeSearch(IGenericClient client, String resourceType, Map<String, String[]> searchParams) {
        try {
            // Build search query
            var search = client.search().forResource(resourceType);
            
            // Add search parameters
            searchParams.forEach((key, values) -> {
                if (values.length > 0) {
                    // Create a proper criterion for the search
                    ICriterion<?> criterion = new StringClientParam(key).matches().value(values[0]);
                    search.where(criterion);
                }
            });
            
            return search.returnBundle(Bundle.class).execute();
        } catch (Exception e) {
            logger.error("Error searching external server: ", e);
            return new Bundle();
        }
    }

    private Bundle combineResults(Bundle... bundles) {
        Bundle combinedBundle = new Bundle();
        combinedBundle.setType(Bundle.BundleType.SEARCHSET);
        
        List<Bundle.BundleEntryComponent> allEntries = new ArrayList<>();
        
        for (Bundle bundle : bundles) {
            if (bundle != null && bundle.getEntry() != null) {
                allEntries.addAll(bundle.getEntry());
            }
        }
        
        combinedBundle.setEntry(allEntries);
        combinedBundle.setTotal(allEntries.size());
        
        return combinedBundle;
    }
}