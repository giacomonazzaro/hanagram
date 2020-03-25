import hanabi
from PIL import Image, ImageDraw, ImageFont

size = 1/3
card_font = ImageFont.truetype('Avenir.ttc', int(50/size))
text_font = ImageFont.truetype('Avenir.ttc', int(20/size))
text_font_small = ImageFont.truetype('Avenir.ttc', int(10/size))

colors_rbg = {'red': (230, 20, 20),
              'green': (50, 150, 50),
              'blue': (50, 100, 250),
              'yellow': (250, 200, 0),
              'white': (230, 230, 230),
              'grey': (100, 100, 100)}


def render_card(image, x, y, color, value):
    width = 50/size
    image.rectangle((x, y, x + width, y + width * 1.3), fill=colors_rbg[color])
    text_fill = (0, 0, 0)
    # if color == 'black': text_fill = (255, 255, 255)
    image.text((x + width/4, y), value, font=card_font, fill=text_fill)

def render_card_friend(image, x, y, color, value):
    width = 50/size
    height = 30/size
    image.rectangle((x, y, x + width, y + height), fill=colors_rbg[color])
    text_fill = (0, 0, 0)
    # if color == 'black': text_fill = (255, 255, 255)
    image.text((x + width/2.5, y + height/8), value, font=text_font, fill=text_fill)

def draw_board_state(game, player_viewing, filename):
    width = int(400 / size)
    height = (width * 16) // 9
    background = (20, 20, 20)
    image = Image.new('RGB', (width, height), background)
    draw = ImageDraw.Draw(image)
    text_fill = (200, 200, 200)
    # piles
    x = 20 / size
    draw.text((x, 25/size), 'Hints: ' + str(game.hints) , font=text_font, fill=text_fill)
    draw.text((x + (100-10)/size, 25/size), 'Errors: ' + str(game.errors) , font=text_font, fill=text_fill)
    draw.text((x + (200-10)/size, 25/size), 'Deck: ' + str(len(game.deck)) , font=text_font, fill=text_fill)
    draw.text((x + (300-10)/size, 25/size), 'Score: ' + str(hanabi.get_score(game)), font=text_font, fill=text_fill)

    left_margin = 35/size
    x = left_margin
    y = 65/size
    for color in hanabi.colors:
      value = game.piles[color]
      if value == 0:
        value = ''
      else:
        value = str(value)
      render_card(draw, x, y, color, value)
      xx = x
      for discarded in sorted(game.discarded[color]):
        draw.text((xx, y + 70/size), str(discarded), font=text_font, fill=(255,255,255))
        xx += 15/size
      x += 70/size

    # hands
    for player in game.players:
      x = left_margin
      y += 110 / size
      draw.text((x, y), player, font=text_font, fill=text_fill)
      
      if player == game.players[game.active_player]:
        draw.ellipse((x-20/size, y+8/size, x-10/size, y+18/size), fill=(255, 255, 255))
      
      y += 30/size
      for card in game.hands[player]:
        color = card.color
        value = str(card.value)
        if player == player_viewing:
          if not card.is_color_known: color = 'grey'
          if not card.is_value_known: value = ''

        render_card(draw, x, y, color, value)

        if player_viewing == player:
          yy = y + 0/size
          xx = x + 5/size

          if not card.is_color_known:
            for not_color in card.not_colors:
              # draw.ellipse((xx, yy, xx + 10/size, yy + 5/size), fill=colors_rbg[not_color])
              start = (xx, yy + 2/size)
              radius =  10/size
              draw.ellipse((start[0], start[1], start[0]+radius, start[1]+radius), fill=background)
              start = (start[0]+2/size, start[1]+2/size)
              radius =  6/size
              draw.ellipse((start[0], start[1], start[0]+radius, start[1]+radius), fill=colors_rbg[not_color])
              xx += 15/size
      
          xx = x + 5/size
          yy = y + 50/size
          if not card.is_value_known:
            for not_value in card.not_values:
              start = (xx-1/size, yy)
              radius =  12/size
              draw.ellipse((start[0], start[1], start[0]+radius, start[1]+radius), fill=background)
              draw.text((xx+5, yy), str(not_value), font=text_font_small, fill=text_fill)
              xx += 15/size

        yy = y + 70/size
        xx = x + 5/size
        if player_viewing != player:
          if not card.is_color_known: color = 'grey'
          if not card.is_value_known: value = ''
          render_card_friend(draw, x, yy, color, str(value))

          if not card.is_color_known:
            for not_color in card.not_colors:
              start = (xx, yy + 2/size)
              radius =  7/size
              draw.ellipse((start[0], start[1], start[0]+radius, start[1]+radius), fill=background)
              start = (start[0]+1/size, start[1]+1/size)
              radius =  5/size
              draw.ellipse((start[0], start[1], start[0]+radius, start[1]+radius), fill=colors_rbg[not_color])
              xx += 25
            
          
          xx = x + 5/size
          yy += 15/size
          if not card.is_value_known:
            for not_value in card.not_values:
              start = (xx-3.5/size, yy)
              radius =  12/size
              draw.ellipse((start[0], start[1], start[0]+radius, start[1]+radius), fill=background)
              draw.text((xx, yy), str(not_value), font=text_font_small, fill=text_fill)
              xx += 15/size

        x += 70/size

      if player_viewing == player: y -= 30/size

    
    image.save(filename)

if __name__ == '__main__':
    game = hanabi.Game(['Giacomo', 'Gabriele'])
    hanabi.give_hint(game, 'Giacomo', 'red')
    hanabi.give_hint(game, 'Giacomo', 'blue')
    hanabi.give_hint(game, 'Giacomo', 'white')
    hanabi.give_hint(game, 'Giacomo', 1)
    hanabi.give_hint(game, 'Giacomo', 2)
    hanabi.give_hint(game, 'Giacomo', 3)
    game.discarded['red'] = [5, 2, 1, 1]
    # game.hands['Giacomo'][0].is_value_known = True
    # game.hands['Giacomo'][0].not_values = [1, 2, 3]
    # game.hands['Giacomo'][0].not_colors = ['red', 'blue', 'green']
    draw_board_state(game, 'Giacomo', 'image.png')
