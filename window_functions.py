##############################################
# THIS FILE HAS SOME HELPER WINDOW FUNCTIONS #
##############################################

# Import the GUI library:
import tkinter as tk

#
# Helper function to create a window with different customisations:
#
def create_window(root, title="New Window", size="800x600"):

    # Create the window using tkinter:
    window = tk.Toplevel(root)

    # Give it a title:
    window.title(title)

    # Set it to a specified size (800x600 by default):
    window.geometry(size)

    # Make sure the whole program is terminated when clicking on the X button:
    window.protocol("WM_DELETE_WINDOW", root.destroy)

    # Return the window object:
    return window

#
# Helper function to close a window and go back to the previous one:
#
def close_window(root, window):

    # Select all widgets inside of the window:
    for widget in window.winfo_children():

        # Make sure to close all of them to avoid memory leaks:
        widget.destroy()

    # Close the current window:
    window.destroy()

    # Bring back the hidden (main) window:
    root.deiconify()

#
# Helper function to create an error window:
#
def error_window(root, error_message):

    # Create the window template using our function:
    window = create_window(root, title="Error", size="400x200")

    # Add a text label:
    tk.Label(window, text=error_message, font=("Helvetica", 14), fg="red").pack(pady=20)

    # Add a button:
    tk.Button(window, text="Back to Main Menu", command=lambda: close_window(root, window), 
              font=("Helvetica", 16), width=20).pack(pady=10)
    
#
# Helper function to create an info window:
#
def info_window(root, message):

    # Create the window template using our function:
    window = create_window(root, title="Información", size="400x200")

    # If the window is closed (user pressed the X button):
    def on_close():

        # Destroy it:
        window.destroy()

        # Show the main window:
        root.deiconify()

    # Set the window protocol:
    window.protocol("WM_DELETE_WINDOW", on_close)

    # Add a text label:
    tk.Label(window, text=message, font=("Helvetica", 14), wraplength=350).pack(pady=20)

    # Add a button:
    tk.Button(window, text="Vale", command=on_close, 
              font=("Helvetica", 16), width=20).pack(pady=10)

#
# Helper function to create a progress window:
#
def create_progress_window(root):
    
    # Create the window template using our function:
    window = create_window(root, title="Descargando...", size="500x400")
    
    # Add a text label:
    label = tk.Label(window, text="Iniciando descarga...", font=("Helvetica", 12, "bold"))
    label.pack(pady=10)
    
    # Add a text area to show the console logs:
    text_area = tk.Text(window, height=15, width=55, font=("Consolas", 10))
    text_area.pack(pady=10, padx=10)
    
    return window, label, text_area

#
# Helper function to decide on double-faced cards:
#
def ask_dfc_option(root):

    # Set 'cancel' as a special value to detect whether the window is closed:
    choice = tk.StringVar(value="cancel")
    
    # Create a modal window:
    dialog = tk.Toplevel(root)
    dialog.title("Se han detectado cartas de doble cara")
    dialog.geometry("400x250")

    # Make it so the user can't click outside of the window:
    dialog.grab_set()

    # Whenever the option is confirmed:
    def confirm():

        # Set 'both' as the default option when confirming:
        if choice.get() == "cancel":
            choice.set("both")

        # Destroy this window:
        dialog.destroy()

    # If the user closes the window:
    def on_x():

        # Keep setting the value to 'cancel':
        choice.set("cancel")

        # Destroy the window:
        dialog.destroy()

    # Set the window protocol:
    dialog.protocol("WM_DELETE_WINDOW", on_x)
    
    # Add a label:
    tk.Label(dialog, text="Se han detectado cartas de doble cara.\n¿Qué caras quieres descargar?", 
             font=("Helvetica", 12, "bold"), pady=15).pack()
    
    # Set 'both' as the default selected option:
    choice.set("both")

    # Create an options set:
    options = [
        ("Solo cara delantera (Front)", "front"),
        ("Solo cara trasera (Back)", "back"),
        ("Ambas caras (Both)", "both")
    ]
    
    # Create a button for each available option:
    for text, val in options:
        tk.Radiobutton(dialog, text=text, variable=choice, value=val, font=("Helvetica", 11)).pack(anchor=tk.W, padx=50)
    
    # Add a confirm button:
    tk.Button(dialog, text="Confirmar y empezar", command=confirm, font=("Helvetica", 12)).pack(pady=20)
    
    # Wait until the window is closed:
    dialog.wait_window()

    # If there was a selected option:
    if choice.get() != "cancel":

        # Return it:
        return choice.get() 
    
    # If the value is 'cancel', return None:
    return None 