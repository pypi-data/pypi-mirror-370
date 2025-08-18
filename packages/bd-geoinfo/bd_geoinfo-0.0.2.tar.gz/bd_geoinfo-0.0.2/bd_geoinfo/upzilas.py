import json
import os


class Upazila:
    """
    Upazila class to manage and retrieve information about upazilas from a JSON data source.

    Usage Example:
        upa = Upazila("Amtali")
        print(upa.get_name())
        print(upa.get_district())
        print(upa.has_upazila())
    """

    __data = None  # Class variable to hold loaded data

    def __init__(self, upazila_name: str):
        """
        Initialize an Upazila object using an upazila name (English or Bangla).
        - এখানে একটি নতুন Upazila অবজেক্ট তৈরি হলে
          JSON ডাটা মেমোরিতে লোড হয় এবং নির্দিষ্ট upazila খোঁজা হয়।
        """
        self.name = upazila_name.strip()
        if Upazila.__data is None:
            Upazila.__data = self._load_data()
        self.upazila_data = self._get_upazila_data()

    @classmethod
    def _data_file(cls):
        """
        Returns the absolute path of the upazilas.json file inside the 'data' folder.
        - JSON ফাইল কোথায় আছে সেটার লোকেশন return করে।
        """
        current_dir = os.path.dirname(__file__)
        return os.path.join(current_dir, "data", "upazilas.json")

    @classmethod
    def _load_data(cls):
        """
        Loads upazila data from the JSON file into memory.
        Handles nested list structures automatically.
        - JSON থেকে সব upazila লোড করে memory তে রাখে।
        - যদি nested list থাকে তাহলে flatten করে।
        """
        file_path = cls._data_file()
        with open(file_path, "r", encoding="utf-8") as file:
            data = json.load(file)
            upazilas = data.get("upazilas", [])

            # Flatten nested list if exists
            flattened = []
            for item in upazilas:
                if isinstance(item, list):
                    flattened.extend(item)
                else:
                    flattened.append(item)
            return flattened

    @classmethod
    def get_all_upazilas_info(cls) -> list:
        """
        Returns all upazilas data.
        - সব upazila data list আকারে return করে।
        """
        if cls.__data is None:
            cls.__data = cls._load_data()
        return cls.__data

    @classmethod
    def get_upazila_names(cls, bn: bool = False) -> list:
        """
        Returns list of all upazila names (English or Bangla).
        - শুধু নামের list return করে।
        - bn=True হলে বাংলা নাম return করবে, না হলে English নাম।
        """
        if cls.__data is None:
            cls.__data = cls._load_data()
        names = []
        for upa in cls.__data:
            if upa is None:
                continue
            names.append(upa.get("bn_name", "") if bn else upa.get("name", ""))
        return names

    def _get_upazila_data(self) -> dict | None:
        """
        Finds and returns the dictionary for the current upazila instance.
        Matching is done by English (case-insensitive) or Bangla name.
        - constructor এ যেই নাম দেওয়া হয়েছিলো,
          তার সাথে মিলে এমন upazila dict return করবে।
        """
        for upa in self.get_all_upazilas_info():
            if not isinstance(upa, dict):
                continue
            name_en = upa.get("name", "").strip().lower()
            name_bn = upa.get("bn_name", "").strip()
            if self.name.lower() == name_en or self.name == name_bn:
                return upa
        return None

    def has_upazila(self) -> bool:
        """
        Checks whether given upazila exists or not.
        - upazila_data পাওয়া গেলে True return করবে।
        """
        return self.upazila_data is not None

    def get_name(self, bn: bool = False) -> str:
        """
        Returns the upazila name.
        - bn=True হলে বাংলা নাম, অন্যথায় English নাম।
        """
        if not self.upazila_data:
            return ""
        return self.upazila_data.get("bn_name", "") if bn else self.upazila_data.get("name", "")

    def get_id(self) -> int | None:
        """
        Returns the ID of the upazila.
        - ID না থাকলে None return করে।
        """
        if not self.upazila_data:
            return None
        return self.upazila_data.get("id")

    def get_district(self, bn: bool = False) -> str:
        """
        Returns the district name of the upazila.
        - bn=True হলে জেলা নাম বাংলায় return করবে।
        """
        if not self.upazila_data:
            return ""
        return self.upazila_data.get("district_name", "") if not bn else self.upazila_data.get("district_bn_name", "")

    def get_division(self, bn: bool = False) -> str:
        """
        Returns the division name of the upazila.
        - bn=True হলে বিভাগ নাম বাংলায় return করবে।
        """
        if not self.upazila_data:
            return ""
        return self.upazila_data.get("division_name", "") if not bn else self.upazila_data.get("division_bn_name", "")

    def get_lat_long(self) -> list:
        """
        Returns [latitude, longitude] of the upazila.
        """
        if not self.upazila_data:
            return []
        return [self.upazila_data.get("lat", ""), self.upazila_data.get("long", "")]

    def get_area(self, unit: str = "km") -> dict | None:
        """
        Returns the area of the upazila in given unit.
        - Default km².
        - যদি "mile" দেয়া হয় তাহলে মাইল-এ convert করে দেয়।
        """
        if not self.upazila_data:
            return None
        area = self.upazila_data.get("area_km2")
        if area is None or area == "unknown":
            return None
        area = float(area)
        if unit.lower() == "mile":
            return {"unit": "mile", "value": round(area * 0.386102, 2)}
        return {"unit": "km", "value": area}

    def get_population(self) -> dict | None:
        """
        Returns population info with year.
        Example: {"population": 149456, "population_year": 2021}
        """
        if not self.upazila_data:
            return None
        pop = self.upazila_data.get("population")
        year = self.upazila_data.get("population_year")
        if pop in [None, "unknown"]:
            return None
        return {"population": pop, "population_year": year}

    def get_headquarter(self) -> str:
        """
        Returns headquarter name of the upazila.
        """
        if not self.upazila_data:
            return ""
        return self.upazila_data.get("headquarter", "")

    def get_unions(self) -> list:
        """
        Returns list of all unions under this upazila.
        """
        if not self.upazila_data:
            return []
        return self.upazila_data.get("unions", [])

    def get_unions_count(self) -> int:
        """
        Returns number of unions in this upazila.
        """
        if not self.upazila_data:
            return 0
        count = self.upazila_data.get("unions_count", 0)
        return int(count) if str(count).isdigit() else 0

    def get_map(self) -> str:
        """
        Returns map coordinate in format 'map:lat,long'
        Example: map:22.95,90.23
        """
        if not self.upazila_data:
            return ""
        return f"map:{self.upazila_data.get('lat','')},{self.upazila_data.get('long','')}"
