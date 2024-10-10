import re


# Takes in a dirty str and cleans it
def clean(dirty: str):
    # Find all the blocks
    clean = dirty.replace("\n", "").replace("\r", "")
    clean = re.sub(r'\s+', ' ', clean)
    return clean
