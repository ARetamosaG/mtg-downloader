#######################################
# THIS FILE HAS SOME HELPER FUNCTIONS #
#######################################

# Import the other files and functions:
from scryfall_downloader import ScryfallDownloader
from window_functions import error_window, info_window, create_progress_window

# Import the GUI libraries:
import tkinter as tk
from tkinter import filedialog

# File handler library:
from pathlib import Path

#
# File selection function:
#
def file_select(root):

    # Open the file explorer:
    file_path = filedialog.askopenfilename(

        # Set the window title:
        title="Selecciona tu decklist...",

        # Filter by text files:
        filetypes=(("Archivos de texto", "*.txt"), ("Todos los archivos", "*.*"))
    )

    # If the user cancelled the file selection:
    if not file_path:

        # End the function:
        return

    #
    # SECURITY CHECK #1: check the file extension
    #

    # If the selected file is not a text file:
    if not file_path.lower().endswith('.txt'):

        # Show an error window:
        error_window(root, "Error: El archivo debe ser un formato .txt")

        # End the function:
        return
    
    #
    # SECURITY CHECK #2: check the file content
    #

    # Create a temporary instance to validate:
    validator = ScryfallDownloader()

    # Valid flag:
    is_valid = False
    
    try:

        # Open the file:
        with open(file_path, 'r', encoding='utf-8') as file:

            # Check each line:
            for line in file:

                # If the line is valid:
                if validator.parse_moxfield_line(line):

                    # Check the boolean variable as true:
                    is_valid = True

                    # End the loop since we only need one valid line:
                    break

    # If there was an error:
    except Exception as e:

        # Show an error window:
        error_window(root, f"No se pudo leer el archivo: {e}")

        # End the function:
        return

    # If the file is not valid:
    if not is_valid:

        # Show an error window:
        error_window(root, "El archivo no parece tener un formato Moxfield válido.\nEjemplo: 1 Arid Mesa (MH2) 244")

        # End the function:
        return

    # Hide the main window:
    root.withdraw()

    # If everything is fine, run the download process and open an extra window:
    window_progress, _, text_log = create_progress_window(root)

    # Handle the closure of the progress window:
    def on_closing():

        # Close the window:
        window_progress.destroy()

        # Show the main window again:
        root.deiconify()

    # Set the window protocol:
    window_progress.protocol("WM_DELETE_WINDOW", on_closing)

    # Extract the filename without extension to use as folder name:
    folder_name = Path(file_path).stem
    
    # Create the full path inside the outputs directory:
    final_output_path = Path("imagenes_descargadas") / folder_name

    #
    # Internal function to update the UI:
    #
    def update_ui(mensaje):

        # Insert the message at the end of the text area:
        text_log.insert(tk.END, mensaje + "\n")

        # Auto scrolling to the last line:
        text_log.see(tk.END)

        # Update the window so it doesn't freeze during the process:
        window_progress.update()

    # Attempt the download process:
    try:

        # Create the downloader instance with the output folder and callback:
        downloader = ScryfallDownloader(
            output_folder=final_output_path, 
            log_callback=update_ui
        )

        # Process the decklist file:
        downloader.process_decklist(file_path)
        
        # Close the progress window when finished:
        window_progress.destroy()

        # Show a success information window:
        info_window(root, "¡Descarga completada con éxito!")
        
    # Catch any critical error during the process:
    except Exception as e:

        # If the progress window still exists:
        if window_progress.winfo_exists(): 
            
            # Close it:
            window_progress.destroy()

        # Bring back the main window:
        root.deiconify()

        # Show an error window with the critical error details:
        error_window(root, f"Error crítico: {str(e)}")