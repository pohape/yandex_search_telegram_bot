import json
import telegram

from data_manager import DataManager
from yandex_wrapper import YandexWrapper


class TgWrapper:
    def __init__(
        self,
        token: str,
        yandex_wrapper: YandexWrapper,
        data_manager: DataManager
    ):
        self.data_manager = data_manager
        self.yandex_wrapper = yandex_wrapper
        application = telegram.ext.ApplicationBuilder().token(token).build()

        incoming_message_handler = telegram.ext.MessageHandler(
            telegram.ext.filters.TEXT & (~telegram.ext.filters.COMMAND),
            self.process_incoming_message
        )

        start_handler = telegram.ext.CommandHandler(
            'start',
            self.process_start_command
        )

        application.add_handler(start_handler)
        application.add_handler(incoming_message_handler)
        application.run_polling(close_loop=False)

    async def process_incoming_message(
            self,
            update: telegram.Update,
            context: telegram.ext.ContextTypes.DEFAULT_TYPE
    ):
        user_id = update.effective_chat.id
        msg = str(update.message.text)

        if msg.isnumeric() and int(msg) >= 1 and int(msg) <= 10:
            last_results = self.data_manager.get_user_last_search_results(
                user_id
            )

            if last_results is None:
                await context.bot.send_message(
                    chat_id=user_id,
                    text="You don't have any last search results to pick one",
                    parse_mode=telegram.constants.ParseMode.HTML
                )

                return None
            elif len(last_results) < int(msg):
                await context.bot.send_message(
                    chat_id=user_id,
                    text="You don't have a search result #{}".format(msg),
                    parse_mode=telegram.constants.ParseMode.HTML
                )

                return None
            else:
                await context.bot.send_message(
                    chat_id=user_id,
                    text=json.dumps(
                        last_results[int(msg) - 1],
                        ensure_ascii=False
                    ),
                    parse_mode=telegram.constants.ParseMode.HTML
                )

                return None
        else:
            error, yandex_search_results_xml = self.yandex_wrapper.search(
                msg
            )

            if error is not None:
                print(error)

                await context.bot.send_message(
                    chat_id=user_id,
                    text="Search error: " + error,
                    parse_mode=telegram.constants.ParseMode.HTML
                )

                return None

            error, query, results = self.yandex_wrapper.parse_results(
                yandex_search_results_xml
            )

            if error is not None:
                print(error)

                await context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text="Parse error: " + error,
                    parse_mode=telegram.constants.ParseMode.HTML
                )

                return None

            self.data_manager.set_user_last_search_results(
                user_id=update.effective_user.id,
                search_results=results
            )

            text_response = "<i>{}</i>:\n\n".format(query)
            result_num = 0

            for result in results:
                result_num += 1
                text_response += '<b>{}. {}</b>\n'.format(
                    result_num,
                    result['title']
                )

                if len(result['text']) > 0:
                    text_response += result['text']
                    text_response += "\n"

                text_response += '<a href="{}">{}</a>\n\n'.format(
                    result['url'],
                    result['domain']
                )

            while True:
                try:
                    await context.bot.send_message(
                        chat_id=update.effective_chat.id,
                        text=text_response,
                        parse_mode=telegram.constants.ParseMode.HTML
                    )

                    break
                except telegram.error.TimedOut:
                    print("TG server send message time out, trying again...")

    async def process_start_command(
        self,
        update: telegram.Update,
        context: telegram.ext.ContextTypes.DEFAULT_TYPE
    ):
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Hi, please send me your search query."
        )
