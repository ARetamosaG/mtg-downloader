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
