from src.login import get_cookie
from src.grab_data import get_prefixes, scrape
from os import environ
import dotenv

# Load .env file
dotenv.load_dotenv()

def main():
    # Check for environmental variables
    if 'TERM' not in environ:
        print("TERM environmental variable not set.")
        exit(1)
    if 'NETID' not in environ:
        print("NETID environmental variable not set.")
        exit(1)
    if 'PASSWORD' not in environ:
        print("PASSWORD environmental variable not set.")
        exit(1)

    # Get the term
    term = environ['CLASS_TERM']

    # Get prefixes
    prefixes = get_prefixes()

    # Call the function to get the cookie
    session_id = get_cookie()

    # GET ALL THE DATA!!
    scrape(session_id, term, prefixes)

if __name__ == '__main__':
    main()
