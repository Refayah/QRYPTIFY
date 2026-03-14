import React, { useEffect, useState } from "react";
import { api } from "./api";
import { useNavigate } from "react-router-dom";

export default function AdminLogs() {
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    fetchLogs();
  }, []);

  const fetchLogs = async () => {
    try {
      const result = await api("getlogs", "GET");

      console.log("Logs API Response:", result);

      if (result.status && result.log_data) {
        setLogs(result.log_data);
      } else {
        setError("Failed to fetch logs");
      }
    } catch (err) {
      setError("Server error while fetching logs");
    } finally {
      setLoading(false);
    }
  };

  return (
  <div className="min-h-screen bg-gradient-to-br from-slate-50 via-white to-blue-50 pt-24 px-10">

    {/* Back Button */}
    <div className="mb-6">
      <button
        onClick={() => navigate("/analysis")}
        className="inline-flex items-center gap-2 rounded-full border border-sky-300 bg-sky-50/70 hover:bg-sky-100 text-black px-4 py-2 text-sm shadow-sm hover:border-sky-400 transition-all duration-200"
      >
        ← Back
      </button>
    </div>

    {/* Glass Card */}
    <div className="bg-white/80 backdrop-blur-sm border border-gray-100 shadow-xl rounded-3xl overflow-hidden">

      {/* Top Gradient Bar */}
      <div className="h-1 bg-gradient-to-r from-blue-600 to-cyan-500"></div>

      <div className="p-8">
        <h2 className="text-3xl font-bold bg-gradient-to-r from-gray-900 via-blue-900 to-cyan-700 bg-clip-text text-transparent mb-6">
          System Logs
        </h2>

        {loading && (
          <div className="flex justify-center py-10">
            <div className="w-10 h-10 border-4 border-blue-200 border-t-blue-600 rounded-full animate-spin"></div>
          </div>
        )}

        {error && (
          <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded-xl text-red-700">
            {error}
          </div>
        )}

        {!loading && !error && (
          <div className="overflow-x-auto rounded-2xl border border-gray-200">
            <table className="min-w-full text-left text-sm">
              <thead className="bg-blue-50 text-blue-800 uppercase text-xs tracking-wider">
                <tr>
                  <th className="px-6 py-4">Actor</th>
                  <th className="px-6 py-4">Action</th>
                  <th className="px-6 py-4">Target User</th>
                  <th className="px-6 py-4">Date Joined</th>
                  <th className="px-6 py-4">Last Login</th>
                  <th className="px-6 py-4">Action Timestamp</th>
                </tr>
              </thead>

              <tbody className="divide-y divide-gray-100 bg-white/70">
                {logs.length === 0 && (
                  <tr>
                    <td colSpan="6" className="text-center py-8 text-gray-500">
                      No logs available
                    </td>
                  </tr>
                )}

                {logs.map((log) => (
                  <tr key={log.id} className="hover:bg-blue-50/40 transition">

                    <td className="px-6 py-4 font-medium text-gray-900">
                      {log.actor?.username || "-"}
                    </td>

                    <td className="px-6 py-4">
                      <span className="px-3 py-1 text-xs font-semibold rounded-full bg-gradient-to-r from-purple-600 to-indigo-600 text-white">
                        {log.action}
                      </span>
                    </td>

                    <td className="px-6 py-4 text-gray-600">
                      {log.target_user?.username || "-"}
                    </td>

                    <td className="px-6 py-4 text-gray-600">
                      {log.actor?.date_joined
                        ? new Date(log.actor.date_joined).toLocaleDateString()
                        : "-"}
                    </td>

                    <td className="px-6 py-4 text-gray-600">
                      {log.actor?.last_login
                        ? new Date(log.actor.last_login).toLocaleString()
                        : "-"}
                    </td>

                    <td className="px-6 py-4 text-gray-500">
                      {new Date(log.created_at).toLocaleString()}
                    </td>

                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  </div>
);
}