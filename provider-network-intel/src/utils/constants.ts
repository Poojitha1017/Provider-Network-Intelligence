export interface CountyInfo {
  name: string;
  fips: string;
}

export const STATE_COUNTY_MAP: Record<string, CountyInfo[]> = {
  "Michigan": [
    { name: "Genesee County", fips: "26049" },
    { name: "Kalamazoo County", fips: "26077" },
    { name: "Macomb County", fips: "26099" },
    { name: "Oakland County", fips: "26125" },
    { name: "Wayne County", fips: "26163" },
  ],
  "North Carolina": [
    { name: "Cumberland County", fips: "37051" },
    { name: "Forsyth County", fips: "37067" },
    { name: "Guilford County", fips: "37081" },
    { name: "Mecklenburg County", fips: "37119" },
    { name: "Wake County", fips: "37183" },
  ],
  "Texas": [
    { name: "Bexar County", fips: "48029" },
    { name: "Collin County", fips: "48085" },
    { name: "Dallas County", fips: "48113" },
    { name: "Harris County", fips: "48201" },
    { name: "Tarrant County", fips: "48439" },
  ],
};

export const STATES_LIST = Object.keys(STATE_COUNTY_MAP).sort();

export const ALL_COUNTIES_LIST = Object.values(STATE_COUNTY_MAP)
  .flat()
  .sort((a, b) => a.name.localeCompare(b.name));
