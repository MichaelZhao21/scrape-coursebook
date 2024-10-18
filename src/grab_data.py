import requests
import re
import json
from bs4 import BeautifulSoup
from .login import get_cookie

base_url = 'https://coursebook.utdallas.edu'
url = 'https://coursebook.utdallas.edu/clips/clip-cb11-hat.zog'
output = 'classes.json'

def get_prefixes():
    res = requests.get(base_url)

    if res.status_code != 200:
        print('Failed to get coursebook website')
        print(res.text)
        exit(1)

    matches = re.findall(r'\<option value="cp_acct.*\<\/select\>', res.text)
    raw_pre = matches[0]
    
    # Use regex to extract all value fields
    values = re.findall(r'value="([^"]+)"', raw_pre)

    return values


def scrape(session_id, term, prefixes):
    # Keep track of all data
    all_data = []

    # Loop through all the classes
    for i, p in enumerate(prefixes):
        while True:
            headers = {
                'accept': '*/*',
                'accept-language': 'en-US,en;q=0.9',
                'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
                'cookie': f'PTGSESSID={session_id}',
                'origin': 'https://coursebook.utdallas.edu',
                'priority': 'u=1, i',
                'referer': 'https://coursebook.utdallas.edu/',
                'sec-ch-ua': '"Chromium";v="130", "Google Chrome";v="130", "Not?A_Brand";v="99"',
                'sec-ch-ua-mobile': '?0',
                'sec-ch-ua-platform': '"Linux"',
                'sec-fetch-dest': 'empty',
                'sec-fetch-mode': 'cors',
                'sec-fetch-site': 'same-origin',
                'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36',
                'x-requested-with': 'XMLHttpRequest',
            }

            monkey_headers = {
                'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
                'accept-language': 'en-US,en;q=0.9',
                'cookie': f'PTGSESSID={session_id}',
                'priority': 'u=0, i',
                'referer': 'https://coursebook.utdallas.edu/',
                'sec-ch-ua': '"Chromium";v="130", "Google Chrome";v="130", "Not?A_Brand";v="99"',
                'sec-ch-ua-mobile': '?0',
                'sec-ch-ua-platform': '"Linux"',
                'sec-fetch-dest': 'document',
                'sec-fetch-mode': 'navigate',
                'sec-fetch-site': 'same-origin',
                'sec-fetch-user': '?1',
                'upgrade-insecure-requests': '1',
                'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36',
            }

            try:
                print(f'[{i+1}/{len(prefixes)}] Getting data for prefix {p}')

                # Form the request data
                data = {
                    'action': 'search',
                    's[]': [f'term_{term}', p]
                }

                # Get the response
                response = requests.post(url, headers=headers, data=data)

                if response.status_code != 200:
                    print('Failed to get the data page')
                    print(response)
                    print(response.text)
                    raise Exception('Failed to get the data page')

                # If 0 items
                if '(no items found)' in response.text:
                    print('\tNo items found')
                    break

                # Get number of items
                items = re.findall(r'\(\s*(\d+)\s*item(?:s)?\s*\)', response.text)
                if len(items) == 0:
                    print('\tFailed to find number of items')
                    raise Exception('Failed to find number of items')

                items = int(items[0])

                if items == 0:
                    print('\tNo items found')
                    break
                elif items == 1:
                    class_data = get_single_class(response.text, term)
                    all_data.append(class_data)
                    break

                # Use the regex to find the desired part of the response
                matches = re.findall(r'\/reportmonkey\\\/cb11-export\\\/(.*?)\\\"', response.text)

                # Print the matched results
                if len(matches) == 0:
                    print('Failed to find the report ID from the response:')
                    print(response.text)
                    raise Exception('Failed to find the report ID from the response')
                report_id = matches[-1]

                monkey_url = f'https://coursebook.utdallas.edu/reportmonkey/cb11-export/{report_id}/json'

                response = requests.get(monkey_url, headers=monkey_headers)

                if response.status_code != 200:
                    print('Failed to get the report response')
                    print(response.text)
                    raise Exception('Failed to get the report response')

                new_data = response.json()
                all_data.extend(new_data['report_data'])
                break
            except Exception as e:
                print(f'Failed to get data for prefix {p}: {e}')
                print(f'Prompting for new token...')
                session_id = get_cookie()


    # Write the data to a file
    with open(output, 'w') as f:
        json.dump(all_data, f, indent=4)


def get_single_class(data, term):
    # Parse the string as JSON to get the HTML part
    data_json = json.loads(data)
    html_content = data_json["sethtml"]["#sr"]

    # Parse the HTML using BeautifulSoup
    soup = BeautifulSoup(html_content, 'html.parser')

    # Extract the required fields
    class_section = soup.find_all('a', class_='stopbubble')[0].text
    class_title = soup.find_all('td', style="line-height: 1.1rem;")[0].text.strip()
    instructor = soup.find_all('a', class_='ptools-popover')[0].text
    schedule_day = get_text_or_none(soup.find_all('span', class_='clstbl__resultrow__day'))
    schedule_time = get_text_or_none(soup.find_all('span', class_='clstbl__resultrow__time'))
    location = get_text_or_none(soup.find_all('div', class_='clstbl__resultrow__location'))

    # Split the section string up
    a = class_section.split(" ")
    prefix = a[0].lower()
    b = a[1].split(".")
    number = b[0]
    section = b[1]

    # Return the extracted values
    return {
        'section_address': class_section.replace(' ', '').lower() + '.' + term,
        'course_prefix': prefix,
        'course_number': number,
        'section': section,
        'title': class_title.replace(r'\(.*\)', ''),
        'term': term,
        'instructors': instructor,
        'days': schedule_day.replace(' & ', ','),
        'times_12h': schedule_time,
        'location': location
    }


def get_text_or_none(out):
    if not out:
        return ""
    return out[0].text.strip()