import { useEffect, useState } from "react";
import { MapContainer, TileLayer, CircleMarker, Popup } from "react-leaflet";
import DashboardLayout from "../components/DashboardLayout";
import PageHeader from "../components/PageHeader";
import FilterPanel from "../components/FilterPanel";
import MapLegend from "../components/MapLegend";
import AreaPopup from "../components/AreaPopup";
import EmptyState from "../components/EmptyState";
import MapResizeHandler from "../components/MapResizeHandler";
import LoadingState from "../components/LoadingState";
import { riskHex } from "../components/RiskBadge";
import { getAreas, getFilterOptions, type FilterOptionsData } from "../services/api";
import type { Area, FilterState } from "../types";
import { MapPinOff } from "lucide-react";
import TwilioAlertModal from "../components/TwilioAlertModal";
import { STATE_COUNTY_MAP } from "../utils/constants";

const DEFAULT_FILTERS: FilterState = {
  state: "All States",
  county: "All Counties",
  specialty: "All Specialties",
  riskLevel: "All",
};

export default function InteractiveMap() {
  const [filters, setFilters] = useState<FilterState>(DEFAULT_FILTERS);
  const [filterOptions, setFilterOptions] = useState<FilterOptionsData | null>(null);
  const [areas, setAreas] = useState<Area[]>([]);
  const [loading, setLoading] = useState(true);
  const [twilioModalOpen, setTwilioModalOpen] = useState(false);
  const [selectedAreaForTwilio, setSelectedAreaForTwilio] = useState<Area | null>(null);


  // 1. Fetch dependent filter options dynamically whenever selected filters change
  useEffect(() => {
    let active = true;
    getFilterOptions({
      state: filters.state,
      county_fips: filters.county,
      specialty: filters.specialty,
      risk_level: filters.riskLevel,
    })
      .then((data) => {
        if (active) setFilterOptions(data);
      })
      .catch((err) => console.error("Error loading filter options:", err));

    return () => {
      active = false;
    };
  }, [filters.state, filters.county, filters.specialty, filters.riskLevel]);

  // 2. Fetch map area markers dynamically whenever filters change
  useEffect(() => {
    let active = true;
    setLoading(true);

    let countyParam = filters.county;
    if (filters.county && filters.county !== "All Counties") {
      const allCounties = Object.values(STATE_COUNTY_MAP).flat();
      const match = allCounties.find((c) => c.name === filters.county);
      if (match) {
        countyParam = match.fips;
      }
    }

    getAreas({
      state: filters.state,
      county: countyParam,
      specialty: filters.specialty,
      riskLevel: filters.riskLevel,
    })
      .then((data) => {
        if (active) {
          setAreas(data);
          setLoading(false);
        }
      })
      .catch((err) => {
        console.error("Error fetching map areas:", err);
        if (active) setLoading(false);
      });

    return () => {
      active = false;
    };
  }, [filters]);

  function handleChange(key: string, value: string) {
    setFilters((prev) => {
      const next = { ...prev, [key]: value } as FilterState;
      if (key === "state") next.county = "All Counties"; // reset dependent filter
      return next;
    });
  }

  function handleReset() {
    setFilters(DEFAULT_FILTERS);
  }

  const stateOptions = ["All States", ...Object.keys(STATE_COUNTY_MAP)];
  const countyOptions = ["All Counties"];
  if (filters.state && filters.state !== "All States") {
    const counties = STATE_COUNTY_MAP[filters.state] || [];
    countyOptions.push(...counties.map((c) => c.name));
  } else {
    const allCounties = Object.values(STATE_COUNTY_MAP).flat();
    countyOptions.push(...Array.from(new Set(allCounties.map((c) => c.name))));
  }

  const specialtyOptions = ["All Specialties", ...(filterOptions?.specialties ?? [])];
  const riskOptions = [
    "All",
    ...(filterOptions?.risk_levels.map((r) => r.replace(" GAP", "").charAt(0).toUpperCase() + r.replace(" GAP", "").slice(1).toLowerCase()) ?? [
      "Low",
      "Medium",
      "High",
      "Critical",
    ]),
  ];

  const center: [number, number] = areas.length > 0 ? [areas[0].latitude, areas[0].longitude] : [37.5, -96];

  return (
    <DashboardLayout
      title="Explore Network"
      subtitle="Visualize provider availability, identify geographic access gaps, and pinpoint areas with the greatest network needs."
    >
      <PageHeader
        title="Provider Access & Risk Map"
        description="Visualize provider availability, identify geographic access gaps, and pinpoint areas with the greatest network needs."
      />

      <div className="mb-4">
        <FilterPanel
          fields={[
            { key: "state", label: "State", options: stateOptions },
            { key: "county", label: "County / Area", options: countyOptions },
            { key: "specialty", label: "Specialty", options: specialtyOptions },
            { key: "riskLevel", label: "Risk Level", options: Array.from(new Set(riskOptions)) },
          ]}
          values={filters as unknown as Record<string, string>}
          onChange={handleChange}
          onReset={handleReset}
          resultCount={areas.length}
        />
      </div>

      <div className="relative overflow-hidden rounded-2xl border border-surface-border shadow-card">
        {loading ? (
          <div className="flex h-[600px] items-center justify-center bg-surface">
            <LoadingState label="Loading network access map..." />
          </div>
        ) : areas.length === 0 ? (
          <EmptyState
            icon={MapPinOff}
            title="No areas match these filters"
            description="Try widening your filters — for example, choose a broader state or set risk level back to All."
            action={
              <button
                onClick={handleReset}
                className="rounded-lg bg-brand-600 px-4 py-2 text-sm font-semibold text-white hover:bg-brand-700"
              >
                Reset filters
              </button>
            }
          />
        ) : (
          <div className="relative h-[600px] w-full">
            <MapContainer center={center} zoom={5} scrollWheelZoom className="h-full w-full">
              <TileLayer
                attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
                url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
              />
              <MapResizeHandler />
              {areas.map((area) => (
                <CircleMarker
                  key={area.id}
                  center={[area.latitude, area.longitude]}
                  radius={10}
                  pathOptions={{
                    color: "#ffffff",
                    weight: 2,
                    fillColor: riskHex(area.riskLevel),
                    fillOpacity: 0.9,
                  }}
                >
                  <Popup minWidth={280} maxWidth={320}>
                    <AreaPopup
                      area={area}
                      onTwilioClick={(a) => {
                        setSelectedAreaForTwilio(a);
                        setTwilioModalOpen(true);
                      }}
                    />
                  </Popup>
                </CircleMarker>
              ))}
            </MapContainer>
            <div className="pointer-events-none absolute bottom-4 left-4 z-[400]">
              <div className="pointer-events-auto">
                <MapLegend />
              </div>
            </div>
          </div>
        )}
      </div>

      <TwilioAlertModal
        isOpen={twilioModalOpen}
        onClose={() => setTwilioModalOpen(false)}
        defaultCountyName={selectedAreaForTwilio?.name}
        defaultSpecialty={selectedAreaForTwilio?.primarySpecialty}
        defaultGapLevel={selectedAreaForTwilio ? `${selectedAreaForTwilio.riskScore}% Risk` : undefined}
      />
    </DashboardLayout>
  );
}

