import json
import os

class Union:
    """
    Union class to manage and retrieve information about unions from a JSON data source.

    Functionalities:
        - Search union by English or Bangla name
        - Retrieve English and Bangla names
        - Retrieve Upazila, District, Division (English & Bangla)
        - Get full formatted address (English & Bangla)
        - Check if union exists
        - List all unions

    Usage Example:
        uni = Union("Burirchar Union")
        print(uni.get_name())           # English name
        print(uni.get_name(bn=True))    # Bangla name
        print(uni.get_upazila())        # Upazila (English)
        print(uni.get_upazila(bn=True)) # Upazila (Bangla)
        print(uni.get_district())       # District (English)
        print(uni.get_district(bn=True))# District (Bangla)
        print(uni.get_division())       # Division (English)
        print(uni.get_division(bn=True))# Division (Bangla)
        print(uni.get_full_address())   # Full address in English
        print(uni.get_full_address(bn=True)) # Full address in Bangla
        print(uni.has_union())          # True / False

        # Get all unions
        all_unions = Union.get_all_unions()
    """

    __data = None  # Class variable to cache loaded JSON data

    def __init__(self, union_name: str):
        """
        Initialize Union instance with union name (English or Bangla).

        :param union_name: Name of the union to search
        """
        self.union_name = union_name.strip()
        self.union_data = self.__find_union()

    @classmethod
    def __load_data(cls):
        """
        Load unions data from JSON file if not already loaded.
        The JSON file should contain a key "unions" which is a list of unions.
        """
        if cls.__data is None:
            file_path = os.path.join(
                os.path.dirname(__file__), "..", "bd_geoinfo", "data", "unions.json"
            )
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                cls.__data = data.get("unions", [])

    def __find_union(self):
        """
        Find and return union data matching the given name.
        Matches English name (case-insensitive) or Bangla name (exact match).

        :return: Dictionary with union data or None if not found
        """
        self.__load_data()
        for union in self.__data:
            if union.get("name", "").strip().lower() == self.union_name.lower():
                return union
            if union.get("bn_name", "").strip() == self.union_name:
                return union
        return None

    def has_union(self) -> bool:
        """Check if the union exists."""
        return self.union_data is not None

    def get_name(self, bn: bool = False) -> str:
        """Get the name of the union. English by default, Bangla if bn=True."""
        if not self.union_data:
            return ""
        if bn:
            return self.union_data.get("bn_name", "")
        return self.union_data.get("name", "")

    def get_upazila(self) -> str:
        """Get the Upazila name. English by default, Bangla if bn=True."""
        if not self.union_data:
            return ""
        return self.union_data.get("upazila_name", "")

    def get_district(self) -> str:
        """Get the District name. English by default, Bangla if bn=True."""
        if not self.union_data:
            return ""
        return self.union_data.get("district_name", "")

    def get_division(self) -> str:
        """Get the Division name. English by default, Bangla if bn=True."""
        if not self.union_data:
            return ""
        return self.union_data.get("division_name", "")

    def get_full_address(self, bn: bool = False) -> str:
        """Get the full formatted address of the union."""
        if not self.union_data:
            return ""
        return f"{self.get_name(bn)}, {self.get_upazila(bn)}, {self.get_district(bn)}, {self.get_division(bn)}"

    @classmethod
    def get_all_unions(cls) -> list:
        """Return a list of all unions in the dataset."""
        cls.__load_data()
        return cls.__data
