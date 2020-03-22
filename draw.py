import hanabi
from PIL import Image, ImageDraw, ImageFont

font = ImageFont.truetype('Avenir.ttc', 50)
colors_rbg = {'red': (255, 0, 0),
              'green': (100, 200, 100),
              'blue': (0, 0, 255),
              'yellow': (200, 200, 0),
              'black': (10, 10, 10)}

def draw_card(image, x, y, color, value):
    width = 50
    image.rectangle((x, y, x + width, y + width * 1.3), fill=colors_rbg[color])
    text_fill = (0, 0, 0)
    if color == 'black': text_fill = (255, 255, 255)
    image.text((x + width/4, y), value, font=font, fill=text_fill)



def draw_board_state(filename):
    image = Image.new('RGB', (400, (400 * 16) // 9), (255, 255, 255))
    draw = ImageDraw.Draw(image)
    draw_card(draw, 20+ 0, 50, 'red', '1')
    draw_card(draw, 20+ 70, 50, 'green', '2')
    draw_card(draw, 20+ 140, 50, 'blue', '3')
    draw_card(draw, 20+ 210, 50, 'yellow', '4')
    draw_card(draw, 20+ 280, 50, 'black', '5')

    image.save(filename)

if __name__ == '__main__':
    draw_board_state('image.png')
