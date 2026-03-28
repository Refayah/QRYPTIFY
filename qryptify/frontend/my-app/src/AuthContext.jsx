// import React, { createContext, useState, useEffect } from 'react';

// export const AuthContext = createContext();

// export function AuthProvider({ children }) {
//   const [accessToken, setAccessToken] = useState(() => {
//     // Initialize from localStorage (backward compatibility)
//     return localStorage.getItem('accessToken') || null;
//   });

//   const [isAuthenticated, setIsAuthenticated] = useState(false);

//   // Function to check auth status by calling an endpoint
//   const checkAuthStatus = async () => {
//     try {
//       // This endpoint should verify cookies and return user info
//       const response = await fetch('/api/user-details/', {
//         credentials: 'include',
//       });
      
//       if (response.ok) {
//         setIsAuthenticated(true);
//         return true;
//       }
//     } catch (error) {
//       console.error('Auth check failed:', error);
//     }
    
//     setIsAuthenticated(false);
//     return false;
//   };

//   // Check auth on mount
//   useEffect(() => {
//     checkAuthStatus();
//   }, []);

//   // ✅ NEW: Get token from cookies via backend endpoint
//   const getTokenFromCookies = async () => {
//     try {
//       const response = await fetch('/api/get-access-token/', {
//         credentials: 'include',
//       });
//       if (response.ok) {
//         const data = await response.json();
//         if (data.access) {
//           setAccessToken(data.access);
//           localStorage.setItem('accessToken', data.access);
//           return data.access;
//         }
//       }
//     } catch (error) {
//       console.error('Failed to get token from cookies:', error);
//     }
//     return null;
//   };

//   // Persist token to localStorage (backward compatibility)
//   useEffect(() => {
//     if (accessToken) {
//       localStorage.setItem('accessToken', accessToken);
//     } else {
//       localStorage.removeItem('accessToken');
//     }
//   }, [accessToken]);

//   // Function to logout (clear both frontend and backend)
//   const logout = async () => {
//     try {
//       await fetch('/api/logout/', {
//         credentials: 'include',
//       });
//     } catch (error) {
//       console.error('Logout error:', error);
//     }
//     setAccessToken(null);
//     localStorage.removeItem('accessToken');
//     setIsAuthenticated(false);
//   };

//   return (
//     <AuthContext.Provider value={{ 
//       accessToken, 
//       setAccessToken,
//       isAuthenticated,
//       setIsAuthenticated,
//       checkAuthStatus,
//       getTokenFromCookies,
//       logout
//     }}>
//       {children}
//     </AuthContext.Provider>
//   );
// }

import React, { createContext, useState, useEffect } from "react";
import { api } from "./components/api";

export const AuthContext = createContext();

export function AuthProvider({ children }) {
  // ✅ Initialize token from localStorage (backward compatibility)
  const [accessToken, setAccessToken] = useState(() => {
    return localStorage.getItem("accessToken") || null;
  });

  const [user, setUser] = useState(null);
  const [authLoading, setAuthLoading] = useState(true);
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  // ✅ Persist token
  useEffect(() => {
    if (accessToken) {
      localStorage.setItem("accessToken", accessToken);
    } else {
      localStorage.removeItem("accessToken");
    }
  }, [accessToken]);

  // ✅ Validate session using token (from first code)
  useEffect(() => {
    const validateSession = async () => {
      if (!accessToken) {
        setAuthLoading(false);
        setIsAuthenticated(false);
        return;
      }

      try {
        const res = await api("user-details", "GET", null, accessToken);

        if (res?.status) {
          setUser(res.user);
          setIsAuthenticated(true);
        } else {
          await logout();
        }
      } catch {
        await logout();
      } finally {
        setAuthLoading(false);
      }
    };

    validateSession();
  }, [accessToken]);

  // ✅ Cookie-based auth check (from second code)
  const checkAuthStatus = async () => {
    try {
      const response = await fetch("/api/user-details/", {
        credentials: "include",
      });

      if (response.ok) {
        setIsAuthenticated(true);
        return true;
      }
    } catch (error) {
      console.error("Auth check failed:", error);
    }

    setIsAuthenticated(false);
    return false;
  };

  // ✅ NEW: Get token from cookies via backend
  const getTokenFromCookies = async () => {
    try {
      const response = await fetch("/api/get-access-token/", {
        credentials: "include",
      });

      if (response.ok) {
        const data = await response.json();

        if (data.access) {
          setAccessToken(data.access);
          localStorage.setItem("accessToken", data.access);
          return data.access;
        }
      }
    } catch (error) {
      console.error("Failed to get token from cookies:", error);
    }

    return null;
  };

  // ✅ Combined logout (frontend + backend + state reset)
  const logout = async () => {
    try {
      await fetch("/api/logout/", {
        credentials: "include",
      });
    } catch (error) {
      console.error("Logout error:", error);
    }

    setAccessToken(null);
    setUser(null);
    setIsAuthenticated(false);
    localStorage.removeItem("accessToken");
  };

  return (
    <AuthContext.Provider
      value={{
        accessToken,
        setAccessToken,
        user,
        setUser,
        authLoading,
        isAuthenticated,
        setIsAuthenticated,
        checkAuthStatus,
        getTokenFromCookies,
        logout,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}