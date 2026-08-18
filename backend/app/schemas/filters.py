from typing import List, Optional
from pydantic import BaseModel, Field


class CountyOption(BaseModel):
    county_fips: str = Field(..., description="County FIPS Code")
    county_name: Optional[str] = Field(None, description="County Name")
    state: Optional[str] = Field(None, description="State Name or Code")


class FilterOptionsResponse(BaseModel):
    states: List[str] = Field(default_factory=list, description="List of unique state names")
    cities: List[str] = Field(default_factory=list, description="List of unique city names")
    county_fips_list: List[str] = Field(default_factory=list, description="List of unique county FIPS codes")
    counties: List[CountyOption] = Field(default_factory=list, description="List of county objects")
    diseases: List[str] = Field(default_factory=list, description="List of unique diseases")
    specialties: List[str] = Field(default_factory=list, description="List of unique specialties")
    risk_levels: List[str] = Field(default_factory=list, description="List of unique risk levels")
