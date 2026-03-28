import React, { useState, useContext } from 'react';
import { useNavigate, Link } from "react-router-dom";
import { Button } from '../components/ui/button';
import { Menu, X, User, CheckCircle, XCircle } from 'lucide-react';
import Logo from './Logo';
import { api } from './api.js';
import { AuthContext } from '../AuthContext.jsx';

export default function Navigation({ activeSection, onNavigate }) {
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const [menuOpen, setMenuOpen] = useState(false);
  const [showLogoutPopup, setShowLogoutPopup] = useState(false);
  const [logoutError, setLogoutError] = useState(null);
  const navigate = useNavigate();
  const { accessToken, setAccessToken } = useContext(AuthContext);

  const navItems = [
    { id: 'home', label: 'Home' },
    { id: 'about', label: 'About' },
    { id: 'help', label: 'Help' }
  ];

  const handleNavClick = (sectionId) => {
    if (onNavigate) onNavigate(sectionId);
    setIsMobileMenuOpen(false);
  };

  // simplified: check context token directly rather than calling server
  const handleLoginClick = () => {
    if (accessToken) {
      navigate('/analysis');
    } else {
      handleNavClick('login');
    }
  };

  const handleLogout = async () => {
    try {
      const result = await api('logout', 'GET', null, accessToken);
      setAccessToken(null);

      if (!result?.status) {
        setLogoutError('Logout failed on server.');
      } else {
        setLogoutError(null);
      }
    } catch (err) {
      setAccessToken(null);
      setLogoutError('Network error while logging out.');
    } finally {
      setShowLogoutPopup(true);
      setMenuOpen(false);

      setTimeout(() => {
        setShowLogoutPopup(false);
        setLogoutError(null);
        navigate('/');
      }, 2500);
    }
  };

  return (
    <>
      <nav className="fixed top-0 left-0 right-0 z-50 bg-white/80 backdrop-blur-xl border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-6">
          <div className="flex items-center justify-between h-16">
            <Logo />
            <div className="hidden md:flex items-center space-x-8">
              {navItems.map((item) => (
                <button
                  key={item.id}
                  onClick={() => handleNavClick(item.id)}
                  className={`text-sm font-medium transition-colors duration-200 ${
                    activeSection === item.id 
                      ? 'text-blue-600' 
                      : 'text-gray-600 hover:text-gray-900'
                  }`}
                >
                  {item.label}
                </button>
              ))}

              {/* show user dropdown when logged in, otherwise Login button */}
              {accessToken ? (
                <div className="relative">
                  <div
                    className="w-10 h-10 bg-gray-100 rounded-full flex items-center justify-center cursor-pointer"
                    onClick={() => setMenuOpen((prev) => !prev)}
                  >
                    <User className="w-6 h-6" />
                  </div>
                  {menuOpen && (
                    <div className="absolute right-0 top-12 w-40 bg-white border border-gray-200 rounded-lg shadow-lg">
                      <Link
                        to="/account"
                        className="block px-4 py-2 hover:bg-gray-100"
                        onClick={() => setMenuOpen(false)}
                      >
                        My Account
                      </Link>
                      <button
                        className="w-full text-left px-4 py-2 hover:bg-gray-100"
                        onClick={handleLogout}
                      >
                        Logout
                      </button>
                    </div>
                  )}
                </div>
              ) : (
                <Button 
                  className="bg-gradient-to-r from-blue-600 to-cyan-500 hover:from-blue-700 hover:to-cyan-600 text-white px-6 shadow-lg"
                  onClick={handleLoginClick}
                >
                  Login
                </Button>
              )}
            </div>

            {/* Mobile menu toggle */}
            <button
              className="md:hidden p-2"
              onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
            >
              {isMobileMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
            </button>
          </div>

          {/* Mobile menu */}
          {isMobileMenuOpen && (
            <div className="md:hidden py-4 border-t border-gray-200">
              {navItems.map((item) => (
                <button
                  key={item.id}
                  onClick={() => handleNavClick(item.id)}
                  className={`block w-full text-left px-4 py-2 text-sm font-medium transition-colors duration-200 ${
                    activeSection === item.id 
                      ? 'text-blue-600 bg-blue-50' 
                      : 'text-gray-600 hover:text-gray-900 hover:bg-gray-50'
                  }`}
                >
                  {item.label}
                </button>
              ))}

              <div className="px-4 pt-2">
                {accessToken ? (
                  <div className="flex flex-col space-y-2">
                    <Link
                      to="/account"
                      className="block w-full text-left px-4 py-2 rounded-md bg-gray-100 hover:bg-gray-200"
                      onClick={() => setIsMobileMenuOpen(false)}
                    >
                      My Account
                    </Link>
                    <button
                      className="w-full text-left px-4 py-2 rounded-md bg-gray-100 hover:bg-gray-200"
                      onClick={handleLogout}
                    >
                      Logout
                    </button>
                  </div>
                ) : (
                  <Button 
                    className="w-full bg-gradient-to-r from-blue-600 to-cyan-500 hover:from-blue-700 hover:to-cyan-600 text-white shadow-lg"
                    onClick={handleLoginClick}
                  >
                    Login
                  </Button>
                )}
              </div>
            </div>
          )}
        </div>
      </nav>

      {/* Logout Popup */}
      {showLogoutPopup && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 transition-opacity">
          <div className="bg-white rounded-2xl shadow-2xl p-8 text-center animate-fadeIn max-w-sm w-full">
            <div className="flex items-center justify-center mb-4">
              {logoutError ? (
                <div className="bg-red-100 p-3 rounded-full">
                  <XCircle className="w-12 h-12 text-red-600 animate-shake" />
                </div>
              ) : (
                <div className="bg-green-100 p-3 rounded-full">
                  <CheckCircle className="w-12 h-12 text-green-500 animate-bounce" />
                </div>
              )}
            </div>
            <h3 className={`text-xl font-semibold ${logoutError ? 'text-red-700' : 'text-gray-900'}`}>
              {logoutError ? 'Logout Failed!' : 'Logged out successfully!'}
            </h3>
            <p className={`mt-2 ${logoutError ? 'text-red-500' : 'text-gray-600'}`}>
              {logoutError
                ? 'Unable to log you out. Please try again later or contact support.'
                : ''}
            </p>
          </div>
        </div>
      )}
    </>
  );
}
// import React, { useState, useContext } from 'react';
// import { useNavigate, Link } from "react-router-dom";
// import { Button } from '../components/ui/button';
// import { Menu, X, User, CheckCircle, XCircle } from 'lucide-react';
// import Logo from './Logo';
// import { api } from './api.js';
// import { AuthContext } from '../AuthContext.jsx';

// export default function Navigation({ activeSection, onNavigate }) {
//   const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
//   const [menuOpen, setMenuOpen] = useState(false);
//   const [showLogoutPopup, setShowLogoutPopup] = useState(false);
//   const [logoutError, setLogoutError] = useState(null);

//   const navigate = useNavigate();

//   // ✅ Combined context values
//   const { accessToken, setAccessToken, user, logout, authLoading } = useContext(AuthContext);

//   const navItems = [
//     { id: 'home', label: 'Home' },
//     { id: 'about', label: 'About' },
//     { id: 'help', label: 'Help' }
//   ];

//   const handleNavClick = (sectionId) => {
//     if (onNavigate) onNavigate(sectionId);
//     setIsMobileMenuOpen(false);
//   };

//   const handleLoginClick = () => {
//     if (accessToken) {
//       navigate('/analysis');
//     } else {
//       handleNavClick('login');
//     }
//   };

//   // ✅ Fully merged logout logic
//   const handleLogout = async () => {
//     try {
//       const result = await api('logout', 'GET', null, accessToken);

//       if (!result?.status) {
//         setLogoutError('Logout failed on server.');
//       } else {
//         setLogoutError(null);
//       }
//     } catch (err) {
//       setLogoutError('Network error while logging out.');
//     } finally {
//       // from first code
//       if (setAccessToken) {
//         setAccessToken(null);
//       }

//       // from second code
//       if (logout) {
//         logout();
//       }

//       setShowLogoutPopup(true);
//       setMenuOpen(false);

//       setTimeout(() => {
//         setShowLogoutPopup(false);
//         setLogoutError(null);
//         navigate('/');
//       }, 2500);
//     }
//   };

//   return (
//     <>
//       <nav className="fixed top-0 left-0 right-0 z-50 bg-white/80 backdrop-blur-xl border-b border-gray-200">
//         <div className="max-w-7xl mx-auto px-6">
//           <div className="flex items-center justify-between h-16">
//             <Logo />

//             <div className="hidden md:flex items-center space-x-8">
//               {navItems.map((item) => (
//                 <button
//                   key={item.id}
//                   onClick={() => handleNavClick(item.id)}
//                   className={`text-sm font-medium transition-colors duration-200 ${
//                     activeSection === item.id 
//                       ? 'text-blue-600' 
//                       : 'text-gray-600 hover:text-gray-900'
//                   }`}
//                 >
//                   {item.label}
//                 </button>
//               ))}

//               {/* ✅ Fully safe auth rendering */}
//               {!authLoading && (
//                 accessToken ? (
//                   <div className="relative">
//                     <div
//                       className="w-10 h-10 bg-blue-600 text-white rounded-full
//                                  flex items-center justify-center font-semibold uppercase
//                                  cursor-pointer"
//                       onClick={() => setMenuOpen((prev) => !prev)}
//                     >
//                       {user?.username
//                         ? user.username.charAt(0)
//                         : <User className="w-6 h-6" />
//                       }
//                     </div>

//                     {menuOpen && (
//                       <div className="absolute right-0 top-12 w-40 bg-white border border-gray-200 rounded-lg shadow-lg">
//                         <Link
//                           to="/account"
//                           className="block px-4 py-2 hover:bg-gray-100"
//                           onClick={() => setMenuOpen(false)}
//                         >
//                           My Account
//                         </Link>
//                         <button
//                           className="w-full text-left px-4 py-2 hover:bg-gray-100"
//                           onClick={handleLogout}
//                         >
//                           Logout
//                         </button>
//                       </div>
//                     )}
//                   </div>
//                 ) : (
//                   <Button 
//                     className="bg-gradient-to-r from-blue-600 to-cyan-500 hover:from-blue-700 hover:to-cyan-600 text-white px-6 shadow-lg"
//                     onClick={handleLoginClick}
//                   >
//                     Login
//                   </Button>
//                 )
//               )}
//             </div>

//             {/* Mobile toggle */}
//             <button
//               className="md:hidden p-2"
//               onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
//             >
//               {isMobileMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
//             </button>
//           </div>

//           {/* Mobile menu */}
//           {isMobileMenuOpen && (
//             <div className="md:hidden py-4 border-t border-gray-200">
//               {navItems.map((item) => (
//                 <button
//                   key={item.id}
//                   onClick={() => handleNavClick(item.id)}
//                   className={`block w-full text-left px-4 py-2 text-sm font-medium transition-colors duration-200 ${
//                     activeSection === item.id 
//                       ? 'text-blue-600 bg-blue-50' 
//                       : 'text-gray-600 hover:text-gray-900 hover:bg-gray-50'
//                   }`}
//                 >
//                   {item.label}
//                 </button>
//               ))}

//               <div className="px-4 pt-2">
//                 {!authLoading && (
//                   accessToken ? (
//                     <div className="flex flex-col space-y-2">
//                       <Link
//                         to="/account"
//                         className="block w-full text-left px-4 py-2 rounded-md bg-gray-100 hover:bg-gray-200"
//                         onClick={() => setIsMobileMenuOpen(false)}
//                       >
//                         My Account
//                       </Link>
//                       <button
//                         className="w-full text-left px-4 py-2 rounded-md bg-gray-100 hover:bg-gray-200"
//                         onClick={handleLogout}
//                       >
//                         Logout
//                       </button>
//                     </div>
//                   ) : (
//                     <Button 
//                       className="w-full bg-gradient-to-r from-blue-600 to-cyan-500 hover:from-blue-700 hover:to-cyan-600 text-white shadow-lg"
//                       onClick={handleLoginClick}
//                     >
//                       Login
//                     </Button>
//                   )
//                 )}
//               </div>
//             </div>
//           )}
//         </div>
//       </nav>

//       {/* Logout Popup */}
//       {showLogoutPopup && (
//         <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 transition-opacity">
//           <div className="bg-white rounded-2xl shadow-2xl p-8 text-center animate-fadeIn max-w-sm w-full">
//             <div className="flex items-center justify-center mb-4">
//               {logoutError ? (
//                 <div className="bg-red-100 p-3 rounded-full">
//                   <XCircle className="w-12 h-12 text-red-600 animate-shake" />
//                 </div>
//               ) : (
//                 <div className="bg-green-100 p-3 rounded-full">
//                   <CheckCircle className="w-12 h-12 text-green-500 animate-bounce" />
//                 </div>
//               )}
//             </div>
//             <h3 className={`text-xl font-semibold ${logoutError ? 'text-red-700' : 'text-gray-900'}`}>
//               {logoutError ? 'Logout Failed!' : 'Logged out successfully!'}
//             </h3>
//             <p className={`mt-2 ${logoutError ? 'text-red-500' : 'text-gray-600'}`}>
//               {logoutError
//                 ? 'Unable to log you out. Please try again later or contact support.'
//                 : ''}
//             </p>
//           </div>
//         </div>
//       )}
//     </>
//   );
// }