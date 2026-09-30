import asyncio

def send_telegram(bot_token, chat_id, user_name, summary):
    """
    Sends an expense summary message to Telegram using python-telegram-bot.
    """
    if not bot_token:
        return False, "Telegram Bot Token not configured in secrets.toml"
    
    try:
        from telegram import Bot
        bot = Bot(token=bot_token)
        text = f"🧾 *ReceiptSnap Summary for {user_name}*\n\n{summary}"
        
        async def _send():
            async with bot:
                await bot.send_message(chat_id=chat_id, text=text, parse_mode="Markdown")

        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
        if loop.is_running():
            import nest_asyncio
            nest_asyncio.apply()
            loop.run_until_complete(_send())
        else:
            loop.run_until_complete(_send())
            
        return True, "Telegram message sent successfully!"
    except Exception as error:
        return False, str(error)
