import json
import os

class Division:
    """
    Division class to manage and retrieve information about divisions from a JSON data source.

    Usage Example:
        div = Division("Dhaka")
        print(div.get_name())
        print(div.get_area(unit="mile"))
        print(div.has_division())
    """

    __data = None  # Class variable to hold loaded data

    def __init__(self, div_name: str):
        """
        Initialize Division instance with division name (English or Bangla).

        :param div_name: Name of the division (English or Bangla)
        """
        self.name = div_name.strip()
        if Division.__data is None:
            Division.__data = self._load_data()
        self.division_data = self._get_division_data()

    @classmethod
    def _data_file(cls):
        """
        Returns the absolute path to the divisions.json file.

        :return: Absolute file path as string
        """
        current_dir = os.path.dirname(__file__)
        return os.path.abspath(os.path.join(current_dir, "data", "divisions.json"))

    @classmethod
    def _load_data(cls):
        """
        Load division data from JSON file once and cache it in the class.

        :return: Dictionary containing all division data
        """
        file_path = cls._data_file()
        with open(file_path, "r", encoding="utf-8") as file:
            return json.load(file)

    @classmethod
    def get_all_divisions_info(cls) -> dict:
        """
        Return the full JSON data of all divisions.

        :return: Dictionary containing all divisions data
        """
        if cls.__data is None:
            cls.__data = cls._load_data()
        return cls.__data

    @classmethod
    def get_division_names(cls, bn: bool = False) -> list:
        """
        Return a list of all division names.

        :param bn: True to return Bangla names, False for English
        :return: List of division names
        """
        data = cls.get_all_divisions_info()
        return [div["bn_name"] if bn else div["name"] for div in data["divisions"]]

    def _get_division_data(self) -> dict | None:
        """
        Retrieve the JSON data dictionary of the current division instance.

        :return: Dictionary of division data or None if not found
        """
        data = self.get_all_divisions_info()
        for div in data["divisions"]:
            if div["name"].strip().lower() == self.name.lower() or div["bn_name"] == self.name:
                return div
        return None

    def has_division(self) -> bool:
        """
        Check if the division exists in the data.

        :return: True if the division exists, False otherwise
        """
        return self.division_data is not None

    def get_name(self, bn: bool = False) -> str:
        """
        Get the division name in English or Bangla.

        :param bn: True for Bangla, False for English
        :return: Name of the division
        """
        if not self.division_data:
            return ""
        return self.division_data["bn_name"] if bn else self.division_data["name"]

    def get_id(self) -> int | None:
        """
        Return the division ID.

        :return: ID as integer or None if not available
        """
        if not self.division_data:
            return None
        return self.division_data.get("id")

    def get_map(self) -> str:
        """
        Return a Google Maps-style string for the division's coordinates.

        :return: String in the format 'map:lat,long'
        """
        if not self.division_data:
            return ""
        return f"map:{self.division_data['lat']},{self.division_data['long']}"

    def get_lat_long(self) -> list:
        """
        Return the latitude and longitude as a list.

        :return: [latitude, longitude] or empty list if not available
        """
        if not self.division_data:
            return []
        return [self.division_data['lat'], self.division_data['long']]

    def get_area(self, unit: str = "km") -> dict | None:
        """
        Return the area of the division in square kilometers or miles.

        :param unit: "km" for square kilometers, "mile" for square miles
        :return: Dictionary with 'unit' and 'value' keys or None if not available
        """
        if not self.division_data:
            return None
        area_km2 = self.division_data.get("area_km2")
        if area_km2 is None:
            return None
        if unit.lower() == "mile":
            return {"unit": "mile", "value": round(area_km2 * 0.386102, 2)}
        return {"unit": "km", "value": area_km2}

    def get_headquarter(self) -> dict | None:
        """
        Return information about the division's headquarter.

        :return: Dictionary with headquarter details or None
        """
        if not self.division_data:
            return None
        return self.division_data.get("headquarter")

    def get_population(self) -> dict | None:
        """
        Return population information of the division with the year.

        :return: Dictionary with 'population' and 'population_year' keys or None
        """
        if not self.division_data:
            return None
        return {
            "population": self.division_data.get("population"),
            "population_year": self.division_data.get("population_year")
        }

    def get_districts(self) -> dict | None:
        """
        Return districts count and list for the division.

        :return: Dictionary with 'districts' key containing a list or None
        """
        if not self.division_data:
            return None
        return {"districts": self.division_data.get("districts", [])}

    def get_stats(self) -> dict | None:
        """
        Return various statistics of the division.

        :return: Dictionary with literacy rate, hospitals, schools, police stations,
                 districts count, courts, voter population, and polling centers
        """
        if not self.division_data:
            return None
        return {
            "literacy_rate": self.division_data.get("literacy_rate"),
            "hospitals_count": self.division_data.get("hospitals_count"),
            "schools_count": self.division_data.get("schools_count"),
            "police_stations": self.division_data.get("police_stations"),
            "districts_count": self.division_data.get("districts_count"),
            "courts": self.division_data.get("courts"),
            "voter_population": self.division_data.get("voter_population"),
            "polling_centers": self.division_data.get("polling_centers")
        }

    def get_weather(self) -> dict | None:
        """
        Return average weather information for the division.

        :return: Dictionary with 'avg_temp_celsius', 'avg_rainfall_mm', 'weather_zone' keys
                 or None if not available
        """
        if not self.division_data:
            return None
        return {
            "avg_temp_celsius": self.division_data.get("avg_temp_celsius"),
            "avg_rainfall_mm": self.division_data.get("avg_rainfall_mm"),
            "weather_zone": self.division_data.get("weather_zone")
        }

    def get_tourist_spots(self) -> list:
        """
        Return a list of tourist spots in the division.

        :return: List of tourist spots or empty list
        """
        if not self.division_data:
            return []
        return self.division_data.get("tourist_spots", [])

    def get_festivals(self) -> list:
        """
        Return a list of festivals celebrated in the division.

        :return: List of festivals or empty list
        """
        if not self.division_data:
            return []
        return self.division_data.get("festivals", [])

    def get_cultural_heritage(self) -> list:
        """
        Return a list of cultural heritage items in the division.

        :return: List of cultural heritage items or empty list
        """
        if not self.division_data:
            return []
        return self.division_data.get("cultural_heritage", [])

    def get_notes(self) -> str:
        """
        Return notes or descriptive information about the division.

        :return: String notes or empty string if not available
        """
        if not self.division_data:
            return ""
        return self.division_data.get("notes", "")

    def get_website(self) -> str:
        """
        Return the official website URL of the division.

        :return: String URL or empty string
        """
        if not self.division_data:
            return ""
        return self.division_data.get("website", "")

    def get_established_date(self) -> str:
        """
        Return the establishment date of the division in 'YYYY-MM-DD' format.

        :return: Date string or empty string if not available
        """
        if not self.division_data:
            return ""
        return self.division_data.get("established", "")
