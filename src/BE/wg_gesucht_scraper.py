import json
import re
import time

from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

load_dotenv(dotenv_path="../../.env")

json_file = []


def get_json_object():
    return {
        "ID": None,
        "Link": None,
        "Ort": None,
        "Straße": None,
        "PLZ": None,
        "Zimmergröße": None,
        "Gesamtmiete": None,
        "Miete": None,
        "Nebenkosten": None,
        "Sonstige Kosten": None,
        "Kaution": None,
        "Ablösevereinbarung": None,
        "frei ab": None,
        "frei bis": None,
        "Anzeige Datum": None,
        "features": [],
        "tab_contents": [],
        "Wohnungsgröße": None,
        "WG_groesse": None,
        "Mitbewohnern_Geschlecht": None,
        "WG_Art": [],
        "Gesuchte_Geschlecht": "Egal",
        "Gesuchte_Alter": [0, 99],
        "Mitbewohner_Alter": [0, 99],
        "smoking": True
    }


# Initialize the Chrome driver
def setup_driver():
    options = webdriver.ChromeOptions()
    options.page_load_strategy = 'none'
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    return driver


def parse_wg_details(details_section):
    data = {
        "Wohnungsgröße": None,
        "WG_groesse": None,
        "Mitbewohnern_Geschlecht": "Egal",
        "WG_Art": [],
        "Gesuchte_Geschlecht": "Egal",
        "Gesuchte_Alter": ["0", "99"],
        "Mitbewohner_Alter": ["0", "99"],
        "smoking": True
    }

    for line in details_section:
        # Wohnungsgröße
        match = re.search(r"Wohnungsgröße:\s*(\d+)\s*m²", line)
        if match:
            data["Wohnungsgröße"] = match.group(1)

        # WG_groesse and Mitbewohnern_Geschlecht
        match = re.search(r"(\d+er)\s*WG\s*\(([^)]+)\)", line)
        if match:
            data["WG_groesse"] = match.group(1).replace("er", "")
            geschlecht = match.group(2)
            if "Frau" in geschlecht:
                data["Mitbewohnern_Geschlecht"] = "F"
            elif "Mann" in geschlecht:
                data["Mitbewohnern_Geschlecht"] = "M"
            elif "gemischte" in geschlecht or "gemischt" in geschlecht:
                data["Mitbewohnern_Geschlecht"] = "G"

        # WG_Art
        if any(keyword in line for keyword in
               ["Studenten-WG", "Business-WG", "Berufstätigen-WG", "keine Zweck-WG", "gemischte WG",
                "Internationals welcome"]):
            data["WG_Art"].extend([keyword for keyword in
                                   ["Studenten-WG", "Business-WG", "Berufstätigen-WG", "keine Zweck-WG", "gemischte WG",
                                    "Internationals welcome"] if keyword in line])

        # Gesuchte_Geschlecht
        if "Geschlecht egal" in line:
            data["Gesuchte_Geschlecht"] = "Egal"
        elif "Mann" in line:
            data["Gesuchte_Geschlecht"] = "M"
        elif "Frau" in line:
            data["Gesuchte_Geschlecht"] = "F"

        # Gesuchte_Alter
        match = re.search(r"zwischen\s*(\d+)\s*und\s*(\d+)\s*Jahren", line)
        if match:
            data["Gesuchte_Alter"] = (match.group(1), match.group(2))

        # Mitbewohner_Alter
        match = re.search(r"Bewohneralter:\s*(\d+)\s*bis\s*(\d+)\s*Jahre", line)
        if match:
            data["Mitbewohner_Alter"] = (match.group(1), match.group(2))

        # Smoking
        if "Rauchen nicht erwünscht" in line:
            data["smoking"] = False
        elif "Rauchen" in line:
            data["smoking"] = True

    return data


# Load the website and handle cookies
def load_website_and_handle_cookies(driver, url):
    driver.get(url)
    time.sleep(5)  # allow page to load
    try:
        consent_button = driver.find_element(By.XPATH, "//*[contains(text(), 'Save')]")
        consent_button.click()
    except Exception as e:
        print("No consent button found or an error occurred:", e)
    time.sleep(5)


# Click the first listing
def interact_with_listing(driver, i, data):
    try:
        listings = driver.find_elements(By.CSS_SELECTOR, 'div.wgg_card.offer_list_item')
        print(f"this is the link: {listings[i].find_element(By.CSS_SELECTOR, 'a[href]').get_attribute('href')}")
        data["Link"] = listings[i].find_element(By.CSS_SELECTOR, 'a[href]').get_attribute('href')
        listings[i].find_element(By.CSS_SELECTOR, 'a[href]').click()
    except Exception as e:
        print("An error occurred while clicking on listing:", e)
    time.sleep(5)


# Retrieve main details about the place
def retrieve_basic_details(driver, data):
    try:
        details_container = driver.find_element(By.CSS_SELECTOR, 'div.section_footer_dark')
        data["Zimmergröße"] = details_container.find_elements(By.CLASS_NAME, 'key_fact_value')[0].text
        data["Gesamtmiete"] = details_container.find_elements(By.CLASS_NAME, 'key_fact_value')[1].text
        # print(data["Zimmergröße"])
        # print(data["Gesamtmiete"])
    except Exception as e:
        print("An error occurred while retrieving data:", e)


# Retrieve financial and operational details
def retrieve_structural_data(driver, data):
    try:
        sections = driver.find_elements(By.CSS_SELECTOR, "div.col-xs-12.col-sm-6")
        for section in sections:
            details = section.find_elements(By.CLASS_NAME, "section_panel_detail")
            values = section.find_elements(By.CLASS_NAME, "section_panel_value")
            for detail, value in zip(details, values):
                key = detail.text.rstrip(':').strip()  # Remove colons and any extra spaces
                data[key] = value.text.strip()  # Ensure no extra spaces in value

        second_sections_details = sections[2].find_elements(By.CSS_SELECTOR, "span.section_panel_detail")
        address = second_sections_details[0].text.strip()

        # Split the string by newline and spaces
        lines = address.split('\n')
        strasse = lines[0].strip()

        # Further split the second line to get PLZ and Ort
        plz, ort = lines[1].strip().split(' ', 1)

        # Remove "Berlin" from the "Ort" if it exists
        ort_parts = ort.split()
        if "Berlin" in ort_parts:
            ort_parts.remove("Berlin")
        ort = " ".join(ort_parts)

        data["Straße"] = strasse
        data["Ort"] = ort
        data["PLZ"] = plz

    except Exception as e:
        print("An error occurred while retrieving financial details:", e)

    try:
        sections2 = driver.find_elements(By.CSS_SELECTOR, "div.panel.section_panel")

        wg_details_section = sections2[4].text.split("\n")

        # Parse WG details and Gesucht wird sections
        parsed_data = parse_wg_details(wg_details_section)

        data.update(parsed_data)

    except Exception as e:
        print("An error occurred while retrieving structural data:", e)

    return data


# Retrieve utility details
def retrieve_utility_details(driver, data):
    try:
        utility_container = driver.find_element(By.CLASS_NAME, "utility_icons")
        utility_divs = utility_container.find_elements(By.CLASS_NAME, "text-center")
        for div in utility_divs:
            text = ' '.join(div.text.split())
            data["features"].append(text)
        # for feature in data["features"]:
        #     print(feature)
        #     print(f"{icon}: {text}")
    except Exception as e:
        print("An error occurred while retrieving utility details:", e)


# Retrieve descriptions Text
def retrieve_ad_description_text(driver, data):
    try:
        tabs = driver.find_elements(By.CLASS_NAME, "section_panel_tab")
        tab_content_ids = [tab.get_attribute('data-text') for tab in tabs]

        for i, tab in enumerate(tabs):
            # Click the tab to activate it, if it's not already active
            if "active" not in tab.get_attribute('class'):
                tab.click()
                time.sleep(2)  # Wait for the tab's content to load

            # Fetch the content associated with this tab
            content_id = tab_content_ids[i]
            if content_id:
                try:
                    active_content = driver.find_element(By.CSS_SELECTOR, content_id)
                    text_content = ' '.join(active_content.text.split())
                    data["tab_contents"].append(text_content)
                except Exception as e:
                    print(f"Failed to fetch content for Tab {i + 1}: {e}")
        # for content in data["tab_contents"]:
        #     print(content)
        #     print(f"Content of Tab {i + 1}:", text_content)
    except Exception as e:
        print("An error occurred while retrieving ad description:", e)


# Main execution function
def scrape_wg_gesucht(entries_count=1):
    driver = setup_driver()
    url = "https://www.wg-gesucht.de/wg-zimmer-in-Berlin.8.0.1.0.html"
    load_website_and_handle_cookies(driver, url)

    for i in range(entries_count):
        data = get_json_object()
        data["ID"] = i + 1
        interact_with_listing(driver, i, data)
        retrieve_basic_details(driver, data)
        retrieve_structural_data(driver, data)
        retrieve_utility_details(driver, data)
        retrieve_ad_description_text(driver, data)
        data["Anzeige Datum"] = time.strftime("%Y-%m-%d %H:%M:%S")
        if data["Zimmergröße"] is not None:
            json_file.append(data)
        driver.back()
        time.sleep(2)
    print(json.dumps(json_file, indent=4, ensure_ascii=False))
    driver.quit()
    with open('output.json', 'w', encoding='utf-8', ) as file:
        json.dump(json_file, file, ensure_ascii=False, indent=4)
    return json_file


if __name__ == "__main__":
    scrape_wg_gesucht()
