$(document).ready(() => {
      

    // Generate schema for services on the current page
    // Remove any existing schema script
    function removeExistingSchema() {
      const serviceSchemaScript = document.getElementById('service-schema');
      if (serviceSchemaScript) {
        serviceSchemaScript.remove();
      }
    }

	  function generateSchema() {

      // Collect the services currently visible in the #list-services container
      const services = document.querySelectorAll('.row-items');
      const serviceList = [];
    
      services.forEach((service, index) => {
        // Check if the service is visible
        if (getComputedStyle(service).display !== 'none') {
          const serviceData = {
            "@type": "ListItem",
            "position": serviceList.length + 1,
            "item": {
              "@type": "Service",
              "provider": {
                "@type": "Organization",
                "name": "CSC Locator",
                "url": "https://cscindia.info/",
                "logo": "https://cscindia.info/images/logo.png"
              },
              "name": service.getAttribute('data-name'),
              "description": "Explore a variety of services offered by Common Service Centers (CSCs) across different locations. Find the best services tailored to your needs, including digital and government services."
            }
          };
          serviceList.push(serviceData);
        }
      });

      // Create the JSON-LD object
      const schemaData = {
        "@context": "http://schema.org",
        "@type": "ItemList",
        "itemListElement": serviceList
      };
  
        removeExistingSchema();
    
        // Inject new JSON-LD schema
        const script = document.createElement('script');
        script.type = 'application/ld+json';
        script.id = 'service-schema';
        script.textContent = JSON.stringify(schemaData);
        document.head.appendChild(script);
      }
  
      // Call the function when the page loads or when pagination is applied
      generateSchema();
      
      // Optional: Hook this function to pagination changes if applicable
      $(document).on('click', '.next-page, .prev-page, .upcoming-page, .earlier-page', function() {
        removeExistingSchema();
        generateSchema();
      });
    })