// // import { getCookie } from "./cookies";
// // import { jwtDecode } from "jwt-decode";

// // // Get the base URL from environment variable
// // const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;

// // // Helper function to get full URL
// // function getFullUrl(endpoint) {
// //   const cleanEndpoint = normalizeEndpoint(endpoint);
// //   // Remove trailing slash from base URL if present, add it back properly
// //   const base = API_BASE_URL.endsWith('/') 
// //     ? API_BASE_URL.slice(0, -1) 
// //     : API_BASE_URL;
  
// //   // If base already includes '/api', don't add it again
// //   if (base.includes('/api')) {
// //     return `${base}/${cleanEndpoint}/`;
// //   }
  
// //   return `${base}/${cleanEndpoint}/`;
// // }

// // function isTokenExpired(token) {
// //   try {
// //     const decoded = jwtDecode(token);
// //     const now = Date.now() / 1000;
// //     return decoded.exp < now;
// //   } catch (e) {
// //     return true;
// //   }
// // }

// // function normalizeEndpoint(endpoint) {
// //   return endpoint.replace(/\/+$/, "");
// // }

// // export async function api(endpoint, method, body = null, token = null) {
// //   try {
// //     console.log("API Base URL:", API_BASE_URL);
// //     const url = getFullUrl(endpoint);
// //     console.log("Making request to:", url);
    
// //     const isFileUpload = body instanceof FormData;
// //     const options = {
// //       method: method,
// //       headers: {},
// //       credentials: "include",
// //     };
    
// //     if (!isFileUpload) {
// //       options.headers["Content-Type"] = "application/json";
// //     }
    
// //     // Attach token if valid
// //     if (token && !isTokenExpired(token)) {
// //       console.log("Access token exists");
// //       options.headers["Authorization"] = `Bearer ${token}`;
// //     } else {
// //       // Only refresh if endpoint is not login/signup/csrf-token
// //       if (!["login", "csrf-token", "user-account-delete", "register", "signup", "logout"].includes(normalizeEndpoint(endpoint))) {
// //         const newAccessToken = await refreshAccessToken("refresh-token", "GET");
// //         if (newAccessToken.status && newAccessToken.access) {
// //           options.headers["Authorization"] = `Bearer ${newAccessToken.access}`;
// //         } else {
// //           console.error("Failed to refresh access token");
// //           return { error: "Failed to refresh access token" };
// //         }
// //       }
// //     }

// //     // Add CSRF token for non-GET requests
// //     if (method !== "GET") {
// //       const csrfToken = getCookie("csrftoken");
// //       if (csrfToken) {
// //         options.headers["X-CSRFToken"] = csrfToken;
// //       }
// //     }

// //     // Attach body if present
// //     if (body !== null) {
// //       if (isFileUpload) {
// //         options.body = body;
// //         console.log("Attaching raw FormData body for file upload.");
// //       } else {
// //         options.body = JSON.stringify(body);
// //         console.log("Attaching stringified JSON body.");
// //       }
// //     }

// //     const response = await fetch(url, options);

// //     if (response.ok) {
// //       const result = await response.json();
// //       return result;
// //     } else {
// //       return { error: `Error: ${response.status} ${response.statusText}` };
// //     }
// //   } catch (error) {
// //     console.error("Error:", error);
// //     alert("An error occurred. Please try again.");
// //     return { error: error.message };
// //   }
// // }

// // async function refreshAccessToken(endpoint, method, body = null) {
// //   try {
// //     const csrfToken = getCookie("csrftoken");
// //     const url = getFullUrl(endpoint);

// //     const options = {
// //       method: method,
// //       headers: {
// //         "Content-Type": "application/json",
// //       },
// //       credentials: "include",
// //     };

// //     if (method !== "GET" && csrfToken) {
// //       options.headers["X-CSRFToken"] = csrfToken;
// //     }
// //     if (body !== null) {
// //       options.body = JSON.stringify(body);
// //     }

// //     const response = await fetch(url, options);

// //     if (response.ok) {
// //       const result = await response.json();
// //       return result;
// //     } else {
// //       return { error: `Error: ${response.status} ${response.statusText}` };
// //     }
// //   } catch (error) {
// //     console.error("Error:", error);
// //     alert("An error occurred. Please try again.");
// //     return { error: error.message };
// //   }
// // }

// import { getCookie } from "./cookies";
// import { jwtDecode } from "jwt-decode";

// // Get the base URL from environment variable
// const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;

// // Helper function to get full URL
// function getFullUrl(endpoint) {
//   const cleanEndpoint = normalizeEndpoint(endpoint);
//   const base = API_BASE_URL.endsWith('/') 
//     ? API_BASE_URL.slice(0, -1) 
//     : API_BASE_URL;
  
//   if (base.includes('/api')) {
//     return `${base}/${cleanEndpoint}/`;
//   }
  
//   return `${base}/${cleanEndpoint}/`;
// }

// function isTokenExpired(token) {
//   try {
//     const decoded = jwtDecode(token);
//     const now = Date.now() / 1000;
//     return decoded.exp < now;
//   } catch (e) {
//     return true;
//   }
// }

// function normalizeEndpoint(endpoint) {
//   return endpoint.replace(/\/+$/, "");
// }

// // ✅ NEW: Function to get token from localStorage or cookies
// async function getAccessToken() {
//   // Try localStorage first (backward compatibility)
//   const localToken = localStorage.getItem('accessToken');
//   if (localToken && !isTokenExpired(localToken)) {
//     return localToken;
//   }
  
//   // If no valid token in localStorage, try to refresh
//   try {
//     const response = await fetch(getFullUrl('refresh-token'), {
//       method: 'GET',
//       credentials: 'include',
//     });
    
//     if (response.ok) {
//       const data = await response.json();
//       if (data.access) {
//         localStorage.setItem('accessToken', data.access);
//         return data.access;
//       }
//     }
//   } catch (error) {
//     console.error('Failed to refresh token:', error);
//   }
  
//   return null;
// }

// export async function api(endpoint, method, body = null, token = null) {
//   try {
//     console.log("API Base URL:", API_BASE_URL);
//     const url = getFullUrl(endpoint);
//     console.log("Making request to:", url);
    
//     const isFileUpload = body instanceof FormData;
//     const options = {
//       method: method,
//       headers: {},
//       credentials: "include",  // ✅ ALWAYS include cookies
//     };
    
//     if (!isFileUpload) {
//       options.headers["Content-Type"] = "application/json";
//     }
    
//     // ✅ MODIFIED: Get token automatically if not provided
//     let accessToken = token;
//     if (!accessToken) {
//       accessToken = await getAccessToken();
//     }
    
//     // Attach token if valid
//     if (accessToken && !isTokenExpired(accessToken)) {
//       console.log("Access token exists");
//       options.headers["Authorization"] = `Bearer ${accessToken}`;
//     } else {
//       // Only refresh if endpoint is not login/signup/csrf-token
//       const excludedEndpoints = ["login", "csrf-token", "user-account-delete", "register", "signup", "logout"];
//       if (!excludedEndpoints.includes(normalizeEndpoint(endpoint))) {
//         try {
//           // Try to refresh token via cookies
//           const refreshResponse = await fetch(getFullUrl('refresh-token'), {
//             method: 'GET',
//             credentials: 'include',
//           });
          
//           if (refreshResponse.ok) {
//             const data = await refreshResponse.json();
//             if (data.access) {
//               localStorage.setItem('accessToken', data.access);
//               options.headers["Authorization"] = `Bearer ${data.access}`;
//             } else {
//               console.error("No access token in refresh response");
//               return { error: "Authentication failed" };
//             }
//           } else {
//             console.error("Refresh token failed");
//             return { error: "Authentication failed" };
//           }
//         } catch (error) {
//           console.error("Token refresh error:", error);
//           return { error: "Authentication failed" };
//         }
//       }
//     }

//     // Add CSRF token for non-GET requests
//     if (method !== "GET") {
//       const csrfToken = getCookie("csrftoken");
//       if (csrfToken) {
//         options.headers["X-CSRFToken"] = csrfToken;
//       }
//     }

//     // Attach body if present
//     if (body !== null) {
//       if (isFileUpload) {
//         options.body = body;
//         console.log("Attaching raw FormData body for file upload.");
//       } else {
//         options.body = JSON.stringify(body);
//         console.log("Attaching stringified JSON body.");
//       }
//     }

//     const response = await fetch(url, options);

//     if (response.ok) {
//       const result = await response.json();
//       return result;
//     } else {
//       // If unauthorized, clear invalid token
//       if (response.status === 401) {
//         localStorage.removeItem('accessToken');
//       }
//       return { error: `Error: ${response.status} ${response.statusText}` };
//     }
//   } catch (error) {
//     console.error("Error:", error);
//     return { error: error.message };
//   }
// }

// // ✅ UPDATED: refreshAccessToken function (simpler now)
// async function refreshAccessToken() {
//   try {
//     const response = await fetch(getFullUrl('refresh-token'), {
//       method: 'GET',
//       credentials: 'include',
//     });

//     if (response.ok) {
//       const result = await response.json();
//       if (result.access) {
//         localStorage.setItem('accessToken', result.access);
//       }
//       return result;
//     } else {
//       return { error: `Error: ${response.status} ${response.statusText}` };
//     }
//   } catch (error) {
//     console.error("Error:", error);
//     return { error: error.message };
//   }
// }

// // ✅ Export the refresh function
// export { refreshAccessToken };

import { getCookie } from "./cookies";
import { jwtDecode } from "jwt-decode";

// ✅ Use environment base URL if available, fallback to localhost
const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL || "http://localhost:8000/api";

// Normalize endpoint
function normalizeEndpoint(endpoint) {
  return endpoint.replace(/\/+$/, "");
}

// Build full URL safely
function getFullUrl(endpoint) {
  const cleanEndpoint = normalizeEndpoint(endpoint);

  const base = API_BASE_URL.endsWith("/")
    ? API_BASE_URL.slice(0, -1)
    : API_BASE_URL;

  // Avoid double /api/api
  if (base.includes("/api")) {
    return `${base}/${cleanEndpoint}/`;
  }

  return `${base}/api/${cleanEndpoint}/`;
}

// Check token expiry
function isTokenExpired(token) {
  try {
    const decoded = jwtDecode(token);
    const now = Date.now() / 1000;
    return decoded.exp < now;
  } catch {
    return true;
  }
}

// Force logout (from first code)
function forceLogout() {
  localStorage.removeItem("accessToken");
  window.location.href = "/";
}

// ✅ Get access token (merged logic)
async function getAccessToken() {
  const localToken = localStorage.getItem("accessToken");

  if (localToken && !isTokenExpired(localToken)) {
    return localToken;
  }

  // Try refreshing using cookies
  try {
    const response = await fetch(getFullUrl("refresh-token"), {
      method: "GET",
      credentials: "include",
    });

    if (response.ok) {
      const data = await response.json();
      if (data.access) {
        localStorage.setItem("accessToken", data.access);
        return data.access;
      }
    }
  } catch (error) {
    console.error("Failed to refresh token:", error);
  }

  return null;
}

// ✅ Main API function
export async function api(endpoint, method, body = null, token = null) {
  try {
    const url = getFullUrl(endpoint);

    const isFileUpload = body instanceof FormData;

    const options = {
      method,
      headers: {},
      credentials: "include", // Always include cookies
    };

    if (!isFileUpload) {
      options.headers["Content-Type"] = "application/json";
    }

    // Determine token source
    let accessToken = token;

    if (!accessToken) {
      accessToken = await getAccessToken();
    }

    const excludedEndpoints = [
      "login",
      "csrf-token",
      "register",
      "signup",
      "logout",
      "user-account-delete",
    ];

    // Attach Authorization header
    if (accessToken && !isTokenExpired(accessToken)) {
      options.headers["Authorization"] = `Bearer ${accessToken}`;
    } else if (!excludedEndpoints.includes(normalizeEndpoint(endpoint))) {
      // Try one more refresh attempt
      const refreshed = await refreshAccessToken();

      if (refreshed?.access) {
        options.headers["Authorization"] = `Bearer ${refreshed.access}`;
      } else {
        forceLogout();
        return { error: "Authentication failed" };
      }
    }

    // CSRF for non-GET
    if (method !== "GET") {
      const csrfToken = getCookie("csrftoken");
      if (csrfToken) {
        options.headers["X-CSRFToken"] = csrfToken;
      }
    }

    // Attach body
    if (body !== null) {
      options.body = isFileUpload ? body : JSON.stringify(body);
    }

    const response = await fetch(url, options);

    if (response.ok) {
      return await response.json();
    } else {
      if (response.status === 401) {
        forceLogout();
      }
      return {
        error: `Error: ${response.status} ${response.statusText}`,
      };
    }
  } catch (error) {
    console.error("API Error:", error);
    return { error: "Network error" };
  }
}

// ✅ Unified refresh function
async function refreshAccessToken() {
  try {
    const response = await fetch(getFullUrl("refresh-token"), {
      method: "GET",
      credentials: "include",
    });

    if (response.ok) {
      const result = await response.json();

      if (result.access) {
        localStorage.setItem("accessToken", result.access);
      }

      return result;
    } else {
      return {
        error: `Error: ${response.status} ${response.statusText}`,
      };
    }
  } catch (error) {
    console.error("Refresh Error:", error);
    return { error: error.message };
  }
}

// Export refresh explicitly
export { refreshAccessToken };