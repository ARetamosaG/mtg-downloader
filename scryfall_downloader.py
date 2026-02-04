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
            name = match.group(2).strip()

            # Extract the set code from the third group:
            set = match.group(3).upper()

            # Extract the collector number from the fourth group:
            collector_number = match.group(4)
            
            # Return a dictionary with the extracted data:
            return {
                'quantity': quantity,
                'name': name,
                'set': set,
                'collector_number': collector_number
            }
        
        # If the line format is incorrect:
        else:

            # Log the error message if the line format:
            self.log(f"No se pudo parsear: {line}")

            # End the function:
            return None
        
    #
    # Helper function to check whether the decklist has DFCs:
    #
    def check_for_dfcs(self, file_path):

        # Attempt the web request:
        try:
            
            # Open the file:
            with open(file_path, 'r', encoding='utf-8') as f:

                # Read the lines:
                lines = f.readlines()
            
            # Initialise a list to store identifiers:
            identifiers = []

            # Iterate through each line:
            for line in lines:

                # Extract the card info:
                info = self.parse_moxfield_line(line)

                # If the line is valid:
                if info:

                    # Add the set and collector number to the list:
                    identifiers.append({"set": info['set'], "collector_number": info['collector_number']})
            
            # Consult the Scryfall API in batches:
            for i in range(0, len(identifiers), 75):

                # Slice the list to get the current batch:
                batch = identifiers[i:i+75]

                # Make the POST request:
                resp = requests.post(f"{self.BASE_URL}/cards/collection", json={"identifiers": batch})

                # If the response is successful:
                if resp.status_code == 200:

                    # Extract the cards data:
                    cards = resp.json().get('data', [])

                    # For each card:
                    for card in cards:

                        # If a card has faces but no main image URI, it is a DFC:
                        if 'card_faces' in card and 'image_uris' not in card:

                            # Return True the first time a DFC is found:
                            return True
                        
            # If no DFCs were found, return False:
            return False
        
        # If any error occurs during the process:
        except Exception:

            # Return False to proceed with default behaviour:
            return False
    
    #
    # Image file download method:
    #
    def download_image(self, card_data, dfc_policy="both", copy_number=None, copy_suffix=""):

        # Clean the name for filenames (replace / or // with _):
        card_name = card_data.get('name', 'Unknown').replace(" // ", "_").replace("/", "_")

        # Get the set code from the data:
        set_code = card_data.get('set', 'Unknown')

        # Get the collector number from the data:
        collector_num = card_data.get('collector_number', 'Unknown')
        
        # Initialise the list of URLs to process:
        urls_to_download = []

        # Check for a DFC (has faces but no main image):
        if 'card_faces' in card_data and 'image_uris' not in card_data:

            # Store the faces data:
            faces = card_data['card_faces']

            # If 'front' was chosen as the selected policy:
            if dfc_policy in ["front", "both"]:

                # Add the front face URL:
                urls_to_download.append((faces[0]['image_uris']['png'], "front"))

            # If 'back' was chosen as the selected policy:
            if dfc_policy in ["back", "both"]:

                # Perform a security check:
                if 'image_uris' in faces[1]:

                    # Add the back face URL:
                    urls_to_download.append((faces[1]['image_uris']['png'], "back"))

        # If it is a single-faced card:
        else:

            # Add the main URL with no suffix:
            urls_to_download.append((card_data['image_uris']['png'], ""))

        # Initialise the success flag:
        success = True

        # Copy number suffix:
        copy_suffix = f"_{copy_number}" if copy_number else ""

        # Iterate through each URL to download:
        for url, face_suffix in urls_to_download:

            # Format the suffix string if it exists:
            face_str = f"_{face_suffix}" if face_suffix else ""
            
            # Construct the final filename:
            filename = f"{card_name}{face_str}{copy_suffix}_{set_code}_{collector_num}.png"

            # Construct the full filepath:
            filepath = self.output_folder / filename
            
            # Start the download attempt:
            try:

                # Log the current download progress:
                self.log(f"Descargando: {filename}")

                # Make the GET request:
                res = requests.get(url, timeout=30)

                # Raise an error for bad responses:
                res.raise_for_status()

                # Open the file in BINARY WRITE MODE:
                with open(filepath, 'wb') as f:

                    # Write the image content:
                    f.write(res.content)

                # Wait for the API delay to avoid rate limiting:
                time.sleep(self.DELAY)

            # If a download fails:
            except Exception as e:

                # Log the error message:
                self.log(f"Error en {filename}: {e}")

                # Set the success flag to False:
                success = False

        # Return the final success status:
        return success
    
    #
    # Main function to process the decklist:
    #
    def process_decklist(self, file_path, dfc_policy="both"):

        # Create the output folder when the process starts:
        self.output_folder.mkdir(parents=True, exist_ok=True)

        # Set the start time:
        self.start_time = time.time()
        
        # Start the file processing block:
        try:

            # Open the decklist file:
            with open(file_path, 'r', encoding='utf-8') as f:

                # Read all lines:
                lines = f.readlines()

            # Process each line:
            for line in lines:

                # Extract the card info:
                card_info = self.parse_moxfield_line(line)

                # If the line is invalid or empty:
                if not card_info:

                    # Skip it:
                    continue

                # Save the number of copies to download:
                quantity = card_info.get('quantity', 1)

                # Construct the Scryfall API URL for the card:
                api_url = f"{self.BASE_URL}/cards/{card_info['set']}/{card_info['collector_number']}"
                
                # Request individual card data:
                try:

                    # GET request to the Scryfall API:
                    response = requests.get(api_url, timeout=30)

                    # Ensure the response is successful:
                    response.raise_for_status()

                    # Parse the JSON data:
                    card_data = response.json()
                    
                    # Download each copy:
                    for i in range(1, quantity + 1):

                        # Increment the total card counter:
                        self.stats['total'] += 1

                        # Add a suffix to avoid overwriting if multiple copies:
                        copy_suffix = f"{i}" if quantity > 1 else ""
                        
                        # Call 'download_image' with the suffix:
                        if self.download_image(card_data, dfc_policy, copy_suffix):

                            # Increment the successful counter:
                            self.stats['successful'] += 1

                        # If the download failed:
                        else:

                            # Increment the failed counter:
                            self.stats['failed'] += 1
                        
                # Catch any API exceptions:
                except Exception as e:

                    # Log the API error:
                    self.log(f"Error API ({card_info['name']}): {e}")

                    # Increment the failed counter:
                    self.stats['failed'] += 1
                
                # Sleep between cards to respect the API limits:
                time.sleep(self.DELAY)

        # Catch any general file processing errors:
        except Exception as e:

            # Log the error:
            self.log(f"Error procesando archivo: {e}")
        
        # Set the end time:
        self.end_time = time.time()
        
        # Display the summary:
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