import React, { useState } from 'react';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const AdminPromotion = () => {
  const [email, setEmail] = useState('');
  const [message, setMessage] = useState('');
  const [loading, setLoading] = useState(false);

  const promoteToAdmin = async (e) => {
    e.preventDefault();
    setLoading(true);
    setMessage('');

    try {
      const response = await axios.post(`${API}/admin/promote-user?email=${email}`);
      setMessage(`✅ ${response.data.message}`);
      setEmail('');
    } catch (error) {
      setMessage(`❌ ${error.response?.data?.detail || 'Error promoting user'}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center">
      <div className="bg-white p-8 rounded-xl shadow-lg max-w-md w-full">
        <h2 className="text-2xl font-bold text-gray-800 mb-6">Promote User to Admin</h2>
        
        {message && (
          <div className={`p-4 rounded-lg mb-4 ${
            message.includes('✅') ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'
          }`}>
            {message}
          </div>
        )}
        
        <form onSubmit={promoteToAdmin}>
          <div className="mb-4">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Email Address
            </label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-green-500"
              placeholder="Enter email to promote to admin"
            />
          </div>
          
          <button
            type="submit"
            disabled={loading}
            className="w-full bg-gradient-to-r from-green-600 to-amber-600 text-white py-2 rounded-lg font-semibold disabled:opacity-50"
          >
            {loading ? 'Promoting...' : 'Promote to Admin'}
          </button>
        </form>
        
        <div className="mt-4 text-sm text-gray-600">
          <p><strong>Note:</strong> This only works for the first admin account or if you're already an admin.</p>
        </div>
      </div>
    </div>
  );
};

export default AdminPromotion;