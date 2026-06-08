import csv
import os
from typing import List, Dict, Union

class LeaderboardRepository:
    def __init__(self, file_path: str = "leaderboard.csv") -> None:
        self.file_path = file_path
        self._ensure_file()

    def _ensure_file(self) -> None:
        """Creates the CSV file with header if it doesn't exist."""
        if not os.path.exists(self.file_path):
            with open(self.file_path, mode='w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(["name", "mode", "time"])

    def save_record(self, name: str, mode: str, time_val: float) -> None:
        """Adds a new record to the leaderboard."""
        with open(self.file_path, mode='a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([name, mode, str(time_val)])

    def list_all(self) -> List[Dict[str, Union[str, float]]]:
        """Returns all records sorted by descending time."""
        records = []
        if not os.path.exists(self.file_path):
            return records

        with open(self.file_path, mode='r', newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    name = row.get("name") or row.get("nome")
                    mode = row.get("mode") or row.get("modo")
                    time_str = row.get("time") or row.get("tempo")
                    
                    if name is not None and mode is not None and time_str is not None:
                        # Translate Portuguese values to English internally
                        if mode == "boca":
                            mode = "mouth"
                        elif mode == "cabeca":
                            mode = "head"
                            
                        records.append({
                            "name": name,
                            "mode": mode,
                            "time": float(time_str)
                        })
                except (ValueError, KeyError):
                    # Ignore malformed rows
                    pass
        
        # Sort descending by time
        records.sort(key=lambda x: x["time"], reverse=True)
        return records

    def filter_by_name(self, search_name: str) -> List[Dict[str, Union[str, float]]]:
        """Filters records by name (case insensitive) and returns them sorted."""
        all_records = self.list_all()
        term = search_name.lower()
        return [r for r in all_records if term in str(r["name"]).lower()]

    def clear(self) -> None:
        """Clears all records by recreating the empty file with header."""
        if os.path.exists(self.file_path):
            os.remove(self.file_path)
        self._ensure_file()
