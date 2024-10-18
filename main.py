import sys
from src.login import get_cookie
from src.grab_data import get_prefixes, scrape


def main():
    # Check for 1 command line argument
    if len(sys.argv) != 2:
        print('Usage: python main.py <term (should be [2 digit year][s/f])>')
        exit(1)
    
    # Get the term from the command line argument
    term = sys.argv[1]

    # Get prefixes
    prefixes = get_prefixes()

    # Call the function to get the cookie
    session_id = get_cookie()

    # GET ALL THE DATA!!
    scrape(session_id, term, prefixes)

if __name__ == '__main__':
    main()
