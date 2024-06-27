import logging
import os
import re
import datetime

from dotenv import load_dotenv
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import openai
import requests

# Importing from user_db.py
from src.mongo.user_db import User, get_user, save_user, Address, ApartmentPreferences, get_empty_user, update_user

# Load environment variables from .env file
load_dotenv(dotenv_path="../../.env")

BOT_TOKEN = os.getenv('BOT_TOKEN')
openai.api_key = os.getenv('OPENAI_API_KEY')

# Creates a bot instance and passed the BOT_TOKEN to it
bot = telebot.TeleBot(BOT_TOKEN)


# Initialize OpenAI client if necessary
client = openai.OpenAI(api_key=openai.api_key)

# create empty user object
# user = get_empty_user()
# user: User


# Function to create a new thread for a user
def create_user(user_id):
    # global user
    try:
        user = get_user(user_id)
        if user is None:
            user = User(id=str(user_id), thread_id=client.beta.threads.create().id)
            save_user(user)
        return user
    except Exception as e:
        logging.error(f"Failed to create thread: {e}")
        return None


# Message handler that handles incoming '/start' and '/hello'
@bot.message_handler(commands=['start', 'hello'])
def send_welcome(message):
    try:
        bot.send_message(message.chat.id, "Welcome!")
        # Create a new thread for the user
        create_user(message.from_user.id)
    except Exception as e:
        logging.error(f"Failed to send welcome message: {e}")


# Handler for '/profile' command
@bot.message_handler(commands=['profile'])
def handle_profile(message):
    try:
        markup = InlineKeyboardMarkup()
        markup.row(InlineKeyboardButton("Profile", callback_data="profile"),
                   InlineKeyboardButton("Preferences", callback_data="preferences"))
        bot.send_message(message.chat.id, "Create / Update your profile:", reply_markup=markup)
    except Exception as e:
        logging.error(f"Failed to handle profile command: {e}")


# Callback query handler for inline buttons
@bot.callback_query_handler(func=lambda call: call.data in ['profile'])
def profile_info(call):
    # global user
    try:
        user = get_user(call.from_user.id)
        # profile = get_user(call.message.chat.id)
        address = user.address
        profile_text = (
            f"Here is your profile information:\n\n"
            f"Full Name: {user.full_name if user.full_name else 'Not set'}\n"
            f"Phone Number: {user.phone_number if user.phone_number else 'Not set'}\n"
            f"Email: {user.email if user.email else 'Not set'}\n"
            f"Address:\n"
            f"     Street: {address.street if address.street else 'Not set'}\n"
            f"     House number: {address.house_number if address.house_number else 'Not set'}\n"
            f"     Zip code: {address.zip_code if address.zip_code else 'Not set'}\n"
            f"     City: {address.city if address.city else 'Not set'}\n"
            f"     Country: {address.country if address.country else 'Not set'}\n"
            f"Date of birth: {user.date_of_birth if user.date_of_birth else 'Not set'}\n"
            f"Employment Type: {user.employment_type if user.employment_type else 'Not set'}\n"
            f"Average monthly net income: {user.average_monthly_net_income if user.average_monthly_net_income else 'Not set'}\n"
            f"Smoker: {user.smoker if user.smoker else 'False'}\n"
        )
        markup = InlineKeyboardMarkup()
        markup.row(
            InlineKeyboardButton("Full Name", callback_data="change_full_name"),
            InlineKeyboardButton("Phone Number", callback_data="change_phone_number"),
        )
        markup.row(
            InlineKeyboardButton("Email", callback_data="change_email"),
            InlineKeyboardButton("Address", callback_data="change_address"),
        )
        markup.row(
            InlineKeyboardButton("Date of birth", callback_data="change_date_of_birth"),
            InlineKeyboardButton("Employment Type", callback_data="change_employment_type")
        )
        markup.row(
            InlineKeyboardButton("Average monthly net income", callback_data="change_average_monthly_net_income"),
            InlineKeyboardButton("Smoker", callback_data="change_smoker")
        )
        markup.row(
            InlineKeyboardButton("Go to Preferences", callback_data="preferences"),
        )
        bot.send_message(call.message.chat.id, profile_text, reply_markup=markup)
    except Exception as e:
        logging.error(f"Failed to display profile information: {e}")


@bot.callback_query_handler(func=lambda call: call.data == 'preferences')
def preferences_info(call):
    # global user
    try:
        user = get_user(call.from_user.id)
        if not user:
            bot.send_message(call.message.chat.id, "User not found. Please start with /start command.")
            return
        preferences = user.apartment_preferences
        preferences_text = (
            f"Here are your apartment preferences:\n\n"
            f"Max Rent: {preferences.max_rent if preferences.max_rent else 'Not set'}\n"
            f"Location: {preferences.location if preferences.location else 'Not set'}\n"
            f"Bezirk: {', '.join(preferences.bezirk) if preferences.bezirk else 'Not set'}\n"
            f"Min Size: {preferences.min_size if preferences.min_size else 'Not set'}\n"
            f"Ready to Move In: {preferences.ready_to_move_in if preferences.ready_to_move_in else 'Not set'}\n"
            f"Preferred Roommates Sex: {preferences.preferred_roommates_sex.replace('_', ' ').title() if preferences.preferred_roommates_sex else 'Not set'}\n"
            f"Preferred Roommate Age: {', '.join(map(str, preferences.preferred_roommate_age)) if preferences.preferred_roommate_age else 'Not set'}\n"
            f"Preferred Roommate Number: {preferences.preferred_roommate_num if preferences.preferred_roommate_num else 'Not set'}\n"
            f"Smoking OK: {preferences.smoking_ok if preferences.smoking_ok else 'False'}\n"
        )
        additional_info = user.additional_info if user.additional_info else []
        additional_info_text = "\n".join(f"- {info}" for info in additional_info) or "Not set"
        preferences_text += f"\nAdditional Information:\n{additional_info_text}"

        markup = InlineKeyboardMarkup()
        markup.row(
            InlineKeyboardButton("Max Rent", callback_data="change_max_rent"),
            InlineKeyboardButton("Location", callback_data="change_location"),
        )
        markup.row(
            InlineKeyboardButton("Bezirk", callback_data="change_bezirk"),
            InlineKeyboardButton("Min Size", callback_data="change_min_size"),
        )
        markup.row(
            InlineKeyboardButton("Ready to Move In", callback_data="change_ready_to_move_in"),
            InlineKeyboardButton("Preferred Roommates Sex", callback_data="change_preferred_roommates_sex"),
        )
        markup.row(
            InlineKeyboardButton("Preferred Roommate Age", callback_data="change_preferred_roommate_age"),
            InlineKeyboardButton("Preferred Roommate Num", callback_data="change_preferred_roommate_num"),
        )
        markup.row(
            InlineKeyboardButton("Smoking OK", callback_data="change_smoking_ok"),
            InlineKeyboardButton("Additional Info", callback_data="change_additional_info")
        )
        markup.row(
            InlineKeyboardButton("Go to Profile", callback_data="profile")
        )
        bot.send_message(call.message.chat.id, preferences_text, reply_markup=markup)
    except Exception as e:
        logging.error(f"Failed to display preferences information: {e}")


@bot.callback_query_handler(func=lambda call: call.data.startswith('change_'))
def handle_update_callback(call):
    try:
        field = '_'.join(call.data.split('_')[1:])
        field_display = field.replace('_', ' ').title()
        if field == "address":
            msg = bot.send_message(call.message.chat.id, "Please enter your new address (e.g., Street-Name Number, "
                                                         "Zip City Country):")
            bot.register_next_step_handler(msg, lambda message: update_address(message, call))
        elif field in ("smoker", "smoking_ok"):
            markup = InlineKeyboardMarkup()
            markup.row(
                InlineKeyboardButton("True", callback_data=f"boolean_true_{field}"),
                InlineKeyboardButton("False", callback_data=f"boolean_false_{field}")
            )
            bot.send_message(call.message.chat.id, "Please select your preference:", reply_markup=markup)
        elif field in ("additional_info", "languages", "preferred_roommate_age", "bezirk"):
            msg = bot.send_message(call.message.chat.id,
                                   f"Please enter your {field_display}, each item separated by commas:")
            bot.register_next_step_handler(msg, lambda message: update_list(message, field, call))
        elif field in ("full_name", "phone_number", "email", "employment_type", "average_monthly_net_income"):
            msg = bot.send_message(call.message.chat.id,
                                   f"Please enter your new {field_display}:")
            bot.register_next_step_handler(msg, lambda message: update_profile(message, field, call))
        elif field == "date_of_birth":
            msg = bot.send_message(call.message.chat.id,
                                   "Please enter your Birthday (Format: 'YYYY-MM-DD'):")
            bot.register_next_step_handler(msg, lambda message: update_profile(message, field, call))
        elif field == "preferred_roommates_sex":
            markup = InlineKeyboardMarkup()
            markup.row(
                InlineKeyboardButton("Female", callback_data=f"sex_preference_female"),
                InlineKeyboardButton("Male", callback_data=f"sex_preference_male")
            )
            markup.row(
                InlineKeyboardButton("Gender irrelevant", callback_data=f"sex_preference_gender_irrelevant"),
                InlineKeyboardButton("Divers", callback_data=f"sex_preference_divers")
            )
            bot.send_message(call.message.chat.id, "Please select your preference:", reply_markup=markup)
        else:
            msg = bot.send_message(call.message.chat.id, f"Please enter your new {field_display}:")
            bot.register_next_step_handler(msg, lambda message: update_preferences(message, field, call))
    except Exception as e:
        logging.error(f"Failed to handle update callback: {e}")


@bot.callback_query_handler(func=lambda call: call.data.startswith('boolean_'))
def update_boolean(call):
    # global user
    try:
        user = get_user(call.from_user.id)
        status = call.data.split('_')[1].lower() == 'true'
        field = call.data.split('_')[2]
        if field == 'smoker':
            user.smoker = status
            update_user(user)
            bot.send_message(call.message.chat.id, f"Your smoking status has been updated to: {status}")
            profile_info(call)
        if field == 'smoking':
            user.apartment_preferences.smoking_ok = status
            update_user(user)
            bot.send_message(call.message.chat.id, f"Your smoker allowed preferences has been updated to: {status}")
            preferences_info(call)
    except Exception as e:
        logging.error(f"Failed to update smoker status: {e}")


@bot.callback_query_handler(func=lambda call: call.data.startswith('sex_preference'))
def update_sex_preferences(call):
    try:
        user = get_user(call.from_user.id)
        preference = '_'.join(call.data.split('_')[2:])
        user.apartment_preferences.preferred_roommates_sex = preference
        update_user(user)
        bot.send_message(call.message.chat.id, f"Your roommate gender preference has been updated to: "
                                               f"{preference.replace('_', ' ').title()}")
        preferences_info(call)
    except Exception as e:
        logging.error(f"Failed to handle update gender preference: {e}")
        bot.send_message(call.message.chat.id, "There was an error updating your preference, please try again.")
        preferences_info(call)


def update_address(message, call):
    # global user
    try:
        user = get_user(message.from_user.id)
        address = message.text
        # Use regex to parse the address
        match = re.match(r'^(.*?[\s\S]+?)\s+(\d+),\s+(\d+)\s+([\s\S]+)\s+([\s\S]+)$', address)
        if match:
            street, house_number, zip_code, city, country = match.groups()
            logging.info(f"Parsed address: {street}, {house_number}, {zip_code}, {city}, {country}")
            new_adress = {
                "street": street,
                "house_number": house_number,
                "zip_code": zip_code,
                "city": city,
                "country": country,
            }
            user.address = Address(**new_adress)
            bot.send_message(message.chat.id, "Your address has been updated.")
            update_user(user)
            profile_info(call)
        else:
            bot.send_message(message.chat.id, "Invalid address format. Please try again.")
            profile_info(call)
    except Exception as e:
        logging.error(f"Failed to handle update address: {e}")
        bot.send_message(message.chat.id, "There was an error updating your address, please try again.")
        profile_info(call)


def update_profile(message, field, call):
    # global user
    try:
        user = get_user(message.from_user.id)
        if field == "date_of_birth":
            date_object = datetime.datetime.strptime(message.text, '%Y-%m-%d').date()
            setattr(user, field, date_object)
        else:
            new_value = message.text
            setattr(user, field, new_value)
        update_user(user)
        field_display = field.replace('_', ' ').title()
        bot.send_message(message.chat.id, f"Your {field_display} has been updated to: {message.text}")
        profile_info(call)
    except Exception as e:
        logging.error(f"Failed to handle update profile: {e}")
        bot.send_message(message.chat.id, "There was an error updating your profile, please try again.")
        profile_info(call)


def update_preferences(message, field, call):
    # global user
    try:
        user = get_user(message.from_user.id)
        if field == "ready_to_move_in":
            date_object = datetime.datetime.strptime(message.text, '%Y-%m-%d').date()
            setattr(user.apartment_preferences, field, date_object)
        else:
            new_value = message.text
            setattr(user.apartment_preferences, field, new_value)
        update_user(user)
        field_display = field.replace('_', ' ').title()
        bot.send_message(message.chat.id, f"Your {field_display} has been updated to: {message.text}")
        preferences_info(call)
    except Exception as e:
        logging.error(f"Failed to handle update preferences: {e}")
        bot.send_message(message.chat.id, "There was an error updating your preferences, please try again.")
        preferences_info(call)


def update_list(message, field, call):
    # global user
    try:
        user = get_user(message.from_user.id)
        new_value = [x.strip() for x in message.text.split(',')]
        if field in ("languages", "additional_info"):
            setattr(user, field, new_value)
        elif field in ("preferred_roommate_age", "bezirk"):
            setattr(user.apartment_preferences, field, new_value)
        update_user(user)
        field_display = field.replace('_', ' ').title()
        bot.send_message(message.chat.id, f"Your {field_display} has been updated.")
        preferences_info(call)
    except Exception as e:
        logging.error(f"Failed to handle update additional information: {e}")
        bot.send_message(message.chat.id, "There was an error, please try again.")
        profile_info(call)


# Handler method for all other text messages
@bot.message_handler(func=lambda msg: True)
def handle_message(message):
    user_id = message.from_user.id

    user_x = get_user(user_id)

    if user_x is None:
        user_x = create_user(user_id)

    # Retrieve or create a new thread_id for the user
    thread_id = user_x.thread_id
    if not thread_id:
        send_welcome(message)
        return

    # Prepare parameters for request
    params = {
        "text": message.text,
        "thread": thread_id,
        "user_name": message.from_user.first_name
    }

    # Send request
    url = 'http://localhost:4000/chat'
    response = requests.post(url, json=params)
    # Reply to the user with the response from AI
    bot.send_message(message.chat.id, response.text)


# Start polling for messages
if __name__ == "__main__":
    bot.infinity_polling()
