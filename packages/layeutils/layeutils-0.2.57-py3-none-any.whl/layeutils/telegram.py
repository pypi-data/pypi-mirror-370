
def send_message(bot_token: str, msg: str, chat_id: str = '6097092665'):
    """Simple sending telegram message via pyTelegramBotAPI

    Args:
        bot_token (str): _description_
        chat_id (str): omit this param will send msg to myself
        msg (str): _description_

    Returns:
        _type_: _description_
    """
    import telebot

    bot = telebot.TeleBot(bot_token)
    return bot.send_message(
        chat_id=chat_id, 
        text=msg, 
        # parse_mode='MarkdownV2'
    )
