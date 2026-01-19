import axios from 'axios';
import type { Plant, FilterOptions, FilterState } from '../types';

const API_URL = 'http://localhost:8000/api';

export const fetchFilters = async (): Promise<FilterOptions> => {
  // Add timestamp to prevent caching
  const response = await axios.get(`${API_URL}/filters?t=${new Date().getTime()}`);
  return response.data;
};

export const fetchPlants = async (search: string, filters: FilterState, ids?: string[]): Promise<Plant[]> => {
  const params = new URLSearchParams();
  if (search) params.append('q', search);
  if (ids && ids.length > 0) {
      ids.forEach(id => params.append('ids', id));
  }

  Object.entries(filters).forEach(([key, values]) => {
    values.forEach(value => {
      params.append(key, value);
    });
  });

  const response = await axios.get(`${API_URL}/plants`, { params });
  return response.data;
};

export const getImageUrl = (imageName: string) => {
    return `http://localhost:8000/images/${imageName}`;
}
