import re
import datetime
import logging

import pytz
from pytz.reference import UTC
import requests
from requests import HTTPError
from bs4 import BeautifulSoup

logging.basicConfig(
    format='%(asctime)s %(message)s',
    datefmt='%m/%d/%Y %I:%M:%S %p',
    level=logging.INFO
)


def convert_date_format_to_string(formatting, timezone):
    """
    Translates time format to real time to be used as
    part of a regex search
    :param formatting: List containing:
        :param: time_format: String containing strftime
        :param: extra_characters: String containing any characters that
                follows after the returned date such as ': '
        :param: offset: Int offsets the returned date by this many days
    :param timezone String containing timezone such as
                    'America/Los_Angeles'
    :return: String containing date followed by extra_characters
    """
    if timezone:
        timezone = pytz.timezone(timezone)
    else:
        timezone = UTC
    time_format, extra_characters, offset = formatting
    date_object = pytz.utc.localize(
        datetime.datetime.utcnow() - datetime.timedelta(days=offset)
    ).astimezone(timezone)
    time = date_object.strftime(time_format)
    # TODO remove this lame hack and solve this for real
    if time.split(',')[1][-2] == '0':
        time = time.replace('0', '', 1)
    return time + extra_characters


def find_matching_pattern(text, patterns):
    if patterns:
        for pattern in patterns:
            if pattern in text:
                return pattern


def set_regex_pattern(start, end, text, start_strf, end_strf, timezone):
    """
    Sets a regular expression pattern that matches any text in-bet
    :param start: String to start matching text after
    :param end: String to stop matching text before
    :param start_strf: String strftime date formatting
    :param end_strf: String strftime date formatting
    :param timezone String containing timezone such as
                    'America/Los_Angeles'
    :return: String regular expression
    """
    regex_pattern = ''
    if start_strf:
        start = [convert_date_format_to_string(start_strf, timezone)]
    if end_strf:
        end = [convert_date_format_to_string(end_strf, timezone)]
    start = find_matching_pattern(text, start)
    end = find_matching_pattern(text, end)
    if start and end:
        regex_pattern = f"(?<={start}).*?(?={end})"
    elif start and not end:
        regex_pattern = f"(?<={start}).*"
    elif end and not start:
        regex_pattern = f".*?(?={end})"
    return regex_pattern


def parse_text_with_regex(text, match_start=None, match_end=None,
                          after_strftime=None, end_strftime=None,
                          timezone=None):
    """
    Searches blob of text and grabs the text between start and end
    :param match_start: String pattern to start matching after
    :param match_end: String pattern to stop matching before
    :param text: String text to search
    :param after_strftime: String date format and time offset
    :param end_strftime: String date format and time offset
    :return: String the match or original text
    """
    re_pattern = set_regex_pattern(
        match_start, match_end, text, after_strftime, end_strftime, timezone
    )
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
            website_text,
            match_start=kwargs.get('match_after'),
            match_end=kwargs.get('stop_matching_at'),
            after_strftime=kwargs.get('match_after_strftime'),
            end_strftime=kwargs.get('stop_matching_at_strftime'),
            timezone=kwargs.get('timezone')
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
