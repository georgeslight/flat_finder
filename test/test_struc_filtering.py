import unittest
from datetime import date
from bson import ObjectId
from src.BE.structural_filtering import filter_apartments, turn_user_to_user_model
import json


class TestApartmentFiltering(unittest.TestCase):
    def setUp(self):
        with open('test_apartments.json', 'r', encoding='utf-8') as file:
            self.apartments = json.load(file)

        with open('test_fitting_apartments.json', 'r', encoding='utf-8') as file:
            self.fitting_apartments = json.load(file)

        self.user1 = {
            '_id': ObjectId('6677f439242205068f743a26'),
            'id': '188',
            'thread_id': '1',
            'full_name': 'John Doe',
            'phone_number': '+49123456789',
            'email': 'john.doe@example.com',
            'address': {
                'street': 'Sample Street',
                'house_number': 10,
                'zip_code': 10115,
                'city': 'Berlin',
                'country': 'Germany'
            },
            'date_of_birth': date(1990, 7, 15),
            'smoker': False,
            'employment_type': 'Part-time',
            'average_monthly_net_income': 2000,
            'languages': ['English', 'German', 'French'],
            'apartment_preferences': {
                'max_rent': 1500,
                'location': 'Berlin',
                'bezirk': ['Kreuzberg', 'Neukölln', 'Pankow'],
                'min_size': 10,
                'ready_to_move_in': '2023-11-01',
                'preferred_roommates_sex': 'gender_irrelevant',
                'preferred_roommate_age': [20, 60],
                'preferred_roommate_num': 3,
                'smoking_ok': True
            },
            'additional_info': [
                'Looking for a vibrant community.',
                'Enjoy cooking and sharing meals.',
                'Passionate about photography.',
                'Need a pet-friendly environment.',
                'Prefer a room with lots of natural light.',
                'Freelancer working from home.',
                'Interested in cultural exchanges.',
                'Fluent in English, German, and French.',
                'Looking for a long-term stay.'
            ]
        }

    def test_filter_apartments_user1(self):
        user = turn_user_to_user_model(self.user1)
        filtered_apartments = filter_apartments(user, self.apartments)

        # Ensure the types are consistent for comparison
        for apt in filtered_apartments['fitting_apartments']:
            apt['Gesuchte_Alter'] = [str(age) for age in apt['Gesuchte_Alter']]
            apt['Mitbewohner_Alter'] = [str(age) for age in apt['Mitbewohner_Alter']]

        for apt in self.fitting_apartments['fitting_apartments']:
            apt['Gesuchte_Alter'] = [str(age) for age in apt['Gesuchte_Alter']]
            apt['Mitbewohner_Alter'] = [str(age) for age in apt['Mitbewohner_Alter']]

        print("Expected output:", json.dumps(self.fitting_apartments, indent=2, ensure_ascii=False))
        print("Filtered apartments for user 1:", json.dumps(filtered_apartments, indent=2, ensure_ascii=False))
        self.assertEqual(filtered_apartments, self.fitting_apartments)


if __name__ == '__main__':
    unittest.main()
