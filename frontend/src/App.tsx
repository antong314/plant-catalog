import { useState, useEffect } from 'react';
import type { Plant, FilterOptions, FilterState } from './types';
import { fetchFilters, fetchPlants } from './services/api';
import { FilterBar } from './components/FilterBar';
import { PlantGrid } from './components/PlantGrid';
import { PlantModal } from './components/PlantModal';
import { Search, Loader2 } from 'lucide-react';

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
        if (showFavoritesOnly && favorites.size === 0) {
            setPlants([]);
            setLoading(false);
            return;
        }
        
        const ids = showFavoritesOnly ? Array.from(favorites) : undefined;
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
  }, [searchQuery, filters, showFavoritesOnly, favorites]);

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

  return (
    <div className="min-h-screen bg-gray-100 font-sans text-gray-900">
      {/* Header */}
      <header className="bg-emerald-800 text-white p-6 shadow-lg sticky top-0 z-40">
        <div className="container mx-auto flex flex-col md:flex-row justify-between items-center gap-4">
          <div>
             <h1 className="text-3xl font-bold flex items-center gap-2">
                🌿 Tropical Plant Catalog
             </h1>
             <p className="text-emerald-200 text-sm mt-1">Explore nature's diversity</p>
          </div>
          
          <div className="flex items-center gap-4 w-full md:w-auto">
             <div className="relative w-full md:w-64">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
                <input 
                    type="text" 
                    placeholder="Search plants..." 
                    className="w-full pl-10 pr-4 py-2 rounded-full bg-white text-gray-900 focus:outline-none focus:ring-2 focus:ring-emerald-400 shadow-inner"
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                />
             </div>
             <button 
                onClick={() => setShowFavoritesOnly(!showFavoritesOnly)}
                className={`px-4 py-2 rounded-full font-semibold transition-all border ${
                    showFavoritesOnly 
                    ? 'bg-yellow-400 text-yellow-900 border-yellow-400 shadow-[0_0_10px_rgba(250,204,21,0.5)]' 
                    : 'bg-emerald-700 text-white border-emerald-600 hover:bg-emerald-600'
                }`}
             >
                {showFavoritesOnly ? '★ Favorites' : '☆ Favorites'}
             </button>
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
                        Found {plants.length} plants
                        {showFavoritesOnly && ' in favorites'}
                    </p>
                </div>
                
                {plants.length > 0 ? (
                    <PlantGrid 
                        plants={plants} 
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
