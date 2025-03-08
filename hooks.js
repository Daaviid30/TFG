(function() {
    // This function send the information to the main script
    function apiCallDetected(apiCall) {
      // Check if the function in the main script is defined
        if (typeof window.pyNotify !== "undefined") {
            // Send the information
            window.pyNotify(apiCall);
        }
    }

    // Define property method allows us to force a change in the API methods
    Object.defineProperty(navigator, "geolocation", {
        // Proxy definition for capture all navigator.geolocation events
        value: new Proxy(navigator.geolocation, {
          // The get method intercepts the API calls
          get(target, prop, receiver) {
            // Intercept calls to navigator.geolocation
            if (typeof target[prop] === "function") {
              return function(...args) {
                apiCallDetected(`navigator.geolocation.${prop}`);
                // return the API call for a normal execution
                return Reflect.apply(target[prop], target, args);
              };
            }
            return Reflect.get(target, prop, receiver);
          }
        }),
        // Allows future modifications on navigator.geolocation
        configurable: true  
      });
      
      

})();
