import pygame as pg
import random, math, time

#Base variables
background_sprite = None
cards = []
tables = []
dealer = []
players = []
store_graphics = []
clock = pg.time.Clock()
game_running = True
patterns = [
    'cipő', 'láb', 'vonat', 'hold', 'cica', 'torta',
    'óra', 'nap', 'mosoly', 'alma', 'hal', 'csillag',
    'csésze', 'kutya', 'kacsa', 'nyuszi', 'kukac', 'madár',
    'ház', 'szív', 'labda', 'szellem', 'fa', 'bagoly'
    ]

left_buttons = [pg.K_0, pg.K_x, pg.K_6, pg.K_o, pg.K_LEFT] 
right_buttons = [pg.K_1, pg.K_c, pg.K_7, pg.K_p, pg.K_RIGHT]

player_button_pairs = ['0 1', 'x c', '6 7', 'o p', '< >']


#Graphics figures
pg.init()

pg.display.set_caption("Zingo")
icon = pg.image.load("PNG\\logo.png")
pg.display.set_icon(icon)
font = pg.font.Font(None, 36)
top_text = 'Új kártyák: SPACE, Új zöld játék: PG up, Új piros játék: PG Down, Kilépés: ESC'#teszt
top_text_value = font.render(f'{top_text}', True, (0, 0, 0))

screen_x = 1200
screen_y = 750
screen = pg.display.set_mode((screen_x, screen_y)) #, pg.RESIZABLE
# Center of screen
s_cx = screen.get_width() // 2
s_cy = screen.get_height() // 2

screen.fill('white')

#Sounds
pg.mixer.init()
sound_fault = pg.mixer.Sound('WAV\\sound_fault.wav')
sound_call_card = pg.mixer.Sound('WAV\\sound_call_card.wav')
sound_insert = pg.mixer.Sound('WAV\\sound_insert.wav')
sound_card_movement = pg.mixer.Sound('WAV\\sound_card_movement.wav')
sound_win = pg.mixer.Sound('WAV\\sound_win.wav')


class Card:
    '''small card'''
    def __init__(self, pattern, image=None, pos=None, visible=True):
        self.pattern = pattern  # word on the card
        self.image = image  # image of the card
        if pos is None:
            pos = pg.Rect(0, 0, 0, 0)  # default value
        self.pos = pos  # center of the card
        self.visible = visible  # visibility

    def __str__(self):
        return str(self.pattern)

    def __eq__(self, pattern):
        return self.pattern == pattern

    def displays(self, visible_from_bottom = 100, close = None, center_position_test = False):
        if self.visible:
            img = self.image
            x = self.pos.x 
            y = self.pos.y
            h = self.image.get_height()
            w = self.image.get_width()
            rx = x - w // 2
            ry = y - h // 2
            if close == None:
                #in case of normal card drawing (moving or on a table)
                screen.blit(img, (rx, ry))
            else:
                partial_height = int(h * visible_from_bottom / 100)
                if close == True:
                    #in case of dealer machine opening (machine top moves back)
                    bottom = ry + h - partial_height
                else:
                    #in case of dealer machine closing (back to the machine)
                    bottom = ry - h + partial_height
                screen.blit(img, (rx, bottom),
                            (0, h - partial_height,
                             w, partial_height))
            if center_position_test:
                pg.draw.circle(screen, 'black', (x, y), 5)


class Column:
    '''columns, where cards stay in FIFO'''
    def __init__(self, cards=None):
        if cards is None:
            cards = []
        self.cards = cards

    def insert(self, card):
        self.cards.append(card)

    def get(self):
        if self.cards:
            return self.cards.pop(0)
        else:
            return None


class Table:
    '''player boards/tables'''
    coor_pattern = ((s_cx // 2, s_cy + s_cy // 2),
                    (s_cx + s_cx // 2, s_cy + s_cy // 2),
                    (s_cx, s_cy + s_cy // 2),
                    (s_cx // 2, s_cy // 2),
                    (s_cx + s_cx // 2, s_cy // 2),
                    (s_cx, s_cy // 2))
    ox = 81 #horizontal distance from the center of the table
    oy = -20 #vertical distance from the center of the table


    def __init__(self, image = None, color='', pos = None,
                patterns = [], occupancy = None, visible = True, pattern_coor = []):
        self.pos = pos #position of the table on the screen
        ox = 55 #x offset
        oy = -15 #y offset
        oh = 63 #height offset
        table_card_coor_pattern = ((-ox, oy - oh),
                                     (0, oy - oh),
                                     (ox, oy - oh),
                                     (-ox, oy),
                                     (0, oy),
                                     (ox, oy),
                                     (-ox, oy + oh),
                                     (0, oy + oh),
                                     (ox, oy + oh))
        self.image = image  #sprite
        self.color = color    #red or green
        if pos is None:
            pos = pg.Rect(400, 200, 400, 200)  # default variables

        self.patterns = patterns
        if occupancy is None:
            occupancy = [False] * 9
        self.occupancy = occupancy #occupy (9 positions / board)
        self.visible = visible #visibility

        self.pattern_coor = table_card_coor_pattern #position coordinates (9)

    def __str__(self):
        #for test
        return (f'{str(self.color)}, {str(self.patterns)}, {str(self.pos)}')
    

    def displays(self, center_position_test = False):
        #display on the screen
        img = self.image
        x = self.pos.x
        y = self.pos.y
        img_size = img.get_size()
        rect = img.get_rect(center=(x, y))
        if self.visible:
            screen.blit(img, rect)
            if center_position_test:
                # for test to see the right center position
                for coors in self.pattern_coor:
                    kx = coors[0] + x
                    ky = coors[1] + y
                    pg.draw.circle(screen, 'black', (kx, ky), 5)


class Store:
    '''stores with two columns'''
    def __init__(self, graphics, x, y, visible):
        self.graphics = graphics
        self.x = x
        self.y = y
        self.visible = visible
        self.dealer_open = False
        self.dealer_close = False
        self.dealer_back = False
        self.card0 = None
        self.card1 = None
        self.dealer_index = 0
        self.back_index = 0

    def displays(self, index):
        img = self.graphics[index]
        x = self.x
        y = self.y
        rect = img.get_rect()
        rect.bottom = y
        rect.centerx = x
        if self.visible:
            screen.blit(img, rect)


class Dealedcard:
    '''dealed card'''
    global top_text_value, top_text #test
    def __init__(self, card = None, original_pos = None,
                 new_pos = None):
        if card == None:
            self.card = None
            self.actual_pos = pg.Rect(0, 0, 0, 0)
        else:
            self.card = card
            self.actual_pos = self.card.pos
        if original_pos == None:
            self.original_pos = pg.Rect(0, 0, 0, 0)
        else:
            self.original_pos = original_pos
        if new_pos == None:
            self.new_pos = pg.Rect(0, 0, 0, 0)
        else:
            self.new_pos = new_pos
        self.moving = False
        self.steps = 0
        self.actual_step = 0

    def equal(self, table, player):
        '''equality checking'''
        #if the image of the choosen card is in the table
        #and the table image is empty returns back with its index
        #loads into tha table
        for index in range(9):
            if (self.card.pattern == table.patterns[index] and
                table.occupancy[index] == False):
                table.occupancy[index] = True
                player.score += 1
                if player.score == 9:
                    #Sound: WIN!
                    sound_win.play()
                    #print('Nyert!')

                return index
        return None

    def start_movement(self, target_table, target_table_index):
        '''starts moving of the card'''
        self.original_pos = self.card.pos.copy()
        self.new_pos.x = target_table.pos.x + target_table.pattern_coor[target_table_index][0]
        self.new_pos.y = target_table.pos.y + target_table.pattern_coor[target_table_index][1]
        self.moving = True
        self.steps = 25 #number of steps from the dealer to the table
        self.actual_step = 0
        #Sound: card moves!
        sound_card_movement.play()
        #print('Kártyamozgatás')

    def move(self):
        '''moves card'''
        if self.moving:
            x_offset = (self.new_pos.x - self.original_pos.x) / self.steps
            y_offset = (self.new_pos.y - self.original_pos.y) / self.steps
            self.card.pos.x = int(self.original_pos.x +
                                    self.actual_step * x_offset)
            self.card.pos.y = int(self.original_pos.y +
                                    self.actual_step * y_offset)
            self.actual_step += 1
            if self.actual_step > self.steps:
                self.moving = False
                return True #just arrived
            return False #still moving
        return None #doesnt move

            
class Player:
    '''Player'''
    def __init__(self, name = '', img = None, score = 0, table = None, visible = False):
        self.name = name
        self.img = img
        self.score = score
        self.table = table
        self.visible = visible

    def __str__(self):
        return (f'{self.name}, {self.score} pont, {self.table}')

    def displays(self):
        if self.visible:

            #draws player icon
            img = self.img
            w = img.get_width()
            h = img.get_height()
            pos = pg.Rect(self.table.pos.x + 30, self.table.pos.y + 50, w, h)
            screen.blit(img, pos)

            #writes player score
            circles_number = 9
            radius = 10
            circles_distance = radius
            for i in range(9):
                x = self.table.pos.x - 132 + (2 * radius + circles_distance) * i + radius
                y = self.table.pos.y - 140
                if self.score > i:
                    pg.draw.circle(screen, 'green', (x, y), radius)
                else:
                    pg.draw.circle(screen, 'red', (x, y), radius, width=1)

            #in case of win, writes WIN
            if self.score == 9:
                font = pg.font.Font(None, 100)
                text = font.render("NYERT!", True, 'green')
                text_rect = pg.Rect(self.table.pos.x - 125, self.table.pos.y - 50, 50, 50)
                screen.blit(text, text_rect)

            #draws control buttons
            font = pg.font.Font(None, 50)
            buttons = player_button_pairs[tables.index(self.table) - start_index]
            buttontext = font.render(buttons, True, 'red')
            buttontext_rect = pg.Rect(self.table.pos.x - 30, self.table.pos.y + 140, 50, 50)
            screen.blit(buttontext, buttontext_rect)
            button_rect = pg.Rect(buttontext_rect.x-10, buttontext_rect.y,
                                buttontext_rect.width + 20,
                                buttontext_rect.height - 10)
            pg.draw.rect(screen, 'black', button_rect, width=1)



def spritesheet(file, row, column):
    '''file, rows, columns: returns with a sprite list'''
    sprites = []
    spritesheet = pg.image.load(file).convert_alpha()
    x_size = int(spritesheet.get_width() / column)  #width in pixels
    y_size = int(spritesheet.get_height() / row)    #height in pixels
    for y in range(row):
        for x in range(column):
            rect = pg.Rect((x * x_size, y * y_size),(x_size, y_size))
            sprites.append(spritesheet.subsurface(rect))
    return sprites


def hatter():
    screen.blit(background_sprite[0], (0,0))


def tables_spritesheet(file, name):
    piros_table_patterns = [['kutya', 'madár', 'mosoly',
                          'óra', 'cica', 'torta',
                          'ház', 'labda', 'vonat'],
                         ['mosoly', 'nyuszi', 'csillag',
                          'torta', 'szellem', 'óra',
                          'cica', 'nap', 'madár'],
                         ['csillag', 'hal', 'labda',
                          'hold', 'cipő', 'szív',
                          'kutya', 'kacsa', 'nap'],
                         ['cica', 'csillag', 'vonat',
                          'szív', 'kutya', 'csésze',
                          'kukac', 'cipő', 'mosoly'],
                         ['kutya', 'vonat', 'nap',
                          'szellem', 'nyuszi', 'óra',
                          'alma', 'labda', 'hold'],
                         ['szív', 'cica', 'madár',
                          'hal', 'csillag', 'nap',
                          'hold', 'láb', 'labda']]

    zold_table_patterns = [['cipő', 'óra', 'kutya',
                         'kacsa', 'szellem', 'láb',
                         'ház', 'cica', 'nyuszi'],
                        ['alma', 'cica', 'szív',
                         'madár', 'nap', 'láb',
                         'hal', 'labda', 'kukac'],
                        ['alma', 'óra', 'mosoly',
                         'ház', 'láb', 'cipő',
                         'csésze', 'csillag', 'vonat'],
                        ['mosoly', 'torta', 'csillag',
                         'szív', 'cipő', 'labda',
                         'vonat', 'fa', 'szellem'],
                        ['nap', 'madár', 'hal',
                         'labda', 'nyuszi', 'ház',
                         'szellem', 'cica', 'hold'],
                        ['kutya', 'madár', 'csillag',
                         'szív', 'bagoly', 'alma',
                         'nyuszi', 'torta', 'mosoly']]


    if name == 'piros':
        table_patterns = piros_table_patterns
    else:
        table_patterns = zold_table_patterns

    sprites = spritesheet(file, 2, 3)

    #generates tables
    for index in range(6):
        tables.append(Table(sprites[index], name,
                            pg.Rect(Table.coor_pattern[index][0],
                                    Table.coor_pattern[index][1], 0, 0),
                            table_patterns[index]))


def graphics_displays():
    #Draws graphics in the loop
    global top_text_value, top_text
    screen.fill((255, 255, 255))  # clears screen

    #Background
    hatter()

    #Tables
    for table in tables:
        table.displays(False)

    #Dealer machine
    dealer.displays(dealer.dealer_index)

    #Cards
    for card in cards:
        normal_card = True
        for i in range(2):
            if (dealed_cards[i] is not None and
                dealed_cards[i].card is not None):
                #is card on the dealer machine?
                if card.pos == dealed_cards[i].card.pos:
                    if dealer.dealer_back:
                        #card back to the dealer machine
                        card.displays(dealer.back_index * 10, False, False)
                        normal_card = False
                    else:
                        #new card when the dealer machine moves back
                        card.displays((10 - dealer.dealer_index) * 10, True, False)
                        normal_card = False
        if normal_card:
            #normal card
            card.displays(100, None, False)

    #Text on the top
    top_text_value = font.render(f'{top_text}', True, (0, 0, 0))
    screen.blit(top_text_value, (20,0))

    #Players
    for player in players:
        player.displays()
    

    #Screen flip
    pg.display.flip()
    clock.tick(40)


def dealer_handling(store):
    #Dealer machine handling
    if store.dealer_back:
        #Dealer machine moves back
        
        if store.back_index > 0:
            store.back_index -= 1
        else:
            #if has card takes it back
            store.back_index = 0
            for i in range(2):
                if dealed_cards[i].card != None:
                    dealed_cards[i].card.visible = False
                    columns[i].insert(dealed_cards[i])
                    dealed_cards[i] = None
                    #Sound: Card back to the machine
                    sound_insert.play()
                    #print('Kártya visszarakás')
            store.dealer_back = False
            store.dealer_open = True
            #Sound: New cards
            sound_call_card.play()
            #print('Kártyakérés')

    #in case of open are we finished it?
    if store.dealer_open:
        store.dealer_index += 1
        if store.dealer_index == 9:
            store.dealer_open = False
            store.dealer_close = True

    #get cards from the machine
    if store.dealer_close:
        if store.dealer_index == 9:
            for i in range(2):
                dealed_cards[i] = Dealedcard(columns[i].get())
                dealed_cards[i].card.visible = True

        store.dealer_index -= 1
        if store.dealer_index == 0:
            store.dealer_close = False


def init():
    global dealer, store_graphics, players, player_icons, background_sprite
    #Cards
    sprite = spritesheet('PNG\\Cards.png', 4, 6)
    for peldany in range(3):
        for pattern in patterns:
            cards.append(Card(pattern, sprite[patterns.index(pattern)]))

    #Dealer machine
    for i in range (10):
        file = f'PNG\\store\\{int(i + 1)}.png'
        store_graphics.append(spritesheet(file, 1, 1)[-1])
    dealer = Store(store_graphics, s_cx, s_cy, True)

    #Players
    sprite = spritesheet('PNG\\PlayerIcons.png', 1, 5)
    player_icons = []
    for i in range(5):
        player_icons.append(sprite[i])

    #Tables
    tables_spritesheet('PNG\\Red_tables.png','piros')
    tables_spritesheet('PNG\\Green_tables.png', 'zöld')

    #Background
    background_sprite = spritesheet('PNG\\Background.png', 1, 1)
    

def new_game():
    #New game
    global cards, tables, columns, players
    global start_index, dealed_cards
    global no_storemovement, no_cardmovement


    #tables shuffle
    #   need to save some variables before mixing
    table_pos = [table.pos for table in tables]
    table_occupancy = [[False] * 9 for _ in range(12)]
    table_visible = [table.visible for table in tables]
    table_pattern_coor = [table.pattern_coor for table in tables]

    #   we have 12 tables with two colors, need to mix them separately
    half = len(tables) // 2
    one_half = tables[:half]
    other_half = tables[half:]
    random.shuffle(one_half)
    random.shuffle(other_half)

    #   copy back the saved variables
    tables = []
    for i in range(6):
        tables.append(one_half[i])
    for i in range(6):
        tables.append(other_half[i])
    for i, table in enumerate(tables):
        table.pos = table_pos[i]
        table.occupancy = table_occupancy[i]
        table.visible = table_visible[i]
        table.pattern_coor = table_pattern_coor[i]

    #default values for tables
    for table in tables:
        table.visible = False
    if game_type == 'piros':
        start_index = 0
    else:
        start_index = 6
    end_index = start_index + players_number + machine_players_number - 1

    for table in tables:
        table_index = tables.index(table)
        if table_index >= start_index and table_index <= end_index:
            table.visible = True

    #Dealer columns
    columns = [Column() for _ in range(2)]
    
    #Cards
    random.shuffle(cards)
    index = 0
    for card in cards:
        card.pos = pg.Rect(s_cx - 30 + index * 60, s_cy - 60, 0, 0)
        card.visible = False
        columns[index].insert(card)
        index = (index + 1) % 2

    #Players
    players = []
    for i in range(2):
        for j in range(6):
            if j == 5:
                players.append(Player(str(i)+str(j)))            
            else:
                players.append(Player(str(i)+str(j), player_icons[j], 0, tables[i * 6 + j]))
    for index in range(start_index, start_index + players_number):
        players[index].visible = True

    #Default values
    no_storemovement = True
    no_cardmovement = True

    dealed_cards = []
    for i in range(2):
        dealed_cards.append(Dealedcard())
    

def button_event(player_index, dealed_card_index):
    '''button event handling: player index, dealed card index'''
    global dealed_cards, no_cardmovement
    if dealed_cards[dealed_card_index].card is not None:
        table_card_index = dealed_cards[dealed_card_index].equal(tables[player_index],
                                                               players[player_index])
        if table_card_index != None:
            dealed_cards[dealed_card_index].start_movement(tables[player_index],
                                               table_card_index)
            no_cardmovement = False
        else:
            #print('Nincs ilyen kártya, rossz gombot nyomtál, vagy már van abból!')
            #Sound: FAULT
            sound_fault.play()
            


#default game paramaters
game_type = 'zöld' #game type
players_number = 5 #0..5 number of players

machine_players_number = 0 #in the future...

#START
init()

new_game()


#Game loop
while game_running:
    #Event handling
    for event in pg.event.get():
        if event.type == pg.QUIT:
            game_running = False
        if event.type == pg.KEYDOWN:
            
            if event.key == pg.K_ESCAPE:
                game_running = False
            if no_cardmovement and no_storemovement:
                
                #New game
                if event.key == pg.K_PAGEUP:
                    game_type = 'zöld'
                    players_number = 5 #0..5
                    machine_players_number = 0
                    new_game()
                if event.key == pg.K_PAGEDOWN:
                    game_type = 'piros'
                    players_number = 5 #0..5
                    machine_players_number = 0
                    new_game()

                #Dealing
                if event.key == pg.K_SPACE:
                    
                    dealer.dealer_back = True
                    dealer.back_index = 9
                    no_storemovement = False

                #Players control
                #   left
                for index, left_button in enumerate(left_buttons):
                    if event.key == left_button:
                        player_index = start_index + index
                        button_event(player_index, 0)
                #   right
                for index, right_button in enumerate(right_buttons):
                    if event.key == right_button:
                        player_index = start_index + index
                        button_event(player_index, 1)

    #event checking only after moving events
    if (dealer.dealer_back or dealer.dealer_open or
        dealer.dealer_close):
        no_storemovement = False
    else:
        no_storemovement = True

    #cards moving in case of call
    for i in range(2):
        if dealed_cards[i] is not None:
            if dealed_cards[i].moving:
                if dealed_cards[i].move():
                    dealed_cards[i] = Dealedcard()
                    no_cardmovement = True

    #Dealer machine
    dealer_handling(dealer)

    #Graphics
    graphics_displays()

#End of program
pg.quit()
