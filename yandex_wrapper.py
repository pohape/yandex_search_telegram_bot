from bs4 import BeautifulSoup
import page_helper


class YandexWrapper:
    def __init__(self, folder_id: str, api_token: str):
        self.folder_id = folder_id
        self.api_token = api_token
        self.base_url = 'https://yandex.ru/'

    def parse_results(self, xml):
        soup = BeautifulSoup(xml, 'xml')
        error = soup.find('error')

        if error is not None:
            return error.text, None, None

        docs = soup.find_all('doc')
        results = []

        for doc in docs:
            url = doc.find('url').text
            domain = doc.find('domain').text
            title = doc.find('title').text
            mime_type = doc.find('mime-type').text
            text = "\n".join(
                [passage.text for passage in doc.find_all('passage')])

            if mime_type == 'text/html' and domain != 'www.youtube.com':
                results.append({
                    'domain': domain,
                    'url': url,
                    'title': title,
                    'text': text
                })

        return None, soup.find('query').text, results

    def search(self, query):
        url = "{}search/xml?folderid={}&apikey={}&query={}".format(
            self.base_url,
            self.folder_id,
            self.api_token,
            query
        )

        error, response_xml = page_helper.download(url)

        if error is not None:
            print(error)

            return error, []

        return error, response_xml
