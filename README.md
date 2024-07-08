# Flat Finder Doc

## Overview

- **Project Name:** Flat Finder
- **Project Description:** Tool for finding shared apartments using user preferences and shared-apartments descriptions.
- **Data Source:** Scraping wg-gesucht using Selenium.
- **Approach:** Unfiltered scraping, temporary storage in a JSON file, structural and deep filtering, recommendation generation.
- **Tools:** Selenium, MongoDB, GPT-3.5, Telegram.

## Components

- [Selenium scrapper](src/BE/wg_gesucht_scraper.py)
- [mongoDB](src/mongo/user_db.py)
- [Telegram Bot](src/FE/app.py)
- [OpenAI Agent](src/setup_assistant/agent.py)

### Use-Cases:

- Profile creation and update.
- Preference setting.
- WG recommendations (active and passive).

## Workflow

- **Creating User:** User will be created in [UI](src/FE/app.py) and preferences will be set. 
- **Scraping:** Collecting data from wg-gesucht using [selenium](src/BE/wg_gesucht_scraper.py). 
- **Storage:** Temporary storage in a [JSON file.](src/FE/output.json)
- **Filtering:** Apartments data will be [filtered](src/BE/structural_filtering.py) for the user.
- **Recommendation:** Deep filtering with non-structural data, generating [recommendation](src/BE/ai_recommendation.py) for user and an example application text.
- **UI notification:** [Notifying](src/FE/app.py) the user of the recommendation and example application.

## [Experimentation](prompt_experiments.md)

---
## Setup

1. **Download Telegram on your [Smart phone (IOS)](https://apps.apple.com/us/app/telegram-messenger/id686449807) or [Desktop (windows)](https://apps.microsoft.com/detail/9nztwsqntd0s?launch=true&mode=full&hl=en-gb&gl=de&ocid=bingwebsearch)**
2. Create an account in Telegram.
3. setup your **env. file** to the flat finder Folder:
4. **Install the requirements:**
      ```bash
      pip install -r requirements.txt
      ```
5. **Run the Agent:**
      ``` python
        python src/BE/main.py
      ```
6. **Run the Telegram Bot:**
      ``` python
        python src/FE/app.py
      ```
6. **Start the conversation with the [FlatFinderHTWBot](https://t.me/FlatFinderHTWBot):**
   1. Start a Chat with the bot using this [link](https://t.me/FlatFinderHTWBot).
   2. Klick on the start button or send **/start**.
   3. send **/profile** to set up your profile and preferences.

### congrats you are ready to go!