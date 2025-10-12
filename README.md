# WordWise
A powerful, user-friendly dictionary with an interactive graphical interface. It provides definitions, examples, synonyms, and antonyms for words using both **offline data** and an **online API**.

Additionally, the project includes a **standalone dictionary app** built using PyInstaller, allowing users to use the dictionary without running Python scripts.

## **Features**  

✔ **Offline & Online Search** – Retrieves word details from a local JSON database and an online API if not found offline.  
✔ **Intelligent Word Matching** – Uses Levenshtein distance to suggest similar words if the search term is incorrect.  
✔ **GUI-Based Search** – Built using **Tkinter**, offering an easy-to-use graphical interface.  
✔ **Word Management** – Allows users to **add, edit, and overwrite** words in the offline dictionary.  
✔ **Speech Feature** – Pronounces words using the `espeak-ng` package.  
✔ **Dictionary App** – A compiled **standalone app** built with **PyInstaller**, eliminating the need for Python installation.

---

## **Installation Guide**  
#### **For Windows**
1. See the `releases` section to get the latest `.exe` file.
2. Double-click to run the file.
3. Download or clone `dictionary.json` file.
4. Paste the file in `APPDATA/WordWise/`

#### **For Linux**
1. See the 'releases` section & download the latest compiled file.
2. Open terminal & paste the following command
```sh
chmod +x wordwise
sudo mv wordwise /usr/local/bin/
cd ~
mkdir ~/.local/share/WordWise/
git clone https://github.com/Mahmud-Mahi/WordWise.git
cd WordWise
mv dictionary.json ~/.local/share/WordWise/
mv wordwise.png ~/.local/share/WordWise/
mv wordwise.desktop ~/.local/share/applications/
```
3. All done!

#### **For macOS **
1. Clone the repository.
2. Build your own app using `main.py` script.
3. Ask any AI chatbot for help.

---

## **How It Works**  

1. **Searching for a Word:**  
   - Type a word in the search box and press **Enter** or click **Search**.  
   - If the word is found in the offline dictionary, its details will be displayed.  
   - If the word isn’t found, the application will try fetching it from the online API.  

2. **Word Suggestions:**  
   - If a word is misspelled, the program suggests a close match.  
   - You can accept the suggestion or manually add a new word.  

3. **Adding a Word:**  
   - If a word is not found, you can choose to add it to the offline dictionary.  
   - You’ll be prompted to enter a definition, examples, synonyms, and antonyms.  

4. **Editing a Word:**  
   - If a word exists in the dictionary, you can overwrite its details by clicking **Edit**.  

5. **Deleting an Entry (Manually):**  
   - Open `offline_dictionary.json` and remove the desired entry.  

6. **Pronunciation Feature:**  
   - Click **Pronounce** to hear the word spoken using `mplayer`.  

---

## **License**  
This project is open-source and licensed under the **MIT License**.  

---

## **Contributions & Issues**  
Feel free to contribute by submitting pull requests. If you encounter any issues, open a ticket in the GitHub **Issues** section.
