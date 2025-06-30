import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate, Link, useNavigate } from 'react-router-dom';
import axios from 'axios';
import './App.css';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Context for authentication
const AuthContext = React.createContext();

// Auth Provider
const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(localStorage.getItem('token'));

  useEffect(() => {
    if (token) {
      axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
      // You could verify token here
    }
  }, [token]);

  const login = (userData, userToken) => {
    setUser(userData);
    setToken(userToken);
    localStorage.setItem('token', userToken);
    axios.defaults.headers.common['Authorization'] = `Bearer ${userToken}`;
  };

  const logout = () => {
    setUser(null);
    setToken(null);
    localStorage.removeItem('token');
    delete axios.defaults.headers.common['Authorization'];
  };

  return (
    <AuthContext.Provider value={{ user, token, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
};

// Custom hook to use auth context
const useAuth = () => {
  const context = React.useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

// Header Component
const Header = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  return (
    <header className="bg-gradient-to-r from-blue-600 to-teal-600 text-white shadow-lg">
      <div className="container mx-auto px-6 py-4">
        <div className="flex items-center justify-between">
          <Link to="/" className="text-2xl font-bold">
            🌳 The Direct Tree
          </Link>
          <nav className="flex items-center space-x-6">
            <Link to="/businesses" className="hover:text-blue-200 transition-colors">
              Browse Businesses
            </Link>
            {user ? (
              <div className="flex items-center space-x-4">
                <span className="text-blue-200">
                  Welcome, {user.first_name}!
                </span>
                {user.role === 'business_owner' && (
                  <Link to="/dashboard" className="hover:text-blue-200 transition-colors">
                    Dashboard
                  </Link>
                )}
                {user.role === 'admin' && (
                  <Link to="/admin" className="hover:text-blue-200 transition-colors">
                    Admin
                  </Link>
                )}
                <button
                  onClick={logout}
                  className="bg-blue-700 hover:bg-blue-800 px-4 py-2 rounded-lg transition-colors"
                >
                  Logout
                </button>
              </div>
            ) : (
              <div className="flex items-center space-x-4">
                <Link to="/login" className="hover:text-blue-200 transition-colors">
                  Login
                </Link>
                <Link to="/register" className="bg-teal-500 hover:bg-teal-600 px-4 py-2 rounded-lg transition-colors">
                  Register
                </Link>
              </div>
            )}
          </nav>
        </div>
      </div>
    </header>
  );
};

// Home Page
const HomePage = () => {
  const [islands, setIslands] = useState([]);
  const [categories, setCategories] = useState([]);
  const [featuredBusinesses, setFeaturedBusinesses] = useState([]);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const [islandsRes, categoriesRes, businessesRes] = await Promise.all([
        axios.get(`${API}/islands`),
        axios.get(`${API}/categories`),
        axios.get(`${API}/businesses?limit=6`)
      ]);
      
      setIslands(islandsRes.data.islands);
      setCategories(categoriesRes.data.categories);
      setFeaturedBusinesses(businessesRes.data);
    } catch (error) {
      console.error('Error fetching data:', error);
    }
  };

  return (
    <div className="min-h-screen">
      {/* Hero Section */}
      <section 
        className="relative h-96 bg-cover bg-center flex items-center justify-center"
        style={{ 
          backgroundImage: "linear-gradient(rgba(0, 91, 150, 0.7), rgba(0, 150, 136, 0.7)), url('https://images.unsplash.com/photo-1568826248417-b40de68c4ad6?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NDQ2NDF8MHwxfHNlYXJjaHwxfHwxNzUxMzEwNDgwfDA&ixlib=rb-4.1.0&q=85')"
        }}
      >
        <div className="text-center text-white hero-text">
          <h1 className="text-5xl font-bold mb-4 hero-title">
            Find & Connect with Local Bahamas Businesses
          </h1>
          <p className="text-xl mb-8 hero-subtitle">
            The Direct Tree - Your trusted directory for licensed businesses across all islands
          </p>
          <Link 
            to="/businesses"
            className="bg-gradient-to-r from-orange-500 to-pink-500 hover:from-orange-600 hover:to-pink-600 text-white px-8 py-3 rounded-full text-lg font-semibold transition-all transform hover:scale-105 shadow-lg"
          >
            Explore Businesses 🏝️
          </Link>
        </div>
      </section>

      {/* Islands Section */}
      <section className="py-16 bg-gray-50">
        <div className="container mx-auto px-6">
          <h2 className="text-3xl font-bold text-center mb-12 text-gray-800">
            Explore Businesses by Island
          </h2>
          <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-4">
            {islands.slice(0, 12).map((island) => (
              <Link
                key={island}
                to={`/businesses?island=${encodeURIComponent(island)}`}
                className="bg-white rounded-lg p-4 text-center shadow-md hover:shadow-lg transition-shadow hover:bg-blue-50"
              >
                <div className="text-2xl mb-2">🏝️</div>
                <div className="font-semibold text-gray-800">{island}</div>
              </Link>
            ))}
          </div>
        </div>
      </section>

      {/* Categories Section */}
      <section className="py-16">
        <div className="container mx-auto px-6">
          <h2 className="text-3xl font-bold text-center mb-12 text-gray-800">
            Browse by Category
          </h2>
          <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-6">
            {categories.slice(0, 12).map((category) => (
              <Link
                key={category}
                to={`/businesses?category=${encodeURIComponent(category)}`}
                className="bg-gradient-to-br from-blue-500 to-teal-500 text-white rounded-lg p-6 text-center hover:from-blue-600 hover:to-teal-600 transition-all transform hover:scale-105 shadow-lg"
              >
                <div className="font-semibold">{category}</div>
              </Link>
            ))}
          </div>
        </div>
      </section>

      {/* Featured Businesses */}
      <section className="py-16 bg-gray-50">
        <div className="container mx-auto px-6">
          <h2 className="text-3xl font-bold text-center mb-12 text-gray-800">
            Featured Businesses
          </h2>
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
            {featuredBusinesses.map((business) => (
              <div key={business.id} className="bg-white rounded-lg shadow-lg overflow-hidden hover:shadow-xl transition-shadow">
                <div className="p-6">
                  <div className="flex items-center justify-between mb-4">
                    <h3 className="text-xl font-bold text-gray-800">{business.business_name}</h3>
                    <div className="flex items-center">
                      <span className="text-yellow-400">⭐</span>
                      <span className="ml-1 text-gray-600">{business.rating_average || 'New'}</span>
                    </div>
                  </div>
                  <p className="text-gray-600 mb-4">{business.description}</p>
                  <div className="flex items-center justify-between text-sm text-gray-500">
                    <span>{business.category}</span>
                    <span>{business.island}</span>
                  </div>
                  <Link
                    to={`/business/${business.id}`}
                    className="mt-4 block w-full bg-blue-600 hover:bg-blue-700 text-white text-center py-2 rounded-lg transition-colors"
                  >
                    View Details
                  </Link>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>
    </div>
  );
};

// Registration Page
const RegisterPage = () => {
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    first_name: '',
    last_name: '',
    role: 'customer',
    phone: ''
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      const response = await axios.post(`${API}/register`, formData);
      login(response.data.user, response.data.token);
      navigate('/');
    } catch (error) {
      setError(error.response?.data?.detail || 'Registration failed');
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center py-12 px-4">
      <div className="max-w-md w-full bg-white rounded-lg shadow-lg p-8">
        <h2 className="text-3xl font-bold text-center text-gray-800 mb-8">
          Create Account
        </h2>
        
        {error && (
          <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-6">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                First Name
              </label>
              <input
                type="text"
                name="first_name"
                required
                value={formData.first_name}
                onChange={handleChange}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-blue-500"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Last Name
              </label>
              <input
                type="text"
                name="last_name"
                required
                value={formData.last_name}
                onChange={handleChange}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-blue-500"
              />
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Email
            </label>
            <input
              type="email"
              name="email"
              required
              value={formData.email}
              onChange={handleChange}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-blue-500"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Password
            </label>
            <input
              type="password"
              name="password"
              required
              value={formData.password}
              onChange={handleChange}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-blue-500"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Phone (Optional)
            </label>
            <input
              type="tel"
              name="phone"
              value={formData.phone}
              onChange={handleChange}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-blue-500"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Account Type
            </label>
            <select
              name="role"
              value={formData.role}
              onChange={handleChange}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-blue-500"
            >
              <option value="customer">Customer</option>
              <option value="business_owner">Business Owner</option>
            </select>
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full bg-blue-600 hover:bg-blue-700 text-white font-semibold py-3 rounded-lg transition-colors disabled:opacity-50"
          >
            {loading ? 'Creating Account...' : 'Create Account'}
          </button>
        </form>

        <div className="mt-6 text-center">
          <p className="text-gray-600">
            Already have an account?{' '}
            <Link to="/login" className="text-blue-600 hover:text-blue-800 font-semibold">
              Sign in
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
};

// Login Page
const LoginPage = () => {
  const [formData, setFormData] = useState({
    email: '',
    password: ''
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      const response = await axios.post(`${API}/login`, formData);
      login(response.data.user, response.data.token);
      navigate('/');
    } catch (error) {
      setError(error.response?.data?.detail || 'Login failed');
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center py-12 px-4">
      <div className="max-w-md w-full bg-white rounded-lg shadow-lg p-8">
        <h2 className="text-3xl font-bold text-center text-gray-800 mb-8">
          Sign In
        </h2>
        
        {error && (
          <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Email
            </label>
            <input
              type="email"
              name="email"
              required
              value={formData.email}
              onChange={handleChange}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-blue-500"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Password
            </label>
            <input
              type="password"
              name="password"
              required
              value={formData.password}
              onChange={handleChange}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-blue-500"
            />
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full bg-blue-600 hover:bg-blue-700 text-white font-semibold py-3 rounded-lg transition-colors disabled:opacity-50"
          >
            {loading ? 'Signing In...' : 'Sign In'}
          </button>
        </form>

        <div className="mt-6 text-center">
          <p className="text-gray-600">
            Don't have an account?{' '}
            <Link to="/register" className="text-blue-600 hover:text-blue-800 font-semibold">
              Create one
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
};

// Business Listing Page
const BusinessListPage = () => {
  const [businesses, setBusinesses] = useState([]);
  const [islands, setIslands] = useState([]);
  const [categories, setCategories] = useState([]);
  const [filters, setFilters] = useState({
    island: '',
    category: ''
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchBusinesses();
    fetchFilters();
  }, [filters]);

  const fetchBusinesses = async () => {
    try {
      const params = new URLSearchParams();
      if (filters.island) params.append('island', filters.island);
      if (filters.category) params.append('category', filters.category);
      
      const response = await axios.get(`${API}/businesses?${params}`);
      setBusinesses(response.data);
    } catch (error) {
      console.error('Error fetching businesses:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchFilters = async () => {
    try {
      const [islandsRes, categoriesRes] = await Promise.all([
        axios.get(`${API}/islands`),
        axios.get(`${API}/categories`)
      ]);
      
      setIslands(islandsRes.data.islands);
      setCategories(categoriesRes.data.categories);
    } catch (error) {
      console.error('Error fetching filters:', error);
    }
  };

  const handleFilterChange = (e) => {
    setFilters({
      ...filters,
      [e.target.name]: e.target.value
    });
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-xl">Loading businesses...</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="container mx-auto px-6">
        <h1 className="text-4xl font-bold text-center mb-8 text-gray-800">
          Browse Businesses
        </h1>

        {/* Filters */}
        <div className="bg-white rounded-lg shadow-md p-6 mb-8">
          <div className="grid md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Filter by Island
              </label>
              <select
                name="island"
                value={filters.island}
                onChange={handleFilterChange}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-blue-500"
              >
                <option value="">All Islands</option>
                {islands.map((island) => (
                  <option key={island} value={island}>{island}</option>
                ))}
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Filter by Category
              </label>
              <select
                name="category"
                value={filters.category}
                onChange={handleFilterChange}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-blue-500"
              >
                <option value="">All Categories</option>
                {categories.map((category) => (
                  <option key={category} value={category}>{category}</option>
                ))}
              </select>
            </div>
          </div>
        </div>

        {/* Business Grid */}
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
          {businesses.map((business) => (
            <div key={business.id} className="bg-white rounded-lg shadow-lg overflow-hidden hover:shadow-xl transition-shadow">
              <div className="p-6">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-xl font-bold text-gray-800">{business.business_name}</h3>
                  <div className="flex items-center">
                    <span className="text-yellow-400">⭐</span>
                    <span className="ml-1 text-gray-600">
                      {business.rating_average || 'New'} ({business.rating_count || 0})
                    </span>
                  </div>
                </div>
                <p className="text-gray-600 mb-4 line-clamp-2">{business.description}</p>
                <div className="space-y-2 text-sm text-gray-500 mb-4">
                  <div className="flex items-center justify-between">
                    <span>{business.category}</span>
                    <span>{business.island}</span>
                  </div>
                  <div className="flex items-center">
                    <span>📍 {business.address}</span>
                  </div>
                  {business.accepts_appointments && (
                    <div className="text-green-600 font-semibold">
                      ✅ Accepts Appointments
                    </div>
                  )}
                </div>
                <Link
                  to={`/business/${business.id}`}
                  className="block w-full bg-blue-600 hover:bg-blue-700 text-white text-center py-2 rounded-lg transition-colors"
                >
                  View Details
                </Link>
              </div>
            </div>
          ))}
        </div>

        {businesses.length === 0 && (
          <div className="text-center py-12">
            <div className="text-gray-500 text-xl mb-4">No businesses found</div>
            <p className="text-gray-400">Try adjusting your filters or check back later.</p>
          </div>
        )}
      </div>
    </div>
  );
};

// Main App Component
function App() {
  return (
    <AuthProvider>
      <Router>
        <div className="App">
          <Header />
          <main>
            <Routes>
              <Route path="/" element={<HomePage />} />
              <Route path="/register" element={<RegisterPage />} />
              <Route path="/login" element={<LoginPage />} />
              <Route path="/businesses" element={<BusinessListPage />} />
            </Routes>
          </main>
        </div>
      </Router>
    </AuthProvider>
  );
}

export default App;