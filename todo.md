# Todo

## Game

## Rendering


## Chatbot
- Handle game end:
    - Send game view to group chat, with player_viewing='' so that we see all the cards
    - Set game status to 'ended'
    - Refuse all inputs in games with status == 'ended'
- /join: check empty string and ask to repeat
- /join: check name collision and ask to repeat

- Send image without writing to disk.
- Dump memory to disk in order to resurrect games after crashes or disconnections
