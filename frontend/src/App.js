import React, { useState, useEffect } from "react";
import "./App.css";
import axios from "axios";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Debug logging
console.log('BACKEND_URL:', BACKEND_URL);
console.log('API base:', API);

// Token management
const getToken = () => localStorage.getItem('authToken');
const setToken = (token) => localStorage.setItem('authToken', token);
const removeToken = () => localStorage.removeItem('authToken');

// Components
const LoginForm = ({ onLogin }) => {
  const [isLogin, setIsLogin] = useState(true);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      const endpoint = isLogin ? '/auth/login' : '/auth/register';
      const fullUrl = `${API}${endpoint}`;
      console.log('Attempting request to:', fullUrl);
      console.log('Request data:', { email, password: '***' });
      
      const response = await axios.post(fullUrl, { email, password });
      console.log('Response status:', response.status);
      console.log('Response data:', response.data);
      
      setToken(response.data.access_token);
      onLogin();
    } catch (err) {
      console.error('Authentication error:', err);
      console.error('Error response:', err.response);
      console.error('Error message:', err.message);
      console.error('Error status:', err.response?.status);
      console.error('Error data:', err.response?.data);
      
      let errorMessage = 'Authentication failed';
      if (err.response?.data?.detail) {
        errorMessage = err.response.data.detail;
      } else if (err.response?.status) {
        errorMessage = `Server error: ${err.response.status}`;
      } else if (err.message) {
        errorMessage = `Network error: ${err.message}`;
      }
      
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center px-4">
      <div className="max-w-md w-full bg-white rounded-xl shadow-lg p-8">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-gray-900">LinkShare</h1>
          <p className="text-gray-600 mt-2">Your personal link collection</p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Email
            </label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Password
            </label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              required
            />
          </div>

          {error && (
            <div className="text-red-600 text-sm text-center bg-red-50 p-3 rounded-lg">
              <div className="font-semibold">Authentication Error:</div>
              <div>{error}</div>
              <div className="text-xs mt-2 text-gray-600">
                Check browser console for more details.
              </div>
            </div>
          )}

          <button
            type="submit"
            disabled={loading}
            className="w-full bg-blue-600 text-white py-3 px-4 rounded-lg hover:bg-blue-700 disabled:opacity-50 font-medium"
          >
            {loading ? 'Please wait...' : (isLogin ? 'Sign In' : 'Sign Up')}
          </button>

          <div className="text-center">
            <button
              type="button"
              onClick={() => setIsLogin(!isLogin)}
              className="text-blue-600 hover:text-blue-700 text-sm"
            >
              {isLogin ? "Don't have an account? Sign up" : "Already have an account? Sign in"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

const LinkCard = ({ link, onDelete }) => {
  const handleDelete = async () => {
    if (window.confirm('Are you sure you want to delete this link?')) {
      try {
        await axios.delete(`${API}/links/${link.id}`, {
          headers: { Authorization: `Bearer ${getToken()}` }
        });
        onDelete(link.id);
      } catch (err) {
        alert('Failed to delete link');
      }
    }
  };

  return (
    <div className="bg-white rounded-xl shadow-lg overflow-hidden hover:shadow-xl transition-shadow duration-300">
      {link.image_url && (
        <img
          src={link.image_url}
          alt={link.title || 'Link preview'}
          className="w-full h-48 object-cover"
          onError={(e) => {
            e.target.style.display = 'none';
          }}
        />
      )}
      
      <div className="p-6">
        <h3 className="text-xl font-semibold text-gray-900 mb-2 line-clamp-2">
          {link.title || 'Untitled Link'}
        </h3>
        
        {link.description && (
          <p className="text-gray-600 mb-4 line-clamp-3">
            {link.description}
          </p>
        )}
        
        <div className="flex items-center justify-between">
          <a
            href={link.url}
            target="_blank"
            rel="noopener noreferrer"
            className="text-blue-600 hover:text-blue-700 text-sm font-medium truncate flex-1 Mr-4"
          >
            {link.url}
          </a>
          
          <button
            onClick={handleDelete}
            className="text-red-500 hover:text-red-700 p-2 rounded-lg hover:bg-red-50"
            title="Delete link"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
            </svg>
          </button>
        </div>
        
        <div className="text-xs text-gray-400 mt-3">
          Added {new Date(link.created_at).toLocaleDateString()}
        </div>
      </div>
    </div>
  );
};

const AddLinkForm = ({ onAdd }) => {
  const [url, setUrl] = useState('');
  const [loading, setLoading] = useState(false);
  const [extracting, setExtracting] = useState(false);

  const extractMetadata = async (url) => {
    setExtracting(true);
    try {
      // Try server-side extraction first (more reliable)
      const response = await axios.post(`${API}/links/extract-metadata`, { url }, {
        headers: { Authorization: `Bearer ${getToken()}` }
      });
      
      return {
        title: response.data.title || '',
        description: response.data.description || '',
        image_url: response.data.image_url || ''
      };
    } catch (error) {
      console.log('Server-side metadata extraction failed, trying client-side fallback');
      
      try {
        // Fallback to client-side extraction
        const response = await fetch(`https://api.allorigins.win/get?url=${encodeURIComponent(url)}`);
        const data = await response.json();
        const html = data.contents;
        
        const parser = new DOMParser();
        const doc = parser.parseFromString(html, 'text/html');
        
        const title = doc.querySelector('meta[property="og:title"]')?.content ||
                     doc.querySelector('title')?.textContent ||
                     '';
        
        const description = doc.querySelector('meta[property="og:description"]')?.content ||
                           doc.querySelector('meta[name="description"]')?.content ||
                           '';
        
        const image = doc.querySelector('meta[property="og:image"]')?.content ||
                     doc.querySelector('meta[name="twitter:image"]')?.content ||
                     '';
        
        return { title, description, image_url: image };
      } catch (clientError) {
        console.log('Client-side metadata extraction also failed, using URL only');
        return { title: '', description: '', image_url: '' };
      }
    } finally {
      setExtracting(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      const metadata = await extractMetadata(url);
      
      const linkData = {
        url,
        title: metadata.title,
        description: metadata.description,
        image_url: metadata.image_url
      };

      const response = await axios.post(`${API}/links`, linkData, {
        headers: { Authorization: `Bearer ${getToken()}` }
      });

      onAdd(response.data);
      setUrl('');
    } catch (err) {
      alert('Failed to add link');
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="bg-white rounded-xl shadow-lg p-6 mb-8">
      <div className="flex gap-3">
        <input
          type="url"
          value={url}
          onChange={(e) => setUrl(e.target.value)}
          placeholder="Enter a URL to save..."
          className="flex-1 px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          required
        />
        <button
          type="submit"
          disabled={loading || extracting}
          className="bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 disabled:opacity-50 font-medium"
        >
          {loading ? (extracting ? 'Extracting...' : 'Adding...') : 'Add Link'}
        </button>
      </div>
    </form>
  );
};

const Dashboard = ({ onLogout }) => {
  const [links, setLinks] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchLinks();
  }, []);

  const fetchLinks = async () => {
    try {
      const response = await axios.get(`${API}/links`, {
        headers: { Authorization: `Bearer ${getToken()}` }
      });
      setLinks(response.data);
    } catch (err) {
      console.error('Failed to fetch links');
    } finally {
      setLoading(false);
    }
  };

  const handleAddLink = (newLink) => {
    setLinks([newLink, ...links]);
  };

  const handleDeleteLink = (linkId) => {
    setLinks(links.filter(link => link.id !== linkId));
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <nav className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <h1 className="text-2xl font-bold text-gray-900">LinkShare</h1>
            <button
              onClick={onLogout}
              className="text-gray-600 hover:text-gray-900 font-medium"
            >
              Sign Out
            </button>
          </div>
        </div>
      </nav>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <AddLinkForm onAdd={handleAddLink} />

        {loading ? (
          <div className="text-center py-12">
            <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
            <p className="mt-4 text-gray-600">Loading your links...</p>
          </div>
        ) : links.length === 0 ? (
          <div className="text-center py-12">
            <svg className="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1" />
            </svg>
            <h3 className="mt-4 text-lg font-medium text-gray-900">No links yet</h3>
            <p className="mt-2 text-gray-600">Start by adding your first link above!</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {links.map((link) => (
              <LinkCard
                key={link.id}
                link={link}
                onDelete={handleDeleteLink}
              />
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const token = getToken();
    if (token) {
      // Verify token is still valid
      axios.get(`${API}/auth/me`, {
        headers: { Authorization: `Bearer ${token}` }
      })
      .then(() => setIsAuthenticated(true))
      .catch(() => removeToken())
      .finally(() => setLoading(false));
    } else {
      setLoading(false);
    }
  }, []);

  const handleLogin = () => {
    setIsAuthenticated(true);
  };

  const handleLogout = () => {
    removeToken();
    setIsAuthenticated(false);
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="App">
      {isAuthenticated ? (
        <Dashboard onLogout={handleLogout} />
      ) : (
        <LoginForm onLogin={handleLogin} />
      )}
    </div>
  );
}

export default App;