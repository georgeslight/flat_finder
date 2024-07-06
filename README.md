# Flat Finder Doc

## Overview

- **Project Name:** Flat Finder
- **Project Description:** Tool for finding shared apartments using user preferences and shared-apartments descriptions.
- **Data Source:** Scraping wg-gesucht using Selenium.
- **Approach:** Unfiltered scraping, temporary storage in a JSON file, structural and deep filtering, recommendation generation.
- **Tools:** Selenium, MongoDB, GPT-3.5, Telegram.

## Components

- [Selenium scrapper](src/BE/wg_gesucht_scraper.py)
- [mongoDB](src/BE/mongoDB.py)
- [Telegram Bot](src/FE/app.py)
- [OpenAI Agent](src/setup_assistant/agent.py)

### Use-Cases:

- Profile creation and update.
- Preference setting.
- WG recommendations (active and passive).

## Workflow

- **Creating User:** User will be created in UI and preferences will be set. ([link](src/FE/app.py))
- **Scraping:** Collecting data from wg-gesucht. ([link](src/BE/wg_gesucht_scraper.py))
- **Storage:** Temporary storage in a JSON file. ([link](src/FE/output.json))
- **Filtering:** Apartments data will be filtered for the user. ([link](src/BE/structural_filtering.py))
- **Recommendation:** Deep filtering with non-structural data, generating recommendation for user and an example application text. ([link](src/BE/ai_recommendation.py))
- **UI notification:** Notifying the user of the recommendation and example application. ([link](src/FE/app.py))
---
## Setup

1. **Download Telegram on your [Smart phone (IOS)](https://apps.apple.com/us/app/telegram-messenger/id686449807) or [Desktop (windows)](https://apps.microsoft.com/detail/9nztwsqntd0s?launch=true&mode=full&hl=en-gb&gl=de&ocid=bingwebsearch)**
2. Create an account in Telegram.
3. **setup your env. file to the flat finder Folder:**
4. **Install the requirements:**
  ```bash
  pip install -r requirements.txt
  ```
5. **Run the Agent:**
  ```bash
    python src/BE/main.py
  ```
5. **Run the Telegram Bot:**
  ```bash
    python src/FE/app.py
  ```
6. **Start the conversation with the bot:**
    - Search for the bot in Telegram with the name you have given in the env file.
    - Start the conversation with the bot by typing /start.
    - typ /profile to set up your profile and preferences.
    - After setting the preferences, the bot will notify you with the recommendations.
---
## Experiments

- Prompt Development:
  - Prompt Level 1 + Output
  - Prompt Level 2 + Output
  - Continued iterations until final prompt.