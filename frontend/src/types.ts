export interface Plant {
  "English Name": string;
  "Botanical Name": string;
  "Plant Family": string;
  Strata: string;
  Lifecycle: string;
  "Time-to-Maturity": string;
  Lifespan: string;
  Zone: string;
  Origin: string;
  Function: string;
  Spacing: string;
  "Image Name": string;
  "Image Prompt": string;
}

export interface FilterOptions {
  plant_family: string[];
  strata: string[];
  lifecycle: string[];
  time_to_maturity: string[];
  lifespan: string[];
  zone: string[];
  origin: string[];
  function: string[];
  spacing: string[];
}

export interface FilterState {
  plant_family: string[];
  strata: string[];
  lifecycle: string[];
  time_to_maturity: string[];
  lifespan: string[];
  zone: string[];
  origin: string[];
  function: string[];
  spacing: string[];
}
