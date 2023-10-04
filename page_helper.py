from bs4 import BeautifulSoup
import requests


def download(url):
    error = None

    try:
        response = requests.get(url)
        response_text = response.text

        if response.status_code != 200:
            error = "Something went wrong, got status code {}".format(
                response.status_code
            )
    except requests.RequestException as e:
        error = "Could not download: {}".format(e)
        response_text = None

    return error, response_text


def get_clean_text(html: str):
    content = BeautifulSoup(html, "html.parser").text

    while content.find('\n\n') > -1:
        content = content.replace('\n\n', '\n')

    return content


def download_and_parse_clean(url):
    error, html = download(url)

    if error:
        return error, None

    return None, get_clean_text(html)
