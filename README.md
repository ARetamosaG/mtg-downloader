# MTG Decklist Image Downloader

A specialised tool designed for Magic The Gathering players who need to collect high quality card images from their decklists quickly and efficiently.

## Purpose

The primary goal of this tool is to simplify the process of gathering card images for printing proxies. Instead of searching for each card manually on databases, this software automates the task by connecting to the Scryfall API. It ensures you get the exact art and edition specified in your decklist (Moxfield format), saving you hours of tedious work when preparing your expensive staples.

---

## Technical Overview

The project is structured into the following Python scripts:

* **`main.py`**: 
    - The entry point of the application. It initialises the main GUI.
* **`scryfall_downloader.py`**: 
    - Handles communication with the Scryfall API, parses the decklist and manages the download stream.
* **`file_select.py`**: 
    - Manages file system interactions, including decklist file validation and the logic for hiding and showing windows during the process.
* **`window_functions.py`**: 
    - A helper module containing reusable UI components, such as custom progress bars, error alerts, and information windows.

---

## Requirements

To run the source code, you will need:

* **Python:** version 3.10 or higher.
* **Libraries:** 
    * `requests` (API communication).
    * `tkinter` (GUI library).
    * `pyinstaller` (optional, to generate an .exe file).

```bash
    pip install requests tkinter pyinstaller
```
---

## Executable file

An executable file is included in the repository, but you can generate your own using the following command:
```bash
    pyinstaller --onefile --windowed main.py
```

The `pyinstaller` library is required to generate the .exe file.

## Version History

* **v1.0**
    * Initial release with Scryfall API integration and basic GUI.
* **v1.1**
    * Added support for double-faced cards (DFCs).
    * New selection window to choose between front, back, or both faces.
    * Added version history to the main menu for better tracking.