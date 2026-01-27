# Import the required libraries:
import requests
import time
import re
from pathlib import Path

# Declare the class:
class ScryfallDownloader:
    """MTG card image downloader, from Scryfall API"""
    
    # Scryfall URL:
    BASE_URL = "https://api.scryfall.com"

    # A 100ms delay between requests is required to avoid blockage:
    DELAY = 0.1
    
    #
    # Initialisation function:
    #
    def __init__(self, output_folder="imagenes_descargadas", log_callback=None):

        # Store the output folder path:
        self.output_folder = Path(output_folder)

        # Create the directory and its parents if they do not exist:
        self.output_folder.mkdir(parents=True, exist_ok=True)

        # Store the callback function to update the GUI:
        self.log_callback = log_callback 

        # Initialise the statistics dictionary:
        self.stats = {
            'successful': 0,
            'failed': 0,
            'total': 0
        }

        # Start time variable:
        self.start_time = None

        # End time variable:
        self.end_time = None

    #
    # Logging function:
    #
    def log(self, message):

        # Print the message:
        print(message)

        # If a GUI callback is provided:
        if self.log_callback:

            # Send the message to the GUI window:
            self.log_callback(message)
    
    #
    # Define the parsing function for Moxfield lines:
    #
    def parse_moxfield_line(self, line):

        # Remove whitespaces from the beginning and end:
        line = line.strip()
        
        # Check if the line is empty or starts with a comment:
        if not line or line.startswith('#'):

            # End the function if it is not a valid card line:
            return None

        # Remove unwanted symbols such as *F* (foil), ★, and others:
        line = re.sub(r'\s*(\*F\*|★)\s*$', '', line)

        # Define the regular expression pattern for Moxfield format:
        pattern = r'^(\d+)\s+(.+?)\s+\(([A-Z0-9]+)\)\s+(\S+)$'

        # Try to match the line with the pattern:
        match = re.match(pattern, line)
        
        # If the line matches the expected format:
        if match:

            # Extract the quantity from the first group:
            quantity = int(match.group(1))

            # Extract the card name from the second group:
            card_name = match.group(2).strip()

            # Extract the set code from the third group:
            set_code = match.group(3).upper()

            # Extract the collector number from the fourth group:
            collector_number = match.group(4)
            
            # Return a dictionary with the extracted data:
            return {
                'quantity': quantity,
                'name': card_name,
                'set': set_code,
                'collector_number': collector_number
            }
        
        # If the line format is incorrect:
        else:

            # Log the error message:
            self.log(f"No se pudo parsear: {line}")

            # End the function:
            return None
    
    #
    # Function to fetch card data from Scryfall:
    #
    def get_card_from_scryfall(self, set_code, collector_number):

        # Construct the API URL using set and collector number:
        url = f"{self.BASE_URL}/cards/{set_code.lower()}/{collector_number}"
        
        # Attempt the web request:
        try:

            # Send a GET request with a 10 second timeout:
            response = requests.get(url, timeout=10)

            # Raise an exception if the status code is not 200:
            response.raise_for_status()

            # Return the JSON response from the API:
            return response.json()
        
        # Catch any request-related errors:
        except requests.exceptions.RequestException as e:

            # Log the error including the set and number:
            self.log(f"Error al obtener carta {set_code} {collector_number}: {e}")

            # End the function:
            return None

    #
    # Method to clean file names:
    #
    def clean_filename(self, filename):

        # Define a string with all forbidden characters in Windows/Linux:
        invalid_chars = '<>:"/\\|?*'

        # Iterate through each invalid character:
        for char in invalid_chars:

            # Replace the forbidden character with an underscore:
            filename = filename.replace(char, '_')

        # Return the clean filename:
        return filename
    
    #
    # Image file download method:
    #
    def download_image(self, card_data, copy_number=1):

        # If the card data is not valid:
        if not card_data:

            # End the function:
            return False
        
        # Try to get the image URIs dictionary:
        image_uris = card_data.get('image_uris')
        
        # Check if it is a double-faced card without main URIs:
        if not image_uris and 'card_faces' in card_data:

            # Use the image URIs from the first face:
            image_uris = card_data['card_faces'][0].get('image_uris')
        
        # Verify if a PNG version of the image exists:
        if not image_uris or 'png' not in image_uris:

            # Log that the PNG format was not found:
            self.log(f"No hay imagen PNG disponible para {card_data.get('name')}")

            # End the function:
            return False
        
        # Extract the specific PNG URL:
        png_url = image_uris['png']
        
        # Clean the card name for the filename:
        card_name = self.clean_filename(card_data['name'])

        # Get the set code in uppercase:
        set_code = card_data['set'].upper()

        # Get the collector number:
        collector_num = card_data['collector_number']
        
        # Format the final filename including copy number:
        filename = f"{card_name}_{set_code}_{collector_num}_{copy_number}.png"

        # Combine the output folder with the filename:
        filepath = self.output_folder / filename
        
        # Attempt to download and save the file:
        try:

            # Log the start of the download:
            self.log(f"Descargando: {filename}")

            # Request the image content with a 30 second timeout:
            img_response = requests.get(png_url, timeout=30)

            # Check for request errors:
            img_response.raise_for_status()
            
            # Open the file path in write-binary mode:
            with open(filepath, 'wb') as f:

                # Write the image content to the file:
                f.write(img_response.content)
            
            # Log the successful save:
            self.log(f"Guardada: {filename}")

            # End the function:
            return True
            
        # Catch any download errors:
        except requests.exceptions.RequestException as e:

            # Log the specific error:
            self.log(f"Error al descargar imagen: {e}")

            # End the function:
            return False
    
    #
    # Main process for the decklist:
    #
    def process_decklist(self, decklist_file):

        # Record the current time as start time:
        self.start_time = time.time()
        
        # Log the beginning of the process:
        self.log(f"\nIniciando descarga de proxies desde: {decklist_file}")

        # Log the absolute path of the output folder:

        self.log(f"Las imágenes se guardarán en: {self.output_folder.absolute()}\n")
        
        # Attempt to read the input file:
        try:

            # Open the text file with UTF-8 encoding:
            with open(decklist_file, 'r', encoding='utf-8') as f:

                # Read all lines into a list:
                lines = f.readlines()

        # Catch the error if the file is missing:
        except FileNotFoundError:

            # Log the missing file error:
            self.log(f"No se encontró el archivo: {decklist_file}")

            # Abort the process:
            return
        
        # Initialise a list for valid card data:
        cards_to_download = []

        # Iterate through each line of the file:
        for line in lines:

            # Parse the line content:
            parsed = self.parse_moxfield_line(line)

            # If the line is valid:
            if parsed:

                # Add the dictionary to our list:
                cards_to_download.append(parsed)

                # Update the total count of cards:
                self.stats['total'] += parsed['quantity']
        
        # Log the total amount of cards found:
        self.log(f"Total de cartas a descargar: {self.stats['total']}\n")
        
        # Iterate through the list of cards to download:
        for card_info in cards_to_download:

            # Log the search of the current card:
            self.log(f"\nBuscando: {card_info['name']} ({card_info['set']}) #{card_info['collector_number']}")
            
            # Fetch data from Scryfall API:
            card_data = self.get_card_from_scryfall(
                card_info['set'], 
                card_info['collector_number']
            )
            
            # If API data was successfully retrieved:
            if card_data:

                # Loop through the required quantity of copies:
                for copy in range(1, card_info['quantity'] + 1):

                    # Attempt to download the image:
                    if self.download_image(card_data, copy):

                        # Increment successful counter:
                        self.stats['successful'] += 1

                    # If download fails:
                    else:

                        # Increment failed counter:
                        self.stats['failed'] += 1
                    
                    # If it is not the last copy or the last card:
                    if copy < card_info['quantity'] or card_info != cards_to_download[-1]:
                        
                        # Wait to respect the API rate limit:
                        time.sleep(self.DELAY)

            # If API data could not be retrieved:
            else:

                # Mark all requested copies as failed:
                self.stats['failed'] += card_info['quantity']
            
            # Wait briefly between different cards:
            time.sleep(self.DELAY)
        
        # Record the current time as end time:
        self.end_time = time.time()
        
        # Trigger the final summary:
        self.print_summary()
    
    # Define the method to display the final summary:
    def print_summary(self):

        # Check if both time markers are valid:
        if self.start_time and self.end_time:

            # Calculate total elapsed seconds:
            elapsed_time = self.end_time - self.start_time

            # Calculate integer minutes:
            minutes = int(elapsed_time // 60)

            # Calculate remaining seconds:
            seconds = elapsed_time % 60

            # Format the time string:
            time_str = f"{minutes}m {seconds:.2f}s" if minutes > 0 else f"{seconds:.2f}s"

        # If time markers are missing:
        else:

            # Set time as Not Available:
            time_str = "N/A"
        
        # Log the decorative separator:
        self.log("\n" + "="*50)

        # Log the summary header:
        self.log("RESUMEN DE DESCARGAS")

        # Log another separator:
        self.log("="*50)

        # Log the successful/total ratio:
        self.log(f"successful: {self.stats['successful']}/{self.stats['total']}")

        # Log the failed/total ratio:
        self.log(f"failed: {self.stats['failed']}/{self.stats['total']}")

        # Log the total time taken:
        self.log(f"Tiempo total: {time_str}")

        # Log the absolute path where images were saved:
        self.log(f"Carpeta de salida: {self.output_folder.absolute()}")

        # Log the closing separator:
        self.log("="*50)