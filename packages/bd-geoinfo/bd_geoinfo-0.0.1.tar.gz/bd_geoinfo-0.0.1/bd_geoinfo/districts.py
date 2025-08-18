import json
import os

class District:
    """
    District class to manage and retrieve information about districts from a JSON data source.

    Usage Example:
        dist = District("Barishal")
        print(dist.get_name())
        print(dist.get_area(unit="mile"))
        print(dist.has_district())
    """

    __data = None  # Class variable to hold loaded data

    def __init__(self, district_name: str):
        """
        Initialize a District object using a district name (English or Bangla).

        The constructor automatically loads all district data from the JSON file (only once)
        and sets the current district's information if found.

        :param district_name: Name of the district (English or Bangla).
        """
        self.name = district_name.strip()
        if District.__data is None:
            District.__data = self._load_data()
        self.district_data = self._get_district_data()

    @classmethod
    def _data_file(cls):
        """
        Returns the absolute path of the districts.json file inside the 'data' folder.

        :return: Full file path (string).
        """
        current_dir = os.path.dirname(__file__)
        return os.path.join(current_dir, "data", "districts.json")

    @classmethod
    def _load_data(cls):
        """
        Loads district data from the JSON file into memory.

        This method is called only once per program run (data is cached in __data).

        :return: Parsed JSON data (dict).
        """
        file_path = cls._data_file()
        with open(file_path, "r", encoding="utf-8") as file:
            return json.load(file)

    @classmethod
    def get_all_districts_info(cls) -> dict:
        """
        Returns the complete JSON data for all districts.

        :return: Dictionary containing all districts data.
        """
        if cls.__data is None:
            cls.__data = cls._load_data()
        return cls.__data

    @classmethod
    def get_district_names(cls, bn: bool = False) -> list:
        """
        Returns a list of all district names.

        :param bn: If True, returns Bangla names, otherwise English names.
        :return: List of district names in the requested language.
        """
        if cls.__data is None:
            cls.__data = cls._load_data()
        
        districts = cls.__data.get("districts", [])
        names = []
        for dist in districts:
            if dist is None:
                continue
            names.append(dist["bn_name"] if bn else dist["name"])
        return names

    def _get_district_data(self) -> dict | None:
        """
        Finds and returns the JSON dictionary for the current district instance.

        Matching is done by either English name (case-insensitive) or Bangla name.

        :return: Dictionary of district data, or None if not found.
        """
        data = self.get_all_districts_info()
        districts_list = data.get("districts", [])
        if not districts_list:
            return None

        for dist in districts_list:
            if dist is None:
                continue
            name_en = dist.get("name", "").strip().lower()
            name_bn = dist.get("bn_name", "").strip()
            if self.name.lower() == name_en or self.name == name_bn:
                return dist
        return None

    def has_district(self) -> bool:
        """
        Checks if the current district exists in the dataset.

        :return: True if district is found, otherwise False.
        """
        return self.district_data is not None

    def get_name(self, bn: bool = False) -> str:
        """
        Returns the district name.

        :param bn: If True, returns Bangla name; otherwise English name.
        :return: District name (string).
        """
        if not self.district_data:
            return ""
        return self.district_data["bn_name"] if bn else self.district_data["name"]

    def get_id(self) -> int | None:
        """
        Returns the district's unique ID.

        :return: District ID (int) or None if not available.
        """
        if not self.district_data:
            return None
        return self.district_data.get("id")

    def get_lat_long(self) -> list:
        """
        Returns the geographical coordinates of the district.

        :return: [latitude, longitude] as strings, or empty list if not found.
        """
        if not self.district_data:
            return []
        return [self.district_data['lat'], self.district_data['long']]

    def get_area(self, unit: str = "km") -> dict | None:
        """
        Returns the area of the district in km² or mi².

        :param unit: "km" for square kilometers (default) or "mile" for square miles.
        :return: Dictionary with 'unit' and 'value', or None if area not found.
        """
        if not self.district_data:
            return None
        area_km2 = self.district_data.get("area_km2")
        if area_km2 is None:
            return None
        if unit.lower() == "mile":
            return {"unit": "mile", "value": round(area_km2 * 0.386102, 2)}
        return {"unit": "km", "value": area_km2}

    def get_population(self) -> dict | None:
        """
        Returns the population of the district along with the reference year.

        :return: Dictionary with 'population' and 'population_year', or None if missing.
        """
        if not self.district_data:
            return None
        return {
            "population": self.district_data.get("population"),
            "population_year": self.district_data.get("population_year")
        }

    def get_map(self) -> str:
        """
        Returns a simple Google Maps-like string using latitude and longitude.

        Example: "map:22.7010,90.3535"

        :return: Map string or empty string if coordinates not available.
        """
        if not self.district_data:
            return ""
        return f"map:{self.district_data['lat']},{self.district_data['long']}"

    def get_established_date(self) -> str:
        """
        Returns the official establishment date of the district.

        :return: Date string in "YYYY-MM-DD" format, or empty string if not available.
        """
        if not self.district_data:
            return ""
        return self.district_data.get("established", "")

    def get_website(self) -> str:
        """
        Returns the official district website URL.

        :return: Website URL string, or empty string if not available.
        """
        if not self.district_data:
            return ""
        return self.district_data.get("website", "")

    def get_headquarter(self) -> dict | None:
        """
        Returns information about the district's administrative headquarter.

        :return: Dictionary with headquarter data, or None if not available.
        """
        if not self.district_data:
            return None
        return self.district_data.get("headquarter")

    def get_upazilas(self) -> list:
        """
        Returns a list of all upazilas under the district.

        :return: List of upazila names.
        """
        if not self.district_data:
            return []
        return self.district_data.get("upazilas", [])

    def get_upazilas_count(self) -> int:
        """
        Returns the total number of upazilas in the district.

        :return: Count of upazilas (int).
        """
        if not self.district_data:
            return 0
        return self.district_data.get("upazilas_count", 0)

    def get_stats(self) -> dict | None:
        """
        Returns various statistics about the district.

        Includes literacy rate, hospitals, schools, police stations, courts,
        voter population, and polling centers.

        :return: Dictionary of stats, or None if not found.
        """
        if not self.district_data:
            return None
        return {
            "literacy_rate": self.district_data.get("literacy_rate"),
            "hospitals_count": self.district_data.get("hospitals_count"),
            "schools_count": self.district_data.get("schools_count"),
            "police_stations": self.district_data.get("police_stations"),
            "courts": self.district_data.get("courts"),
            "voter_population": self.district_data.get("voter_population"),
            "polling_centers": self.district_data.get("polling_centers")
        }

    def get_weather(self) -> dict | None:
        """
        Returns average climate and weather information for the district.

        Includes average temperature (°C), rainfall (mm), and weather zone.

        :return: Dictionary with weather data, or None if not found.
        """
        if not self.district_data:
            return None
        return {
            "avg_temp_celsius": self.district_data.get("avg_temp_celsius"),
            "avg_rainfall_mm": self.district_data.get("avg_rainfall_mm"),
            "weather_zone": self.district_data.get("weather_zone")
        }

    def get_tourist_spots(self) -> list:
        """
        Returns a list of popular tourist spots in the district.

        :return: List of tourist spot names.
        """
        if not self.district_data:
            return []
        return self.district_data.get("tourist_spots", [])

    def get_festivals(self) -> list:
        """
        Returns a list of major festivals celebrated in the district.

        :return: List of festival names.
        """
        if not self.district_data:
            return []
        return self.district_data.get("festivals", [])

    def get_cultural_heritage(self) -> list:
        """
        Returns a list of cultural heritage elements of the district.

        :return: List of heritage items (strings).
        """
        if not self.district_data:
            return []
        return self.district_data.get("cultural_heritage", [])

    def get_notes(self) -> str:
        """
        Returns a descriptive note or extra information about the district.

        :return: Notes string, or empty string if not available.
        """
        if not self.district_data:
            return ""
        return self.district_data.get("notes", "")
    

    def get_division(self,bn:bool = False) -> str:
        """
        Returns the division name of a district.

        :return: string type of a division.
        """
        divisions = ['Barishal', 'Chattogram', 'Dhaka', 'Khulna', 'Mymensingh', 'Rajshahi', 'Rangpur', 'Sylhet']
        bn_divisions = ['বরিশাল', 'চট্টগ্রাম', 'ঢাকা', 'খুলনা', 'ময়মনসিংহ', 'রাজশাহী', 'রংপুর', 'সিলেট']
        if not self.district_data:
            return ""
        
        return divisions[self.district_data.get("division_id")-1] if not bn else bn_divisions[self.district_data.get("division_id")-1]
