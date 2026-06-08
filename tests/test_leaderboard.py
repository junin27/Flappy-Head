import unittest
import os
from src.data.leaderboard import LeaderboardRepository

class TestLeaderboardRepository(unittest.TestCase):
    def setUp(self) -> None:
        self.test_csv = "test_leaderboard.csv"
        self.repo = LeaderboardRepository(self.test_csv)
        self.repo.clear()

    def tearDown(self) -> None:
        if os.path.exists(self.test_csv):
            os.remove(self.test_csv)

    def test_save_and_list_empty(self) -> None:
        # When instantiated with no records
        records = self.repo.list_all()
        # Must return empty list
        self.assertEqual(len(records), 0)

    def test_save_record(self) -> None:
        # When we save a record
        self.repo.save_record("Alice", "mouth", 15.5)
        # Must return in the list
        records = self.repo.list_all()
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0]["name"], "Alice")
        self.assertEqual(records[0]["mode"], "mouth")
        self.assertEqual(records[0]["time"], 15.5)

    def test_descending_sorting(self) -> None:
        # When we save multiple records with different times
        self.repo.save_record("Bob", "head", 10.0)
        self.repo.save_record("Alice", "mouth", 20.0)
        self.repo.save_record("Charlie", "mouth", 15.0)

        # Must return list sorted by descending time
        records = self.repo.list_all()
        self.assertEqual(records[0]["name"], "Alice")
        self.assertEqual(records[1]["name"], "Charlie")
        self.assertEqual(records[2]["name"], "Bob")

    def test_filter_by_name(self) -> None:
        # When we filter by partial name (case insensitive)
        self.repo.save_record("Alice Silva", "mouth", 20.0)
        self.repo.save_record("Alicia", "head", 15.0)
        self.repo.save_record("Bob", "mouth", 10.0)

        result = self.repo.filter_by_name("alic")
        self.assertEqual(len(result), 2)
        # Must also return sorted
        self.assertEqual(result[0]["name"], "Alice Silva")
        self.assertEqual(result[1]["name"], "Alicia")

    def test_clear_database(self) -> None:
        # When we save and then clear
        self.repo.save_record("Alice", "mouth", 20.0)
        self.repo.clear()
        # No records should remain
        self.assertEqual(len(self.repo.list_all()), 0)

if __name__ == "__main__":
    unittest.main()
