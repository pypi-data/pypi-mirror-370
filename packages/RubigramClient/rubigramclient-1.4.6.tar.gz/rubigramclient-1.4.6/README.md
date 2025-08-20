# Rubigram
A lightweight Python library to build Rubika bots easily.

## Installation
```bash
pip install RubigramClient
```

## Send Message
```python
from rubigram import Client, filters
from rubigram.types import Update

bot = Client("your_bot_token", "you_endpoint_url")

@bot.on_message(filters.command("start"))
async def start_handler(client, message: Update):    
    await message.reply("Hi, WELCOME TO RUBIGRAM")

bot.run()
```

## Send Message & Get receiveInlineMessage
```python
from rubigram import Client, filters
from rubigram.types import Update, Button, Keypad, KeypadRow, InlineMessage


bot = Client(token="bot_token", endpoint="endpoint_url")


@bot.on_message(filters.command("start"))
async def start(_, message: Update):
    inline = Keypad(
        rows=[
            KeypadRow(
                buttons=[
                    Button("1", "Simple", "Button 1"),
                    Button("2", "Simple", "Button 2")
                ]
            )
        ]
    )
    await bot.send_message(message.chat_id, "Hi", inline_keypad=inline)
    

@bot.on_inline_message(filters.button(["1", "2"]))
async def button(_, message: InlineMessage):
    if message.aux_data.button_id == "1":
        await bot.send_message(message.chat_id, "You Click Button 1")
    elif message.aux_data.button_id == "2":
        await bot.send_message(message.chat_id, "You Click Button 2")
        
bot.run()
```