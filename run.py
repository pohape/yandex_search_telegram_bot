import logging
from bs4 import BeautifulSoup
import requests
from telegram import Update
import telegram.ext
import config


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)


async def process_start_command(
        update: Update,
        context: telegram.ext.ContextTypes.DEFAULT_TYPE
):
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Hi, please send me your search query."
    )


async def process_incoming_message(
        update: Update,
        context: telegram.ext.ContextTypes.DEFAULT_TYPE
):
    error, yandex_search_results_xml = yandex_search(update.message.text)

    if error is not None:
        print(error)

        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Search error: " + error,
            parse_mode=telegram.constants.ParseMode.HTML
        )

        return None

    error, query, results = parse_results(yandex_search_results_xml)

    if error is not None:
        print(error)

        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Parse error: " + error,
            parse_mode=telegram.constants.ParseMode.HTML
        )

        return None

    text_response = "<i>{}</i>:\n\n".format(query)

    for result in results:
        text_response += '<b>{}</b>'.format(
            result['title'])
        text_response += "\n"
        if len(result['text']) > 0:
            text_response += result['text']
            text_response += "\n"
        text_response += '<a href="{}">{}</a>'.format(
            result['url'],
            result['domain']
        )
        text_response += "\n\n"

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=text_response,
        parse_mode=telegram.constants.ParseMode.HTML
    )


def parse_results(xml):
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


def yandex_search(query):
    url = "https://yandex1.ru/search/xml?folderid={}&apikey={}&query={}".format(
        config.yandex_folder_id,
        config.yandex_api_token,
        query
    )

    error, response_xml = download(url)

    if error is not None:
        print(error)

        return error, []

    return error, response_xml


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


if __name__ == '__main__':
    application = telegram.ext.ApplicationBuilder().token(
        config.telegram_token
    ).build()

    incoming_message_handler = telegram.ext.MessageHandler(
        telegram.ext.filters.TEXT & (~telegram.ext.filters.COMMAND),
        process_incoming_message
    )

    start_handler = telegram.ext.CommandHandler('start', process_start_command)
    application.add_handler(start_handler)
    application.add_handler(incoming_message_handler)

    while True:
        try:
            application.run_polling()
            break
        except telegram.error.InvalidToken:
            print("Telegram invalid token: " + config.telegram_token)
            quit()
        except telegram.error.TimedOut:
            print("Telegram server connection time out. Trying again...")
