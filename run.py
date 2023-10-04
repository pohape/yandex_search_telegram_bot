import logging
import telegram.ext
import config
from data_manager import DataManager
from tg_wrapper import TgWrapper
from yandex_wrapper import YandexWrapper


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

if __name__ == '__main__':
    data_manager = DataManager()
    yandex_wrapper = YandexWrapper(
        folder_id=config.yandex_folder_id,
        api_token=config.yandex_api_token
    )

    while True:
        tg_wrapper = None

        try:
            tg_wrapper = TgWrapper(
                token=config.telegram_token,
                yandex_wrapper=yandex_wrapper,
                data_manager=data_manager
            )

            break
        except telegram.error.InvalidToken:
            print("Telegram invalid token: " + config.telegram_token)
            quit()
        except telegram.error.TimedOut:
            print("Telegram server connection time out. Trying again...")
