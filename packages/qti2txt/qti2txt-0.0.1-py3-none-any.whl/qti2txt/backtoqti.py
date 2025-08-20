import subprocess
from .qti2txt import logger
from pathlib import Path
import text2qti

# Used for testing to see whether you can convert the file back to QTI using text2qti. Install using pip text2qti
def convert_to_qti(input_file):

    # Check if the file exists and Validate by extension
    if not Path(input_file).is_file():
        raise FileNotFoundError(f"The file {input_file} does not exist.")
    if not input_file.endswith(".txt"):
        raise ValueError("Invalid input file format")

    try:
        result = subprocess.run(
            ["text2qti", input_file], capture_output=True, text=True
        )
        logger.info("Conversion to QTI format successful.")
    except subprocess.CalledProcessError as e:
        logger.warning("Conversion to QTI format failed.")
        logger.debug(f"Subprocess error: {e.stderr}")

if __name__ == "__main__":
    input_file = input("Path to input file: ")
    convert_to_qti(input_file)
