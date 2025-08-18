import json
import os

class Postcode:
    """
    Postcode class to manage and retrieve information about postcodes from a JSON data source.

    Usage Example:
        p = Postcode("8710")                  # By postcode
        print(p.has_postcode())               # True or False
        print(p.get_postcode())               # Returns postcode string
        print(p.get_name())                   # Returns area name in English
        print(p.get_name(bn=True))            # Returns area name in Bangla
        print(p.get_upazila())                # Returns upazila name
        print(p.get_district())               # Returns district name
        print(p.get_division())               # Returns division name
        print(p.get_full_address())           # Returns full address as string
    """

    __data = None  # Class variable to hold loaded JSON data (cached)

    def __init__(self, code: str):
        """
        Initialize a Postcode instance with a given postcode.

        :param code: Postcode string (e.g., "8710")
        """
        self.code = code.strip()
        if Postcode.__data is None:
            Postcode.__data = self._load_data()
        self.postcode_data = self._get_postcode_data()

    @classmethod
    def _data_file(cls):
        """
        Get the absolute path to the postcodes.json file.

        :return: Absolute file path as string
        """
        current_dir = os.path.dirname(__file__)
        return os.path.abspath(os.path.join(current_dir, "data", "postcodes.json"))

    @classmethod
    def _load_data(cls):
        """
        Load postcode data from JSON file.
        Returns list of postcode dictionaries.

        :return: List of postcodes
        """
        with open(cls._data_file(), "r", encoding="utf-8") as f:
            data = json.load(f)
            # Handle dict {"postcodes": [...]} or list [...]
            if isinstance(data, dict) and "postcodes" in data:
                return data["postcodes"]
            elif isinstance(data, list):
                return data
            return []

    @classmethod
    def get_all_postcodes_info(cls) -> list:
        """
        Return the complete postcode dataset.

        :return: List of all postcode dictionaries
        """
        if cls.__data is None:
            cls.__data = cls._load_data()
        return cls.__data

    def _get_postcode_data(self):
        """
        Find and return the postcode data matching the instance code.

        :return: Dictionary of postcode data or None if not found
        """
        for p in self.get_all_postcodes_info():
            if str(p.get("postcode", "")).strip() == self.code:
                return p
        return None

    def has_postcode(self) -> bool:
        """
        Check if the postcode exists in the dataset.

        :return: True if exists, False otherwise
        """
        return self.postcode_data is not None

    def get_postcode(self) -> str:
        """
        Return the postcode string.

        :return: Postcode string
        """
        if not self.postcode_data:
            return ""
        return self.postcode_data.get("postcode", "")

    def get_name(self, bn: bool = False) -> str:
        """
        Get the area name corresponding to the postcode.

        :param bn: If True, return Bangla name; else return English name
        :return: Area name string
        """
        if not self.postcode_data:
            return ""
        return self.postcode_data["bn_name"] if bn else self.postcode_data["name"]

    def get_upazila(self) -> str:
        """
        Get the upazila/sub-district of the postcode.

        :return: Upazila name string
        """
        if not self.postcode_data:
            return ""
        return self.postcode_data.get("upazila_name", "")

    def get_district(self) -> str:
        """
        Get the district of the postcode.

        :return: District name string
        """
        if not self.postcode_data:
            return ""
        return self.postcode_data.get("district_name", "")

    def get_division(self) -> str:
        """
        Get the division of the postcode.

        :return: Division name string
        """
        if not self.postcode_data:
            return ""
        return self.postcode_data.get("division_name", "")

    def get_full_address(self, bn: bool = False) -> str:
        """
        Get the full address corresponding to the postcode as a formatted string.

        :param bn: If True, return address in Bangla; else return in English
        :return: Full address string
        """
        if not self.postcode_data:
            return ""
        if bn:
            return f"{self.postcode_data['bn_name']}, {self.postcode_data['upazila_name']}, {self.postcode_data['district_name']}, {self.postcode_data['division_name']}, {self.postcode_data['postcode']}"
        return f"{self.postcode_data['name']}, {self.postcode_data['upazila_name']}, {self.postcode_data['district_name']}, {self.postcode_data['division_name']}, {self.postcode_data['postcode']}"
