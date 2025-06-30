import time
from datetime import datetime

def current_timestamp():
    """Get the current timestamp."""
    return int(time.time())  # You can customize this if needed, e.g., datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def convert_to_human_readable(timestamp):
    # Convert timestamp to integer if it's a string
    if isinstance(timestamp, str):
        try:
            timestamp = int(timestamp)  # Convert string to integer
        except ValueError:
            # Handle the case where conversion fails
            return "Invalid Timestamp"
    
    return datetime.utcfromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')

# Example of other helper functions you might need
def sanitize_string(text: str):
    """Sanitize text for use in the database."""
    return text.strip().replace("'", "''")  # Just a simple example
