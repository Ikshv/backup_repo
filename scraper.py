import time
from utils.result import Results

from simhash import Simhash
import nltk

nltk.download('punkt')
from nltk.tokenize import word_tokenize
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import re


def scraper(url, resp, result):
    # resp={'status': resp.status_code, 'error': None, 'url': url, 'raw_response': {'url': resp.url, 'content': resp.text}}
    if url in result.visited_urls or is_calendar_url(url):  # If the URL has already been visited, return an empty list
        return []
    result.add_to_visited(url)
    result.add_subdomain(url)
    links = extract_next_links(url, resp, result)
    result.log_results(url)  # Log the results
    return [link for link in links if is_valid(link)]


def extract_next_links(url, resp, result):
    # Implementation required.
    # url: the URL that was used to get the page
    # resp.url: the actual url of the page
    # resp.status: the status code returned by the server. 200 is OK, you got the page. Other numbers mean that there was some kind of problem.
    # resp.error: when status is not 200, you can check the error here, if needed.
    # resp.raw_response: this is where the page actually is. More specifically, the raw_response has two parts:
    #         resp.raw_response.url: the url, again
    #         resp.raw_response.content: the content of the page!
    # Return a list with the hyperlinks (as strings) scrapped from resp.raw_response.content
    extracted_links = []
    # Proceed only for successful HTTP responses
    # print(resp.status, resp.raw_response.content, resp.raw_response.url, resp.url, url)
    if resp.status == 200 and resp.raw_response and resp.raw_response.content:
        # Parse the HTML content of the page
        print("starting to parse")
        soup = BeautifulSoup(resp.raw_response.content, 'html.parser')
        # Find all anchor tags and extract href attributes
        text = soup.get_text(separator=' ', strip=True)
        if not is_new_page(text, result):
            return []
        tokens = extract_data(text)
        for token in tokens:
            result.add_word_to_common_count(token)
        result.handle_max_words_per_page(url, len(tokens))  # Handle max words per page
        for link in soup.find_all('a', href=True):  # Extract all links
            # Resolve relative URLs to absolute URLs
            absolute_link = urljoin(url, link['href']).split('#')[0]
            if not is_calendar_url(absolute_link):
                extracted_links.append(absolute_link)
    if resp.status != 200:
        print(f"Error: {resp.error} for URL: {url}")
    ## TODO: DETECT AND AVOID SIMILAR PAGES W/ NO INFO
    ## TODO: DETECT AND AVOID CRAWLING VERY LARGE FILES, ESP W/ LOW INFO VAL.
    return extracted_links


def extract_data(text):
    # Extract data from the page
    # Implementation required.
    # soup: a beautiful soup object
    # resp: the response object associated with the page
    # Return a dictionary with the data you want to save from the page    
    tokens = word_tokenize(text)
    return [token.lower() for token in tokens if token.isalnum()]


def calculate_text_to_html_ratio(content):
    soup = BeautifulSoup(content, 'html.parser')
    text = soup.get_text(separator=' ', strip=True)
    html_length = len(content)
    text_length = len(text)
    if html_length == 0: return 0  # Avoid division by zero
    return text_length / html_length

def is_calendar_url(url):
    patterns = [
        r'.*calendar.*',
        r'.*event.*',
        r'.*schedule.*',
        r'.*\?date=.*',
        r'.*\?start=.*&end=.*',
        r'https?://[^/]+/calendar/.*',
        r'https?://[^/]+/events/.*',
        r'.*\d{4}/\d{2}/\d{2}.*',
        r'.*\d{2}/\d{2}/\d{4}.*'
    ]
    return any(re.search(pattern, url) for pattern in patterns)


def is_valid(url):
    # Decide whether to crawl this url or not. 
    # If you decide to crawl it, return True; otherwise return False.
    # There are already some conditions that return False.
    try:
        parsed = urlparse(url)
        if parsed.scheme not in set(["http", "https"]):
            return False
        if not re.match(
                r".*\.ics\.uci\.edu.*|"
                + r".*\.cs\.uci\.edu.*|"
                + r".*\.informatics\.uci\.edu.*|"
                + r".*\.stat\.uci\.edu.*|"
                + r"today\.uci\.edu/department/information_computer_sciences.*", parsed.netloc.lower()):
            return False
        return not re.match(
            r".*\.(css|js|bmp|gif|jpe?g|ico"
            + r"|png|tiff?|mid|mp2|mp3|mp4"
            + r"|wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|pdf"
            + r"|ps|eps|tex|ppt|pptx|doc|docx|xls|xlsx|names"
            + r"|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso"
            + r"|epub|dll|cnf|tgz|sha1"
            + r"|thmx|mso|arff|rtf|jar|csv"
            + r"|rm|smil|wmv|swf|wma|zip|rar|gz)$", parsed.path.lower())

    except TypeError:
        print("TypeError for ", parsed)
        raise


def get_features(s):
    width = 5
    s = s.lower()
    s = re.sub(r'[^\w]+', '', s)
    return [s[i:i + width] for i in range(max(len(s) - width + 1, 1))]


def is_new_page(text, results):
    ##TODO: Implement simhash
    simhash_value = Simhash(get_features(text))
    return results.handle_simhash(simhash_value)
