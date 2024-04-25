import pygame as pg
import random, math, time, sys

#Global variables
game_running = None
screen_width = 800
screen_height = 749
counter = 0
random_board = []
board_lines = []
sample = []
sprite_background = None
game_level = 1
char_width = 33
char_height = 33
board_x_offset = 247 + char_width // 2
board_y_offset = 295 + char_height // 2
board_matrix_size = 9
#board_cell_size = char_width
#hidden_x_y = []
selected_value = None

#Graphics figures
pg.init()
clock = pg.time.Clock()
font_obj = pg.font.Font('Graph\\segoepr.ttf', 36)
pg.display.set_caption("Sodoku")
##icon = pg.image.load("PNG\\logo.png")
##pg.display.set_icon(icon)
screen = pg.display.set_mode((screen_width, screen_height))
#Center of screen
screen_center_x = screen.get_width() // 2
screen_center_y = screen.get_height() // 2


#CLASSES
class Char:


    def __init__(self, x_pos, y_pos, value = '', color = 'black', visible = True):
        self.x_pos = x_pos
        self.y_pos = y_pos
        self.x_coor = board_x_offset + self.x_pos * char_width
        self.y_coor = board_y_offset + self.y_pos * char_height
        self.value = value
        self.color = color
        self.visible = visible

    def displays(self):
        if self.visible:
            text_surface = font_obj.render(str(self.value), True, self.color)
            text_rect = text_surface.get_rect()
            text_rect.center = (self.x_coor, self.y_coor)
            screen.blit(text_surface, text_rect)


def spritesheet_loader(file, row, column):
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


def displays_background():
    screen.blit(sprite_background[0], (0,0))


def displays_chars():
    #board
    for board_line in board_lines:
        for board_char in board_line:
            board_char.displays()
    #samples
    for y in range(3):
        for x in range(3):
            sample[y][x].displays()
    #level
    for i in range(8):
        level_control[i].displays()  


def displays_graphics():
    #graphics elements in a loop

    #background
    displays_background()

    #chars
    displays_chars()

    #delay and screen flip
    pg.display.flip()
    clock.tick(40)
    

def board_generator():
    rows = []
    for index in range(9):
        no_possible = True
        fault_counter = 0
        while no_possible:
            #after 100 times goes back and starts a new board
            #(impossible board setup)
            if fault_counter == 100:
                return False

            no_possible = False
            elements = list(range(1, 10))
            if rows == []:
                #first row
                new_list = elements.copy()
                random.shuffle(new_list)
            else:
                #other rows
                new_list = []
                possible_elements = elements.copy()
                for element_index in range(9):
                    #removes last element from the list
                    if new_list != []:
                        if new_list[-1] in possible_elements:
                            possible_elements.remove(new_list[-1])

                    #removes column elements form the list
                    possible_column_elements = possible_elements.copy()
                    for row in rows:
                        if row[element_index] in possible_column_elements:
                            possible_column_elements.remove(row[element_index])
                        
                    #removes 3x3 field elements from the list
                    actual_row = len(rows)
                    actual_field_elements = []
                    field_first_row = actual_row // 3 * 3
                    field_first_column = element_index // 3 * 3
                    field_last_row = field_first_row + 2
                    field_last_column = field_first_column + 2
                    for y in range(field_first_row, field_last_row + 1):
                        for x in range(field_first_column, field_last_column + 1):
                            if y < actual_row:
                                actual_field_elements.append(rows[y][x])
                    #   checking field components in the remain components
                    for actual_field_element in actual_field_elements:
                        if actual_field_element in possible_column_elements:
                            possible_column_elements.remove(actual_field_element)

                    #in case of no more possibility: repeat the row
                    if len(new_list) <9 and possible_column_elements == []:
                        no_possible = True
                        fault_counter += 1
                        break
                    else:
                        #mixing the possible numbers    
                        random_element = random.choice(possible_column_elements)
                        #one number is finished
                        new_list.append(random_element)

        #row is finished    
        rows.append(new_list)
    return rows


def matrix_unselect(x, y, selected_value):
        board_lines[y][x].value = selected_value
        board_lines[y][x].visible = False
        return None


def matrix_select(x, y, selected_value):
    if board_lines[y][x].color != 'black':
        saved_value = board_lines[y][x].value
        board_lines[y][x].value = 'X'
        board_lines[y][x].color = 'orange'
        board_lines[y][x].visible = True
        return (x, y, saved_value)
    elif board_lines[y][x].value == 'X':
        matrix_unselect(x, y, selected_value)
        return None


def write_selected(selected_value, selected_sample):
    board_lines[selected_value[1]][selected_value[0]].value = selected_sample


def is_valid_unit(unit):
    if len(unit) == 9 and len(unit) == len(set(unit)):
        return True
    return False


def check_win():
    #board checking based on the sudoku rules
    #horizontal: 9 rows
    for board_line in board_lines:
        unit = []
        for board_char in board_line:
            if board_char.visible:
                unit.append(board_char.value)
        if not is_valid_unit(unit):
            #fault in a row
            return False
    
    #vertical: 9 columns
    for board_column in zip(*board_lines):
        unit = []
        for board_char in board_column:
            if board_char.visible:
                unit.append(board_char.value)
        if not is_valid_unit(unit):
            #fault in a column
            return False
    
    #3x3 fields: 9 pieces
    for i in range(0, 9, 3):
        for j in range(0, 9, 3):
            unit = []    
            for x in range(i, i + 3):
                for y in range(j, j + 3):
                    if board_lines[x][y].visible:
                        unit.append(board_lines[x][y].value)
            if not is_valid_unit(unit):
                #fault in a 3x3 field
                return False
    #board is complete and good
    return True


def win():
    for board_line in board_lines:
        for board_char in board_line:
            board_char.color = 'green'
            #sound: win
            sound_win.play()

def level_handling(direction = None):
    global game_level
    if direction == 'up':
        if game_level < 8:
            game_level += 1
    elif direction == 'down':
        if game_level > 1:
            game_level -= 1
    for i in range(8):
        if game_level < i + 1:
            level_control[i].color = level_char_color[0]
        else:
            level_control[i].color = level_char_color[1]
    new_game()
    


def init():
    global sprite_background, sample, sound_win, sound_click
    global sound_write, level_control, level_char_color
    sprite_background = spritesheet_loader('Graph\\BG800x749.png', 1, 1)

    #sounds
    pg.mixer.init()
    sound_background = pg.mixer.Sound('Sound\\Sound_background.mp3')
    sound_win = pg.mixer.Sound('Sound\\Sound_win.wav')
    sound_click = pg.mixer.Sound('Sound\\Sound_click.mp3')
    sound_write = pg.mixer.Sound('Sound\\Sound_write.mp3')
    sound_background.play(-1)

    #samples
    sample = []
    for y in range(3):
        sample_chars = []
        for x in range(3):
            sample_chars.append(Char(x + 3, y - 4, y *3 + x + 1, 'orange', True))
        sample.append(sample_chars)

    #level control
    level_control = []
    level_char_color = ('lightslategray', 'lawngreen')
    for i in range(1, 9, 1):
        level_control.append(Char(15, 13 - i, '▄', level_char_color[0], True))


def new_game():
    global game_running, random_board, board_lines, hidden_x_y, selected_value
    game_running = True
    selected_value = None

    #generates board
    board_ok = True
    while board_ok:
        random_board = board_generator()
        if random_board != False:
            board_ok = False

    #sets numbers of board based on the level
    #generates hidden positions
    hidden_chars = game_level * 9
    hidden_x_y = []
    for i in range(hidden_chars):
        while True:
            x_y = (random.randint(0, 8), random.randint(0, 8))
            if x_y not in hidden_x_y:
                break
        hidden_x_y.append(x_y)
    #setting hidden positions on the board
    board_lines = []
    for y, random_board_line in enumerate(random_board):
        board_chars = []
        for x,random_board_number in enumerate(random_board_line):
            #hidden positions
            if (x, y) in hidden_x_y: 
                board_chars.append(Char(x, y, 0, 'orange', False))
            #normal positions
            else:
                board_chars.append(Char(x, y, random_board_number, 'black', True))
        board_lines.append(board_chars)
    

def test():
    #displays random board in consol for test
    print('   ┌─┬─┬─┬─┬─┬─┬─┬─┬─┐')
    for row in random_board:
        print(f'{random_board.index(row)+1}: ', end='')
        for element in row:
            print(f'|{element}', end='')
        print('|')
    print('   └─┴─┴─┴─┴─┴─┴─┴─┴─┘')


#MAIN PROGRAM
init()

level_handling()

#test()

#MAIN LOOP
while game_running:
    screen.fill('white')
    
    #Event handling
    for event in pg.event.get():
        if event.type == pg.QUIT:
            game_running = False
        elif event.type == pg.MOUSEBUTTONDOWN:
            if event.button == 1:
                mouse_pos = pg.mouse.get_pos()
                matrix_mouse_x = (mouse_pos[0] - board_x_offset + char_width // 2) // char_width
                matrix_mouse_y = (mouse_pos[1] - board_y_offset + char_height // 2) // char_height

                #clicking on the board
                if ((matrix_mouse_x >= 0) and (matrix_mouse_y >= 0) and
                    (matrix_mouse_x <= 8) and (matrix_mouse_y <= 8)):
                    #sound: click
                    sound_click.play()
                    checked = False
                    #no any previous selection
                    if selected_value == None:
                        selected_value = matrix_select(matrix_mouse_x, matrix_mouse_y, selected_value)
                        checked = True
                    elif selected_value != None:
                        #if the selection is already selected -> clear the selection
                        if (selected_value[0], selected_value[1]) == (matrix_mouse_x, matrix_mouse_y):
                            selected_value = matrix_unselect(selected_value[0],
                                                             selected_value[1],
                                                             selected_value[2])
                        #if we have a selection -> clear and jump to the new
                        else:
                             selected_value = matrix_unselect(selected_value[0],
                                                             selected_value[1],
                                                             selected_value[2])
                             selected_value = matrix_select(matrix_mouse_x, matrix_mouse_y, selected_value)

                #clicking on the samples
                if ((matrix_mouse_x >= 3) and (matrix_mouse_y >= -4) and
                    (matrix_mouse_x <= 5) and (matrix_mouse_y <= -2)):
                    if selected_value != None:
                        selected_sample = sample[matrix_mouse_y + 4][matrix_mouse_x - 3].value
                        write_selected(selected_value, selected_sample)
                        selected_value = None
                        #sound: write
                        sound_write.play()
                        if check_win():
                            win()

                #clicking on the level control
                if ((matrix_mouse_x == 15) and (matrix_mouse_y >= 4) and
                    (matrix_mouse_y <= 12)):
                    game_level = 13 - matrix_mouse_y
                    level_handling()

        elif event.type == pg.KEYDOWN:

            #ESC: exit
            if event.key == pg.K_ESCAPE:
                game_running = False

            #space: new game
            if event.key == pg.K_SPACE:
                level_handling()


            #up: new game with level up
            if event.key == pg.K_UP:
                level_handling('up')

            #down: new game with level down
            if event.key == pg.K_DOWN:
                level_handling('down')
            
    #Graphics
    displays_graphics()

#End of program
pg.quit()
