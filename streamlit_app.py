import streamlit as st
import streamlit_shortcuts
import random
import time
import os
from datetime import datetime

# Function to load settings from a file
def load_settings(settings_file):
    settings = {
        "num_exercises": 5,
        "num1_limit": 10,
        "base_values": [1, 2]
    }
    try:
        with open(settings_file, "r") as file:
            lines = file.readlines()
            for line in lines:
                if "Aantal oefeningen" in line:
                    settings["num_exercises"] = int(line.split("=")[1])
                    print(f'Read amount of exercices: {settings["num_exercises"]}')
                elif "Hoogste factor" in line:
                    settings["num1_limit"] = int(line.split("=")[1])
                    print(f'Highest factor: {settings["num1_limit"]}')
                elif "Maaltafels van" in line:
                    settings["base_values"] = [int(value) for value in line.split("=")[1].strip().split(",")]
                    print(f'Base values: {settings["base_values"]}')
    except FileNotFoundError:
        generate_default_settings(settings_file)
        print(f'Default settingsfile not found!')
    return settings

# Function to generate default settings file
def generate_default_settings(settings_file):
    default_settings = "Aantal oefeningen = 5\nHoogste factor(Standaard: 10) = 10\nMaaltafels van (gescheiden door komma) = 1,2"
    with open(settings_file, "w") as file:
        file.write(default_settings)

# Load settings
settings_file = "Maaltafels_instellingen.txt"
settings = load_settings(settings_file)

# Streamlit application
st.title("Maaltafel Oefening")

# Ask for user's name
username = st.text_input("Wat is jouw naam?", "")

# Initialize session state
if "exercise" not in st.session_state:
    st.session_state.exercise = {
        "correct_count": 0,
        "num_exercises": settings["num_exercises"],
        "base_values": settings["base_values"],
        "num1_limit": settings["num1_limit"],
        "start_time": None,
        "questionstr": "",
        "answer": None,
        "previousExc": [0, 0]
    }

# Start exercise
if st.button("Start Oefening") and username:
    st.session_state.exercise["start_time"] = time.time()
    st.session_state.exercise["correct_count"] = 0
    st.session_state.exercise["num_exercises"] = settings["num_exercises"]
    st.session_state.exercise["previousExc"] = [0, 0]
    st.experimental_rerun()

# Check user's answer
def check_result(user_input):
    if user_input.isdigit():
        if int(user_input) == st.session_state.exercise["answer"]:
            st.session_state.exercise["correct_count"] += 1
            st.success("Correct!")
        else:
            st.error(f"Incorrect. Het juiste antwoord is {st.session_state.exercise['answer']}.")
            error_message = f"Fout: {st.session_state.exercise['questionstr']} = {user_input} (Juist: {st.session_state.exercise['answer']})\n"
            write_error_to_file(error_message)
    else:
        st.warning("Voer a.u.b. een geldig geheel getal in!")

# Generate next exercise
def next_exercise():
    if st.session_state.exercise["num_exercises"] > 0:
        num1 = random.randint(1, st.session_state.exercise["num1_limit"])
        num2 = random.choice(st.session_state.exercise["base_values"])
        while st.session_state.exercise["previousExc"][0] == num1 and st.session_state.exercise["previousExc"][1] == num2:
            num1 = random.randint(1, st.session_state.exercise["num1_limit"])
            num2 = random.choice(st.session_state.exercise["base_values"])
        st.session_state.exercise["questionstr"] = f"{num1} x {num2}"
        st.session_state.exercise["answer"] = num1 * num2
        st.session_state.exercise["previousExc"] = [num1, num2]
        st.session_state.exercise["num_exercises"] -= 1
    else:
        finish()

# Finish the exercise
def finish():
    end_time = time.time()
    elapsed_time = end_time - st.session_state.exercise["start_time"] if st.session_state.exercise["start_time"] else 0
    result_message = (
        f"Beste {username}, je hebt {st.session_state.exercise['correct_count']} op "
        f"{settings['num_exercises']} gehaald, met maaltafels tot {st.session_state.exercise['base_values']}.\n"
        f"Totaal benodigde tijd: {elapsed_time:.1f} seconden."
    )
    st.info(result_message)
    st.session_state.exercise["start_time"] = None
    write_result_to_file(result_message, elapsed_time)

# Write error to file
def write_error_to_file(error_message):
    with open("Laatste_foutjes_maaltafels.txt", "a") as error_file:
        error_file.write(username + ": " + error_message)

# Write result to file
def write_result_to_file(result_message, elapsed_time):
    timestamp = datetime.now().strftime("%d/%m/%Y - %H:%M:%S")
    result_entry = f"{username}: tafels van {st.session_state.exercise['base_values']}, met een max. factor van {st.session_state.exercise['num1_limit']}: {st.session_state.exercise['correct_count']}/{settings['num_exercises']} in {elapsed_time:.2f} seconden ({timestamp})\n"
    with open("Maaltafels_resultaat.txt", "a") as logfile:
        logfile.write(result_entry)

# Display current exercise
if st.session_state.exercise["start_time"]:
    st.write(f"Nog {st.session_state.exercise['num_exercises']} oefeningen te gaan.")
    st.write(st.session_state.exercise["questionstr"])
    user_answer = st.text_input("Jouw antwoord", "")
    if st.button("Check Antwoord"):
        check_result(user_answer)
        next_exercise()
        st.experimental_rerun()

# Display the initial instructions
if not st.session_state.exercise["start_time"]:
    st.write("Vul je naam in en druk op 'Start Oefening' om te beginnen.")