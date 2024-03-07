from bs4 import BeautifulSoup
import requests
import json

#muscle_list = ["neck", "trapezius", "shoulder", "chest", "back", "erector-spinae", "biceps", "triceps", "forearm", "abs", "leg", "calf", "hips", "cardio", "full-body"]
muscle_list = ["neck"]

base_url = "https://fitnessprogramer.com/exercise-primary-muscle/{}/page/{}/"

exercises = {}

def parse_muscle_work_details(details_url):
    """
    Fetches and parses the muscle work details from the given URL.

    Args:
    - details_url (str): The URL to fetch the muscle work details from.

    Returns:
    - dict: A dictionary containing the muscles worked and their involvement.
    """
    response = requests.get(details_url)
    if response.status_code != 200:
        return {}

    details_soup = BeautifulSoup(response.text, 'html.parser')
    muscles_worked = {}

    # Find all the progress bar containers that indicate muscle work levels
    for bar in details_soup.select('.vc_progress_bar .vc_single_bar'):
        label = bar.find('small', class_='vc_label').get_text(strip=True)
        percentage = bar.find('span', class_='vc_bar')['data-percentage-value']
        muscles_worked[label] = percentage

    return muscles_worked

def parse_article(article):
    """
    Parses an article BeautifulSoup object and extracts information into a dictionary.

    Args:
    - article (BeautifulSoup object): The article to parse.

    Returns:
    - dict: A dictionary containing the extracted information.
    """
    # Initialize an empty dictionary to store the extracted information
    article_info = {}

    # Extract the title and URL
    title_tag = article.find('h2', class_='title').find('a')
    article_info['title'] = title_tag.get_text(strip=True)
    article_info['url'] = title_tag['href']

    # Extract equipment
    equipment_tag = article.find('div', class_='exercise_meta equipment')
    article_info['equipment'] = equipment_tag.get_text(strip=True).replace('Equipment:', '').strip()

    # Extract primary muscles
    primary_muscles_tag = article.find('div', class_='exercise_meta primary_muscles')
    article_info['primary_muscles'] = primary_muscles_tag.get_text(strip=True).replace('Primary Muscles:', '').strip()

    # Extract image URL
    img_tag = article.find('img')
    article_info['image_url'] = img_tag['src'] if img_tag else None

    # Extract details URL
    details_tag = article.find('a', class_='button')
    if details_tag:
        article_info['details_url'] = details_tag['href']
        
        # Fetch and parse muscle work details from the details URL
        muscle_work_details = parse_muscle_work_details(article_info['details_url'])
        article_info['muscles_worked'] = muscle_work_details

    return article_info

for muscle in muscle_list:
    print(f"Current muscle group: {muscle}")
    # Start with the first page
    page_number = 1
    has_next_page = True

    while has_next_page:
        print(f"Scraping page {page_number}")
        url = base_url.format(muscle, page_number)
        page = requests.get(url)
        print("Fetching:", url)
        print("Status Code:", page.status_code)

        if page.status_code == 200:
            soup = BeautifulSoup(page.text, 'html.parser')
            target_div = soup.find('div', class_='wpt_exercise_archive taxonomy_archive')

            # Extract articles
            articles = target_div.find_all('article') if target_div else []
            for article in articles:
                parsed_article = parse_article(article)
                exercises[parsed_article["title"]] = parsed_article
                # Perform additional processing on each article here
            
            # Check for next page
            pagination_div = soup.find('div', class_='pagination winner_pagination')
            next_page_link = pagination_div.find('a', class_='next page-numbers') if pagination_div else None
            has_next_page = True if next_page_link else False
        else:
            print(f"Failed to fetch the page for {muscle}, status code: {page.status_code}")
            has_next_page = False  # Stop if there's an issue fetching the page

        page_number += 1  # Move to the next page

    print("-" * 40)  # Print a separator for readability

with open("dump.json", "w") as outfile:
    json.dump(exercises, outfile)
