import unittest
from datetime import date
from http.client import HTTPException
from unittest.mock import patch
from BE.structural_filtering import filter_apartments
from mongo.user_db import User, ApartmentPreferences


class TestFilterApartments(unittest.TestCase):

    def setUp(self):
        # Set up the user data
        self.user = User(
            id='5',
            full_name='John Doe',
            date_of_birth=date(1990, 7, 15),
            apartment_preferences=ApartmentPreferences(
                max_rent=700,
                bezirk=['Kreuzberg', 'Neukölln'],
                min_size=20,
                ready_to_move_in='2023-11-01',
                preferred_roommates_sex='Egal',
                preferred_roommate_age=[20, 30],
                smoking_ok=True
            )
        )
        # Set up the apartment data
        self.apartments = [
            {
                "ID": 11,
                "Ort": "Kreuzberg",
                "Zimmergröße": "25m²",
                "Gesamtmiete": "690€",
                "frei ab": "2023-11-01",
                "Mitbewohnern_Geschlecht": "Egal",
                "Gesuchte_Alter": [20, 30],
                "Mitbewohner_Alter": [20, 30],
                "smoking": True
            },
            {
                "ID": 12,
                "Ort": "Neukölln",
                "Zimmergröße": "22m²",
                "Gesamtmiete": "700€",
                "frei ab": "2023-11-01",
                "Mitbewohnern_Geschlecht": "Egal",
                "Gesuchte_Alter": [20, 30],
                "Mitbewohner_Alter": [20, 30],
                "smoking": True
            }
        ]

    @patch('your_module.load_apartments')  # Mock the load_apartments function
    def test_filter_apartments_with_data(self, mock_load_apartments):
        mock_load_apartments.return_value = self.apartments
        result = filter_apartments(self.user)
        self.assertIn('fitting_apartments', result)
        self.assertEqual(len(result['fitting_apartments']), 2)

    def test_filter_apartments_without_data(self):
        result = filter_apartments(self.user, self.apartments)
        self.assertIn('fitting_apartments', result)
        self.assertEqual(len(result['fitting_apartments']), 2)

    def test_no_matching_apartments(self):
        # Modify apartments so they do not match
        self.apartments[0]["Gesamtmiete"] = "800€"
        self.apartments[1]["Gesamtmiete"] = "800€"
        result = filter_apartments(self.user, self.apartments)
        self.assertEqual(result['message'], 'No matching apartments found.')

    @patch('your_module.load_apartments')  # Mock the load_apartments function
    def test_filter_apartments_no_data_loaded(self, mock_load_apartments):
        mock_load_apartments.return_value = []
        with self.assertRaises(HTTPException):
            filter_apartments(self.user)


if __name__ == '__main__':
    unittest.main()
