import React from 'react';
import type { Plant } from '../types';
import { getImageUrl } from '../services/api';
import { Star } from 'lucide-react';

interface Props {
  plants: Plant[];
  favorites: Set<string>; // Set of Botanical Names
  onPlantClick: (plant: Plant) => void;
  onToggleFavorite: (plant: Plant, e: React.MouseEvent) => void;
}

export const PlantGrid: React.FC<Props> = ({ plants, favorites, onPlantClick, onToggleFavorite }) => {
  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6 p-4">
      {plants.map((plant) => (
        <div
          key={plant['Botanical Name']}
          className="bg-white rounded-lg shadow-md hover:shadow-xl transition-shadow cursor-pointer overflow-hidden border border-gray-200 flex flex-col"
          onClick={() => onPlantClick(plant)}
        >
          <div className="relative h-48 w-full bg-gray-200">
            <img
              src={getImageUrl(plant['Image Name'])}
              alt={plant['English Name']}
              className="h-full w-full object-cover"
              loading="lazy"
            />
            <button
              onClick={(e) => {
                e.stopPropagation();
                onToggleFavorite(plant, e);
              }}
              className="absolute top-2 right-2 p-2 bg-white/80 rounded-full hover:bg-white transition-colors"
            >
              <Star
                className={`w-5 h-5 ${
                  favorites.has(plant['Botanical Name'])
                    ? 'fill-yellow-400 text-yellow-400'
                    : 'text-gray-400'
                }`}
              />
            </button>
          </div>
          <div className="p-4 flex-1">
            <h3 className="font-bold text-lg text-gray-900 line-clamp-1">{plant['English Name']}</h3>
            <p className="text-sm text-gray-500 italic mb-2">{plant['Botanical Name']}</p>
            <div className="flex flex-wrap gap-1">
                <span className="text-xs px-2 py-1 bg-green-100 text-green-800 rounded-full">{plant['Plant Family']}</span>
                <span className="text-xs px-2 py-1 bg-blue-100 text-blue-800 rounded-full">{plant['Origin']}</span>
            </div>
          </div>
        </div>
      ))}
    </div>
  );
};
