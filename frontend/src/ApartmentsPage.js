import React, { useState, useEffect } from 'react';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const ApartmentsPage = () => {
  const [apartments, setApartments] = useState([]);
  const [islands, setIslands] = useState([]);
  const [filters, setFilters] = useState({
    island: '',
    property_type: '',
    min_rent: '',
    max_rent: '',
    bedrooms: ''
  });
  const [loading, setLoading] = useState(true);
  const [showCreateForm, setShowCreateForm] = useState(false);

  const [newApartment, setNewApartment] = useState({
    title: '',
    description: '',
    address: '',
    island: '',
    bedrooms: 1,
    bathrooms: 1,
    monthly_rent: '',
    property_type: 'Apartment',
    furnishing: 'Unfurnished',
    amenities: [],
    utilities_included: [],
    lease_duration: 'Negotiable',
    available_date: '',
    contact_name: '',
    contact_email: '',
    contact_phone: ''
  });

  const propertyTypes = ['Apartment', 'House', 'Condo', 'Room', 'Studio'];
  const furnishingOptions = ['Furnished', 'Semi-Furnished', 'Unfurnished'];
  const availableAmenities = ['Pool', 'Gym', 'A/C', 'Parking', 'Washer/Dryer', 'Balcony', 'Garden', 'Security'];
  const availableUtilities = ['Water', 'Electricity', 'Internet', 'Cable', 'Gas'];
  const leaseDurations = ['Monthly', '6 Months', '1 Year', 'Negotiable'];

  useEffect(() => {
    fetchApartments();
    fetchIslands();
  }, [filters]);

  const fetchApartments = async () => {
    try {
      setLoading(true);
      const params = new URLSearchParams();
      if (filters.island) params.append('island', filters.island);
      if (filters.property_type) params.append('property_type', filters.property_type);
      if (filters.min_rent) params.append('min_rent', filters.min_rent);
      if (filters.max_rent) params.append('max_rent', filters.max_rent);
      if (filters.bedrooms) params.append('bedrooms', filters.bedrooms);
      
      const response = await axios.get(`${API}/apartments?${params}`);
      setApartments(response.data);
    } catch (error) {
      console.error('Error fetching apartments:', error);
    } finally {
      setLoading(false);
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

  const handleFilterChange = (e) => {
    setFilters({
      ...filters,
      [e.target.name]: e.target.value
    });
  };

  const handleCreateApartment = async (e) => {
    e.preventDefault();
    try {
      // Create apartment listing
      const response = await axios.post(`${API}/apartment/create`, newApartment);
      const apartmentId = response.data.id;
      
      // Create payment
      const paymentResponse = await axios.post(`${API}/apartment/${apartmentId}/create-payment`);
      
      // Redirect to PayPal
      if (paymentResponse.data.approval_url) {
        window.location.href = paymentResponse.data.approval_url;
      }
    } catch (error) {
      console.error('Error creating apartment:', error);
      alert('Error creating apartment listing. Please try again.');
    }
  };

  const handleInputChange = (e) => {
    const { name, value, type, checked } = e.target;
    
    if (type === 'checkbox') {
      if (name === 'amenities') {
        const updatedAmenities = checked 
          ? [...newApartment.amenities, value]
          : newApartment.amenities.filter(item => item !== value);
        setNewApartment({ ...newApartment, amenities: updatedAmenities });
      } else if (name === 'utilities_included') {
        const updatedUtilities = checked 
          ? [...newApartment.utilities_included, value]
          : newApartment.utilities_included.filter(item => item !== value);
        setNewApartment({ ...newApartment, utilities_included: updatedUtilities });
      }
    } else {
      setNewApartment({ ...newApartment, [name]: value });
    }
  };

  const clearFilters = () => {
    setFilters({
      island: '',
      property_type: '',
      min_rent: '',
      max_rent: '',
      bedrooms: ''
    });
  };

  return (
    <div className="min-h-screen bg-white">
      {/* Header */}
      <div className="bg-gradient-to-r from-green-600 to-brown-600 text-white py-16">
        <div className="container mx-auto px-6 text-center">
          <h1 className="text-4xl font-bold mb-4">🏠 Apartment Rentals</h1>
          <p className="text-xl opacity-90">Find your perfect home in The Bahamas</p>
        </div>
      </div>

      <div className="container mx-auto px-6 py-8">
        {/* Action Buttons */}
        <div className="flex justify-between items-center mb-8">
          <div className="flex space-x-4">
            <button
              onClick={() => setShowCreateForm(!showCreateForm)}
              className="bg-green-600 hover:bg-green-700 text-white px-6 py-3 rounded-lg font-semibold transition-all"
            >
              {showCreateForm ? 'Cancel' : 'List Your Property'}
            </button>
          </div>
        </div>

        {/* Create Apartment Form */}
        {showCreateForm && (
          <div className="bg-gray-50 p-6 rounded-xl mb-8 border border-gray-200">
            <h3 className="text-2xl font-bold mb-6 text-gray-800">📝 List Your Property</h3>
            
            <div className="bg-blue-50 p-4 rounded-lg border border-blue-200 mb-6">
              <h4 className="font-semibold text-green-800">Property Listing Fee: $10</h4>
              <p className="text-sm text-gray-600 mt-2">
                After creating your listing, you'll be redirected to PayPal for payment. Your property will be live immediately after payment confirmation.
              </p>
            </div>

            <form onSubmit={handleCreateApartment} className="space-y-6">
              <div className="grid md:grid-cols-2 gap-6">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Property Title *</label>
                  <input
                    type="text"
                    name="title"
                    value={newApartment.title}
                    onChange={handleInputChange}
                    className="w-full p-3 border border-gray-300 rounded-lg"
                    required
                    placeholder="e.g., Spacious 2BR Ocean View Apartment"
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Property Type *</label>
                  <select
                    name="property_type"
                    value={newApartment.property_type}
                    onChange={handleInputChange}
                    className="w-full p-3 border border-gray-300 rounded-lg"
                    required
                  >
                    {propertyTypes.map(type => (
                      <option key={type} value={type}>{type}</option>
                    ))}
                  </select>
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Description *</label>
                <textarea
                  name="description"
                  value={newApartment.description}
                  onChange={handleInputChange}
                  className="w-full p-3 border border-gray-300 rounded-lg"
                  rows="4"
                  required
                  placeholder="Describe your property, its features, and what makes it special..."
                />
              </div>

              <div className="grid md:grid-cols-2 gap-6">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Address *</label>
                  <input
                    type="text"
                    name="address"
                    value={newApartment.address}
                    onChange={handleInputChange}
                    className="w-full p-3 border border-gray-300 rounded-lg"
                    required
                    placeholder="e.g., 123 Ocean Drive"
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Island *</label>
                  <select
                    name="island"
                    value={newApartment.island}
                    onChange={handleInputChange}
                    className="w-full p-3 border border-gray-300 rounded-lg"
                    required
                  >
                    <option value="">Select Island</option>
                    {islands.map(island => (
                      <option key={island} value={island}>{island}</option>
                    ))}
                  </select>
                </div>
              </div>

              <div className="grid md:grid-cols-4 gap-6">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Bedrooms *</label>
                  <select
                    name="bedrooms"
                    value={newApartment.bedrooms}
                    onChange={handleInputChange}
                    className="w-full p-3 border border-gray-300 rounded-lg"
                    required
                  >
                    {[1,2,3,4,5,6].map(num => (
                      <option key={num} value={num}>{num}</option>
                    ))}
                  </select>
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Bathrooms *</label>
                  <select
                    name="bathrooms"
                    value={newApartment.bathrooms}
                    onChange={handleInputChange}
                    className="w-full p-3 border border-gray-300 rounded-lg"
                    required
                  >
                    {[1,2,3,4,5,6].map(num => (
                      <option key={num} value={num}>{num}</option>
                    ))}
                  </select>
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Monthly Rent (USD) *</label>
                  <input
                    type="number"
                    name="monthly_rent"
                    value={newApartment.monthly_rent}
                    onChange={handleInputChange}
                    className="w-full p-3 border border-gray-300 rounded-lg"
                    required
                    placeholder="1200"
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Furnishing *</label>
                  <select
                    name="furnishing"
                    value={newApartment.furnishing}
                    onChange={handleInputChange}
                    className="w-full p-3 border border-gray-300 rounded-lg"
                    required
                  >
                    {furnishingOptions.map(option => (
                      <option key={option} value={option}>{option}</option>
                    ))}
                  </select>
                </div>
              </div>

              <div className="grid md:grid-cols-2 gap-6">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Available Date *</label>
                  <input
                    type="date"
                    name="available_date"
                    value={newApartment.available_date}
                    onChange={handleInputChange}
                    className="w-full p-3 border border-gray-300 rounded-lg"
                    required
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Lease Duration *</label>
                  <select
                    name="lease_duration"
                    value={newApartment.lease_duration}
                    onChange={handleInputChange}
                    className="w-full p-3 border border-gray-300 rounded-lg"
                    required
                  >
                    {leaseDurations.map(duration => (
                      <option key={duration} value={duration}>{duration}</option>
                    ))}
                  </select>
                </div>
              </div>

              <div className="grid md:grid-cols-2 gap-6">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Amenities</label>
                  <div className="grid grid-cols-2 gap-2">
                    {availableAmenities.map(amenity => (
                      <label key={amenity} className="flex items-center space-x-2">
                        <input
                          type="checkbox"
                          name="amenities"
                          value={amenity}
                          checked={newApartment.amenities.includes(amenity)}
                          onChange={handleInputChange}
                          className="text-green-600"
                        />
                        <span className="text-sm">{amenity}</span>
                      </label>
                    ))}
                  </div>
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Utilities Included</label>
                  <div className="grid grid-cols-2 gap-2">
                    {availableUtilities.map(utility => (
                      <label key={utility} className="flex items-center space-x-2">
                        <input
                          type="checkbox"
                          name="utilities_included"
                          value={utility}
                          checked={newApartment.utilities_included.includes(utility)}
                          onChange={handleInputChange}
                          className="text-green-600"
                        />
                        <span className="text-sm">{utility}</span>
                      </label>
                    ))}
                  </div>
                </div>
              </div>

              <div className="grid md:grid-cols-3 gap-6">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Contact Name *</label>
                  <input
                    type="text"
                    name="contact_name"
                    value={newApartment.contact_name}
                    onChange={handleInputChange}
                    className="w-full p-3 border border-gray-300 rounded-lg"
                    required
                    placeholder="John Smith"
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Contact Email *</label>
                  <input
                    type="email"
                    name="contact_email"
                    value={newApartment.contact_email}
                    onChange={handleInputChange}
                    className="w-full p-3 border border-gray-300 rounded-lg"
                    required
                    placeholder="john@example.com"
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Contact Phone *</label>
                  <input
                    type="tel"
                    name="contact_phone"
                    value={newApartment.contact_phone}
                    onChange={handleInputChange}
                    className="w-full p-3 border border-gray-300 rounded-lg"
                    required
                    placeholder="+1-242-555-0123"
                  />
                </div>
              </div>

              <button
                type="submit"
                className="w-full bg-green-600 hover:bg-green-700 text-white font-semibold py-4 rounded-xl transition-all"
              >
                Create Listing & Pay $10
              </button>
            </form>
          </div>
        )}

        {/* Filters */}
        <div className="bg-gray-50 p-6 rounded-xl mb-8">
          <h3 className="text-lg font-semibold mb-4 text-gray-800">🔍 Filter Properties</h3>
          <div className="grid md:grid-cols-5 gap-4">
            <select
              name="island"
              value={filters.island}
              onChange={handleFilterChange}
              className="p-3 border border-gray-300 rounded-lg"
            >
              <option value="">All Islands</option>
              {islands.map(island => (
                <option key={island} value={island}>{island}</option>
              ))}
            </select>
            
            <select
              name="property_type"
              value={filters.property_type}
              onChange={handleFilterChange}
              className="p-3 border border-gray-300 rounded-lg"
            >
              <option value="">All Types</option>
              {propertyTypes.map(type => (
                <option key={type} value={type}>{type}</option>
              ))}
            </select>
            
            <input
              type="number"
              name="min_rent"
              value={filters.min_rent}
              onChange={handleFilterChange}
              placeholder="Min Rent"
              className="p-3 border border-gray-300 rounded-lg"
            />
            
            <input
              type="number"
              name="max_rent"
              value={filters.max_rent}
              onChange={handleFilterChange}
              placeholder="Max Rent"
              className="p-3 border border-gray-300 rounded-lg"
            />
            
            <select
              name="bedrooms"
              value={filters.bedrooms}
              onChange={handleFilterChange}
              className="p-3 border border-gray-300 rounded-lg"
            >
              <option value="">Any Bedrooms</option>
              {[1,2,3,4,5,6].map(num => (
                <option key={num} value={num}>{num} BR</option>
              ))}
            </select>
          </div>
          
          <button
            onClick={clearFilters}
            className="mt-4 bg-gray-600 hover:bg-gray-700 text-white px-4 py-2 rounded-lg"
          >
            Clear Filters
          </button>
        </div>

        {/* Apartments Grid */}
        {loading ? (
          <div className="text-center py-8">
            <div className="text-gray-600">Loading apartments...</div>
          </div>
        ) : apartments.length === 0 ? (
          <div className="text-center py-12">
            <div className="text-gray-600 text-lg">No apartments found matching your criteria.</div>
            <button
              onClick={() => setShowCreateForm(true)}
              className="mt-4 bg-green-600 hover:bg-green-700 text-white px-6 py-3 rounded-lg"
            >
              Be the first to list a property!
            </button>
          </div>
        ) : (
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
            {apartments.map((apartment) => (
              <div key={apartment.id} className="bg-white rounded-xl shadow-lg overflow-hidden hover:shadow-xl transition-all">
                {/* Photos */}
                <div className="h-48 bg-gradient-to-r from-green-400 to-blue-400 relative overflow-hidden">
                  {apartment.photos && apartment.photos.length > 0 ? (
                    <img 
                      src={apartment.photos[0]} 
                      alt={apartment.title}
                      className="w-full h-full object-cover"
                    />
                  ) : (
                    <div className="w-full h-full flex items-center justify-center text-white text-lg font-semibold">
                      🏠 {apartment.property_type}
                    </div>
                  )}
                  <div className="absolute top-2 right-2 bg-green-600 text-white px-2 py-1 rounded-lg text-sm font-semibold">
                    ${apartment.monthly_rent}/mo
                  </div>
                </div>
                
                <div className="p-6">
                  <h3 className="text-xl font-bold text-gray-800 mb-2">{apartment.title}</h3>
                  <p className="text-gray-600 mb-4 line-clamp-2">{apartment.description}</p>
                  
                  <div className="space-y-2 text-sm text-gray-600 mb-4">
                    <div className="flex items-center justify-between">
                      <span>📍 {apartment.island}</span>
                      <span>{apartment.bedrooms} BR • {apartment.bathrooms} Bath</span>
                    </div>
                    <div className="flex items-center justify-between">
                      <span>🏠 {apartment.property_type}</span>
                      <span>🪑 {apartment.furnishing}</span>
                    </div>
                    <div>📅 Available: {new Date(apartment.available_date).toLocaleDateString()}</div>
                  </div>
                  
                  {apartment.amenities && apartment.amenities.length > 0 && (
                    <div className="mb-4">
                      <div className="flex flex-wrap gap-1">
                        {apartment.amenities.slice(0, 3).map((amenity) => (
                          <span key={amenity} className="bg-blue-100 text-blue-800 px-2 py-1 rounded-full text-xs">
                            {amenity}
                          </span>
                        ))}
                        {apartment.amenities.length > 3 && (
                          <span className="bg-gray-100 text-gray-600 px-2 py-1 rounded-full text-xs">
                            +{apartment.amenities.length - 3} more
                          </span>
                        )}
                      </div>
                    </div>
                  )}
                  
                  <div className="bg-gray-50 p-3 rounded-lg">
                    <div className="text-sm text-gray-600 mb-1">Contact: {apartment.contact_name}</div>
                    <div className="text-sm text-gray-600">📧 {apartment.contact_email}</div>
                    <div className="text-sm text-gray-600">📞 {apartment.contact_phone}</div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default ApartmentsPage;