import hanabi
from PIL import Image, ImageDraw, ImageFont

card_font = ImageFont.truetype('Avenir.ttc', 50)
text_font = ImageFont.truetype('Avenir.ttc', 20)
text_font_small = ImageFont.truetype('Avenir.ttc', 10)
colors_rbg = {'red': (230, 20, 20),
              'green': (50, 150, 50),
              'blue': (50, 100, 250),
              'yellow': (250, 200, 0),
              'black': (230, 230, 230),
              'grey': (100, 100, 100)}


def render_card(image, x, y, color, value):
    width = 50
    image.rectangle((x, y, x + width, y + width * 1.3), fill=colors_rbg[color])
    text_fill = (0, 0, 0)
    # if color == 'black': text_fill = (255, 255, 255)
    image.text((x + width/4, y), value, font=card_font, fill=text_fill)

def render_card_friend(image, x, y, color, value):
    width = 50
    height = 30
    image.rectangle((x, y, x + width, y + height), fill=colors_rbg[color])
    text_fill = (0, 0, 0)
    # if color == 'black': text_fill = (255, 255, 255)
    image.text((x + width/2.5, y + height/8), value, font=text_font, fill=text_fill)

def draw_board_state(game, player_viewing, filename):
    width = 400
    height = (width * 16) // 9
    image = Image.new('RGB', (width, height), (20, 20, 20))
    draw = ImageDraw.Draw(image)
    text_fill = (200, 200, 200)
    # piles
    x = 20
    draw.text((x, 10), 'Hints: ' + str(game.hints) , font=text_font, fill=text_fill)
    draw.text((x + 100-10, 10), 'Errors: ' + str(game.errors) , font=text_font, fill=text_fill)
    draw.text((x + 200-10, 10), 'Deck: ' + str(len(game.deck)) , font=text_font, fill=text_fill)
    draw.text((x + 300-10, 10), 'Score: ' + str(hanabi.get_score(game)), font=text_font, fill=text_fill)

    left_margin = 35
    x = left_margin
    y = 50
    for color in hanabi.colors:
      value = game.piles[color]
      if value == 0:
        value = ''
      else:
        value = str(value)
      render_card(draw, x, 50, color, value)
      xx = x
      for discarded in sorted(game.discarded[color]):
        draw.text((xx, y + 70), str(discarded), font=text_font, fill=(255,255,255))
        xx += 15
      x += 70

    # hands
    for player in game.players:
      x = left_margin
      y += 110
      draw.text((x, y), player, font=text_font, fill=text_fill)
      
      if player == game.players[game.active_player]:
        draw.ellipse((x-20, y+8, x-10, y+18), fill=(255, 255, 255))
      
      y += 30
      for card in game.hands[player]:
        color = card.color
        value = str(card.value)
        if player == player_viewing:
          if not card.is_color_known: color = 'grey'
          if not card.is_value_known: value = ''

        render_card(draw, x, y, color, value)

        if player_viewing == player:
          yy = y + 5
          xx = x + 5

          if not card.is_color_known:
            for not_color in card.not_colors:
              draw.rectangle((xx, yy, xx + 10, yy + 5), fill=colors_rbg[not_color])
              xx += 15
      
          xx = x + 5
          yy = y + 50
          if not card.is_value_known:
            for not_value in card.not_values:
              draw.text((xx, yy), str(not_value), font=text_font_small, fill=(0,0,0))
              xx += 10

        yy = y + 70
        xx = x + 5
        if player_viewing != player:
          if not card.is_color_known: color = 'grey'
          if not card.is_value_known: value = ''
          render_card_friend(draw, x, yy, color, str(value))

          if not card.is_color_known:
            for not_color in card.not_colors:
              draw.rectangle((xx, yy + 2, xx + 10, yy + 6), fill=colors_rbg[not_color])
              xx += 15
            
          
          xx = x + 5
          yy += 15
          if not card.is_value_known:
            for not_value in card.not_values:
              draw.text((xx, yy), str(not_value), font=text_font_small, fill=(0,0,0))
              xx += 10

        x += 70

      if player_viewing == player: y -= 30

    
    image.save(filename)

if __name__ == '__main__':
    game = hanabi.Game(['Giacomo', 'Gabriele'])
    hanabi.give_hint(game, 'Gabriele', 'red')
    hanabi.give_hint(game, 'Gabriele', 'blue')
    hanabi.give_hint(game, 'Gabriele', 1)
    hanabi.give_hint(game, 'Gabriele', 2)
    game.discarded['red'] = [5, 2, 1, 1]
    # game.hands['Giacomo'][0].is_value_known = True
    # game.hands['Giacomo'][0].not_values = [1, 2, 3]
    # game.hands['Giacomo'][0].not_colors = ['red', 'blue', 'green']
    draw_board_state(game, 'Giacomo', 'image.png')
