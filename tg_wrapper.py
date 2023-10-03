import telegram


class TgWrapper:
    def __init__(self, token: str, yandex_wrapper):
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
        error, yandex_search_results_xml = self.yandex_wrapper.search(
            update.message.text
        )

        if error is not None:
            print(error)

            await context.bot.send_message(
                chat_id=update.effective_chat.id,
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

        while True:
            try:
                await context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text=text_response,
                    parse_mode=telegram.constants.ParseMode.HTML
                )

                break
            except telegram.error.TimedOut:
                print("Telegram server send message time out, trying again...")

    async def process_start_command(
        self,
        update: telegram.Update,
        context: telegram.ext.ContextTypes.DEFAULT_TYPE
    ):
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Hi, please send me your search query."
        )
