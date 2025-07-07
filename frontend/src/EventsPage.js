import React, { useState, useEffect } from 'react';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const EventsPage = () => {
  const [events, setEvents] = useState([]);
  const [eventCategories, setEventCategories] = useState([]);
  const [islands, setIslands] = useState([]);
  const [filters, setFilters] = useState({
    island: '',
    category: '',
    date: ''
  });
  const [loading, setLoading] = useState(true);
  const [showCreateForm, setShowCreateForm] = useState(false);

  const [newEvent, setNewEvent] = useState({
    title: '',
    description: '',
    category: '',
    island: '',
    location: '',
    event_date: '',
    start_time: '',
    end_time: '',
    organizer_name: '',
    organizer_email: '',
    organizer_phone: '',
    ticket_price: '',
    ticket_link: ''
  });

  useEffect(() => {
    fetchEvents();
    fetchEventCategories();
    fetchIslands();
  }, [filters]);

  const fetchEvents = async () => {
    try {
      const params = new URLSearchParams();
      if (filters.island) params.append('island', filters.island);
      if (filters.category) params.append('category', filters.category);
      if (filters.date) params.append('date', filters.date);
      
      const response = await axios.get(`${API}/events?${params}`);
      setEvents(response.data);
    } catch (error) {
      console.error('Error fetching events:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchEventCategories = async () => {
    try {
      const response = await axios.get(`${API}/event-categories`);
      setEventCategories(response.data.categories);
    } catch (error) {
      console.error('Error fetching event categories:', error);
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

  const handleCreateEvent = async (e) => {
    e.preventDefault();
    try {
      // Create event (unpaid)
      const response = await axios.post(`${API}/event/create`, newEvent);
      const eventId = response.data.id;
      
      // Create payment
      const paymentResponse = await axios.post(`${API}/event/${eventId}/create-payment`);
      
      // Redirect to PayPal
      if (paymentResponse.data.approval_url) {
        window.location.href = paymentResponse.data.approval_url;
      }
    } catch (error) {
      console.error('Error creating event:', error);
      alert('Failed to create event. Please try again.');
    }
  };

  const handleInputChange = (e) => {
    setNewEvent({
      ...newEvent,
      [e.target.name]: e.target.value
    });
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-xl">Loading events...</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-green-50 to-amber-50 py-8">
      <div className="container mx-auto px-6">
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-gray-800 mb-4">
            🎉 Bahamas Events
          </h1>
          <p className="text-gray-600 text-lg">
            Discover exciting events happening across all islands
          </p>
          <button
            onClick={() => setShowCreateForm(!showCreateForm)}
            className="mt-4 bg-gradient-to-r from-green-600 to-amber-600 hover:from-green-700 hover:to-amber-700 text-white px-6 py-3 rounded-lg font-semibold transition-all transform hover:scale-105"
          >
            Create Event
          </button>
        </div>

        {/* Create Event Form */}
        {showCreateForm && (
          <div className="bg-white rounded-xl shadow-lg p-6 mb-8">
            <h2 className="text-2xl font-bold text-gray-800 mb-6">Create New Event</h2>
            <form onSubmit={handleCreateEvent} className="space-y-4">
              <div className="grid md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Event Title
                  </label>
                  <input
                    type="text"
                    name="title"
                    required
                    value={newEvent.title}
                    onChange={handleInputChange}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-green-500"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Category
                  </label>
                  <select
                    name="category"
                    required
                    value={newEvent.category}
                    onChange={handleInputChange}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-green-500"
                  >
                    <option value="">Select Category</option>
                    {eventCategories.map((category) => (
                      <option key={category} value={category}>{category}</option>
                    ))}
                  </select>
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Description
                </label>
                <textarea
                  name="description"
                  required
                  rows="3"
                  value={newEvent.description}
                  onChange={handleInputChange}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-green-500"
                />
              </div>

              <div className="grid md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Island
                  </label>
                  <select
                    name="island"
                    required
                    value={newEvent.island}
                    onChange={handleInputChange}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-green-500"
                  >
                    <option value="">Select Island</option>
                    {islands.map((island) => (
                      <option key={island} value={island}>{island}</option>
                    ))}
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Location
                  </label>
                  <input
                    type="text"
                    name="location"
                    required
                    value={newEvent.location}
                    onChange={handleInputChange}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-green-500"
                  />
                </div>
              </div>

              <div className="grid md:grid-cols-3 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Event Date
                  </label>
                  <input
                    type="date"
                    name="event_date"
                    required
                    value={newEvent.event_date}
                    onChange={handleInputChange}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-green-500"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Start Time
                  </label>
                  <input
                    type="time"
                    name="start_time"
                    required
                    value={newEvent.start_time}
                    onChange={handleInputChange}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-green-500"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    End Time
                  </label>
                  <input
                    type="time"
                    name="end_time"
                    required
                    value={newEvent.end_time}
                    onChange={handleInputChange}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-green-500"
                  />
                </div>
              </div>

              <div className="grid md:grid-cols-3 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Organizer Name
                  </label>
                  <input
                    type="text"
                    name="organizer_name"
                    required
                    value={newEvent.organizer_name}
                    onChange={handleInputChange}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-green-500"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Organizer Email
                  </label>
                  <input
                    type="email"
                    name="organizer_email"
                    required
                    value={newEvent.organizer_email}
                    onChange={handleInputChange}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-green-500"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Phone (Optional)
                  </label>
                  <input
                    type="tel"
                    name="organizer_phone"
                    value={newEvent.organizer_phone}
                    onChange={handleInputChange}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-green-500"
                  />
                </div>
              </div>

              <div className="grid md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Ticket Price (Optional)
                  </label>
                  <input
                    type="text"
                    name="ticket_price"
                    placeholder="e.g., $25 or Free"
                    value={newEvent.ticket_price}
                    onChange={handleInputChange}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-green-500"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Ticket Link (Optional)
                  </label>
                  <input
                    type="url"
                    name="ticket_link"
                    placeholder="https://tickets.example.com"
                    value={newEvent.ticket_link}
                    onChange={handleInputChange}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-green-500"
                  />
                </div>
              </div>

              <div className="bg-green-100 border border-green-300 rounded-lg p-4">
                <div className="flex items-start">
                  <span className="text-green-500 text-lg mr-2">💰</span>
                  <div>
                    <h4 className="font-semibold text-green-800">Event Listing</h4>
                    <p className="text-sm text-gray-600 mt-2">
                      After creating your event, you'll be redirected to PayPal for payment. Your event will be live immediately after payment confirmation.
                    </p>
                  </div>
                </div>
              </div>

              <div className="flex space-x-4">
                <button
                  type="submit"
                  className="bg-gradient-to-r from-green-600 to-amber-600 hover:from-green-700 hover:to-amber-700 text-white px-6 py-2 rounded-lg font-semibold transition-all"
                >
                  Create Event & Pay $5
                </button>
                <button
                  type="button"
                  onClick={() => setShowCreateForm(false)}
                  className="bg-gray-500 hover:bg-gray-600 text-white px-6 py-2 rounded-lg font-semibold transition-all"
                >
                  Cancel
                </button>
              </div>
            </form>
          </div>
        )}

        {/* Filters */}
        <div className="bg-white rounded-lg shadow-md p-6 mb-8">
          <div className="grid md:grid-cols-3 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Filter by Island
              </label>
              <select
                name="island"
                value={filters.island}
                onChange={handleFilterChange}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-green-500"
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
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-green-500"
              >
                <option value="">All Categories</option>
                {eventCategories.map((category) => (
                  <option key={category} value={category}>{category}</option>
                ))}
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Filter by Date
              </label>
              <input
                type="date"
                name="date"
                value={filters.date}
                onChange={handleFilterChange}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-green-500"
              />
            </div>
          </div>
        </div>

        {/* Events Grid */}
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
          {events.map((event) => (
            <div key={event.id} className="bg-white rounded-xl shadow-lg overflow-hidden hover:shadow-2xl transition-all transform hover:scale-105">
              <div className="p-6">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-xl font-bold text-gray-800">{event.title}</h3>
                  <span className="bg-green-100 text-green-800 px-3 py-1 rounded-full text-sm font-medium">
                    {event.category}
                  </span>
                </div>
                
                <p className="text-gray-600 mb-4 line-clamp-2">{event.description}</p>
                
                <div className="space-y-2 text-sm text-gray-600 mb-4">
                  <div className="flex items-center">
                    <span className="mr-2">📅</span>
                    <span>{new Date(event.event_date).toLocaleDateString()} • {event.start_time} - {event.end_time}</span>
                  </div>
                  <div className="flex items-center">
                    <span className="mr-2">📍</span>
                    <span>{event.location}, {event.island}</span>
                  </div>
                  <div className="flex items-center">
                    <span className="mr-2">👤</span>
                    <span>{event.organizer_name}</span>
                  </div>
                  {event.ticket_price && (
                    <div className="flex items-center">
                      <span className="mr-2">🎫</span>
                      <span>{event.ticket_price}</span>
                    </div>
                  )}
                </div>

                {event.ticket_link && (
                  <a
                    href={event.ticket_link}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="block w-full bg-gradient-to-r from-green-600 to-amber-600 hover:from-green-700 hover:to-amber-700 text-white text-center py-2 rounded-lg transition-all font-medium"
                  >
                    Get Tickets 🎫
                  </a>
                )}
              </div>
            </div>
          ))}
        </div>

        {events.length === 0 && (
          <div className="text-center py-12">
            <div className="text-gray-500 text-xl mb-4">No events found</div>
            <p className="text-gray-400">Try adjusting your filters or be the first to create an event!</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default EventsPage;