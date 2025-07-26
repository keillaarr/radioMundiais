import React, { useState, useEffect, useRef } from "react";
import "./App.css";
import axios from "axios";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

function App() {
  const [stations, setStations] = useState([]);
  const [countries, setCountries] = useState([]);
  const [loading, setLoading] = useState(false);
  const [currentStation, setCurrentStation] = useState(null);
  const [isPlaying, setIsPlaying] = useState(false);
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedCountry, setSelectedCountry] = useState("");
  const [favorites, setFavorites] = useState([]);
  const [showFavorites, setShowFavorites] = useState(false);
  
  const audioRef = useRef(null);

  // Load initial data
  useEffect(() => {
    loadStations();
    loadCountries();
    loadFavorites();
  }, []);

  const loadStations = async (country = "", query = "") => {
    setLoading(true);
    try {
      const params = new URLSearchParams();
      if (country) params.append('country', country);
      if (query) params.append('name', query);
      params.append('limit', '50');
      
      const response = await axios.get(`${API}/stations?${params}`);
      setStations(response.data);
    } catch (error) {
      console.error('Error loading stations:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadCountries = async () => {
    try {
      const response = await axios.get(`${API}/countries`);
      setCountries(response.data.slice(0, 50)); // Limit to top 50 countries
    } catch (error) {
      console.error('Error loading countries:', error);
    }
  };

  const loadFavorites = async () => {
    try {
      const response = await axios.get(`${API}/favorites`);
      setFavorites(response.data);
    } catch (error) {
      console.error('Error loading favorites:', error);
    }
  };

  const handleSearch = () => {
    loadStations(selectedCountry, searchQuery);
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter') {
      handleSearch();
    }
  };

  const playStation = (station) => {
    if (currentStation?.stationuuid === station.stationuuid && isPlaying) {
      // Pause current station
      audioRef.current.pause();
      setIsPlaying(false);
    } else {
      // Play new station
      setCurrentStation(station);
      if (audioRef.current) {
        audioRef.current.src = station.url;
        audioRef.current.play().then(() => {
          setIsPlaying(true);
        }).catch(error => {
          console.error('Error playing station:', error);
          alert('Não foi possível reproduzir esta rádio. Tente outra.');
        });
      }
    }
  };

  const toggleFavorite = async (station) => {
    const isFavorited = favorites.some(f => f.station_uuid === station.stationuuid);
    
    try {
      if (isFavorited) {
        await axios.delete(`${API}/favorites/${station.stationuuid}`);
        setFavorites(favorites.filter(f => f.station_uuid !== station.stationuuid));
      } else {
        const favoriteData = {
          station_uuid: station.stationuuid,
          station_name: station.name,
          station_url: station.url,
          country: station.country
        };
        const response = await axios.post(`${API}/favorites`, favoriteData);
        setFavorites([...favorites, response.data]);
      }
    } catch (error) {
      console.error('Error toggling favorite:', error);
    }
  };

  const isFavorited = (station) => {
    return favorites.some(f => f.station_uuid === station.stationuuid);
  };

  const displayStations = showFavorites ? 
    stations.filter(station => isFavorited(station)) : 
    stations;

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-900 via-blue-900 to-indigo-900">
      {/* Header */}
      <header className="bg-black/20 backdrop-blur-md border-b border-white/10">
        <div className="container mx-auto px-4 py-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="w-12 h-12 bg-gradient-to-r from-pink-500 to-violet-500 rounded-full flex items-center justify-center">
                <svg className="w-6 h-6 text-white" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M9.383 3.076A1 1 0 0110 4v12a1 1 0 01-1.617.776l-4.5-3.5A1 1 0 013 12.5v-5a1 1 0 01.383-.776l4.5-3.5z" clipRule="evenodd" />
                  <path d="M14.657 2.929a1 1 0 011.414 0A9.972 9.972 0 0119 10a9.972 9.972 0 01-2.929 7.071 1 1 0 01-1.414-1.414A7.971 7.971 0 0017 10c0-2.21-.894-4.208-2.343-5.657a1 1 0 010-1.414zm-2.829 2.828a1 1 0 011.415 0A5.983 5.983 0 0115 10a5.983 5.983 0 01-1.757 4.243 1 1 0 01-1.415-1.414A3.984 3.984 0 0013 10a3.984 3.984 0 00-1.172-2.829 1 1 0 010-1.414z" />
                </svg>
              </div>
              <div>
                <h1 className="text-3xl font-bold text-white">World Radio</h1>
                <p className="text-blue-200">Rádios do mundo inteiro</p>
              </div>
            </div>
            
            <button
              onClick={() => setShowFavorites(!showFavorites)}
              className={`px-4 py-2 rounded-lg transition-all duration-200 ${
                showFavorites 
                  ? 'bg-pink-500 text-white' 
                  : 'bg-white/10 text-white hover:bg-white/20'
              }`}
            >
              ❤️ Favoritas ({favorites.length})
            </button>
          </div>
        </div>
      </header>

      {/* Search Controls */}
      <div className="container mx-auto px-4 py-6">
        <div className="bg-white/10 backdrop-blur-md rounded-xl p-6 border border-white/20">
          <div className="flex flex-col md:flex-row gap-4">
            <div className="flex-1">
              <input
                type="text"
                placeholder="Buscar rádios..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                onKeyPress={handleKeyPress}
                className="w-full px-4 py-3 bg-white/10 border border-white/20 rounded-lg text-white placeholder-white/60 focus:outline-none focus:ring-2 focus:ring-pink-500"
              />
            </div>
            
            <select
              value={selectedCountry}
              onChange={(e) => setSelectedCountry(e.target.value)}
              className="px-4 py-3 bg-white/10 border border-white/20 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-pink-500"
            >
              <option value="">Todos os países</option>
              {countries.map((country) => (
                <option key={country.iso_3166_1} value={country.name} className="text-black">
                  {country.name} ({country.stationcount})
                </option>
              ))}
            </select>
            
            <button
              onClick={handleSearch}
              disabled={loading}
              className="px-6 py-3 bg-gradient-to-r from-pink-500 to-violet-500 text-white rounded-lg hover:from-pink-600 hover:to-violet-600 transition-all duration-200 disabled:opacity-50"
            >
              {loading ? 'Buscando...' : 'Buscar'}
            </button>
          </div>
        </div>
      </div>

      {/* Current Playing */}
      {currentStation && (
        <div className="container mx-auto px-4 pb-6">
          <div className="bg-gradient-to-r from-pink-500/20 to-violet-500/20 backdrop-blur-md rounded-xl p-6 border border-pink-500/30">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-4">
                <div className="w-16 h-16 bg-gradient-to-r from-pink-500 to-violet-500 rounded-full flex items-center justify-center">
                  {isPlaying ? (
                    <div className="flex space-x-1">
                      <div className="w-1 h-8 bg-white animate-pulse"></div>
                      <div className="w-1 h-6 bg-white animate-pulse" style={{animationDelay: '0.1s'}}></div>
                      <div className="w-1 h-4 bg-white animate-pulse" style={{animationDelay: '0.2s'}}></div>
                    </div>
                  ) : (
                    <svg className="w-8 h-8 text-white" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM9.555 7.168A1 1 0 008 8v4a1 1 0 001.555.832l3-2a1 1 0 000-1.664l-3-2z" clipRule="evenodd" />
                    </svg>
                  )}
                </div>
                <div>
                  <h3 className="text-xl font-bold text-white">{currentStation.name}</h3>
                  <p className="text-blue-200">{currentStation.country} • {currentStation.bitrate}kbps</p>
                </div>
              </div>
              
              <div className="flex space-x-2">
                <button
                  onClick={() => toggleFavorite(currentStation)}
                  className={`p-2 rounded-full transition-all duration-200 ${
                    isFavorited(currentStation) 
                      ? 'text-pink-400 hover:text-pink-300' 
                      : 'text-white/60 hover:text-white'
                  }`}
                >
                  ❤️
                </button>
                <button
                  onClick={() => playStation(currentStation)}
                  className="p-2 bg-white/20 hover:bg-white/30 rounded-full text-white transition-all duration-200"
                >
                  {isPlaying ? '⏸️' : '▶️'}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Stations Grid */}
      <div className="container mx-auto px-4 pb-8">
        {loading ? (
          <div className="text-center py-12">
            <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-pink-500"></div>
            <p className="text-white mt-4">Carregando rádios...</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
            {displayStations.map((station) => (
              <div key={station.stationuuid} className="bg-white/10 backdrop-blur-md rounded-xl p-6 border border-white/20 hover:bg-white/20 transition-all duration-200">
                <div className="flex items-start justify-between mb-4">
                  <div className="flex-1">
                    {station.favicon && (
                      <img 
                        src={station.favicon} 
                        alt="" 
                        className="w-12 h-12 rounded-lg mb-3 bg-white/10"
                        onError={(e) => e.target.style.display = 'none'}
                      />
                    )}
                    <h3 className="font-bold text-white text-lg mb-2 line-clamp-2">{station.name}</h3>
                    <div className="space-y-1 text-sm text-blue-200">
                      {station.country && <p>🌍 {station.country}</p>}
                      {station.language && <p>🗣️ {station.language}</p>}
                      {station.bitrate > 0 && <p>📻 {station.bitrate}kbps</p>}
                      {station.codec && <p>🎵 {station.codec}</p>}
                    </div>
                  </div>
                </div>
                
                <div className="flex space-x-2">
                  <button
                    onClick={() => playStation(station)}
                    className={`flex-1 py-2 px-4 rounded-lg transition-all duration-200 ${
                      currentStation?.stationuuid === station.stationuuid && isPlaying
                        ? 'bg-pink-500 text-white'
                        : 'bg-gradient-to-r from-pink-500 to-violet-500 hover:from-pink-600 hover:to-violet-600 text-white'
                    }`}
                  >
                    {currentStation?.stationuuid === station.stationuuid && isPlaying ? '⏸️ Pausar' : '▶️ Tocar'}
                  </button>
                  
                  <button
                    onClick={() => toggleFavorite(station)}
                    className={`p-2 rounded-lg transition-all duration-200 ${
                      isFavorited(station)
                        ? 'bg-pink-500 text-white'
                        : 'bg-white/20 text-white hover:bg-white/30'
                    }`}
                  >
                    ❤️
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
        
        {!loading && displayStations.length === 0 && (
          <div className="text-center py-12">
            <div className="text-6xl mb-4">📻</div>
            <p className="text-white text-xl">
              {showFavorites ? 'Nenhuma rádio favoritada ainda' : 'Nenhuma rádio encontrada'}
            </p>
            <p className="text-blue-200 mt-2">
              {showFavorites ? 'Adicione algumas rádios aos favoritos!' : 'Tente buscar por outro termo ou país'}
            </p>
          </div>
        )}
      </div>

      {/* Audio Element */}
      <audio 
        ref={audioRef} 
        onEnded={() => setIsPlaying(false)}
        onError={() => {
          setIsPlaying(false);
          console.error('Audio error');
        }}
      />
    </div>
  );
}

export default App;