# Hanagram
Telegram bot to play Hanabi with your friends.

# Telegram game
How to play a Telegram game:
- Start the server with `python3 main.py <your-bot-token>`
- Add your bot to a chat.
- Send `\new_game` to create a new game.
- Each player now sends `\join <my-name>`
- Send `\start` to start playing!

# Local game
How to play a local game. Let's say players are Alice, Bob and Casey. 
- Run `python3 hanabi.py Alice Bob Casey`
- On each turn, type one of those actions:
    - `play <index of card to play>`
    - `discard <index of card to play>`
    - `hint <player name to hint> <color or value>`
