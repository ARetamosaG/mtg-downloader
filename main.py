#########################################################
# THIS FILE CONTAINS DIFFERENT FUNCTIONS FOR THE SYSTEM #
#########################################################

# Import helper functions:
from file_select import file_select

# Import the GUI library:
import tkinter as tk

#
# Create the main menu for the program:
#
def main_menu():

    # Initialise the main menu:
    root = tk.Tk()

    # Select a bigger size:
    root.geometry("800x600")

    # Give it a title:
    root.title("Descargador de imágenes de decklists")

    # Create a frame to hold the elements inside the window:
    frame = tk.Frame(root)

    # Center the frame:
    frame.pack(expand=True)

    # Add a label to the frame:
    tk.Label(frame, text="Descargador de imágenes de decklists", font=("Helvetica", 24, "bold")).pack(pady=10)
    tk.Label(frame, text="by AdryRG", font=("Helvetica", 14, "bold")).pack(pady=10)

    # Add the following buttons:
    tk.Button(frame, text="Seleccionar decklist (.txt)", command=lambda:file_select(root),
              width=25, height=2, font=("Helvetica", 16)).pack(pady=10)
    tk.Button(frame, text="Cerrar el programa", command=root.destroy,
              width=25, height=2, font=("Helvetica", 16)).pack(pady=10)

    # Loop the menu:
    root.mainloop()

# Run the main function:
main_menu()