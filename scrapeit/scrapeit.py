import re
import logging

import requests
from requests import HTTPError
from bs4 import BeautifulSoup

logging.basicConfig(
    format='%(asctime)s %(message)s',
    datefmt='%m/%d/%Y %I:%M:%S %p',
    level=logging.INFO
)


def set_regex_pattern(start, end):
    """
    Sets a regular expression pattern that matches any text in-bet
    :param start:
    :param end: String
    :return: String regular expression
    """
    regex_pattern = ''
    if start and end:
        regex_pattern = f"(?<={start}).*?(?={end})"
    elif start and not end:
        regex_pattern = f"(?<={start}).*"
    elif end and not start:
        regex_pattern = f".*?(?={end})"
    return regex_pattern


def parse_text_with_regex(match_start, match_end, text):
    """
    Searches blob of text and grabs the text between start and end
    :param match_start: String pattern to start matching after
    :param match_end: String pattern to stop matching before
    :param text: String text to search
    :return: String the match or original text
    """
    re_pattern = set_regex_pattern(match_start, match_end)
    re_match = re.search(re_pattern, text, re.DOTALL)
    if re_match and re_match[0].strip():
        return re_match[0]
    else:
        return text


def make_soup(content):
    """
    Return a BeautifulSoup4 object.
    :param content: String containing HTML
    :return: bs4 object
    """
    return BeautifulSoup(content, "html.parser")


def make_request(url):
    """
    Make GET request to url
    :param url: String URL to load
    :return: requests object
    """
    headers = {
        'User-Agent':
            "Mozilla/5.0"
            " (Windows NT 10.0; Win64; x64; rv:59.0)"
            " Gecko/20100101 Firefox/59.0"
    }
    return requests.get(url, headers=headers)


def get_text_from_single_tag(soup, tag, selector):
    """
    Returns text from the first element that matches tag and selector.
    :param soup: bs4 object
    :param tag: String HTML tag name
    :param selector: Dict property and value to identify the tag
    :return: String text from the matching element
    """
    return soup.find(
        tag,
        selector
    ).get_text().strip()


def get_text_from_many_tags(soup, tag, selector):
    """
    Returns text from any element that matches tag and selector.
    :param soup: bs4 object
    :param tag: String HTML tag name
    :param selector: Dict property and value to identify the tag
    :return: String containing text from all matching elements
    """
    matching_text = ''
    potential_matches = soup.findAll(
        tag,
        selector
    )
    for match in potential_matches:
        matching_text += match.get_text().strip()
    return matching_text


def get_target_from_soup(soup, **kwargs):
    """
    Uses the config to retrieve the desired text from the soup.
    :param soup: bs4 object
    :param kwargs: config file
    :return: String text from the matching elements
    """
    if kwargs['selector_is_unique']:
        website_text = get_text_from_single_tag(
            soup,
            kwargs['selector'][0],
            kwargs['selector'][1]
        )
    else:
        website_text = get_text_from_many_tags(
            soup,
            kwargs['selector'][0],
            kwargs['selector'][1]
        )
    if kwargs['use_regex']:
        website_text = parse_text_with_regex(
            kwargs['match_after'],
            kwargs['stop_matching_at'],
            website_text
        )
    return website_text


def get_text(url_key, **kwargs):
    """
    Use this method to return text from a matching selector
    :param url_key: String key to urls dictionary
    :param kwargs: config file
    :return: String text from the matching elements
    """
    url = kwargs['urls'][url_key]
    response = make_request(url)
    if response.ok:
        soup = make_soup(response.content)
        matching_text = get_target_from_soup(soup, **kwargs)
    else:
        raise HTTPError(f"Received {response.status_code} from {url}")
    if matching_text:
        return matching_text.replace('\n', '').strip()
    else:
        logging.error(f'The selector or regex for {url} returned no matches!')
