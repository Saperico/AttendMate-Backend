import unittest
from script import add_class_to_database, engine

class TestDatabaseOperations(unittest.TestCase):
    def test_add_class_to_database(self):
        test_data = {
            "subject_name": "Test Subject",
            "class_type": "lecture",
            "class_code": "TST123",
            "day": "monday",
            "class_start_time": "10:00",
            "room": "101"
        }

        add_class_to_database(**test_data)

        with engine.connect() as connection:
            result = connection.execute("SELECT * FROM class WHERE subjectNumber = 'TST123'").fetchone()
            self.assertIsNotNone(result)
            self.assertEqual(result["subjectName"], "Test Subject")

if __name__ == '__main__':
    unittest.main()