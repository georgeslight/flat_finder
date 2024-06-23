import unittest
from datetime import date
from src.mongo.user_db import User, save_user, get_user, update_user


class TestUserFunctions(unittest.TestCase):

    def setUp(self):
        self.new_user_data = {
            "id": "5",
            "thread_id": "1",
            "full_name": "John Doe",
            "phone_number": "+49123456789",
            "email": "john.doe@example.com",
            "address": {
                "street": "Sample Street",
                "house_number": 10,
                "zip_code": 10115,
                "city": "Berlin",
                "country": "Germany"
            },
            "date_of_birth": "1990-07-15",
            "employment_type": "Part-time",
            "average_monthly_net_income": 2000,
            "smoker": True,
            "languages": ["English", "German", "French"],
            "apartment_preferences": {
                "max_rent": 700,
                "location": "Berlin",
                "bezirk": ["Kreuzberg", "Neukölln"],
                "min_size": 20,
                "ready_to_move_in": "2023-11",
                "preferred_roommates_sex": "Egal",
                "preferred_roommate_age": [20, 30],
                "preferred_roommate_num": 3,
                "smoking_ok": True
            },
            "additional_info": [
                "Looking for a vibrant community.",
                "Enjoy cooking and sharing meals.",
                "Passionate about photography.",
                "Need a pet-friendly environment.",
                "Prefer a room with lots of natural light.",
                "Freelancer working from home.",
                "Interested in cultural exchanges.",
                "Fluent in English, German, and French.",
                "Looking for a long-term stay."
            ]
        }

        self.updated_user_data_new = {
            "id": "5",
            "thread_id": "1",
            "full_name": "John Doe",
            "phone_number": "+49123456789",
            "email": "john.doe@example.com",
            "address": {
                "street": "Sample Street",
                "house_number": 10,
                "zip_code": 10115,
                "city": "Berlin",
                "country": "Germany"
            },
            "date_of_birth": "1990-07-15",
            "employment_type": "Part-time",
            "average_monthly_net_income": 5000,
            "smoker": True,
            "languages": ["English", "German", "French"],
            "apartment_preferences": {
                "max_rent": 700,
                "location": "Berlin",
                "bezirk": ["Kreuzberg", "Neukölln"],
                "min_size": 20,
                "ready_to_move_in": "2023-11",
                "preferred_roommates_sex": "Egal",
                "preferred_roommate_age": [20, 30],
                "preferred_roommate_num": 3,
                "smoking_ok": True
            },
            "additional_info": [
                "Looking for a vibrant community.",
                "Enjoy cooking and sharing meals.",
                "Passionate about photography.",
                "Need a pet-friendly environment.",
                "Prefer a room with lots of natural light.",
                "Freelancer working from home.",
                "Interested in cultural exchanges.",
                "Fluent in English, German, and French.",
                "Looking for a long-term stay."
            ]
        }

    def test_user_lifecycle(self):
        # Save the new user
        new_user = User(**self.new_user_data)
        save_user(new_user)

        # Update the user
        updated_user = User(**self.updated_user_data_new)
        update_user(updated_user)

        # Retrieve the user and check the updated details
        retrieved_user = get_user("5")
        self.updated_user_data_new['date_of_birth'] = date.fromisoformat('1990-07-15')
        self.assertEqual(retrieved_user.dict(), self.updated_user_data_new)


if __name__ == '__main__':
    unittest.main()
