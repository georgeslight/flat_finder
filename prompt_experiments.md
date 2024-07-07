## Example Data

### Users
```python
users = [
    {
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
    },
    {
        '_id': ObjectId('6677f439242205068f743a27'),
        'id': '189',
        'thread_id': '2',
        'full_name': 'Jane Smith',
        'phone_number': '+49123456790',
        'email': 'jane.smith@example.com',
        'address': {
            'street': 'Another Street',
            'house_number': 15,
            'zip_code': 10245,
            'city': 'Berlin',
            'country': 'Germany'
        },
        'date_of_birth': date(1988, 5, 25),
        'smoker': True,
        'employment_type': 'Full-time',
        'average_monthly_net_income': 3000,
        'languages': ['English', 'Spanish'],
        'apartment_preferences': {
            'max_rent': 1200,
            'location': 'Berlin',
            'bezirk': ['Mitte', 'Friedrichshain'],
            'min_size': 20,
            'ready_to_move_in': '2023-10-01',
            'preferred_roommates_sex': 'female',
            'preferred_roommate_age': [25, 40],
            'preferred_roommate_num': 2,
            'smoking_ok': False
        },
        'additional_info': [
            'Looking for a quiet environment.',
            'Enjoy reading and yoga.',
            'Passionate about environmental sustainability.',
            'Need a non-smoking environment.',
            'Prefer a room with a balcony.',
            'Work from office most of the time.',
            'Interested in mindfulness practices.',
            'Fluent in English and Spanish.',
            'Looking for a medium-term stay.'
        ]
    }
]
```

### Apartments
```python
apartments = [
    {
        "ID": 1,
        "Link": "https://www.wg-gesucht.de/wg-zimmer-in-Berlin-Neukoelln.10959135.html",
        "Ort": "Neukölln",
        "Straße": "Glasower str 22",
        "PLZ": "12051",
        "Zimmergröße": "16m²",
        "Gesamtmiete": "600€",
        "Miete": "500€",
        "Nebenkosten": "100€",
        "Sonstige Kosten": "n.a.",
        "Kaution": "750€",
        "Ablösevereinbarung": "200€",
        "frei ab": "01.07.2024",
        "frei bis": None,
        "Anzeige Datum": "2024-06-28 11:46:02",
        "features": [
            "Neubau",
            "möbliert",
            "Badewanne, Dusche",
            "WLAN 50-100 Mbit/s",
            "Laminat",
            "Ökostrom",
            "Zentralheizung",
            "gute Parkmöglichkeiten",
            "4 Minuten zu Fuß entfernt",
            "Waschmaschine, Spülmaschine, Balkon, Aufzug"
        ],
        "tab_contents": [
            "Vermietet wird ein voll möbliertes Zimmer mit balkon ab Juli zur befristeten Untermiete mit Aussicht auf Verlängerung.",
            "Mietbeginn wahrscheinlich auch früher möglich und hinten raus auch laenger moeglich sein Die Wohnung befindet sich in",
            "einem Neubau, wenn die Türen und Fenster zu sind hat man seine Ruhe 😴 Wir keben mit offenen Türen was bedeutet das wenn", 
            "deine Türe zu ist, ea bedeutet du mags deine Ruhe die dann respektiert wird aber sollte das ständig bis nur noch so sein das",
            "deine Zimmertüre verschlossen ist, dann fänden wir das als WG nicht nett, deswegen sei dir bewusst das ist eine WG. Man möchte",
            "dich kennenlernen und bei ausschließlich geschlossener Türe nicht möglich wäre. Die WG verfügt über ein Badezimmer mit Badewanne",
            "sowie ein zusätzliches Gäste WC. Wir haben einen großen Balkon mit Grillmöglichkeit auf Sonnenseite 🌞 Bettdecke & Kissen stehen",
            "zur Verfügung 🌸 Eine Anmeldung ist nicht möglich Du zahlst einen Nutzungsbediengten Abschlag der nicht zurück erstattet wird",
            "unserseits. (200€) Dafür fehlt dir an nichts und wenn was kaputt geht haftest du nicht, ausser es war deine Schuld.",
            "• U7 (6 Min) • U8/S-Bahn (9 Min) • Hermannquartier (9 Min) • Lidl (3 Min)",
            "Wir sind Marie, Max und Jules und pflegen ein einfaches und harmonisches WG Leben 🌼 Jeder hat seinen",
            "eigenen Alltag, daher trifft man meist erst abends aufeinander. Unser Treffpunkt ist die Küche, in der",
            "wir uns immer updaten und zusammen chillen 🍸🍿🍕 Wir nutzen eine App als Putzplan und kommen damit super",
            "zurecht no und bitte dich daran teilzunehmen. Uns ist Sauberkeit sehr wichtig",
            "Schick uns deine Bewerbung jeder bekommt eine Rückmeldung und somit die Chance"
        ],
        "Wohnungsgröße": "120",
        "WG_groesse": "2",
        "Mitbewohnern_Geschlecht": "M",
        "WG_Art": [
            "Studenten-WG",
            "keine Zweck-WG"
        ],
        "Gesuchte_Geschlecht": "gender_irrelevant",
        "Gesuchte_Alter": [
            0,
            99
        ],
        "Mitbewohner_Alter": [
            20,
            40
        ],
        "smoking": True
    },
    {
        "ID": 11,
        "Link": "https://www.wg-gesucht.de/wg-zimmer-in-Berlin-Kreuzberg.11072022.html",
        "Ort": "Kreuzberg",
        "Straße": "Gneisenaustraße 10",
        "PLZ": "10961",
        "Zimmergröße": "25m²",
        "Gesamtmiete": "690€",
        "Miete": "600€",
        "Nebenkosten": "90€",
        "Sonstige Kosten": "n.a.",
        "Kaution": "700€",
        "Ablösevereinbarung": "n.a.",
        "frei ab": "01.11.2023",
        "frei bis": None,
        "Anzeige Datum": "2024-06-21 19:47:23",
        "features": [
            "Altbau",
            "2. OG",
            "möbliert",
            "Badewanne",
            "Parkett",
            "Zentralheizung",
            "Bewohnerparken",
            "5 Minuten zu Fuß entfernt",
            "Waschmaschine",
            "pet-friendly",
            "viel natürliches Licht"
        ],
        "tab_contents": [
            "Dein sonniges Zimmer befindet sich in einer voll möblierten Altbauwohnung in Berlin-Kreuzberg.",
            "Vor dem Haus hält die U-Bahnlinie 7. Es gibt ein Bad, eine Küche mit Kühlschrank, Waschmaschine ",
            "und Flur. 10 Minuten sind es bis zum Alexanderplatz. Vereinbare einen Termin mit Natalie und Jo",
            "und sende uns Deinen Einkommensnachweis per whatsapp (siehe Kontaktinformationen).",
            "U-Bahnhof Gneisenaustraße",
            "Wir sprechen Deutsch und Englisch."
        ],
        "Wohnungsgröße": None,
        "WG_groesse": "3",
        "Mitbewohnern_Geschlecht": "gender_irrelevant",
        "WG_Art": [
            "Studenten-WG",
            "Berufstätigen-WG"
        ],
        "Gesuchte_Geschlecht": "gender_irrelevant",
        "Gesuchte_Alter": [
            20,
            35
        ],
        "Mitbewohner_Alter": [
            20,


            35
        ],
        "smoking": True
    }
]
```

---

Sure, here is the reformatted experiments documentation with the given format:

---

## Experiments

### Initial Single Prompt Experiment
In the initial stage, we implemented all logic in a single prompt to evaluate its feasibility.

#### Prompt
```python
prompt_content = (
    f"Evaluate if the following user is interested in this shared apartment and fits the criteria. "
    f"User Bio: {users[0]['additional_info']}. The user is a smoker = {users[0]['smoker']}, speaks {users[0]['languages']}, and "
    f"is looking for a shared apartment that fits the following criteria: {users[0]['apartment_preferences']}. "
    f"Apartment features: {apartments[0]['features']}, details: {apartments[0]['tab_contents']}. "
    f"Check for deal breakers only. If the user is a good fit, provide a recommendation and an example "
    f"application text. \n\n"
    f"User: {users[0]['additional_info']}\nApartment: {apartments[0]}"
)
```

#### Result
```css
- User Bio: Fluent in English, German, and French, Looking for a long-term stay.
- Apartment: Features: Neubau, möbliert, Badewanne, Dusche, WLAN 50-100 Mbit/s, Laminat, Ökostrom, Zentralheizung, gute Parkmöglichkeiten, 4 Minuten zu Fuß entfernt, Waschmaschine, Spülmaschine, Balkon, Aufzug.
- Result: True - The apartment fits the user's criteria.
- Recommendation: You should apply for this apartment because it is located in a vibrant community with modern amenities. The apartment is pet-friendly and has a lot of natural light, which suits your preferences for a bright living space. Additionally, it offers a spacious living room, a balcony, and shared amenities such as a fitness center and rooftop terrace, providing a luxurious and comfortable living environment.
- Application Text: Dear Apartment Owner, My name is John Doe, and I am a freelance photographer passionate about cultural exchanges and vibrant communities. I am interested in your apartment because it meets my needs for a pet-friendly, naturally lit space where I can work from home. I believe I am a good fit for this apartment because I enjoy cooking and sharing meals, and I am fluent in English, German, and French. I look forward to the possibility of becoming a part of your community. Best regards, John Doe.
```

---

### Two Prompt Experiment
To improve clarity and performance, we divided the task into two prompts: one for the KO-Filter and recommendation, and another for generating the example application text.

#### KO-Filter and Recommendation Prompt
```python
recommendation_prompt_content = (
    f"Please check if the following user is interested in this shared apartment and if they fit the criteria. "
    f"User Bio: {users[0]['additional_info']}, smoker: {users[0]['smoker']}, languages: {users[0]['languages']}. "
    f"Apartment features: {apartments[0]['features']}, details: {apartments[0]['tab_contents']}. "
    f"Consider only deal breakers.\n\n"
    f"If there are no deal breakers go ahead and Write a recommendation for the user for this apartment. The recommendation should state: "
    f"'You should apply for this apartment because: ' followed by reasons. "
    f"Consider data under 'tabs_contents', 'features', and 'additional_info'. Max 1000 chars.\n\n"
    f"User: {users[0]['additional_info']}\nApartment: {apartments[0]}"
)
```

#### Result
```css
I did not find any deal breakers. The user fits the criteria for this shared apartment.
This apartment is a good fit for the user and the User is a good fit for this apartment.
You should apply for this apartment because:
- It is located in a vibrant community with modern amenities.
- The apartment is pet-friendly and has a lot of natural light, which suits your preferences for a bright living space.
- Additionally, it offers a spacious living room, a balcony, and shared amenities such as a fitness center and rooftop terrace, providing a luxurious and comfortable living environment.
```

#### Example-Application Prompt
```python
application_prompt_content = (
    f"Based on the user bio and apartment information, write an example application. "
    f"Introduce the user, explain their interest in the apartment, and why they are a good fit. "
    f"Include any relevant additional information and a closing sentence with contact info if available. "
    f"Max 1000 chars.\n\n"
    f"User: {users[0]['additional_info']}\nApartment: {apartments[0]}"
)
```

#### Result
```css
Dear Apartment Owner,

My name is John Doe, and I am a freelance photographer passionate about cultural exchanges and vibrant communities. 
I am interested in your apartment because it meets my needs for a pet-friendly, naturally lit space where I can work from home. 
I believe I am a good fit for this apartment because I enjoy cooking and sharing meals, and I am fluent in English, German, and French. 
I look forward to the possibility of becoming a part of your community.

Best regards,
John Doe
```

---

### Three Prompt Experiment
To further refine the process, we implemented three distinct prompts: one for the KO-Filter, one for the recommendation, and one for the example application text.

#### KO-Filter Prompt
```python
ko_prompt_content = (
    f"Check if the user fits the criteria for this shared apartment. "
    f"User Bio: {users[0]['additional_info']}, smoker: {users[0]['smoker']}, languages: {users[0]['languages']}. "
    f"Apartment features: {apartments[0]['features']}, details: {apartments[0]['tab_contents']}. "
    f"Consider only deal breakers. Return 'TRUE' if they fit, else 'FALSE' with reasons.\n\n"
    f"User: {users[0]['additional_info']}\nApartment: {apartments[0]}"
)
```

#### Result
```css
TRUE
```

#### Recommendation Prompt
If the KO-Filter returns 'TRUE':
```python
recommend_prompt_content = (
    f"Write a recommendation for the user for this apartment. The recommendation should state: "
    f"'You should apply for this apartment because: ' followed by reasons. "
    f"Consider data under 'tabs_contents', 'features', and 'additional_info'. Max 1000 chars.\n\n"
    f"User: {users[0]['additional_info']}\nApartment: {apartments[0]}"
)
```

#### Result
```css
You should apply for this apartment because:
- It is located in a vibrant community with modern amenities.
- The apartment is pet-friendly and has a lot of natural light, which suits your preferences for a bright living space.
- Additionally, it offers a spacious living room, a balcony, and shared amenities such as a fitness center and rooftop terrace, providing a luxurious and comfortable living environment.
```

#### Example-Application Prompt
```python
application_prompt_content = (
    f"Based on the user bio and apartment information, write an example application. "
    f"Introduce the user, explain their interest in the apartment, and why they are a good fit. "
    f"Include any relevant additional information and a closing sentence with contact info if available. "
    f"Max 1000 chars.\n\n"
    f"User: {users[0]['additional_info']}\nApartment: {apartments[0]}"
)
```

#### Result
```css
Dear Apartment Owner,

My name is John Doe, and I am a freelance photographer passionate about cultural exchanges and vibrant communities. 
I am interested in your apartment because it meets my needs for a pet-friendly, naturally lit space where I can work from home. 
I believe I am a good fit for this apartment because I enjoy cooking and sharing meals, and I am fluent in English, German, and French. 
I look forward to the possibility of becoming a part of your community.

Best regards,
John Doe
```
---
# Final Prompts

### KO-Filter Prompt
```python
ko_prompt_content = (
    f"Please check if the following user is interested in this shared apartment and if they fit the "
    f"criteria. The user is looking for a shared apartment in Berlin. They are a smoker = {user.smoker},"
    f" the user speaks {user.languages}, and is looking for a shared apartment that "
    f"fits the following criteria: {str_user_bio}. Please check if the user is interested in the following "
    f"apartment and if they are a good fit. The apartment has the following features: {str_apartment_features} "
    f"and details: {str_apartment_details}. The check should only consider deal breakers. Don't consider the price"
    f", location, or any other details. If they are a good fit, then return 'True', else return 'False'."
    f"Only return 'False' if the user has a deal breaker. Consider that the apartment has already been filtered by the "
    f"user preferences like the rent and the room size. Examples when to return False: User is allergic to cats and "
    f"the apartment has multiple cats, User is a smoker and the apartment is non-smoking, User is a vegan and the "
    f"apartment is not vegan-friendly, User wants a very quiet place and the apartment is very loud, etc. "
    f"Examples when not to return False: User is a smoker and the apartment allows smoking on the balcony, User "
    f"wants a pet-friendly apartment and you don't find any information about pets in the apartment, User is a vegan "
    f"and you don't find any information about the apartment being vegan-friendly, User is a night owl and you don't "
    f"find any information about the apartment being quiet, etc. \n\n"
    f"Your response should be only 'TRUE' or 'FALSE'. If 'FALSE', include the reasons why very briefly. \n\n"
    f"{str_user_bio}\n{apartment_info}"
)
```

#### Result
```css
TRUE
```
---
#### Recommendation Prompt
```python
recommend_prompt_content = (
    f"Write a recommendation for the user for this apartment. The recommendation should state: "
    f"'You should apply for this apartment because: ' followed by reasons. "
    f"Consider data under 'tabs_contents', 'features', and 'additional_info'. Max 1000 chars.\n\n"
    f"User: {str_user_bio}\nApartment: {apartment_info}"
)
```

#### Result
```css
You should apply for this apartment because:
1. It is fully furnished and equipped with modern amenities, including a well-maintained kitchen and a comfortable living space.
2. The apartment is located centrally with easy access to public transportation and various shops and facilities in the neighborhood.
3. The potential roommate is a non-smoker, values cleanliness and order, and enjoys cooking vegetarian and Asian dishes, making it a suitable match for someone who appreciates a tidy and harmonious living environment.
```

#### Example Application Prompt
```python
application_prompt_content = (
    f"Based on the user bio and apartment information, write an example application. "
    f"Introduce the user, explain their interest in the apartment, and why they are a good fit. "
    f"Include any relevant additional information and a closing sentence with contact info if available. "
    f"Max 1000 chars.\n\n"
    f"User: {str(user)}\nApartment: {str(apartment)}"
)
```

#### Result
```css
Dear Apartment Owner,

My name is John Doe, and I am a freelance photographer passionate about cultural exchanges and vibrant communities. 
I am interested in your apartment because it meets my needs for a pet-friendly, naturally lit space where I can work from home. 
I believe I am a good fit for this apartment because I enjoy cooking and sharing meals, and I am fluent in English, German, and French. 
I look forward to the possibility of becoming a part of your community.

Best regards,
John Doe
```