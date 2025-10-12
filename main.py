import json
import requests
import Levenshtein
import tkinter as tk
from tkinter import messagebox, simpledialog
from tkinter import *
import threading
import os
import platform
from gtts import gTTS
import subprocess

# ---------------------------
# Data Handling Functions
# ---------------------------

# Global dictionary variable for offline words.
wordnet_data = {}

def get_app_dir():
    """Return platform-specific path for storing the dictionary file."""
    system = platform.system()

    if system == "Linux":
        base_dir = os.path.expanduser("~/.local/share/WordWise")
    elif system == "Windows":
        base_dir = os.path.join(os.getenv("APPDATA"), "WordWise")
    elif system == "Darwin":  # macOS
        base_dir = os.path.expanduser("~/Library/Application Support/WordWise")
    else:
        base_dir = os.path.expanduser("~/.WordWise")

    # Ensure the directory exists
    os.makedirs(base_dir, exist_ok=True)
    return base_dir

def load_json(file_name):
    """Load JSON data from a file."""
    try:
        with open(file_name, "r") as file:
            data = json.load(file)
        return data 
    except FileNotFoundError:
        print("File not found")
        return {}
    except json.JSONDecodeError:
        print("Invalid JSON")
        return {}


# Define the JSON file path and load offline dictionary data.
app_dir = get_app_dir()
json_file = os.path.join(app_dir, "dictionary.json")
wordnet_data = load_json(json_file)

def save_json():
    """Save the updated wordnet_data to the JSON file."""
    with open(json_file, "w") as file:
        json.dump(wordnet_data, file, indent=4)
    print("Dictionary updated.")

def output(word):
    """Retrieve and format word details from wordnet_data."""
    word = word.strip().lower()
    # To avoid potential key error
    if word not in wordnet_data:
        return {"Word": word.capitalize(),
                "Definition": "Not found",
                "Examples": "",
                "Synonyms": "",
                "Antonyms": ""}
    return {
        "Word": word.capitalize(),
        "Definition": wordnet_data[word]['definition'],
        "Examples": ', '.join(wordnet_data[word]['examples']),
        "Synonyms": ', '.join(wordnet_data[word]['synonyms']),
        "Antonyms": ', '.join(wordnet_data[word]['antonyms'])
    }

def find_closest_match(word):
    """Find the closest match from the offline dictionary using Levenshtein distance."""
    words = list(wordnet_data.keys())
    if not words:
        return ""
    closest_match = min(words, key=lambda w: Levenshtein.distance(word, w))
    if Levenshtein.distance(word, closest_match) <= 2 and closest_match.lower() != word.lower():
        return closest_match
    return ""

def add_word(word):
    """Add a new word to the offline dictionary after confirmation."""
    word = word.strip().lower()  # Normalize the input word
    answer = messagebox.askyesno("Confirmation", f"Add '{word}' to dictionary?")
    if not answer:
        print("Word not added.")
        messagebox.showinfo("Info", f"{word} not added")
        return
    if answer:
        definition = simpledialog.askstring("Enter definition", f"Definition for '{word}':")
        examples = simpledialog.askstring("Enter examples", f"Examples for '{word}' (separate by commas):")
        synonyms = simpledialog.askstring("Enter synonyms", f"Synonyms for '{word}' (separate by commas):")
        antonyms = simpledialog.askstring("Enter antonyms", f"Antonyms for '{word}' (separate by commas):")

        # Check if all fields are empty or None
        if not any([definition, examples, synonyms, antonyms]):
            messagebox.showinfo("Info", "Word not added. All fields are empty.")
            return
        
        # Update the global dictionary
        wordnet_data[word] = {
            "definition": definition if definition else "",
            "examples": [e.strip() for e in examples.split(",")] if examples else [],
            "synonyms": [s.strip() for s in synonyms.split(",")] if synonyms else [],
            "antonyms": [a.strip() for a in antonyms.split(",")] if antonyms else []
        }
    try:
        save_json()
        messagebox.showinfo("Updated", f"The word '{word}' added.")
        entry_word.focus_set()
        suggestion_yes.pack_forget()
        suggestion_no.pack_forget()
        frame_btn.pack_forget()
        display_result(output(word), word)

    except Exception as e:
        messagebox.showerror("Error", f"An error occurred while saving: {e}")

def overwrite(word):
    """Overwrite the searched word after conformation"""
    word = word.strip().lower()
    answer = messagebox.askyesno("Conformation", f"the word '{word}' already exists. \nWant to overwrite it?")
    if not answer:
        print("Cancelled overwrite")
        messagebox.showinfo("Info", f"Overwrite cancelled")
        return

    existing_data = wordnet_data.get(word, {})  # Get existing data if available

    definition = simpledialog.askstring("Enter definition", f"Definition for '{word}':") or existing_data.get("definition", "")
    examples = simpledialog.askstring("Enter examples", f"Examples for '{word}' (separate by commas):")
    synonyms = simpledialog.askstring("Enter synonyms", f"Synonyms for '{word}' (separate by commas):")
    antonyms = simpledialog.askstring("Enter antonyms", f"Antonyms for '{word}' (separate by commas):")
    
    # If the user skips an entry, keep the existing data
    wordnet_data[word] = {
        "definition": definition,  # Definition is updated (can be empty)
        "examples": [e.strip() for e in examples.split(",")] if examples else existing_data.get("examples", []),
        "synonyms": [s.strip() for s in synonyms.split(",")] if synonyms else existing_data.get("synonyms", []),
        "antonyms": [a.strip() for a in antonyms.split(",")] if antonyms else existing_data.get("antonyms", [])
    }
    try:
        save_json()
        messagebox.showinfo("Success", f"'{word}' has been updated.")
        entry_word.focus_set()
        display_result(output(word), word)

    except Exception as e:
        messagebox.showerror("Error", f"An error occurred while saving: {e}")


def fetch_word(word):
    """Fetch word details from the online dictionary API."""
    url = f"https://api.dictionaryapi.dev/api/v2/entries/en/{word}"
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        if response.status_code != 200:
            label.config(text=f"Error: Unable to fetch '{word}' from the online dictionary.")
            return {}
    
        data = response.json()
        meanings = data[0].get("meanings", [])
        if not meanings:
            label.config(text=f"Error: '{word}' not found online.")
            print(f"Error: '{word}' not found online.")
            return {}

        definitions = []
        examples = []
        synonyms = set()   # Use a set to avoid duplicates.
        antonyms = set()
        for meaning in meanings:
            for def_entry in meaning.get("definitions", []):
                definitions.append(def_entry.get("definition", "No definition available"))
                ex = def_entry.get("example")
                if ex:
                    examples.append(ex)
                for s in def_entry.get("synonyms", []):
                    synonyms.add(s)
                for a in def_entry.get("antonyms", []):
                    antonyms.add(a)

        if not definitions:
            definitions.append("No definition available")
            
        # Save the fetched word in the offline dictionary.
        wordnet_data[word] = {
            "definition": definitions[0],
            "examples": examples,
            "synonyms": list(synonyms),
            "antonyms": list(antonyms)
        }
        save_json()
        return output(word)

    except (KeyError, KeyboardInterrupt, requests.exceptions.RequestException) as e:
        print(e)
        return {}

def search_word(word):
    """Search for a word in the offline dictionary; if not found, fetch online."""
    word = word.strip().lower()
    if word in wordnet_data:
        return output(word)
    elif not word:
        return {}
    else:
        return fetch_word(word)

def play_audio(file_path):
    """Play an audio file using system's default media player."""
    system = platform.system()
    try:
        if system == "Windows":
            os.startfile(file_path)
        elif system == "Darwin":  # macOS
            subprocess.run(["open", file_path], check=False)
        elif system == "Linux":
            if os.system(f"command -v mplayer >/dev/null") == 0:
                subprocess.run(["mplayer", file_path], check=False)
            elif os.system(f"command -v aplay >/dev/null") == 0:
                subprocess.run(["aplay", file_path], check=False)
            elif os.system(f"command -v ffplay >/dev/null") == 0:
                subprocess.run(["ffplay", "-nodisp", "-autoexit", file_path], check=False)
            elif os.ssytem(f"command -v xdg-open >/dev/null") == 0:
                subprocess.run(["xdg-open", file_path], check=False)
            else:
                messagebox.showerror("Error", "No suitable audio player found. Please install ffplay, aplay, mplayer, or xdg-open.")
        else:
            messagebox.showerror("Error", "Unsupported OS for audio playback.")
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred while playing audio: {e}")
            

# ---------------------------
# GUI Functions
# ---------------------------

def display_result(result, search_term):
    """Update the GUI with search results or suggestion buttons."""
    # Hide any previous suggestion buttons.
    suggestion_yes.pack_forget()
    suggestion_no.pack_forget()
    frame_btn.pack_forget()
    
    if isinstance(result, dict) and result:
        text = (
            f"Word: {result['Word']}\n"
            f"Definition: {result['Definition']}\n"
            f"Examples: {result['Examples']}\n"
            f"Synonyms: {result['Synonyms']}\n"
            f"Antonyms: {result['Antonyms']}"
        )
        label.config(text=text)
    else:
        # No result found; try to suggest a close match.
        match = find_closest_match(search_term)
        print(f"DEBUG: For search term '{search_term}', found suggestion: '{match}'")  # Debug print
        if match:
            label.config(text=f"Did you mean '{match}'?")
            suggestion_yes.config(command=lambda m=match: yes(m))
            suggestion_no.config(command=lambda w=search_term: handle_no(w))
            suggestion_yes.pack(side="left", padx=10, pady=10)
            suggestion_no.pack(side="right", padx=10, pady=10)
            frame_btn.pack(side="bottom", padx=40, pady=0)
            # Give focus to the Yes button so Enter triggers it.
            suggestion_yes.focus_set()
        else:
            # No similar word found; offer to add the word.
            label.config(text=f"No similar words found. Would you like to add '{search_term}'?")
            suggestion_yes.config(command=lambda w=search_term: add_word(w))
            suggestion_no.config(command=lambda w=search_term: handle_no(w))
            suggestion_yes.pack(side="left", padx=10, pady=10)
            suggestion_no.pack(side="right", padx=10, pady=10)
            frame_btn.pack(side="bottom", padx=40, pady=0)
            suggestion_yes.focus_set()
    window.update_idletasks()

def update_overwrite_button(event=None):
    """Enable the overwrite button if the searched word exists in the dictionary."""
    if entry_word.get().strip().lower() in wordnet_data:
        overwrite_button.config(state=tk.NORMAL)
    else:
        overwrite_button.config(state=tk.DISABLED)

def async_search(word):
    """Run the search in a separate thread and update the GUI in the main thread."""
    result = search_word(word)
    window.after(0, display_result, result, word)
    window.after(0, update_overwrite_button, word)

def update_label(event=None):
    """Start a new search thread using the word in the entry widget."""
    suggestion_yes.pack_forget()
    suggestion_no.pack_forget()
    frame_btn.pack_forget()
    search_term = entry_word.get().strip().lower()
    if search_term:
        threading.Thread(target=async_search, args=(search_term,)).start()
        entry_word.focus_set()   # Automatically select the entry box
    else:
        label.config(text="Please enter a word.")

def check_entry(event=None):
    """Enable or disable the search button based on entry content."""
    if entry_word.get().strip():
        search_button.config(state=tk.NORMAL)
    else:
        search_button.config(state=tk.DISABLED)
    entry_word.focus_set()

def delete():
    """Clear the entry widget."""
    entry_word.delete(0, tk.END)
    entry_word.focus_set()

def yes(match):
    """When a suggestion is accepted, search using the suggested word."""
    result = search_word(match)
    display_result(result, match)
    entry_word.focus_set()

def handle_no(word):
    """Handle the case where the suggestion is declined."""
    suggestion_yes.pack_forget()
    suggestion_no.pack_forget()
    frame_btn.pack_forget()
    entry_word.focus_set()
    label.config(text=f"'{word}' not found.")

def pronounce_word(word):
    """Pronounce the given word using gTTS."""
    try:
        tts = gTTS(text=word, lang='en')
        audio_file = os.path.join(app_dir, 'temp_audio.mp3')
        tts.save(audio_file)
        print(f"Playing audio...",{audio_file})
        play_audio(audio_file)
        os.remove(audio_file)
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred while pronouncing the word: {e}")


# ---------------------------
# Creating the GUI
# ---------------------------

window = tk.Tk()
window.title("WordWise")
window.configure(bg='#262933')
window.resizable(False, True)

# Set the application icon. (Adjust the path as needed.)
try:
    icon_path = os.path.join(app_dir, "wordwise.png")
    icon = tk.PhotoImage(file=icon_path)
    window.iconphoto(True, icon)
except Exception as e:
    print("Icon not loaded:", e)

# Frame for the entrybox & primary buttons
frame = Frame(window)
frame.pack(side="top")

# Entry widget for word search.
entry_word = tk.Entry(frame,
                   font=("Cantarell", 13),
                   bg='#262933',
                   fg='white',
                   insertbackground='white',  # This sets the text cursor (caret) color
                   width=35,
                   relief=tk.SUNKEN,
                   bd=2)
entry_word.pack(pady=10, padx=5)
entry_word.bind("<KeyRelease>", check_entry)
entry_word.bind("<Return>", update_label)

# Main control buttons.
search_button = tk.Button(frame, text="Search",
                          font=("Cantarell", 11),
                          bg='#262933',
                          fg='white',
                          state="disabled",
                          command=update_label)

delete_button = tk.Button(frame, text="Delete",
                          font=("Cantarell", 11),
                          bg='#262933',
                          fg='white',
                          command=delete)

pronounce_button = tk.Button(frame, text="Pronounce",
                             font=("Cantarell", 11),
                             bg='#262933',
                             fg='white',
                             command=lambda: pronounce_word(entry_word.get().strip().lower()))

# Frame for suggestion button
frame_btn = Frame(window, bg='#262933')

# Suggestion buttons (initially not packed).
suggestion_yes = tk.Button(frame_btn, text="Yes",
                           font=("Cantarell", 11),
                           bg='#262933',
                           fg='green',
                           activeforeground='green',
                           bd=2,
                           relief="raised")
# Bind the Return key for the Yes button.
suggestion_yes.bind("<Return>", lambda event: suggestion_yes.invoke())

suggestion_no = tk.Button(frame_btn, text="No",
                          font=("Cantarell", 11),
                          bg='#262933',
                          fg='orange',
                          activeforeground='orange')

overwrite_button = tk.Button(frame, text="Edit",
                          font=("Cantarell", 11),
                          bg='#262933',
                          fg='red',
                          activeforeground='red',
                          state="disabled",
                          command=lambda: overwrite(entry_word.get()))

# Output label for displaying word details.
label = tk.Label(window, text="",
                 font=("Cantarell", 12),
                 bg='#262933',
                 fg='white',
                 justify=tk.LEFT,
                 wraplength=380)

# Pack the main control buttons
label.pack(side="top", pady=15, padx=5)
search_button.pack(side="left", padx=20, pady=10)
delete_button.pack(side="left", padx=20, pady=10)
overwrite_button.pack(side="left",padx=20, pady=10)
pronounce_button.pack(side="right", padx=20, pady=10)

# Automatically focus the entry box when app starts
entry_word.focus_set()

# ---------------------------
# Start the Application
# ---------------------------
window.mainloop()
