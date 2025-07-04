import React, { useState, useEffect } from 'react';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const AdminDashboard = () => {
  const [activeTab, setActiveTab] = useState('pending-businesses');
  const [pendingBusinesses, setPendingBusinesses] = useState([]);
  const [pendingReviews, setPendingReviews] = useState([]);
  const [stats, setStats] = useState({
    totalBusinesses: 0,
    pendingBusinesses: 0,
    totalReviews: 0,
    pendingReviews: 0
  });
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetchPendingBusinesses();
    fetchPendingReviews();
    fetchStats();
  }, []);

  const fetchPendingBusinesses = async () => {
    try {
      const response = await axios.get(`${API}/admin/businesses/pending`);
      setPendingBusinesses(response.data);
    } catch (error) {
      console.error('Error fetching pending businesses:', error);
    }
  };

  const fetchPendingReviews = async () => {
    try {
      const response = await axios.get(`${API}/admin/reviews/pending`);
      setPendingReviews(response.data);
    } catch (error) {
      console.error('Error fetching pending reviews:', error);
    }
  };

  const fetchStats = async () => {
    try {
      const [businessesRes, reviewsRes] = await Promise.all([
        axios.get(`${API}/businesses`),
        axios.get(`${API}/admin/reviews/pending`)
      ]);
      
      setStats({
        totalBusinesses: businessesRes.data.length,
        pendingBusinesses: pendingBusinesses.length,
        totalReviews: 'N/A', // Would need a separate endpoint
        pendingReviews: reviewsRes.data.length
      });
    } catch (error) {
      console.error('Error fetching stats:', error);
    }
  };

  const approveBusiness = async (businessId) => {
    if (!window.confirm('Are you sure you want to approve this business?')) return;
    
    setLoading(true);
    try {
      await axios.put(`${API}/admin/business/${businessId}/approve`);
      alert('Business approved successfully!');
      fetchPendingBusinesses();
      fetchStats();
    } catch (error) {
      console.error('Error approving business:', error);
      alert('Error approving business. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const rejectBusiness = async (businessId) => {
    if (!window.confirm('Are you sure you want to reject this business?')) return;
    
    setLoading(true);
    try {
      await axios.put(`${API}/admin/business/${businessId}/reject`);
      alert('Business rejected successfully!');
      fetchPendingBusinesses();
      fetchStats();
    } catch (error) {
      console.error('Error rejecting business:', error);
      alert('Error rejecting business. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const approveReview = async (reviewId) => {
    if (!window.confirm('Are you sure you want to approve this review?')) return;
    
    setLoading(true);
    try {
      await axios.put(`${API}/admin/review/${reviewId}/approve`);
      alert('Review approved successfully!');
      fetchPendingReviews();
      fetchStats();
    } catch (error) {
      console.error('Error approving review:', error);
      alert('Error approving review. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const TabButton = ({ id, label, count }) => (
    <button
      onClick={() => setActiveTab(id)}
      className={`px-6 py-3 rounded-lg font-semibold transition-all ${
        activeTab === id
          ? 'bg-gradient-to-r from-green-600 to-amber-600 text-white shadow-lg'
          : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
      }`}
    >
      {label}
      {count > 0 && (
        <span className="ml-2 bg-red-500 text-white text-xs px-2 py-1 rounded-full">
          {count}
        </span>
      )}
    </button>
  );

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="container mx-auto px-6">
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-gray-800 mb-2">Admin Dashboard</h1>
          <p className="text-gray-600">Manage businesses, reviews, and platform operations</p>
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <div className="bg-white rounded-xl shadow-lg p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-500 text-sm">Total Businesses</p>
                <p className="text-3xl font-bold text-green-600">{stats.totalBusinesses}</p>
              </div>
              <div className="text-green-500 text-3xl">🏢</div>
            </div>
          </div>
          
          <div className="bg-white rounded-xl shadow-lg p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-500 text-sm">Pending Approvals</p>
                <p className="text-3xl font-bold text-orange-600">{pendingBusinesses.length}</p>
              </div>
              <div className="text-orange-500 text-3xl">⏳</div>
            </div>
          </div>
          
          <div className="bg-white rounded-xl shadow-lg p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-500 text-sm">Pending Reviews</p>
                <p className="text-3xl font-bold text-blue-600">{pendingReviews.length}</p>
              </div>
              <div className="text-blue-500 text-3xl">📝</div>
            </div>
          </div>
          
          <div className="bg-white rounded-xl shadow-lg p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-500 text-sm">Platform Status</p>
                <p className="text-lg font-bold text-green-600">Active</p>
              </div>
              <div className="text-green-500 text-3xl">✅</div>
            </div>
          </div>
        </div>

        {/* Tab Navigation */}
        <div className="flex flex-wrap gap-4 mb-8">
          <TabButton 
            id="pending-businesses" 
            label="Pending Businesses" 
            count={pendingBusinesses.length} 
          />
          <TabButton 
            id="pending-reviews" 
            label="Pending Reviews" 
            count={pendingReviews.length} 
          />
        </div>

        {/* Content Area */}
        <div className="bg-white rounded-xl shadow-lg">
          {activeTab === 'pending-businesses' && (
            <div className="p-6">
              <h2 className="text-2xl font-bold text-gray-800 mb-6">Pending Business Approvals</h2>
              
              {pendingBusinesses.length === 0 ? (
                <div className="text-center py-12">
                  <div className="text-gray-400 text-6xl mb-4">🎉</div>
                  <p className="text-xl text-gray-500">No pending business approvals!</p>
                  <p className="text-gray-400">All businesses have been reviewed.</p>
                </div>
              ) : (
                <div className="space-y-6">
                  {pendingBusinesses.map((business) => (
                    <div key={business.id} className="border border-gray-200 rounded-lg p-6 hover:shadow-md transition-shadow">
                      <div className="flex justify-between items-start mb-4">
                        <div>
                          <h3 className="text-xl font-bold text-gray-800">{business.business_name}</h3>
                          <p className="text-gray-600">{business.email}</p>
                        </div>
                        <span className="bg-yellow-100 text-yellow-800 px-3 py-1 rounded-full text-sm font-medium">
                          Pending Review
                        </span>
                      </div>
                      
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
                        <div>
                          <p className="text-sm text-gray-500">Category</p>
                          <p className="font-medium">{business.category}</p>
                        </div>
                        <div>
                          <p className="text-sm text-gray-500">Island</p>
                          <p className="font-medium">{business.island}</p>
                        </div>
                        <div>
                          <p className="text-sm text-gray-500">License Number</p>
                          <p className="font-medium">{business.license_number}</p>
                        </div>
                        <div>
                          <p className="text-sm text-gray-500">Phone</p>
                          <p className="font-medium">{business.phone}</p>
                        </div>
                      </div>
                      
                      <div className="mb-4">
                        <p className="text-sm text-gray-500 mb-2">Description</p>
                        <p className="text-gray-700">{business.description}</p>
                      </div>
                      
                      <div className="mb-4">
                        <p className="text-sm text-gray-500 mb-2">Address</p>
                        <p className="text-gray-700">{business.address}</p>
                      </div>
                      
                      <div className="flex space-x-4">
                        <button
                          onClick={() => approveBusiness(business.id)}
                          disabled={loading}
                          className="bg-green-600 hover:bg-green-700 text-white px-6 py-2 rounded-lg font-semibold transition-colors disabled:opacity-50"
                        >
                          ✅ Approve
                        </button>
                        <button
                          onClick={() => rejectBusiness(business.id)}
                          disabled={loading}
                          className="bg-red-600 hover:bg-red-700 text-white px-6 py-2 rounded-lg font-semibold transition-colors disabled:opacity-50"
                        >
                          ❌ Reject
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}

          {activeTab === 'pending-reviews' && (
            <div className="p-6">
              <h2 className="text-2xl font-bold text-gray-800 mb-6">Pending Review Approvals</h2>
              
              {pendingReviews.length === 0 ? (
                <div className="text-center py-12">
                  <div className="text-gray-400 text-6xl mb-4">🎉</div>
                  <p className="text-xl text-gray-500">No pending review approvals!</p>
                  <p className="text-gray-400">All reviews have been moderated.</p>
                </div>
              ) : (
                <div className="space-y-6">
                  {pendingReviews.map((review) => (
                    <div key={review.id} className="border border-gray-200 rounded-lg p-6 hover:shadow-md transition-shadow">
                      <div className="flex justify-between items-start mb-4">
                        <div>
                          <div className="flex items-center mb-2">
                            <div className="flex text-yellow-400 mr-2">
                              {'★'.repeat(review.rating)}{'☆'.repeat(5-review.rating)}
                            </div>
                            <span className="text-gray-600">({review.rating}/5)</span>
                          </div>
                          <p className="text-gray-600">
                            {review.is_anonymous ? 'Anonymous Review' : `Review by User ID: ${review.user_id}`}
                          </p>
                        </div>
                        <span className="bg-yellow-100 text-yellow-800 px-3 py-1 rounded-full text-sm font-medium">
                          Pending Approval
                        </span>
                      </div>
                      
                      <div className="mb-4">
                        <p className="text-sm text-gray-500 mb-2">Review Comment</p>
                        <p className="text-gray-700 bg-gray-50 p-3 rounded-lg">{review.comment}</p>
                      </div>
                      
                      <div className="mb-4">
                        <p className="text-sm text-gray-500">Business ID</p>
                        <p className="font-medium">{review.business_id}</p>
                      </div>
                      
                      <div className="flex space-x-4">
                        <button
                          onClick={() => approveReview(review.id)}
                          disabled={loading}
                          className="bg-green-600 hover:bg-green-700 text-white px-6 py-2 rounded-lg font-semibold transition-colors disabled:opacity-50"
                        >
                          ✅ Approve Review
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default AdminDashboard;