import { useState, useEffect } from 'react';
import type { Plant, FilterOptions, FilterState } from './types';
import { fetchFilters, fetchPlants } from './services/api';
import { FilterBar } from './components/FilterBar';
import { PlantGrid } from './components/PlantGrid';
import { PlantModal } from './components/PlantModal';
import { Search, Loader2 } from 'lucide-react';

import logo from './assets/logo.webp';

function App() {
  console.log('App component rendering');
  // Data State
  const [plants, setPlants] = useState<Plant[]>([]);
  const [filterOptions, setFilterOptions] = useState<FilterOptions | null>(null);
  const [loading, setLoading] = useState(true);

  // Filter State
  const [searchQuery, setSearchQuery] = useState('');
  const [filters, setFilters] = useState<FilterState>({
    plant_family: [],
    strata: [],
    lifecycle: [],
    time_to_maturity: [],
    lifespan: [],
    zone: [],
    origin: [],
    function: [],
    spacing: [],
  });

  // Favorites State
  const [favorites, setFavorites] = useState<Set<string>>(() => {
    const saved = localStorage.getItem('plant_favorites');
    return new Set(saved ? JSON.parse(saved) : []);
  });
  const [showFavoritesOnly, setShowFavoritesOnly] = useState(false);

  // Modal State
  const [selectedPlant, setSelectedPlant] = useState<Plant | null>(null);

  // Load Filters on Mount
  useEffect(() => {
    fetchFilters().then(setFilterOptions).catch(console.error);
  }, []);

  // Load Plants when filters/search change
  useEffect(() => {
    const loadPlants = async () => {
      setLoading(true);
      try {
        const ids = showFavoritesOnly ? Array.from(favorites) : undefined;
        // Optimization: If showing favorites only and we have no favorites, skip fetch
        if (showFavoritesOnly && favorites.size === 0) {
            setPlants([]);
            setLoading(false);
            return;
        }
        
        const data = await fetchPlants(searchQuery, filters, ids);
        setPlants(data);
      } catch (error) {
        console.error('Failed to fetch plants', error);
      } finally {
        setLoading(false);
      }
    };

    // Simple debounce
    const timeoutId = setTimeout(loadPlants, 300);
    return () => clearTimeout(timeoutId);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [searchQuery, filters, showFavoritesOnly]); // Removed favorites from dependency to prevent fetch on toggle

  const visiblePlants = showFavoritesOnly 
    ? plants.filter(p => favorites.has(p['Botanical Name'])) 
    : plants;

  // Save Favorites
  useEffect(() => {
    localStorage.setItem('plant_favorites', JSON.stringify(Array.from(favorites)));
  }, [favorites]);

  const handleToggleFavorite = (plant: Plant, e?: React.MouseEvent) => {
    if (e) e.stopPropagation();
    const id = plant['Botanical Name'];
    setFavorites(prev => {
      const next = new Set(prev);
      if (next.has(id)) next.delete(id);
      else next.add(id);
      return next;
    });
  };

  const handleFilterChange = (key: keyof FilterState, values: string[]) => {
    setFilters(prev => ({ ...prev, [key]: values }));
  };

  const handleToggleFavoritesView = () => {
    const newShowFavoritesOnly = !showFavoritesOnly;
    setShowFavoritesOnly(newShowFavoritesOnly);
    
    if (newShowFavoritesOnly) {
      // Clear all filters when switching to favorites view
      setSearchQuery('');
      setFilters({
        plant_family: [],
        strata: [],
        lifecycle: [],
        time_to_maturity: [],
        lifespan: [],
        zone: [],
        origin: [],
        function: [],
        spacing: [],
      });
    }
  };

  const handleClearFilters = () => {
    setSearchQuery('');
    setFilters({
      plant_family: [],
      strata: [],
      lifecycle: [],
      time_to_maturity: [],
      lifespan: [],
      zone: [],
      origin: [],
      function: [],
      spacing: [],
    });
  };

  const hasActiveFilters = searchQuery.length > 0 || Object.values(filters).some(arr => arr.length > 0);

  return (
    <div className="min-h-screen bg-gray-100 font-sans text-gray-900">
      {/* Header */}
      <header className="bg-emerald-800 text-white p-6 shadow-lg sticky top-0 z-40">
        <div className="container mx-auto flex flex-col md:flex-row justify-between items-center gap-4">
          <div className="w-full md:w-1/3 text-center md:text-left">
             <div className="flex items-center justify-center md:justify-start gap-3">
                <img src={logo} alt="Porvenir Design" className="h-12 w-auto" />
                <div>
                    <h1 className="text-2xl font-bold leading-tight">
                        Tropical Plant Catalog
                    </h1>
                    <p className="text-emerald-200 text-xs">Explore nature's diversity</p>
                </div>
             </div>
          </div>
          
          <div className="flex flex-col sm:flex-row items-center gap-4 w-full md:w-2/3 justify-end">
             <div className="relative w-full sm:max-w-md flex-1">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
                <input 
                    type="text" 
                    placeholder="Search plants..." 
                    className="w-full pl-10 pr-4 py-2 rounded-full bg-white text-gray-900 focus:outline-none focus:ring-2 focus:ring-emerald-400 shadow-inner"
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                />
             </div>
             
             <div className="flex gap-2">
                <button 
                    onClick={handleClearFilters}
                    disabled={!hasActiveFilters}
                    className={`px-4 py-2 rounded-full font-semibold transition-all border whitespace-nowrap ${
                        hasActiveFilters
                        ? 'bg-emerald-700 text-white border-emerald-600 hover:bg-emerald-600 cursor-pointer'
                        : 'bg-emerald-800/50 text-emerald-400 border-emerald-800/50 cursor-not-allowed'
                    }`}
                >
                    Clear Filters
                </button>
                <button 
                    onClick={handleToggleFavoritesView}
                    className={`px-4 py-2 rounded-full font-semibold transition-all border whitespace-nowrap ${
                        showFavoritesOnly 
                        ? 'bg-yellow-400 text-yellow-900 border-yellow-400 shadow-[0_0_10px_rgba(250,204,21,0.5)]' 
                        : 'bg-emerald-700 text-white border-emerald-600 hover:bg-emerald-600'
                    }`}
                >
                    {showFavoritesOnly ? '★ Favorites' : '☆ Favorites'}
                </button>
             </div>
          </div>
        </div>
      </header>

      <main className="container mx-auto p-4 md:p-6 space-y-6">
        {/* Filters */}
        {filterOptions && (
          <FilterBar 
            options={filterOptions} 
            filters={filters} 
            onFilterChange={handleFilterChange} 
          />
        )}

        {/* Content */}
        {loading ? (
           <div className="flex justify-center items-center h-64">
              <Loader2 className="w-12 h-12 text-emerald-600 animate-spin" />
           </div>
        ) : (
            <>
                <div className="flex justify-between items-center px-2">
                    <p className="text-gray-500">
                        Found {visiblePlants.length} plants
                        {showFavoritesOnly && ' in favorites'}
                    </p>
                </div>
                
                {visiblePlants.length > 0 ? (
                    <PlantGrid 
                        plants={visiblePlants} 
                        favorites={favorites}
                        onPlantClick={setSelectedPlant}
                        onToggleFavorite={handleToggleFavorite}
                    />
                ) : (
                    <div className="text-center py-20 bg-white rounded-lg border border-dashed border-gray-300 text-gray-500">
                        {showFavoritesOnly 
                            ? "You haven't added any favorites yet." 
                            : "No plants found matching your criteria."}
                    </div>
                )}
            </>
        )}
      </main>

      <PlantModal 
        plant={selectedPlant}
        isOpen={!!selectedPlant}
        onClose={() => setSelectedPlant(null)}
        isFavorite={selectedPlant ? favorites.has(selectedPlant['Botanical Name']) : false}
        onToggleFavorite={() => selectedPlant && handleToggleFavorite(selectedPlant)}
      />
    </div>
  );
}

export default App;
