import React, { useEffect, useState } from "react";
import { api } from "./api";
import { useNavigate } from "react-router-dom";

export default function AdminUsers() {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    fetchUsers();
  }, []);

  const fetchUsers = async () => {
    try {
      const result = await api("login", "GET");

      console.log("Users API Response:", result);

      if (result.status && result.data) {
        setUsers(result.data);
      } else if (Array.isArray(result)) {
        setUsers(result);
      } else {
        setError("Failed to fetch users");
      }
    } catch (err) {
      setError("Server error while fetching users");
    } finally {
      setLoading(false);
    }
  };

  const deleteUser = async (username) => {
    const confirmDelete = window.confirm(
      `Are you sure you want to delete ${username}?`
    );
    if (!confirmDelete) return;

    try {
      const result = await api(`delete-user/${username}`, "DELETE");

      if (result.status) {
        fetchUsers();
      } else {
        alert("Failed to delete user");
      }
    } catch (err) {
      alert("Server error while deleting user");
    }
  };

  return (
  <div className="min-h-screen bg-gradient-to-br from-slate-50 via-white to-blue-50 p-8">
    
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
        <h1 className="text-3xl font-bold bg-gradient-to-r from-gray-900 via-blue-900 to-cyan-700 bg-clip-text text-transparent mb-6">
          All Users
        </h1>

        {error && (
          <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded-xl text-red-700">
            {error}
          </div>
        )}

        {loading ? (
          <div className="flex justify-center py-10">
            <div className="w-10 h-10 border-4 border-blue-200 border-t-blue-600 rounded-full animate-spin"></div>
          </div>
        ) : (
          <div className="overflow-x-auto rounded-2xl border border-gray-200">
  <table className="w-full text-sm text-left">
    <thead className="bg-blue-50 text-blue-800 uppercase text-xs tracking-wider">
      <tr>
        <th className="px-6 py-4">Username</th>
        <th className="px-6 py-4">Email</th>
        <th className="px-6 py-4">Role</th>
        <th className="px-6 py-4">Status</th>
        <th className="px-6 py-4">Date Joined</th>
        <th className="px-6 py-4">Last Login</th>
        <th className="px-6 py-4 text-center">Actions</th>
      </tr>
    </thead>

    <tbody className="divide-y divide-gray-100 bg-white/70">
      {users.map((user) => (
        <tr key={user.id} className="hover:bg-blue-50/40 transition">

          {/* Username */}
          <td className="px-6 py-4 font-medium text-gray-900">
            {user.username}
          </td>

          {/* Email */}
          <td className="px-6 py-4 text-gray-600">
            {user.email}
          </td>

          {/* Role */}
          <td className="px-6 py-4 capitalize">
            <span className="px-3 py-1 text-xs font-semibold rounded-full bg-gradient-to-r from-blue-600 to-cyan-500 text-white">
              {user.role}
            </span>
          </td>

          {/* Status */}
          <td className="px-6 py-4">
            <span
              className={`px-3 py-1 text-xs font-semibold rounded-full ${
                user.is_active
                  ? "bg-green-100 text-green-700"
                  : "bg-red-100 text-red-600"
              }`}
            >
              {user.is_active ? "Active" : "Inactive"}
            </span>
          </td>

          {/* Date Joined */}
          <td className="px-6 py-4 text-gray-600">
            {user.date_joined
              ? new Date(user.date_joined).toLocaleDateString()
              : "-"}
          </td>

          {/* Last Login */}
          <td className="px-6 py-4 text-gray-600">
            {user.last_login
              ? new Date(user.last_login).toLocaleString()
              : "Never"}
          </td>

          {/* Delete Button */}
          {/* <td className="px-6 py-4 text-center">
            <button
              onClick={() => deleteUser(user.username)}
              className="px-4 py-2 text-xs font-semibold rounded-full bg-gradient-to-r from-red-500 to-red-600 text-white hover:from-red-600 hover:to-red-700 shadow-md transition-all duration-200"
            >
              Delete
            </button>
          </td> */}
          <td className="px-6 py-4 text-center">
            <button
              onClick={() => deleteUser(user.username)}
              disabled={user.role === "admin"}
              className={`px-4 py-2 text-xs font-semibold rounded-full shadow-md transition-all duration-200
                ${
                  user.role === "admin"
                    ? "bg-gray-300 text-gray-500 cursor-not-allowed"
                    : "bg-gradient-to-r from-red-500 to-red-600 text-white hover:from-red-600 hover:to-red-700"
                }`}
            >
              Delete
            </button>
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