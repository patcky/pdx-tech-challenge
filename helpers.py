import csv
import logging

def save_to_csv(data: list, file_path: str) -> None:
    """Save a dict to a CSV file."""
    try:
        with open(file_path, "w") as csv_file:
            writer = csv.DictWriter(csv_file, data[0].keys())
            writer.writeheader()
            writer.writerows(data)

    except:
        logging.error("Error saving to CSV.")
        raise
