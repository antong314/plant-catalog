import React from 'react';
import Select from 'react-select';
import type { MultiValue } from 'react-select';
import type { FilterOptions, FilterState } from '../types';

interface Props {
  options: FilterOptions;
  filters: FilterState;
  onFilterChange: (key: keyof FilterState, values: string[]) => void;
}

const FILTER_LABELS: Record<keyof FilterState, string> = {
  plant_family: 'Plant Family',
  strata: 'Strata',
  lifecycle: 'Lifecycle',
  time_to_maturity: 'Time to Maturity',
  lifespan: 'Lifespan',
  zone: 'Zone',
  origin: 'Origin',
  function: 'Function',
  spacing: 'Spacing',
};

export const FilterBar: React.FC<Props> = ({ options, filters, onFilterChange }) => {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 p-4 bg-gray-50 rounded-lg shadow-sm">
      {(Object.keys(options) as Array<keyof FilterOptions>).map((key) => (
        <div key={key} className="flex flex-col">
          <label className="text-sm font-semibold text-gray-700 mb-1">
            {FILTER_LABELS[key]}
          </label>
          <Select
            isMulti
            options={options[key].map((val) => ({ label: val, value: val }))}
            value={filters[key].map((val) => ({ label: val, value: val }))}
            onChange={(newValue: MultiValue<{ label: string; value: string }>) => {
              onFilterChange(
                key,
                newValue.map((v) => v.value)
              );
            }}
            className="basic-multi-select"
            classNamePrefix="select"
            placeholder={`Select ${FILTER_LABELS[key]}...`}
          />
        </div>
      ))}
    </div>
  );
};
