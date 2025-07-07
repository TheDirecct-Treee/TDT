import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate, Link, useNavigate, useLocation, useSearchParams } from 'react-router-dom';
import axios from 'axios';
import EventsPage from './EventsPage';
import TermsAndConditions from './pages/TermsAndConditions';
import PrivacyPolicy from './pages/PrivacyPolicy';
import AdminDashboard from './AdminDashboard';
import AdminPromotion from './AdminPromotion';
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
    <header className="bg-green-700 text-white shadow-lg">
      <div className="container mx-auto px-6 py-4">
        <div className="flex items-center justify-between">
          <Link to="/" className="flex items-center space-x-3 text-white hover:opacity-90 transition-opacity group">
            <div className="flex items-center space-x-3">
              {/* User's Exact Logo Design */}
              <svg width="80" height="80" viewBox="0 0 200 200" fill="none" xmlns="http://www.w3.org/2000/svg" className="group-hover:scale-105 transition-transform">
                {/* Circuit Tree Design - Exact Match */}
                <g transform="translate(100, 100)">
                  {/* Root Chip */}
                  <rect x="-15" y="50" width="30" height="15" fill="#8b4513" stroke="#654321" strokeWidth="2" rx="2"/>
                  <line x1="-20" y1="55" x2="-15" y2="55" stroke="#654321" strokeWidth="2"/>
                  <line x1="15" y1="55" x2="20" y2="55" stroke="#654321" strokeWidth="2"/>
                  <line x1="-20" y1="60" x2="-15" y2="60" stroke="#654321" strokeWidth="2"/>
                  <line x1="15" y1="60" x2="20" y2="60" stroke="#654321" strokeWidth="2"/>
                  
                  {/* Main Trunk */}
                  <line x1="0" y1="50" x2="0" y2="20" stroke="#84cc5c" strokeWidth="4"/>
                  
                  {/* First Level Branches */}
                  <line x1="-30" y1="35" x2="30" y2="35" stroke="#84cc5c" strokeWidth="3"/>
                  <line x1="-30" y1="35" x2="-30" y2="10" stroke="#84cc5c" strokeWidth="3"/>
                  <line x1="30" y1="35" x2="30" y2="10" stroke="#84cc5c" strokeWidth="3"/>
                  
                  {/* Second Level Branches */}
                  <line x1="-50" y1="20" x2="-10" y2="20" stroke="#84cc5c" strokeWidth="2"/>
                  <line x1="10" y1="20" x2="50" y2="20" stroke="#84cc5c" strokeWidth="2"/>
                  <line x1="-50" y1="20" x2="-50" y2="-5" stroke="#84cc5c" strokeWidth="2"/>
                  <line x1="-10" y1="20" x2="-10" y2="-5" stroke="#84cc5c" strokeWidth="2"/>
                  <line x1="10" y1="20" x2="10" y2="-5" stroke="#84cc5c" strokeWidth="2"/>
                  <line x1="50" y1="20" x2="50" y2="-5" stroke="#84cc5c" strokeWidth="2"/>
                  
                  {/* Third Level Branches */}
                  <line x1="-70" y1="5" x2="-30" y2="5" stroke="#84cc5c" strokeWidth="1.5"/>
                  <line x1="-20" y1="5" x2="20" y2="5" stroke="#84cc5c" strokeWidth="1.5"/>
                  <line x1="30" y1="5" x2="70" y2="5" stroke="#84cc5c" strokeWidth="1.5"/>
                  
                  {/* Circuit Nodes */}
                  <circle cx="-50" cy="-5" r="3" fill="#84cc5c"/>
                  <circle cx="-10" cy="-5" r="3" fill="#84cc5c"/>
                  <circle cx="10" cy="-5" r="3" fill="#84cc5c"/>
                  <circle cx="50" cy="-5" r="3" fill="#84cc5c"/>
                  <circle cx="-30" cy="10" r="2.5" fill="#84cc5c"/>
                  <circle cx="30" cy="10" r="2.5" fill="#84cc5c"/>
                  <circle cx="0" cy="20" r="2.5" fill="#84cc5c"/>
                  
                  {/* End Nodes */}
                  <circle cx="-70" cy="5" r="2" fill="#84cc5c"/>
                  <circle cx="-30" cy="5" r="2" fill="#84cc5c"/>
                  <circle cx="-20" cy="5" r="2" fill="#84cc5c"/>
                  <circle cx="20" cy="5" r="2" fill="#84cc5c"/>
                  <circle cx="30" cy="5" r="2" fill="#84cc5c"/>
                  <circle cx="70" cy="5" r="2" fill="#84cc5c"/>
                </g>
              </svg>
              
              {/* Text Logo */}
              <div className="flex flex-col">
                <h1 className="text-2xl font-bold text-white tracking-wide" style={{ fontFamily: "'Exo 2', 'Orbitron', 'Rajdhani', sans-serif" }}>
                  THE DIRECT TREE
                </h1>
                <p className="text-sm text-green-200 tracking-wider font-medium">
                  BRANCH OUT & STAND TALL
                </p>
              </div>
            </div>
          </Link>
          <nav className="flex items-center space-x-6">
            <Link to="/businesses" className="hover:text-green-200 transition-colors font-medium">
              Browse Businesses
            </Link>
            <Link to="/events" className="hover:text-green-200 transition-colors font-medium">
              Events
            </Link>
            {user ? (
              <div className="flex items-center space-x-4">
                <span className="text-green-100">
                  Welcome, {user.first_name}! 👋
                </span>
                {user.role === 'business_owner' && (
                  <Link to="/dashboard" className="hover:text-green-200 transition-colors font-medium">
                    Dashboard
                  </Link>
                )}
                {user.role === 'admin' && (
                  <Link to="/admin" className="hover:text-green-200 transition-colors font-medium">
                    Admin
                  </Link>
                )}
                <button
                  onClick={logout}
                  className="bg-white/20 hover:bg-white/30 backdrop-blur-sm px-4 py-2 rounded-full transition-all font-medium"
                >
                  Logout
                </button>
              </div>
            ) : (
              <div className="flex items-center space-x-4">
                <Link to="/login" className="hover:text-green-200 transition-colors font-medium">
                  Login
                </Link>
                <Link to="/register" className="bg-gradient-to-r from-amber-600 to-orange-600 hover:from-amber-700 hover:to-orange-700 px-6 py-2 rounded-full transition-all font-medium shadow-lg transform hover:scale-105">
                  Join Us
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

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const [islandsRes, categoriesRes] = await Promise.all([
        axios.get(`${API}/islands`),
        axios.get(`${API}/categories`)
      ]);
      
      setIslands(islandsRes.data.islands);
      setCategories(categoriesRes.data.categories);
    } catch (error) {
      console.error('Error fetching data:', error);
    }
  };

  return (
    <div className="min-h-screen">
      {/* Hero Section */}
      <section 
        className="relative h-screen flex items-center justify-center overflow-hidden bg-gradient-to-br from-gray-100 to-green-50"
        style={{ 
          backgroundImage: "linear-gradient(135deg, rgba(255, 255, 255, 0.9), rgba(34, 197, 94, 0.1)), url('data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTkyMCIgaGVpZ2h0PSIxMDgwIiB2aWV3Qm94PSIwIDAgMTkyMCAxMDgwIiBmaWxsPSJub25lIiB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciPgo8IS0tIExhcmdlIGJhY2tncm91bmQgdmVyc2lvbiBvZiB5b3VyIGNpcmN1aXQgdHJlZSBsb2dvIC0tPgo8ZGVmcz4KICA8cGF0dGVybiBpZD0iY2lyY3VpdFBhdHRlcm4iIHg9IjAiIHk9IjAiIHdpZHRoPSIyMDAiIGhlaWdodD0iMjAwIiBwYXR0ZXJuVW5pdHM9InVzZXJTcGFjZU9uVXNlIj4KICAgIDwhLS0gUmVwZWF0aW5nIGNpcmN1aXQgcGF0dGVybiAtLT4KICAgIDxnIG9wYWNpdHk9IjAuMTUiPgogICAgICA8IS0tIE1haW4gVHJ1bmsgLS0+CiAgICAgIDxsaW5lIHgxPSIxMDAiIHkxPSIxNTAiIHgyPSIxMDAiIHkyPSIxMjAiIHN0cm9rZT0iIzg0Y2M1YyIgc3Ryb2tlLXdpZHRoPSI0Ii8+CiAgICAgIDwhLS0gQnJhbmNoZXMgLS0+CiAgICAgIDxsaW5lIHgxPSI4MCIgeTE9IjEzMCIgeDI9IjEyMCIgeTI9IjEzMCIgc3Ryb2tlPSIjODRjYzVjIiBzdHJva2Utd2lkdGg9IjMiLz4KICAgICAgPGxpbmUgeDE9IjgwIiB5MT0iMTMwIiB4Mj0iODAiIHkyPSIxMTAiIHN0cm9rZT0iIzg0Y2M1YyIgc3Ryb2tlLXdpZHRoPSIzIi8+CiAgICAgIDxsaW5lIHgxPSIxMjAiIHkxPSIxMzAiIHgyPSIxMjAiIHkyPSIxMTAiIHN0cm9rZT0iIzg0Y2M1YyIgc3Ryb2tlLXdpZHRoPSIzIi8+CiAgICAgIDwhLS0gTm9kZXMgLS0+CiAgICAgIDxjaXJjbGUgY3g9IjgwIiBjeT0iMTEwIiByPSIzIiBmaWxsPSIjODRjYzVjIi8+CiAgICAgIDxjaXJjbGUgY3g9IjEyMCIgY3k9IjExMCIgcj0iMyIgZmlsbD0iIzg0Y2M1YyIvPgogICAgICA8Y2lyY2xlIGN4PSIxMDAiIGN5PSIxMjAiIHI9IjMiIGZpbGw9IiM4NGNjNWMiLz4KICAgICAgPCEtLSBSb290IGNoaXAgLS0+CiAgICAgIDxyZWN0IHg9IjkwIiB5PSIxNTAiIHdpZHRoPSIyMCIgaGVpZ2h0PSIxMCIgZmlsbD0iIzZkNTQzMyIgc3Ryb2tlPSIjNGEzNzI2IiBzdHJva2Utd2lkdGg9IjEiLz4KICAgIDwvZz4KICA8L3BhdHRlcm4+CjwvZGVmcz4KPCEtLSBCYWNrZ3JvdW5kIGZpbGwgLS0+CjxyZWN0IHdpZHRoPSIxMDAlIiBoZWlnaHQ9IjEwMCUiIGZpbGw9InVybCgjY2lyY3VpdFBhdHRlcm4pIi8+Cjwvc3ZnPgo=')", 
          backgroundSize: "cover",
          backgroundPosition: "center",
          backgroundRepeat: "no-repeat"
        }}
      >
        {/* Floating Elements */}
        <div className="absolute inset-0 overflow-hidden">
          <div className="absolute top-20 left-10 w-32 h-32 bg-white/10 rounded-full blur-xl animate-pulse"></div>
          <div className="absolute bottom-20 right-10 w-40 h-40 bg-amber-300/20 rounded-full blur-xl animate-pulse delay-300"></div>
          <div className="absolute top-1/2 left-1/4 w-24 h-24 bg-green-300/20 rounded-full blur-xl animate-pulse delay-700"></div>
        </div>

        <div className="text-center text-white hero-text relative z-10 max-w-5xl mx-auto px-6">
          <div className="mb-8">
            {/* User's Exact Logo for Hero Section */}
            <svg width="120" height="120" viewBox="0 0 200 200" fill="none" xmlns="http://www.w3.org/2000/svg" className="mx-auto">
              <g transform="translate(100, 100)">
                {/* Root Chip */}
                <rect x="-18" y="60" width="36" height="18" fill="#8b4513" stroke="#654321" strokeWidth="2" rx="2"/>
                <line x1="-25" y1="66" x2="-18" y2="66" stroke="#654321" strokeWidth="2"/>
                <line x1="18" y1="66" x2="25" y2="66" stroke="#654321" strokeWidth="2"/>
                <line x1="-25" y1="72" x2="-18" y2="72" stroke="#654321" strokeWidth="2"/>
                <line x1="18" y1="72" x2="25" y2="72" stroke="#654321" strokeWidth="2"/>
                
                {/* Main Trunk */}
                <line x1="0" y1="60" x2="0" y2="25" stroke="#ffffff" strokeWidth="5"/>
                
                {/* First Level Branches */}
                <line x1="-35" y1="42" x2="35" y2="42" stroke="#ffffff" strokeWidth="4"/>
                <line x1="-35" y1="42" x2="-35" y2="12" stroke="#ffffff" strokeWidth="4"/>
                <line x1="35" y1="42" x2="35" y2="12" stroke="#ffffff" strokeWidth="4"/>
                
                {/* Second Level Branches */}
                <line x1="-60" y1="25" x2="-12" y2="25" stroke="#ffffff" strokeWidth="3"/>
                <line x1="12" y1="25" x2="60" y2="25" stroke="#ffffff" strokeWidth="3"/>
                <line x1="-60" y1="25" x2="-60" y2="-5" stroke="#ffffff" strokeWidth="3"/>
                <line x1="-12" y1="25" x2="-12" y2="-5" stroke="#ffffff" strokeWidth="3"/>
                <line x1="12" y1="25" x2="12" y2="-5" stroke="#ffffff" strokeWidth="3"/>
                <line x1="60" y1="25" x2="60" y2="-5" stroke="#ffffff" strokeWidth="3"/>
                
                {/* Third Level Branches */}
                <line x1="-80" y1="8" x2="-36" y2="8" stroke="#ffffff" strokeWidth="2"/>
                <line x1="-24" y1="8" x2="24" y2="8" stroke="#ffffff" strokeWidth="2"/>
                <line x1="36" y1="8" x2="80" y2="8" stroke="#ffffff" strokeWidth="2"/>
                
                {/* Circuit Nodes */}
                <circle cx="-60" cy="-5" r="4" fill="#ffffff"/>
                <circle cx="-12" cy="-5" r="4" fill="#ffffff"/>
                <circle cx="12" cy="-5" r="4" fill="#ffffff"/>
                <circle cx="60" cy="-5" r="4" fill="#ffffff"/>
                <circle cx="-35" cy="12" r="3" fill="#ffffff"/>
                <circle cx="35" cy="12" r="3" fill="#ffffff"/>
                <circle cx="0" cy="25" r="3" fill="#ffffff"/>
                
                {/* End Nodes */}
                <circle cx="-80" cy="8" r="3" fill="#ffffff"/>
                <circle cx="-36" cy="8" r="3" fill="#ffffff"/>
                <circle cx="-24" cy="8" r="3" fill="#ffffff"/>
                <circle cx="24" cy="8" r="3" fill="#ffffff"/>
                <circle cx="36" cy="8" r="3" fill="#ffffff"/>
                <circle cx="80" cy="8" r="3" fill="#ffffff"/>
              </g>
            </svg>
          </div>
          <h1 className="text-6xl md:text-7xl font-bold mb-6 hero-title text-gray-800 drop-shadow-lg" style={{ fontFamily: "'Exo 2', 'Orbitron', 'Rajdhani', sans-serif" }}>
            The Direct Tree
          </h1>
          <p className="text-2xl md:text-3xl mb-10 hero-subtitle text-gray-700 font-semibold">
            <span className="inline-block animate-bounce bg-white/90 px-4 py-2 rounded-lg shadow-lg text-green-700">
              Branch out and stand tall
            </span>
          </p>
          
          {/* CTA Buttons */}
          <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
            <Link 
              to="/businesses"
              className="bg-green-600 hover:bg-green-700 text-white px-10 py-4 rounded-lg text-xl font-semibold transition-all transform hover:scale-105 shadow-lg border-2 border-green-700 hover:border-green-800"
            >
              <span>Explore Businesses</span>
            </Link>
            <Link 
              to="/events"
              className="bg-amber-600 hover:bg-amber-700 text-white px-10 py-4 rounded-lg text-xl font-semibold transition-all transform hover:scale-105 shadow-lg border-2 border-amber-700 hover:border-amber-800"
            >
              <span>Browse Events</span>
            </Link>
          </div>
          
          {/* Stats */}
          <div className="mt-16 grid grid-cols-2 gap-8 max-w-2xl mx-auto">
            <div className="text-center bg-white/80 rounded-lg p-4 shadow-lg">
              <div className="text-3xl font-bold text-green-700 mb-2">17</div>
              <div className="text-gray-600 text-sm font-medium">Islands Covered</div>
            </div>
            <div className="text-center bg-white/80 rounded-lg p-4 shadow-lg">
              <div className="text-3xl font-bold text-green-700 mb-2">24/7</div>
              <div className="text-gray-600 text-sm font-medium">Platform Access</div>
            </div>
          </div>
        </div>

        {/* Scroll Indicator */}
        <div className="absolute bottom-8 left-1/2 transform -translate-x-1/2 animate-bounce">
          <div className="w-8 h-12 border-2 border-white/50 rounded-full flex justify-center">
            <div className="w-1 h-3 bg-white/70 rounded-full mt-2 animate-pulse"></div>
          </div>
        </div>
      </section>

      {/* Search Section */}
      <section className="py-12 bg-white">
        <div className="container mx-auto px-6 max-w-4xl">
          <h2 className="text-3xl font-bold text-center mb-8 text-gray-800">
            🔍 Find Your Perfect Business
          </h2>
          <div className="bg-white p-8 rounded-lg shadow-lg">
            <div className="flex flex-col md:flex-row gap-4">
              <div className="flex-1">
                <input
                  type="text"
                  placeholder="Search for restaurants, hair salons, mechanics, braiders, cakes..."
                  className="w-full px-6 py-4 border border-gray-300 rounded-xl focus:outline-none focus:border-green-500 focus:ring-2 focus:ring-green-200 text-lg shadow-sm"
                  onKeyDown={(e) => {
                    if (e.key === 'Enter' && e.target.value.trim()) {
                      window.location.href = `/businesses?search=${encodeURIComponent(e.target.value.trim())}`;
                    }
                  }}
                />
              </div>
              <button
                onClick={(e) => {
                  const searchInput = e.target.parentElement.querySelector('input');
                  if (searchInput.value.trim()) {
                    window.location.href = `/businesses?search=${encodeURIComponent(searchInput.value.trim())}`;
                  }
                }}
                className="bg-green-600 hover:bg-green-700 text-white px-8 py-4 rounded-lg font-semibold transition-all transform hover:scale-105 shadow-lg whitespace-nowrap"
              >
                Search Now
              </button>
            </div>
            <p className="text-center text-gray-600 mt-4">
              Find exactly what you need across all Bahamas islands
            </p>
          </div>
        </div>
      </section>

      {/* Islands Section */}
      <section className="py-16 bg-gradient-to-br from-green-50 to-amber-50">
        <div className="container mx-auto px-6">
          <h2 className="text-3xl font-bold text-center mb-12 text-gray-800">
            <svg width="40" height="40" viewBox="0 0 100 100" fill="none" xmlns="http://www.w3.org/2000/svg" className="inline-block mr-3 mb-2">
              <g transform="translate(50, 50)">
                {/* Root Chip */}
                <rect x="-12" y="30" width="24" height="12" fill="#8b4513" stroke="#654321" strokeWidth="1" rx="2"/>
                <line x1="-15" y1="34" x2="-12" y2="34" stroke="#654321" strokeWidth="1"/>
                <line x1="12" y1="34" x2="15" y2="34" stroke="#654321" strokeWidth="1"/>
                <line x1="-15" y1="38" x2="-12" y2="38" stroke="#654321" strokeWidth="1"/>
                <line x1="12" y1="38" x2="15" y2="38" stroke="#654321" strokeWidth="1"/>
                
                {/* Main Trunk */}
                <line x1="0" y1="30" x2="0" y2="15" stroke="#84cc5c" strokeWidth="3"/>
                
                {/* First Level Branches */}
                <line x1="-20" y1="22" x2="20" y2="22" stroke="#84cc5c" strokeWidth="2"/>
                <line x1="-20" y1="22" x2="-20" y2="8" stroke="#84cc5c" strokeWidth="2"/>
                <line x1="20" y1="22" x2="20" y2="8" stroke="#84cc5c" strokeWidth="2"/>
                
                {/* Second Level Branches */}
                <line x1="-35" y1="15" x2="-8" y2="15" stroke="#84cc5c" strokeWidth="1.5"/>
                <line x1="8" y1="15" x2="35" y2="15" stroke="#84cc5c" strokeWidth="1.5"/>
                <line x1="-35" y1="15" x2="-35" y2="0" stroke="#84cc5c" strokeWidth="1.5"/>
                <line x1="-8" y1="15" x2="-8" y2="0" stroke="#84cc5c" strokeWidth="1.5"/>
                <line x1="8" y1="15" x2="8" y2="0" stroke="#84cc5c" strokeWidth="1.5"/>
                <line x1="35" y1="15" x2="35" y2="0" stroke="#84cc5c" strokeWidth="1.5"/>
                
                {/* Circuit Nodes */}
                <circle cx="-35" cy="0" r="2" fill="#84cc5c"/>
                <circle cx="-8" cy="0" r="2" fill="#84cc5c"/>
                <circle cx="8" cy="0" r="2" fill="#84cc5c"/>
                <circle cx="35" cy="0" r="2" fill="#84cc5c"/>
                <circle cx="-20" cy="8" r="2" fill="#84cc5c"/>
                <circle cx="20" cy="8" r="2" fill="#84cc5c"/>
                <circle cx="0" cy="15" r="2" fill="#84cc5c"/>
              </g>
            </svg>
            Explore Businesses by Island
          </h2>
          <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-4">
            {islands.slice(0, 12).map((island) => (
              <Link
                key={island}
                to={`/businesses?island=${encodeURIComponent(island)}`}
                className="bg-white rounded-xl p-4 text-center shadow-md hover:shadow-xl transition-all transform hover:scale-105 hover:bg-gradient-to-br hover:from-green-50 hover:to-amber-50 group"
              >
                <div className="mb-2 group-hover:scale-110 transition-transform">
                  <svg width="48" height="48" viewBox="0 0 100 100" fill="none" xmlns="http://www.w3.org/2000/svg" className="mx-auto">
                    <g transform="translate(50, 50)">
                      {/* Root Chip */}
                      <rect x="-12" y="30" width="24" height="12" fill="#8b4513" stroke="#654321" strokeWidth="1" rx="2"/>
                      <line x1="-15" y1="34" x2="-12" y2="34" stroke="#654321" strokeWidth="1"/>
                      <line x1="12" y1="34" x2="15" y2="34" stroke="#654321" strokeWidth="1"/>
                      <line x1="-15" y1="38" x2="-12" y2="38" stroke="#654321" strokeWidth="1"/>
                      <line x1="12" y1="38" x2="15" y2="38" stroke="#654321" strokeWidth="1"/>
                      
                      {/* Main Trunk */}
                      <line x1="0" y1="30" x2="0" y2="15" stroke="#84cc5c" strokeWidth="3"/>
                      
                      {/* First Level Branches */}
                      <line x1="-20" y1="22" x2="20" y2="22" stroke="#84cc5c" strokeWidth="2"/>
                      <line x1="-20" y1="22" x2="-20" y2="8" stroke="#84cc5c" strokeWidth="2"/>
                      <line x1="20" y1="22" x2="20" y2="8" stroke="#84cc5c" strokeWidth="2"/>
                      
                      {/* Second Level Branches */}
                      <line x1="-35" y1="15" x2="-8" y2="15" stroke="#84cc5c" strokeWidth="1.5"/>
                      <line x1="8" y1="15" x2="35" y2="15" stroke="#84cc5c" strokeWidth="1.5"/>
                      <line x1="-35" y1="15" x2="-35" y2="0" stroke="#84cc5c" strokeWidth="1.5"/>
                      <line x1="-8" y1="15" x2="-8" y2="0" stroke="#84cc5c" strokeWidth="1.5"/>
                      <line x1="8" y1="15" x2="8" y2="0" stroke="#84cc5c" strokeWidth="1.5"/>
                      <line x1="35" y1="15" x2="35" y2="0" stroke="#84cc5c" strokeWidth="1.5"/>
                      
                      {/* Circuit Nodes */}
                      <circle cx="-35" cy="0" r="2" fill="#84cc5c"/>
                      <circle cx="-8" cy="0" r="2" fill="#84cc5c"/>
                      <circle cx="8" cy="0" r="2" fill="#84cc5c"/>
                      <circle cx="35" cy="0" r="2" fill="#84cc5c"/>
                      <circle cx="-20" cy="8" r="2" fill="#84cc5c"/>
                      <circle cx="20" cy="8" r="2" fill="#84cc5c"/>
                      <circle cx="0" cy="15" r="2" fill="#84cc5c"/>
                    </g>
                  </svg>
                </div>
                <div className="font-semibold text-gray-800 text-sm">{island}</div>
              </Link>
            ))}
          </div>
        </div>
      </section>

      {/* Categories Section */}
      <section className="py-16 bg-white">
        <div className="container mx-auto px-6">
          <h2 className="text-3xl font-bold text-center mb-12 text-gray-800">
            🎯 Browse by Category
          </h2>
          <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-6">
            {categories.slice(0, 12).map((category) => (
              <Link
                key={category}
                to={`/businesses?category=${encodeURIComponent(category)}`}
                className="bg-white border-2 border-green-200 hover:border-green-400 text-gray-800 hover:text-green-700 rounded-xl p-6 text-center transition-all transform hover:scale-105 shadow-lg hover:shadow-xl"
              >
                <div className="font-semibold text-sm">{category}</div>
              </Link>
            ))}
          </div>
        </div>
      </section>

      {/* Coming Soon - Featured Businesses */}
      <section className="py-16 bg-gradient-to-br from-teal-50 to-orange-50">
        <div className="container mx-auto px-6">
          <h2 className="text-3xl font-bold text-center mb-12 text-gray-800">
            ⭐ Featured Businesses
          </h2>
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
            {[1, 2, 3, 4, 5, 6].map((slot) => (
              <div key={slot} className="bg-white rounded-xl shadow-lg overflow-hidden border-2 border-dashed border-gray-200">
                <div className="h-32 bg-gradient-to-r from-gray-100 to-gray-200 flex items-center justify-center">
                  <div className="text-gray-400 text-center">
                    <div className="text-3xl mb-2">📷</div>
                    <div className="text-sm">Cover Photo</div>
                  </div>
                </div>
                
                <div className="p-6">
                  <div className="flex items-start justify-between mb-4">
                    <div className="flex items-center space-x-3">
                      <div className="w-16 h-16 rounded-full bg-gray-200 flex items-center justify-center">
                        <span className="text-gray-400 text-xl">🏢</span>
                      </div>
                      <div>
                        <div className="h-4 bg-gray-200 rounded w-32 mb-2"></div>
                        <div className="h-3 bg-gray-200 rounded w-24"></div>
                      </div>
                    </div>
                    <div className="w-12 h-12 rounded-lg bg-gray-200 flex items-center justify-center">
                      <span className="text-gray-400 text-sm">📍</span>
                    </div>
                  </div>

                  <div className="h-3 bg-gray-200 rounded w-full mb-2"></div>
                  <div className="h-3 bg-gray-200 rounded w-3/4 mb-4"></div>
                  
                  <div className="flex items-center justify-between text-sm mb-4">
                    <div className="h-6 bg-gray-200 rounded-full w-20"></div>
                    <div className="h-6 bg-gray-200 rounded-full w-20"></div>
                  </div>
                  
                  <div className="bg-gray-200 text-gray-400 text-center py-3 rounded-xl">
                    Your Business Here
                  </div>
                </div>
              </div>
            ))}
          </div>
          
          <div className="text-center mt-12">
            <p className="text-gray-600 text-lg mb-4">
              Ready to showcase your business? Join our growing community!
            </p>
            <Link 
              to="/register"
              className="inline-block bg-green-600 hover:bg-green-700 text-white px-8 py-3 rounded-lg text-lg font-semibold transition-all transform hover:scale-105 shadow-lg"
            >
              List Your Business
            </Link>
          </div>
        </div>
      </section>
    </div>
  );
};

// Registration Page with License Upload
const RegisterPage = () => {
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    first_name: '',
    last_name: '',
    role: 'customer',
    phone: ''
  });
  const [businessData, setBusinessData] = useState({
    business_name: '',
    category: '',
    island: '',
    license_number: ''
  });
  const [licenseFile, setLicenseFile] = useState(null);
  const [categories, setCategories] = useState([]);
  const [islands, setIslands] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(false);
  const [message, setMessage] = useState('');
  const [agreements, setAgreements] = useState({
    termsAndConditions: false,
    privacyPolicy: false
  });

  useEffect(() => {
    fetchCategories();
    fetchIslands();
  }, []);

  const fetchCategories = async () => {
    try {
      const response = await axios.get(`${API}/categories`);
      setCategories(response.data.categories);
    } catch (error) {
      console.error('Error fetching categories:', error);
    }
  };

  const fetchIslands = async () => {
    try {
      const response = await axios.get(`${API}/islands`);
      setIslands(response.data.islands);
    } catch (error) {
      console.error('Error fetching islands:', error);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    // Check agreements
    if (!agreements.termsAndConditions || !agreements.privacyPolicy) {
      setError('Please agree to both Terms & Conditions and Privacy Policy to continue');
      setLoading(false);
      return;
    }

    // Validate business owner requirements
    if (formData.role === 'business_owner') {
      if (!businessData.business_name || !businessData.category || !businessData.island || !businessData.license_number) {
        setError('Please fill in all business information');
        setLoading(false);
        return;
      }
      if (!licenseFile) {
        setError('Please upload your business license');
        setLoading(false);
        return;
      }
    }

    try {
      const response = await axios.post(`${API}/register`, formData);
      setError('');
      setSuccess(true);
      setMessage(response.data.message || 'Registration successful! Please check your email to verify your account.');
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

  const handleBusinessChange = (e) => {
    setBusinessData({
      ...businessData,
      [e.target.name]: e.target.value
    });
  };

  const handleFileChange = (e) => {
    setLicenseFile(e.target.files[0]);
  };

  const handleAgreementChange = (e) => {
    setAgreements({
      ...agreements,
      [e.target.name]: e.target.checked
    });
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-green-50 to-amber-50 flex items-center justify-center py-12 px-4">
      <div className="max-w-2xl w-full bg-white rounded-lg shadow-lg p-8">
        <h2 className="text-3xl font-bold text-center text-gray-800 mb-8">
          Join The Direct Tree Family! 🌟
        </h2>
        
        {error && (
          <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
            {error}
          </div>
        )}

        {success && (
          <div className="bg-green-100 border border-green-400 text-green-700 px-4 py-3 rounded mb-4">
            <div className="flex items-center">
              <span className="text-green-500 mr-2">✅</span>
              {message}
            </div>
            <p className="text-sm mt-2">
              Check your email and click the verification link to activate your account.
            </p>
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Personal Information */}
          <div className="bg-gray-50 p-4 rounded-lg">
            <h3 className="font-semibold text-gray-800 mb-4">Personal Information</h3>
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
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-green-500"
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
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-green-500"
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
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-green-500"
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
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-green-500"
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
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-green-500"
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
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-green-500"
              >
                <option value="customer">Customer</option>
                <option value="business_owner">Business Owner</option>
              </select>
            </div>
          </div>

          {/* Business Information (only for business owners) */}
          {formData.role === 'business_owner' && (
            <div className="bg-amber-50 p-4 rounded-lg border border-amber-200">
              <h3 className="font-semibold text-gray-800 mb-4">🏢 Business Information</h3>
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Business Name
                  </label>
                  <input
                    type="text"
                    name="business_name"
                    required={formData.role === 'business_owner'}
                    value={businessData.business_name}
                    onChange={handleBusinessChange}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-amber-500"
                  />
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Category
                    </label>
                    <select
                      name="category"
                      required={formData.role === 'business_owner'}
                      value={businessData.category}
                      onChange={handleBusinessChange}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-amber-500"
                    >
                      <option value="">Select Category</option>
                      {categories.map((category) => (
                        <option key={category} value={category}>{category}</option>
                      ))}
                    </select>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Island
                    </label>
                    <select
                      name="island"
                      required={formData.role === 'business_owner'}
                      value={businessData.island}
                      onChange={handleBusinessChange}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-amber-500"
                    >
                      <option value="">Select Island</option>
                      {islands.map((island) => (
                        <option key={island} value={island}>{island}</option>
                      ))}
                    </select>
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Business License Number
                  </label>
                  <input
                    type="text"
                    name="license_number"
                    required={formData.role === 'business_owner'}
                    value={businessData.license_number}
                    onChange={handleBusinessChange}
                    placeholder="Enter your government-issued license number"
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-amber-500"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Business License Document
                  </label>
                  <input
                    type="file"
                    accept=".pdf,.jpg,.jpeg,.png"
                    onChange={handleFileChange}
                    required={formData.role === 'business_owner'}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-amber-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-amber-50 file:text-amber-700 hover:file:bg-amber-100"
                  />
                  <p className="text-xs text-gray-500 mt-1">
                    Upload a clear copy of your government business license (PDF, JPG, PNG)
                  </p>
                </div>

                <div className="bg-green-100 border border-green-300 rounded-lg p-3">
                  <div className="flex items-start">
                    <span className="text-green-500 text-lg mr-2">ℹ️</span>
                    <div>
                      <h4 className="font-semibold text-green-800">License Verification Required</h4>
                      <p className="text-green-700 text-sm">
                        All businesses must have a valid Bahamas government license. Your application will be reviewed by our admin team before approval.
                      </p>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Terms and Privacy Policy Agreement */}
          <div className="bg-blue-50 p-4 rounded-lg border border-blue-200">
            <h3 className="font-semibold text-gray-800 mb-4">📋 Agreement Required</h3>
            <div className="space-y-3">
              <div className="flex items-start">
                <input
                  type="checkbox"
                  id="termsAndConditions"
                  name="termsAndConditions"
                  checked={agreements.termsAndConditions}
                  onChange={handleAgreementChange}
                  className="mt-1 mr-3 w-4 h-4 text-green-600 border-gray-300 rounded focus:ring-green-500"
                  required
                />
                <label htmlFor="termsAndConditions" className="text-sm text-gray-700">
                  I agree to The Direct Tree's{' '}
                  <Link to="/terms" target="_blank" className="text-green-600 hover:text-green-800 underline font-semibold">
                    Terms and Conditions
                  </Link>
                </label>
              </div>
              
              <div className="flex items-start">
                <input
                  type="checkbox"
                  id="privacyPolicy"
                  name="privacyPolicy"
                  checked={agreements.privacyPolicy}
                  onChange={handleAgreementChange}
                  className="mt-1 mr-3 w-4 h-4 text-green-600 border-gray-300 rounded focus:ring-green-500"
                  required
                />
                <label htmlFor="privacyPolicy" className="text-sm text-gray-700">
                  I agree to The Direct Tree's{' '}
                  <Link to="/privacy-policy" target="_blank" className="text-green-600 hover:text-green-800 underline font-semibold">
                    Privacy Policy
                  </Link>
                </label>
              </div>
            </div>
            
            <div className="mt-3 text-xs text-gray-600 bg-gray-50 p-2 rounded">
              <span className="text-blue-600">ℹ️</span> By registering, you confirm that you have read and understood our terms and privacy practices.
            </div>
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full bg-gradient-to-r from-green-600 to-amber-600 hover:from-green-700 hover:to-amber-700 text-white font-semibold py-3 rounded-xl transition-all disabled:opacity-50 transform hover:scale-105"
          >
            {loading ? 'Creating Account...' : 'Join The Direct Tree'}
          </button>
        </form>

        <div className="mt-6 text-center">
          <p className="text-gray-600">
            Already have an account?{' '}
            <Link to="/login" className="text-green-600 hover:text-green-800 font-semibold">
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
  const [success, setSuccess] = useState(false);
  const [message, setMessage] = useState('');
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
    category: '',
    search: ''
  });
  const [loading, setLoading] = useState(true);
  const location = useLocation();

  useEffect(() => {
    // Parse URL parameters
    const urlParams = new URLSearchParams(location.search);
    const initialFilters = {
      island: urlParams.get('island') || '',
      category: urlParams.get('category') || '',
      search: urlParams.get('search') || ''
    };
    setFilters(initialFilters);
  }, [location.search]);

  useEffect(() => {
    fetchBusinesses();
    if (islands.length === 0 || categories.length === 0) {
      fetchFilters();
    }
  }, [filters]);

  const fetchBusinesses = async () => {
    try {
      const params = new URLSearchParams();
      if (filters.island) params.append('island', filters.island);
      if (filters.category) params.append('category', filters.category);
      
      // Use search endpoint if there's a search query
      let url = `${API}/businesses`;
      if (filters.search) {
        url = `${API}/businesses/search`;
        params.append('q', filters.search);
      }
      
      const response = await axios.get(`${url}?${params}`);
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

        {/* Search and Filters */}
        <div className="bg-white rounded-lg shadow-md p-6 mb-8">
          {/* Search Bar */}
          <div className="mb-6">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              🔍 Search Businesses
            </label>
            <input
              type="text"
              name="search"
              value={filters.search}
              onChange={handleFilterChange}
              placeholder="Search for restaurants, hair salons, mechanics, etc..."
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:border-green-500 focus:ring-2 focus:ring-green-200 text-lg"
            />
            <p className="text-sm text-gray-500 mt-1">
              Search by business name, category, or services (e.g., "braider", "cakes", "mechanic")
            </p>
          </div>
          
          {/* Filters */}
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
            <div key={business.id} className="bg-white rounded-xl shadow-lg overflow-hidden hover:shadow-2xl transition-all transform hover:scale-105 group">
              {/* Cover Photo */}
              {business.cover_photo && (
                <div className="h-32 bg-gradient-to-r from-green-400 to-amber-400 relative overflow-hidden">
                  <img 
                    src={business.cover_photo} 
                    alt={`${business.business_name} cover`}
                    className="w-full h-full object-cover group-hover:scale-110 transition-transform duration-300"
                  />
                  <div className="absolute inset-0 bg-black bg-opacity-20"></div>
                </div>
              )}
              
              <div className="p-6 relative">
                {/* Profile Photo & Logo Row */}
                <div className="flex items-start justify-between mb-4">
                  <div className="flex items-center space-x-3">
                    {/* Profile Photo */}
                    {business.profile_photo ? (
                      <img 
                        src={business.profile_photo} 
                        alt={business.business_name}
                        className="w-16 h-16 rounded-full object-cover border-4 border-white shadow-lg"
                      />
                    ) : (
                      <div className="w-16 h-16 rounded-full bg-gradient-to-br from-green-400 to-amber-400 flex items-center justify-center text-white font-bold text-xl shadow-lg">
                        {business.business_name.charAt(0)}
                      </div>
                    )}
                    
                    <div>
                      <h3 className="text-xl font-bold text-gray-800 group-hover:text-green-600 transition-colors">
                        {business.business_name}
                      </h3>
                      <div className="flex items-center mt-1">
                        {business.rating_average > 0 ? (
                          <div className="flex items-center bg-yellow-50 px-2 py-1 rounded-full">
                            <span className="text-yellow-500 text-sm">★★★★★</span>
                            <span className="ml-1 text-gray-700 font-medium text-sm">
                              {business.rating_average} ({business.rating_count})
                            </span>
                          </div>
                        ) : (
                          <span className="bg-blue-50 text-blue-600 px-2 py-1 rounded-full text-sm font-medium">New Business</span>
                        )}
                      </div>
                    </div>
                  </div>
                  
                  {/* Logo */}
                  {business.logo && (
                    <img 
                      src={business.logo} 
                      alt={`${business.business_name} logo`}
                      className="w-12 h-12 rounded-lg object-contain bg-gray-50 p-1 shadow-sm"
                    />
                  )}
                </div>

                <p className="text-gray-600 mb-4 line-clamp-2">{business.description}</p>
                
                <div className="space-y-2 text-sm mb-4">
                  <div className="flex items-center justify-between">
                    <span className="bg-green-100 text-green-800 px-3 py-1 rounded-full font-medium">
                      {business.category}
                    </span>
                    <span className="bg-blue-100 text-blue-800 px-3 py-1 rounded-full font-medium">
                      {business.island}
                    </span>
                  </div>
                  <div className="flex items-center text-gray-500">
                    <span>📍 {business.address}</span>
                  </div>
                  {business.accepts_appointments && (
                    <div className="flex items-center text-green-600 font-semibold">
                      <span className="text-green-500 mr-1">✅</span>
                      Accepts Appointments
                    </div>
                  )}
                </div>
                
                <Link
                  to={`/business/${business.id}`}
                  className="block w-full bg-gradient-to-r from-green-600 to-amber-600 hover:from-green-700 hover:to-amber-700 text-white text-center py-3 rounded-xl transition-all font-semibold transform hover:scale-105 shadow-lg"
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

// Email Verification Page
const EmailVerificationPage = () => {
  const [searchParams] = useSearchParams();
  const [verifying, setVerifying] = useState(true);
  const [message, setMessage] = useState('');
  const [success, setSuccess] = useState(false);
  const { login } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    const verifyEmail = async () => {
      const token = searchParams.get('token');
      
      if (!token) {
        setMessage('Invalid verification link');
        setVerifying(false);
        return;
      }

      try {
        const response = await axios.post(`${API}/verify-email`, { token });
        login(response.data.user, response.data.token);
        setMessage('Email verified successfully! Welcome to The Direct Tree!');
        setSuccess(true);
        setTimeout(() => navigate('/'), 3000);
      } catch (error) {
        setMessage(error.response?.data?.detail || 'Verification failed');
        setSuccess(false);
      } finally {
        setVerifying(false);
      }
    };

    verifyEmail();
  }, [searchParams, login, navigate]);

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-teal-50 flex items-center justify-center">
      <div className="bg-white rounded-xl shadow-lg p-8 max-w-md w-full text-center">
        {verifying ? (
          <div>
            <div className="loading-spinner mx-auto mb-4"></div>
            <h2 className="text-2xl font-bold text-gray-800 mb-4">
              Verifying Your Email...
            </h2>
            <p className="text-gray-600">Please wait while we verify your account.</p>
          </div>
        ) : (
          <div>
            <div className={`text-6xl mb-4 ${success ? '🎉' : '❌'}`}>
              {success ? '🎉' : '❌'}
            </div>
            <h2 className="text-2xl font-bold text-gray-800 mb-4">
              {success ? 'Email Verified!' : 'Verification Failed'}
            </h2>
            <p className={`mb-6 ${success ? 'text-gray-600' : 'text-red-600'}`}>
              {message}
            </p>
            {!success && (
              <Link
                to="/register"
                className="bg-gradient-to-r from-blue-600 to-teal-600 text-white px-6 py-3 rounded-lg hover:from-blue-700 hover:to-teal-700 transition-all inline-block"
              >
                Try Again
              </Link>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

// Photo Gallery Component
const PhotoGallery = ({ businessId, isOwner = false }) => {
  const [photos, setPhotos] = useState([]);
  const [uploading, setUploading] = useState(false);
  const [selectedFiles, setSelectedFiles] = useState([]);

  useEffect(() => {
    if (businessId) {
      fetchPhotos();
    }
  }, [businessId]);

  const fetchPhotos = async () => {
    try {
      const response = await axios.get(`${API}/business/${businessId}/photos`);
      setPhotos(response.data);
    } catch (error) {
      console.error('Error fetching photos:', error);
    }
  };

  const handleFileSelect = (e) => {
    const files = Array.from(e.target.files);
    setSelectedFiles(files);
  };

  const uploadPhotos = async () => {
    if (!selectedFiles.length) return;

    setUploading(true);
    const formData = new FormData();
    selectedFiles.forEach(file => formData.append('files', file));

    try {
      await axios.post(`${API}/business/${businessId}/upload-photos`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      setSelectedFiles([]);
      fetchPhotos();
      alert('Photos uploaded successfully!');
    } catch (error) {
      console.error('Upload failed:', error);
      alert('Upload failed. Please try again.');
    } finally {
      setUploading(false);
    }
  };

  const deletePhoto = async (photoId) => {
    if (!window.confirm('Are you sure you want to delete this photo?')) {
      return;
    }

    try {
      await axios.delete(`${API}/photos/${photoId}`);
      fetchPhotos();
    } catch (error) {
      console.error('Delete failed:', error);
      alert('Failed to delete photo.');
    }
  };

  return (
    <div className="photo-gallery">
      <h3 className="text-xl font-bold text-gray-800 mb-4">📸 Photo Gallery</h3>
      
      {isOwner && (
        <div className="upload-section mb-6 p-4 bg-gradient-to-r from-blue-50 to-teal-50 rounded-lg">
          <h4 className="font-semibold text-gray-800 mb-3">Upload Photos</h4>
          <input
            type="file"
            multiple
            accept="image/*"
            onChange={handleFileSelect}
            className="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100 mb-3"
          />
          {selectedFiles.length > 0 && (
            <div className="mb-3">
              <p className="text-sm text-gray-600">Selected: {selectedFiles.length} files</p>
            </div>
          )}
          <button
            onClick={uploadPhotos}
            disabled={uploading || selectedFiles.length === 0}
            className="bg-gradient-to-r from-blue-600 to-teal-600 text-white px-4 py-2 rounded-lg hover:from-blue-700 hover:to-teal-700 transition-all disabled:opacity-50"
          >
            {uploading ? 'Uploading...' : 'Upload Photos'}
          </button>
        </div>
      )}

      {photos.length > 0 ? (
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
          {photos.map((photo) => (
            <div key={photo.id} className="relative group">
              <img
                src={photo.thumbnail_url}
                alt={photo.original_filename}
                className="w-full h-32 object-cover rounded-lg shadow-md hover:shadow-lg transition-shadow cursor-pointer"
                onClick={() => window.open(photo.optimized_url, '_blank')}
              />
              {isOwner && (
                <button
                  onClick={() => deletePhoto(photo.id)}
                  className="absolute top-2 right-2 bg-red-600 text-white rounded-full w-6 h-6 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity text-xs"
                >
                  ×
                </button>
              )}
            </div>
          ))}
        </div>
      ) : (
        <div className="text-center py-8 text-gray-500">
          {isOwner ? 'Upload some photos to showcase your work!' : 'No photos available yet.'}
        </div>
      )}
    </div>
  );
};
const BusinessDashboard = () => {
  const { user } = useAuth();
  const [business, setBusiness] = useState(null);
  const [subscription, setSubscription] = useState(null);
  const [loading, setLoading] = useState(true);
  const [planId, setPlanId] = useState(null);

  useEffect(() => {
    fetchBusinessData();
    fetchSubscriptionStatus();
  }, []);

  const fetchBusinessData = async () => {
    try {
      const response = await axios.get(`${API}/businesses`);
      const userBusiness = response.data.find(b => b.user_id === user.id);
      setBusiness(userBusiness);
    } catch (error) {
      console.error('Error fetching business:', error);
    }
  };

  const fetchSubscriptionStatus = async () => {
    try {
      const response = await axios.get(`${API}/paypal/subscription-status`);
      setSubscription(response.data);
    } catch (error) {
      console.error('Error fetching subscription:', error);
    } finally {
      setLoading(false);
    }
  };

  const createBillingPlan = async () => {
    try {
      const response = await axios.post(`${API}/paypal/create-plan`);
      setPlanId(response.data.plan_id);
      return response.data.plan_id;
    } catch (error) {
      console.error('Error creating plan:', error);
      throw error;
    }
  };

  const startSubscription = async () => {
    try {
      setLoading(true);
      
      // Create plan if needed
      let currentPlanId = planId;
      if (!currentPlanId) {
        currentPlanId = await createBillingPlan();
      }

      // Create subscription
      const response = await axios.post(`${API}/paypal/create-subscription`, {
        plan_id: currentPlanId
      });

      // Redirect to PayPal
      if (response.data.approval_url) {
        window.location.href = response.data.approval_url;
      }
    } catch (error) {
      console.error('Error starting subscription:', error);
      alert('Failed to start subscription. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const cancelSubscription = async () => {
    if (!window.confirm('Are you sure you want to cancel your subscription?')) {
      return;
    }

    try {
      setLoading(true);
      await axios.post(`${API}/paypal/cancel-subscription/${subscription.subscription_id}`);
      await fetchSubscriptionStatus();
      alert('Subscription cancelled successfully');
    } catch (error) {
      console.error('Error cancelling subscription:', error);
      alert('Failed to cancel subscription. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-xl">Loading dashboard...</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-teal-50 py-8">
      <div className="container mx-auto px-6">
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-gray-800 mb-2">
            Business Dashboard 📊
          </h1>
          <p className="text-gray-600">Welcome back, {user.first_name}!</p>
        </div>

        <div className="grid lg:grid-cols-2 gap-8">
          {/* Business Info Card */}
          <div className="bg-white rounded-xl shadow-lg p-6">
            <h2 className="text-2xl font-bold text-gray-800 mb-4">
              🏢 Your Business
            </h2>
            {business ? (
              <div className="space-y-4">
                <div>
                  <h3 className="text-xl font-semibold text-gray-800">{business.business_name}</h3>
                  <p className="text-gray-600">{business.description}</p>
                </div>
                <div className="grid grid-cols-2 gap-4 text-sm">
                  <div>
                    <span className="font-medium text-gray-700">Category:</span>
                    <div className="bg-blue-100 text-blue-800 px-2 py-1 rounded-full inline-block ml-2">
                      {business.category}
                    </div>
                  </div>
                  <div>
                    <span className="font-medium text-gray-700">Island:</span>
                    <div className="bg-teal-100 text-teal-800 px-2 py-1 rounded-full inline-block ml-2">
                      {business.island}
                    </div>
                  </div>
                  <div>
                    <span className="font-medium text-gray-700">Status:</span>
                    <div className={`px-2 py-1 rounded-full inline-block ml-2 ${
                      business.status === 'approved' ? 'bg-green-100 text-green-800' :
                      business.status === 'pending' ? 'bg-yellow-100 text-yellow-800' :
                      'bg-red-100 text-red-800'
                    }`}>
                      {business.status}
                    </div>
                  </div>
                  <div>
                    <span className="font-medium text-gray-700">Rating:</span>
                    <div className="ml-2 inline-flex items-center">
                      <span className="text-yellow-400">⭐</span>
                      <span className="ml-1">{business.rating_average || 'New'} ({business.rating_count || 0} reviews)</span>
                    </div>
                  </div>
                </div>
              </div>
            ) : (
              <div className="text-center py-8">
                <p className="text-gray-500 mb-4">No business profile found</p>
                <Link
                  to="/create-business"
                  className="bg-gradient-to-r from-blue-600 to-teal-600 text-white px-6 py-3 rounded-lg hover:from-blue-700 hover:to-teal-700 transition-all"
                >
                  Create Business Profile
                </Link>
              </div>
            )}
          </div>

          {/* Subscription Card */}
          <div className="bg-white rounded-xl shadow-lg p-6">
            <h2 className="text-2xl font-bold text-gray-800 mb-4">
              💳 Subscription
            </h2>
            
            {subscription && subscription.status !== 'NONE' ? (
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <span className="font-medium text-gray-700">Status:</span>
                  <div className={`px-3 py-1 rounded-full font-medium ${
                    subscription.status === 'ACTIVE' ? 'bg-green-100 text-green-800' :
                    subscription.status === 'PENDING' ? 'bg-yellow-100 text-yellow-800' :
                    subscription.status === 'CANCELLED' ? 'bg-red-100 text-red-800' :
                    'bg-gray-100 text-gray-800'
                  }`}>
                    {subscription.status}
                  </div>
                </div>
                
                <div className="flex items-center justify-between">
                  <span className="font-medium text-gray-700">Amount:</span>
                  <span className="text-lg font-bold text-gray-800">
                    ${subscription.amount} {subscription.currency}/month
                  </span>
                </div>

                {subscription.trial_end_date && (
                  <div className="flex items-center justify-between">
                    <span className="font-medium text-gray-700">Trial ends:</span>
                    <span className="text-gray-600">
                      {new Date(subscription.trial_end_date).toLocaleDateString()}
                    </span>
                  </div>
                )}

                {subscription.next_billing_date && (
                  <div className="flex items-center justify-between">
                    <span className="font-medium text-gray-700">Next billing:</span>
                    <span className="text-gray-600">
                      {new Date(subscription.next_billing_date).toLocaleDateString()}
                    </span>
                  </div>
                )}

                {subscription.status === 'ACTIVE' && (
                  <button
                    onClick={cancelSubscription}
                    disabled={loading}
                    className="w-full bg-red-600 hover:bg-red-700 text-white py-2 rounded-lg transition-colors disabled:opacity-50"
                  >
                    {loading ? 'Cancelling...' : 'Cancel Subscription'}
                  </button>
                )}
              </div>
            ) : (
              <div className="text-center space-y-4">
                <div className="bg-gradient-to-br from-orange-100 to-pink-100 p-6 rounded-lg">
                  <h3 className="text-xl font-bold text-gray-800 mb-2">
                    Start Your Subscription 🚀
                  </h3>
                  <p className="text-gray-600 mb-4">
                    Get full access to The Direct Tree platform
                  </p>
                  <div className="text-center">
                    <div className="text-3xl font-bold text-gray-800 mb-2">$20/month</div>
                    <div className="text-sm text-gray-600 mb-4">
                      ✨ 7-day free trial included
                    </div>
                    <ul className="text-left text-sm text-gray-600 space-y-1 mb-6">
                      <li>✅ Business profile listing</li>
                      <li>✅ Customer reviews & ratings</li>
                      <li>✅ Appointment booking system</li>
                      <li>✅ Photo gallery uploads</li>
                      <li>✅ Business analytics</li>
                    </ul>
                  </div>
                </div>
                
                <button
                  onClick={startSubscription}
                  disabled={loading || !business}
                  className="w-full bg-gradient-to-r from-orange-500 to-pink-500 hover:from-orange-600 hover:to-pink-600 text-white py-3 rounded-lg font-semibold transition-all disabled:opacity-50 transform hover:scale-105"
                >
                  {loading ? 'Starting...' : 'Start Subscription'}
                </button>
                
                {!business && (
                  <p className="text-sm text-gray-500">
                    Create a business profile first to subscribe
                  </p>
                )}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

// Subscription Success Page
const SubscriptionSuccess = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const [executing, setExecuting] = useState(true);

  useEffect(() => {
    const executeSubscription = async () => {
      const params = new URLSearchParams(location.search);
      const token = params.get('token');
      const payerId = params.get('PayerID');
      
      if (token && payerId) {
        try {
          await axios.post(`${API}/paypal/execute-subscription/${token}?payer_id=${payerId}`);
          setExecuting(false);
          setTimeout(() => navigate('/dashboard'), 3000);
        } catch (error) {
          console.error('Error executing subscription:', error);
          setExecuting(false);
        }
      } else {
        setExecuting(false);
      }
    };

    executeSubscription();
  }, [location, navigate]);

  return (
    <div className="min-h-screen bg-gradient-to-br from-green-50 to-teal-50 flex items-center justify-center">
      <div className="bg-white rounded-xl shadow-lg p-8 max-w-md w-full text-center">
        {executing ? (
          <div>
            <div className="loading-spinner mx-auto mb-4"></div>
            <h2 className="text-2xl font-bold text-gray-800 mb-4">
              Activating Your Subscription...
            </h2>
            <p className="text-gray-600">Please wait while we set up your account.</p>
          </div>
        ) : (
          <div>
            <div className="text-6xl mb-4">🎉</div>
            <h2 className="text-2xl font-bold text-gray-800 mb-4">
              Subscription Successful!
            </h2>
            <p className="text-gray-600 mb-6">
              Your subscription has been activated. You'll be billed $20/month after your 7-day trial period.
            </p>
            <Link
              to="/dashboard"
              className="bg-gradient-to-r from-green-600 to-teal-600 text-white px-6 py-3 rounded-lg hover:from-green-700 hover:to-teal-700 transition-all inline-block"
            >
              Go to Dashboard
            </Link>
          </div>
        )}
      </div>
    </div>
  );
};

// Subscription Cancel Page
const SubscriptionCancel = () => {
  return (
    <div className="min-h-screen bg-gradient-to-br from-red-50 to-orange-50 flex items-center justify-center">
      <div className="bg-white rounded-xl shadow-lg p-8 max-w-md w-full text-center">
        <div className="text-6xl mb-4">❌</div>
        <h2 className="text-2xl font-bold text-gray-800 mb-4">
          Subscription Cancelled
        </h2>
        <p className="text-gray-600 mb-6">
          Your subscription was not activated. You can try again anytime from your dashboard.
        </p>
        <Link
          to="/dashboard"
          className="bg-gradient-to-r from-blue-600 to-teal-600 text-white px-6 py-3 rounded-lg hover:from-blue-700 hover:to-teal-700 transition-all inline-block"
        >
          Back to Dashboard
        </Link>
      </div>
    </div>
  );
};
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
              <Route path="/verify-email" element={<EmailVerificationPage />} />
              <Route path="/businesses" element={<BusinessListPage />} />
              <Route path="/events" element={<EventsPage />} />
              <Route path="/dashboard" element={<BusinessDashboard />} />
              <Route path="/admin" element={<AdminDashboard />} />
              <Route path="/admin/promote" element={<AdminPromotion />} />
              <Route path="/subscription/success" element={<SubscriptionSuccess />} />
              <Route path="/subscription/cancel" element={<SubscriptionCancel />} />
              <Route path="/terms" element={<TermsAndConditions />} />
              <Route path="/privacy-policy" element={<PrivacyPolicy />} />
            </Routes>
          </main>
        </div>
      </Router>
    </AuthProvider>
  );
}

export default App;