// import React, { useContext, useState, useEffect, useRef } from 'react'
// import { Link, useNavigate } from 'react-router-dom'
// import Logo from './Logo'
// import { User, CheckCircle, XCircle } from 'lucide-react'
// import { api } from './api'
// import { AuthContext } from '../AuthContext.jsx'

// // ---------- PERSISTENT ANALYSIS STATE (module-level, survives navigation) ----------
// let _persistedResult = null;
// let _persistedError = null;
// let _persistedFileName = null;

// // Button component
// const Button = ({ variant, children, ...rest }) => (
//   <button
//     className={`px-4 py-2 rounded ${variant === 'outline' ? 'border border-gray-400 bg-white' : 'bg-blue-500 text-white'}`}
//     {...rest}
//   >
//     {children}
//   </button>
// );

// const createPageUrl = (page) => (page === 'Home' ? '/' : '/analysis');

// async function UploadFile({ file }) {
//   try {
//     const formData = new FormData();
//     formData.append('file', file);
//     const result = await api('analyze-input-file', 'POST', formData);
//     if (result.status) {
//       console.log("successfully processed the file");
//       return result.predicted_results[0];
//     } else {
//       console.log("error in processing the file");
//     }
//   } catch (e) {
//     console.log(e);
//     alert("Error in uploading the file");
//   }
// }

// const AppHeader = ({ onLogout }) => {
//   const [menuOpen, setMenuOpen] = useState(false);
//   const [showLogoutPopup, setShowLogoutPopup] = useState(false);
//   const [logoutError, setLogoutError] = useState(null);
//   const [isAdmin, setIsAdmin] = useState(false);

//   const { accessToken, setAccessToken, user } = useContext(AuthContext);
//   const navigate = useNavigate();

//   useEffect(() => {
//     const checkUserRole = async () => {
//       try {
//         const result = await api('user-details', 'GET');
//         if (result.status && (result.user.role === 'admin' || result.user.role === 'Admin')) {
//           setIsAdmin(true);
//         }
//       } catch (error) {
//         console.error('Error fetching user details:', error);
//       }
//     };
//     checkUserRole();
//   }, []);

//   const handleLogout = async () => {
//     // Clear persisted state on logout
//     _persistedResult = null;
//     _persistedError = null;
//     _persistedFileName = null;
//     try {
//       const result = await api('logout', 'GET', null, accessToken);
//       setAccessToken(null);
//       if (!result.status) {
//         setLogoutError('Logout failed due to a server error.');
//       }
//     } catch (err) {
//       setAccessToken(null);
//       setLogoutError('Unable to connect to logout service. Please try again.');
//     }
//     setShowLogoutPopup(true);
//     setMenuOpen(false);
//     setTimeout(() => {
//       setShowLogoutPopup(false);
//       setLogoutError(null);
//       if (onLogout) onLogout();
//       navigate('/');
//     }, 3000);
//   };

//   return (
//     <>
//       <header className="fixed top-0 left-0 right-0 z-50 bg-white/90 backdrop-blur-lg border-b border-gray-200">
//         <div className="max-w-7xl mx-auto px-6">
//           <div className="flex items-center justify-between h-16">
//             <Logo />
//             <div className="flex items-center gap-4 relative">
//               {isAdmin && (
//                 <>
//                   <Button variant="outline" onClick={() => { setMenuOpen(false); navigate('/admin/users'); }}>
//                     View Users
//                   </Button>
//                   <Button variant="outline" onClick={() => { setMenuOpen(false); navigate('/admin/logs'); }}>
//                     View Logs
//                   </Button>
//                 </>
//               )}
//               <a href={createPageUrl('Home')}>
//                 <Button variant="outline">Home</Button>
//               </a>
//               <div
//                 className="w-10 h-10 bg-blue-600 rounded-full flex items-center justify-center cursor-pointer"
//                 onClick={() => setMenuOpen((prev) => !prev)}
//               >
//                 {user?.username ? (
//                   <span className="font-semibold text-white uppercase">
//                     {user.username.charAt(0)}
//                   </span>
//                 ) : (
//                   <User className="w-6 h-6" />
//                 )}
//               </div>
//               {menuOpen && (
//                 <div className="absolute right-0 top-12 w-40 bg-white border border-gray-200 rounded-lg shadow-lg z-50">
//                   <Link
//                     to="/account"
//                     className="block px-4 py-2 hover:bg-gray-100"
//                     onClick={() => setMenuOpen(false)}
//                   >
//                     My Account
//                   </Link>
//                   <button
//                     className="w-full text-left px-4 py-2 hover:bg-gray-100"
//                     onClick={handleLogout}
//                   >
//                     Logout
//                   </button>
//                 </div>
//               )}
//             </div>
//           </div>
//         </div>
//       </header>

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
//                 : 'Redirecting to home page...'}
//             </p>
//           </div>
//         </div>
//       )}
//     </>
//   );
// };

// // ---------- FILE UPLOAD ----------
// const FileUploadBox = ({ onFileSelect, isLoading, fileName }) => {
//   const handleFileChange = (ev) => {
//     if (ev.target.files.length > 0) onFileSelect(ev.target.files[0]);
//   };

//   return (
//     <div className="bg-white rounded-2xl shadow-lg border border-gray-200 flex flex-col items-center justify-center p-8 min-h-[280px]">
//       <input
//         type="file"
//         id="file-upload"
//         className="hidden"
//         onChange={handleFileChange}
//         disabled={isLoading}
//       />
//       <label
//         htmlFor="file-upload"
//         className={`w-full text-center group cursor-pointer ${isLoading ? 'cursor-not-allowed' : ''}`}
//       >
//         <div
//           className={`relative border-2 border-dashed rounded-xl p-10 transition-colors duration-300 ${
//             fileName
//               ? 'border-blue-400 bg-blue-50'
//               : isLoading
//               ? 'border-gray-300 bg-gray-100'
//               : 'border-gray-300 group-hover:border-blue-500 group-hover:bg-blue-50'
//           }`}
//         >
//           <div className="flex flex-col items-center text-gray-600">
//             <svg
//               className={`w-12 h-12 mb-4 transition-transform duration-300 ${
//                 fileName
//                   ? 'text-blue-500'
//                   : isLoading
//                   ? 'text-gray-300'
//                   : 'text-gray-400 group-hover:scale-110 group-hover:text-blue-600'
//               }`}
//               fill="none"
//               stroke="currentColor"
//               viewBox="0 0 24 24"
//             >
//               <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2"
//                 d="M4 16v2a2 2 0 002 2h12a2 2 0 002-2v-2M7 10l5-5m0 0l5 5m-5-5v12" />
//             </svg>
//             <h3 className="text-xl font-semibold mb-2">
//               {fileName ? 'File Selected' : 'Upload Encrypted File'}
//             </h3>
//             {fileName ? (
//               <div className="flex items-center gap-2 bg-white border border-blue-200 rounded-lg px-3 py-1.5 mt-1 max-w-full">
//                 <svg className="w-4 h-4 text-blue-500 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
//                   <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2"
//                     d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
//                 </svg>
//                 <span className="text-sm text-blue-700 font-medium truncate max-w-[200px]" title={fileName}>
//                   {fileName}
//                 </span>
//               </div>
//             ) : (
//               <p className="text-sm">Click here to select your file</p>
//             )}
//             {fileName && (
//               <p className="text-xs text-gray-400 mt-2">Click to select a different file</p>
//             )}
//           </div>
//         </div>
//       </label>
//     </div>
//   );
// };

// // ---------- PROCESSING ----------
// const ProcessingAnimation = () => (
//   <div className="flex flex-col items-center justify-center h-full text-center">
//     <div className="relative w-24 h-24 mb-6">
//       <div className="w-full h-full border-4 border-dashed border-blue-200 rounded-full animate-spin"></div>
//     </div>
//     <h3 className="text-2xl font-semibold text-gray-800">Processing...</h3>
//     <p className="text-gray-500 mt-2">Our AI is analyzing the cryptographic patterns.</p>
//   </div>
// );

// // ---------- RESULTS ----------
// const ResultsDisplay = ({ result, isLoading, error }) => {
//   if (isLoading)
//     return (
//       <div className="bg-white rounded-2xl shadow-lg border border-gray-200 p-8 min-h-[280px]">
//         <ProcessingAnimation />
//       </div>
//     );

//   if (error)
//     return (
//       <div className="bg-white rounded-2xl shadow-lg border border-red-200 p-8 min-h-[280px] flex flex-col items-center justify-center text-center">
//         <h3 className="text-2xl font-semibold text-red-700">Analysis Failed</h3>
//         <p className="text-red-500 mt-2">{error}</p>
//       </div>
//     );

//   if (!result)
//     return (
//       <div className="bg-white rounded-2xl shadow-lg border border-gray-200 p-8 min-h-[280px] flex flex-col items-center justify-center text-center">
//         <h3 className="text-2xl font-semibold text-gray-800">Awaiting File</h3>
//         <p className="text-gray-500 mt-2">Upload an encrypted file to begin the analysis.</p>
//       </div>
//     );

//   return (
//     <div className="bg-white rounded-2xl shadow-lg border border-gray-200 p-8 min-h-[280px] flex flex-col justify-center">
//       <p className="text-xs text-gray-400 uppercase tracking-widest mb-1">Top algorithm detected</p>
//       <p className="text-3xl font-semibold text-gray-900 mb-4">{result.predicted_algorithm}</p>

//       <div className="flex gap-3 mb-4">
//         <div className="flex-1 bg-gray-50 rounded-xl p-3">
//           <p className="text-xs text-gray-400 mb-1">Confidence</p>
//           <p className="text-xl font-semibold text-gray-900">{result.algorithm_confidence}%</p>
//         </div>
//         <div className="flex-1 bg-gray-50 rounded-xl p-3">
//           <p className="text-xs text-gray-400 mb-1">Category</p>
//           <p className="text-base font-semibold text-gray-900">{result.predicted_category}</p>
//         </div>
//         <div className="flex-1 bg-gray-50 rounded-xl p-3">
//           <p className="text-xs text-gray-400 mb-1">Type</p>
//           <p className="text-sm font-semibold text-gray-900">{result.predicted_type}</p>
//         </div>
//       </div>

//       <div className="flex gap-2 flex-wrap">
//         <span className="text-xs bg-blue-50 text-blue-700 px-3 py-1 rounded-full">
//           Category · {result.category_confidence}%
//         </span>
//         <span className="text-xs bg-green-50 text-green-700 px-3 py-1 rounded-full">
//           Type · {result.type_confidence}%
//         </span>
//       </div>
//     </div>
//   );
// };

// // ---------- TOP-5 COMPARISON ----------
// const Top5Comparison = ({ result }) => {
//   if (!result?.top5) return null;

//   return (
//     <div className="bg-white rounded-2xl shadow-lg border border-gray-200 p-6 mt-6">
//       <p className="text-xs text-gray-400 uppercase tracking-widest mb-4">Top 5 algorithm comparison</p>
//       <div className="flex flex-col gap-4 max-h-64 overflow-y-auto pr-2">
//         {result.top5.map((item) => (
//           <div key={item.rank}>
//             <div className="flex justify-between items-center mb-1">
//               <div className="flex items-center gap-2">
//                 <span className="text-xs font-medium text-gray-400 bg-gray-100 rounded-full w-6 h-6 flex items-center justify-center">
//                   #{item.rank}
//                 </span>
//                 <span className={`text-sm ${item.rank === 1 ? 'font-semibold text-gray-900' : 'text-gray-700'}`}>
//                   {item.algorithm}
//                 </span>
//               </div>
//               <span className={`text-sm ${item.rank === 1 ? 'font-semibold text-gray-900' : 'text-gray-500'}`}>
//                 {item.probability.toFixed(2)}%
//               </span>
//             </div>
//             <div className="h-1.5 bg-gray-100 rounded-full overflow-hidden">
//               <div
//                 className="h-full rounded-full transition-all duration-500"
//                 style={{
//                   width: `${item.probability}%`,
//                   backgroundColor: item.rank === 1 ? '#3B82F6' : '#93C5FD',
//                 }}
//               />
//             </div>
//           </div>
//         ))}
//       </div>
//     </div>
//   );
// };

// // ---------- MAIN PAGE ----------
// export default function AnalysisPage({ onForceHome }) {
//   // Initialise from persisted module-level state so navigating away and back restores results
//   const [isLoading, setIsLoading] = useState(false);
//   const [analysisResult, setAnalysisResult] = useState(_persistedResult);
//   const [error, setError] = useState(_persistedError);
//   const [fileName, setFileName] = useState(_persistedFileName);

//   // Keep persisted state in sync whenever local state changes
//   useEffect(() => { _persistedResult = analysisResult; }, [analysisResult]);
//   useEffect(() => { _persistedError = error; }, [error]);
//   useEffect(() => { _persistedFileName = fileName; }, [fileName]);

//   const handleFileSelect = async (file) => {
//     setIsLoading(true);
//     setAnalysisResult(null);
//     setError(null);
//     setFileName(file.name);

//     try {
//       const algorithms_prediction = await UploadFile({ file });
//       if (algorithms_prediction && algorithms_prediction.predicted_algorithm) {
//         setAnalysisResult(algorithms_prediction);
//       } else {
//         setError("Backend returned incomplete results");
//       }
//     } catch (e) {
//       console.error(e);
//       setError('An unexpected error occurred during analysis.');
//     } finally {
//       setIsLoading(false);
//     }
//   };

//   return (
//     <div className="min-h-screen bg-gray-50 pt-24 pb-12">
//       <AppHeader onLogout={onForceHome} />
//       <main className="max-w-7xl mx-auto px-6">
//         <div className="grid lg:grid-cols-2 gap-8">
//           <FileUploadBox onFileSelect={handleFileSelect} isLoading={isLoading} fileName={fileName} />
//           <ResultsDisplay result={analysisResult} isLoading={isLoading} error={error} />
//         </div>
//         <Top5Comparison result={analysisResult} />
//       </main>
//     </div>
//   );
// }

import React, { useContext, useState, useEffect, useRef } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import Logo from './Logo'
import { User, CheckCircle, XCircle } from 'lucide-react'
import { api } from './api'
import { AuthContext } from '../AuthContext.jsx'

// ---------- PERSISTENT ANALYSIS STATE (module-level, survives navigation) ----------
let _persistedResult = null;
let _persistedError = null;
let _persistedFileName = null;

// Button component
const Button = ({ variant, children, ...rest }) => (
  <button
    className={`px-4 py-2 rounded ${variant === 'outline' ? 'border border-gray-400 bg-white' : 'bg-blue-500 text-white'}`}
    {...rest}
  >
    {children}
  </button>
);

const createPageUrl = (page) => (page === 'Home' ? '/' : '/analysis');

async function UploadFile({ file }) {
  try {
    // try {
    //     const result = await api('user-details', 'GET');
    //     if (result.status && (result.user.role === 'auditor' || result.user.role === 'Auditor')) {
    //       alert("Access denied: You don't have permission (Admin or Auditor role required)");
    //       return;
    //     }
    //   } catch (error) {
    //     console.error('Error fetching user details:', error);
    //   }
    const formData = new FormData();
    formData.append('file', file);
    const result = await api('analyze-input-file', 'POST', formData);
    if (result.error) {
      if (result.error.includes('403')) {
        console.log("User role not authorized - Status 403");
        alert("Access denied: You don't have permission (Admin or Auditor role required)");
        return;
      }
      console.log("Other error:", result.error);
      return;
    }
    if (result.status) {
      console.log("successfully processed the file");
      return result.predicted_results[0];
    } else {
      if(result.status)
      console.log("error in processing the file");
    }
  } catch (e) {
    console.log(e);
    alert("Error in uploading the file");
  }
}

const AppHeader = ({ onLogout }) => {
  const [menuOpen, setMenuOpen] = useState(false);
  const [showLogoutPopup, setShowLogoutPopup] = useState(false);
  const [logoutError, setLogoutError] = useState(null);
  const [isAdmin, setIsAdmin] = useState(false);
  const [isAuditor,setIsAuditor]=useState(false);

  const { accessToken, setAccessToken, user } = useContext(AuthContext);
  const navigate = useNavigate();

  useEffect(() => {
    const checkUserRole = async () => {
      try {
        const result = await api('user-details', 'GET');
        if (result.status && (result.user.role === 'admin' || result.user.role === 'Admin')) {
          setIsAdmin(true);
        }
        if (result.status && (result.user.role === 'auditor' || result.user.role === 'Auditor')) {
          setIsAuditor(true);
        }
      } catch (error) {
        console.error('Error fetching user details:', error);
      }
    };
    checkUserRole();
  }, []);

  const handleLogout = async () => {
    _persistedResult = null;
    _persistedError = null;
    _persistedFileName = null;
    try {
      const result = await api('logout', 'GET', null, accessToken);
      setAccessToken(null);
      if (!result.status) {
        setLogoutError('Logout failed due to a server error.');
      }
    } catch (err) {
      setAccessToken(null);
      setLogoutError('Unable to connect to logout service. Please try again.');
    }
    setShowLogoutPopup(true);
    setMenuOpen(false);
    setTimeout(() => {
      setShowLogoutPopup(false);
      setLogoutError(null);
      if (onLogout) onLogout();
      navigate('/');
    }, 3000);
  };

  return (
    <>
      <header className="fixed top-0 left-0 right-0 z-50 bg-white/90 backdrop-blur-lg border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-6">
          <div className="flex items-center justify-between h-16">
            <Logo />
            <div className="flex items-center gap-4 relative">
              {(isAdmin || isAuditor) && (
                <>
                  <Button variant="outline" onClick={() => { setMenuOpen(false); navigate('/admin/users'); }}>
                    View Users
                  </Button>
                  <Button variant="outline" onClick={() => { setMenuOpen(false); navigate('/admin/logs'); }}>
                    View Logs
                  </Button>
                </>
              )}
              <a href={createPageUrl('Home')}>
                <Button variant="outline">Home</Button>
              </a>
             <div
                className="w-10 h-10 bg-blue-600 rounded-full flex items-center justify-center cursor-pointer"
                onClick={() => setMenuOpen((prev) => !prev)}
              >
                {user?.username ? (
                  <span className="font-semibold text-white uppercase">
                    {user.username.charAt(0)}
                  </span>
                ) : (
                  <User className="w-6 h-6" />
                )}
              </div>
              {menuOpen && (
                <div className="absolute right-0 top-12 w-40 bg-white border border-gray-200 rounded-lg shadow-lg z-50">
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
          </div>
        </div>
      </header>

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
                : 'Redirecting to home page...'}
            </p>
          </div>
        </div>
      )}
    </>
  );
};

// ---------- FILE UPLOAD ----------
const FileUploadBox = ({ onFileSelect, isLoading, fileName }) => {
  const inputRef = useRef(null);

  const handleFileChange = (ev) => {
    if (ev.target.files.length > 0) {
      onFileSelect(ev.target.files[0]);
      // Reset so the same or a new file can always be selected again
      ev.target.value = '';
    }
  };

  return (
    <div className="bg-white rounded-2xl shadow-lg border border-gray-200 flex flex-col items-center justify-center p-8 min-h-[280px]">
      <input
        ref={inputRef}
        type="file"
        id="file-upload"
        className="hidden"
        onChange={handleFileChange}
        disabled={isLoading}
      />
      <label
        htmlFor="file-upload"
        className={`w-full text-center group cursor-pointer ${isLoading ? 'cursor-not-allowed' : ''}`}
      >
        <div
          className={`relative border-2 border-dashed rounded-xl p-10 transition-colors duration-300 ${
            fileName
              ? 'border-blue-400 bg-blue-50'
              : isLoading
              ? 'border-gray-300 bg-gray-100'
              : 'border-gray-300 group-hover:border-blue-500 group-hover:bg-blue-50'
          }`}
        >
          <div className="flex flex-col items-center text-gray-600">
            <svg
              className={`w-12 h-12 mb-4 transition-transform duration-300 ${
                fileName
                  ? 'text-blue-500'
                  : isLoading
                  ? 'text-gray-300'
                  : 'text-gray-400 group-hover:scale-110 group-hover:text-blue-600'
              }`}
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2"
                d="M4 16v2a2 2 0 002 2h12a2 2 0 002-2v-2M7 10l5-5m0 0l5 5m-5-5v12" />
            </svg>
            <h3 className="text-xl font-semibold mb-2">
              {fileName ? 'File Selected' : 'Upload Encrypted File'}
            </h3>
            {fileName ? (
              <div className="flex items-center gap-2 bg-white border border-blue-200 rounded-lg px-3 py-1.5 mt-1 max-w-full">
                <svg className="w-4 h-4 text-blue-500 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2"
                    d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
                <span className="text-sm text-blue-700 font-medium truncate max-w-[200px]" title={fileName}>
                  {fileName}
                </span>
              </div>
            ) : (
              <p className="text-sm">Click here to select your file</p>
            )}
            {fileName && (
              <p className="text-xs text-gray-400 mt-2">Click to select a different file</p>
            )}
          </div>
        </div>
      </label>
    </div>
  );
};

// ---------- PROCESSING ----------
const ProcessingAnimation = () => (
  <div className="flex flex-col items-center justify-center h-full text-center">
    <div className="relative w-24 h-24 mb-6">
      <div className="w-full h-full border-4 border-dashed border-blue-200 rounded-full animate-spin"></div>
    </div>
    <h3 className="text-2xl font-semibold text-gray-800">Processing...</h3>
    <p className="text-gray-500 mt-2">Our AI is analyzing the cryptographic patterns.</p>
  </div>
);

// ---------- RESULTS ----------
const ResultsDisplay = ({ result, isLoading, error }) => {
  if (isLoading)
    return (
      <div className="bg-white rounded-2xl shadow-lg border border-gray-200 p-8 min-h-[280px]">
        <ProcessingAnimation />
      </div>
    );

  if (error)
    return (
      <div className="bg-white rounded-2xl shadow-lg border border-red-200 p-8 min-h-[280px] flex flex-col items-center justify-center text-center">
        <h3 className="text-2xl font-semibold text-red-700">Analysis Failed</h3>
        {/* <p className="text-red-500 mt-2">{error}</p> */}
      </div>
    );

  if (!result)
    return (
      <div className="bg-white rounded-2xl shadow-lg border border-gray-200 p-8 min-h-[280px] flex flex-col items-center justify-center text-center">
        <h3 className="text-2xl font-semibold text-gray-800">Awaiting File</h3>
        <p className="text-gray-500 mt-2">Upload an encrypted file to begin the analysis.</p>
      </div>
    );

  return (
    <div className="bg-white rounded-2xl shadow-lg border border-gray-200 p-8 min-h-[280px] flex flex-col justify-center">
      <p className="text-xs text-gray-400 uppercase tracking-widest mb-1">Top algorithm detected</p>
      <p className="text-3xl font-semibold text-gray-900 mb-4">{result.predicted_algorithm}</p>

      <div className="flex gap-3 mb-4">
        <div className="flex-1 bg-gray-50 rounded-xl p-3">
          <p className="text-xs text-gray-400 mb-1">Confidence</p>
          <p className="text-xl font-semibold text-gray-900">{result.algorithm_confidence}%</p>
        </div>
        <div className="flex-1 bg-gray-50 rounded-xl p-3">
          <p className="text-xs text-gray-400 mb-1">Category</p>
          <p className="text-base font-semibold text-gray-900">{result.predicted_category}</p>
        </div>
        <div className="flex-1 bg-gray-50 rounded-xl p-3">
          <p className="text-xs text-gray-400 mb-1">Type</p>
          <p className="text-sm font-semibold text-gray-900">{result.predicted_type}</p>
        </div>
      </div>

      <div className="flex gap-2 flex-wrap">
        <span className="text-xs bg-blue-50 text-blue-700 px-3 py-1 rounded-full">
          Category · {result.category_confidence}%
        </span>
        <span className="text-xs bg-green-50 text-green-700 px-3 py-1 rounded-full">
          Type · {result.type_confidence}%
        </span>
      </div>
    </div>
  );
};

// ---------- TOP-5 COMPARISON ----------
const Top5Comparison = ({ result }) => {
  if (!result?.top5) return null;

  return (
    <div className="bg-white rounded-2xl shadow-lg border border-gray-200 p-6 mt-6">
      <p className="text-xs text-gray-400 uppercase tracking-widest mb-4">Top 5 algorithm comparison</p>
      <div className="flex flex-col gap-4 max-h-64 overflow-y-auto pr-2">
        {result.top5.map((item) => (
          <div key={item.rank}>
            <div className="flex justify-between items-center mb-1">
              <div className="flex items-center gap-2">
                <span className="text-xs font-medium text-gray-400 bg-gray-100 rounded-full w-6 h-6 flex items-center justify-center">
                  #{item.rank}
                </span>
                <span className={`text-sm ${item.rank === 1 ? 'font-semibold text-gray-900' : 'text-gray-700'}`}>
                  {item.algorithm}
                </span>
              </div>
              <span className={`text-sm ${item.rank === 1 ? 'font-semibold text-gray-900' : 'text-gray-500'}`}>
                {item.probability.toFixed(2)}%
              </span>
            </div>
            <div className="h-1.5 bg-gray-100 rounded-full overflow-hidden">
              <div
                className="h-full rounded-full transition-all duration-500"
                style={{
                  width: `${item.probability}%`,
                  backgroundColor: item.rank === 1 ? '#3B82F6' : '#93C5FD',
                }}
              />
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

// ---------- MAIN PAGE ----------
export default function AnalysisPage({ onForceHome }) {
  const [isLoading, setIsLoading] = useState(false);
  const [analysisResult, setAnalysisResult] = useState(_persistedResult);
  const [error, setError] = useState(_persistedError);
  const [fileName, setFileName] = useState(_persistedFileName);

  useEffect(() => { _persistedResult = analysisResult; }, [analysisResult]);
  useEffect(() => { _persistedError = error; }, [error]);
  useEffect(() => { _persistedFileName = fileName; }, [fileName]);

  const handleFileSelect = async (file) => {
    setIsLoading(true);
    setAnalysisResult(null);
    setError(null);
    setFileName(file.name);

    try {
      const algorithms_prediction = await UploadFile({ file });
      if (algorithms_prediction && algorithms_prediction.predicted_algorithm) {
        setAnalysisResult(algorithms_prediction);
      } else {
        setError("Backend returned incomplete results");
      }
    } catch (e) {
      console.error(e);
      setError('An unexpected error occurred during analysis.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 pt-24 pb-12">
      <AppHeader onLogout={onForceHome} />
      <main className="max-w-7xl mx-auto px-6">
        <div className="grid lg:grid-cols-2 gap-8">
          <FileUploadBox onFileSelect={handleFileSelect} isLoading={isLoading} fileName={fileName} />
          <ResultsDisplay result={analysisResult} isLoading={isLoading} error={error} />
        </div>
        <Top5Comparison result={analysisResult} />
      </main>
    </div>
  );
}