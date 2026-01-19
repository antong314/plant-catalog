import React, { useEffect } from 'react';
import type { Plant } from '../types';
import { getImageUrl } from '../services/api';
import { X, Star } from 'lucide-react';

interface Props {
  plant: Plant | null;
  isOpen: boolean;
  onClose: () => void;
  isFavorite: boolean;
  onToggleFavorite: () => void;
}

export const PlantModal: React.FC<Props> = ({ plant, isOpen, onClose, isFavorite, onToggleFavorite }) => {
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape') onClose();
    };

    if (isOpen) {
      window.addEventListener('keydown', handleKeyDown);
    }
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [isOpen, onClose]);

  if (!isOpen || !plant) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50 backdrop-blur-sm" onClick={onClose}>
      <div 
        className="bg-white rounded-xl shadow-2xl max-w-6xl w-full max-h-[95vh] overflow-y-auto flex flex-col md:flex-row" 
        onClick={e => e.stopPropagation()}
      >
        <div className="md:w-3/5 relative bg-gray-100 flex items-center justify-center">
          <img
            src={getImageUrl(plant['Image Name'])}
            alt={plant['English Name']}
            className="w-full h-auto max-h-[90vh] object-contain"
          />
           <button
            onClick={onClose}
            className="absolute top-4 left-4 p-2 bg-black/50 text-white rounded-full hover:bg-black/70 md:hidden"
          >
            <X className="w-6 h-6" />
          </button>
        </div>
        
        <div className="md:w-2/5 p-6 md:p-8 flex flex-col">
          <div className="flex justify-between items-start mb-6">
            <div>
              <h2 className="text-3xl font-bold text-gray-900">{plant['English Name']}</h2>
              <p className="text-xl text-gray-600 italic">{plant['Botanical Name']}</p>
            </div>
            <div className="flex gap-2">
                <button
                    onClick={onToggleFavorite}
                    className="p-2 hover:bg-gray-100 rounded-full transition-colors"
                    title="Toggle Favorite"
                >
                    <Star
                    className={`w-8 h-8 ${
                        isFavorite
                        ? 'fill-yellow-400 text-yellow-400'
                        : 'text-gray-300'
                    }`}
                    />
                </button>
                <button
                    onClick={onClose}
                    className="p-2 hover:bg-gray-100 rounded-full transition-colors hidden md:block"
                >
                    <X className="w-8 h-8 text-gray-500" />
                </button>
            </div>
          </div>

          <div className="space-y-4 flex-1">
            <InfoRow label="Family" value={plant['Plant Family']} />
            <InfoRow label="Origin" value={plant['Origin']} />
            <InfoRow label="Zone" value={plant['Zone']} />
            <InfoRow label="Strata" value={plant['Strata']} />
            <InfoRow label="Lifecycle" value={plant['Lifecycle']} />
            <InfoRow label="Time to Maturity" value={plant['Time-to-Maturity']} />
            <InfoRow label="Lifespan" value={plant['Lifespan']} />
            <InfoRow label="Function" value={plant['Function']} />
            <InfoRow label="Spacing" value={plant['Spacing']} />
          </div>
        </div>
      </div>
    </div>
  );
};

const InfoRow: React.FC<{ label: string; value: string }> = ({ label, value }) => (
  <div className="flex border-b border-gray-100 last:border-0 py-2">
    <span className="w-1/3 font-semibold text-gray-600">{label}</span>
    <span className="w-2/3 text-gray-900">{value}</span>
  </div>
);
