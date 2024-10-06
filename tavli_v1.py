import pygame as pg
import random
import os
import time

os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (150,30)

pg.init()
move_sound = pg.mixer.Sound("sounds/piece_move.wav")
winning_sound = pg.mixer.Sound("sounds/applause.wav")
move_sound.set_volume(1)
size = (1024, 868)  # window size W x H
screen = pg.display.set_mode(size)
background = pg.image.load("img/board.png") 
font = pg.font.SysFont(None, 24)
my_color = (71, 40, 21)

# placement variables
puck_size = 56
col1_x = 868
col7_x = 423
low_y = 686
high_y = 28
col_dist = 64.5
col_width = 56
col_height = 271

# variables for roll buttons
bwidth = 140 # = Button Width
bheight = 50 # = Button Height
# wxpos = 150 # = White X Position
# wypos = 800 # = White Y Position
bxpos = 80 # = Black X Position
bypos = 780 # = Black Y Position

# various flags and vars
running = True
current_turn = None # specifies current turn as "white" or "black"
end_of_turn = True  # flag to signify end of turn
show_moves_flag = False # flag to turn on or off available moves indicator
active_col = None   # variable specifying selected column
active_puck = None  # variable specifying selected puck
home_white = False  # flag checking if whites can be collected
home_black = False  # flag checking if blacks can be collected
collected_white = 0 # counter for collected white pucks
collected_black = 0 # counter for collected black pucks

# images
roll_button = pg.image.load("img/roll_b_inactive.png")
active_roll_button = pg.image.load("img/roll_b_active.png")
highlight_col_bot = pg.image.load("img/col_light_bot.png")
highlight_col_top = pg.image.load("img/col_light_top.png")

# dice
class Dice:
    def __init__(self):
        d1 = 0
        d2 = 0
        d3 = 0
        d4 = 0
        doubles = None

# gamemode: 1 = 2d4, 2 = 1d4,1d8, 3 = 2d8
# d1, d2 are the normal dice, d3, d4 are reserved for doubles
gamemode = None
dice = Dice()
moves = []

# for positioning the pucks
def position(x, y):
    x = x
    y = y
    c_x = 100
    c_y = 28

    if x >= 6:
        x += 1
    if y >= 6:
        c_y += 22

    X = c_x + (x * 63.8)
    Y = c_y + (y * 57.9)

    return (X, Y)

# roll the dice
def roll(dice):
    # roll 2 dice based on gamemode
    if gamemode == 1:
        dice.d1 = random.randint(1, 4)
        dice.d2 = random.randint(1, 4)
    elif gamemode == 2:
        dice.d1 = random.randint(1, 4)
        dice.d2 = random.randint(1, 8)
    elif gamemode == 3:
        dice.d1 = random.randint(1, 8)
        dice.d2 = random.randint(1, 8)
    else:
        dice.d1 = random.randint(1, 6)
        dice.d2 = random.randint(1, 6)
    # check for doubles
    # dice.d1 = dice.d2 #debug
    if dice.d1 == dice.d2:
        dice.doubles = True
        dice.d3 = dice.d1
        dice.d4 = dice.d1
    else: 
        dice.doubles = False
        dice.d3 = 0
        dice.d4 = 0

    return dice

# id = color, coordinates for placement purposes
class puck:
    def __init__(self, color):
        self.color = color
        self.hit = False
        # get image
        if self.color == "white":
            self.image = pg.image.load("img/white_puck.png")
        else:
            self.image = pg.image.load("img/black_puck.png")

    def get_coords(self, col, sz):    
        # get y
        if 0 <= col <= 12:
            self.y_coord = low_y - sz * puck_size
            # get x
            if col == 0:
                self.x_coord = black_mid.xpos
                self.y_coord = black_mid.ypos + sz * puck_size
            elif 1 <= col <= 6:
                self.x_coord = col1_x - (col-1) * col_dist
            else:
                self.x_coord = col7_x - (col-7) * col_dist
        else: 
            self.y_coord = high_y + sz * puck_size
            # get x
            if col == 25:
                self.x_coord = white_mid.xpos
                self.y_coord = white_mid.ypos - sz * puck_size
            elif 19 <= col <= 24:
                self.x_coord = col1_x - (24-col) * col_dist
            else:
                self.x_coord = col7_x - (18-col) * col_dist
        # print(col, self.color, self.x_coord, self.y_coord) #debug

# array of white pucks
whites = [
    puck("white"), puck("white"), puck("white"), puck("white"), puck("white"), 
    puck("white"), puck("white"), puck("white"), puck("white"), puck("white"), 
    puck("white"), puck("white"), puck("white"), puck("white"), puck("white")
]

# array of black pucks
blacks = [
    puck("black"), puck("black"), puck("black"), puck("black"), puck("black"), 
    puck("black"), puck("black"), puck("black"), puck("black"), puck("black"), 
    puck("black"), puck("black"), puck("black"), puck("black"), puck("black")
]

# for column stack class
class column:
    def __init__(self, number, xpos, ypos):
        self.pucks = []
        self.number = number
        self.color = None
        self.size = 0
        self.xpos = xpos
        self.ypos = ypos

    def remove_piece(self): #poping
        if len(self.pucks) > 0:
            self.size -= 1
            if self.size == 0:
                self.color == None
            return self.pucks.pop()

    def add_piece(self, piece_to_add): #pushing
        self.color = piece_to_add.color
        self.pucks.append(piece_to_add)
        # call to get the new coordinates of the puck
        piece_to_add.get_coords(self.number, self.size)
        self.size += 1

white_mid = column(25, 485, 322)
black_mid = column(0, 485, 398)

# to move piece (from and to refer to columns)
def move(FROM, TO):
    pg.mixer.Sound.play(move_sound)
    pg.mixer.Sound.play(move_sound)
    # check if a puck is hit
    if TO.color != None and TO.color != FROM.color:
        # move to corresponding middle
        if current_turn == "white":
            move(TO, black_mid)
        else:
            move(TO, white_mid)
    # perform original move
    TO.add_piece(FROM.remove_piece())

d1ok = False
d2ok = False

def legal_moves(col):
    # clear list
    moves.clear()
    # moves.append(col)
    if not turn_over():
        moves.append(col)
        if current_turn == "white":
            legal_moves_white()
        else:
            legal_moves_black()

def legal_moves_white():
    # color of curernt column 
    curr_color = columns[moves[0]-1].color
    if curr_color == "white" and dice.d1+dice.d2+dice.d3+dice.d4 > 0:
        # for doubles
        if dice.doubles:
            if moves[0] + dice.d1 <= 24 and (curr_color == columns[moves[0]-1 + dice.d1].color or 0 <= columns[moves[0]-1 + dice.d1].size <= 1):
                moves.append(columns[moves[0]-1 + dice.d1])
                d1ok = True
            else: d1ok = False
            if dice.d2 > 0 and moves[0] + 2*dice.d1 <= 24 and (curr_color == columns[moves[0]-1 + 2*dice.d1].color or 0 <= columns[moves[0]-1 + 2*dice.d1].size <= 1) and d1ok:
                moves.append(columns[moves[0]-1 + 2*dice.d1])
            if dice.d3 > 0 and moves[0] + 3*dice.d1 <= 24 and (curr_color == columns[moves[0]-1 + 3*dice.d1].color or 0 <= columns[moves[0]-1 + 3*dice.d1].size <= 1) and d1ok:
                moves.append(columns[moves[0]-1 + 3*dice.d1])
            if dice.d4 > 0 and moves[0] + 4*dice.d1 <= 24 and (curr_color == columns[moves[0]-1 + 4*dice.d1].color or 0 <= columns[moves[0]-1 + 4*dice.d1].size <= 1) and d1ok:
                moves.append(columns[moves[0]-1 + 4*dice.d1])
        else:
            #  not out of bounds              if source color = destination color                  or destination is empty or has 1 puck                       
            if dice.d1 > 0 and moves[0] + dice.d1 <= 24 and (curr_color == columns[moves[0]-1 + dice.d1].color or 0 <= columns[moves[0]-1 + dice.d1].size <= 1):
                moves.append(columns[moves[0]-1 + dice.d1])
                d1ok = True
            else: d1ok = False
            # same for d2
            if dice.d2 > 0 and moves[0] + dice.d2 <= 24 and (curr_color == columns[moves[0]-1 + dice.d2].color or 0 <= columns[moves[0]-1 + dice.d2].size <= 1):
                moves.append(columns[moves[0]-1 + dice.d2])
                d2ok = True
            else: d2ok = False
            # same for d1+d2
            if dice.d1 > 0 and dice.d2 > 0 and moves[0] + dice.d1 + dice.d2 <= 24 and (curr_color == columns[moves[0]-1 + dice.d1 + dice.d2].color or 0 <= columns[moves[0]-1 + dice.d1 + dice.d2].size <= 1) and (d1ok or d2ok):
                moves.append(columns[moves[0]-1 + dice.d1 + dice.d2])
        
def legal_moves_black():
    # color of curernt column 
    curr_color = columns[moves[0]-1].color
    if curr_color == "black" and dice.d1+dice.d2+dice.d3+dice.d4 > 0:
        # same for doubles
        if dice.doubles:
            if 1 <= moves[0] - dice.d1 and (curr_color == columns[moves[0]-1 - dice.d1].color or 0 <= columns[moves[0]-1 - dice.d1].size <= 1):
                moves.append(columns[moves[0]-1 - dice.d1])
                d1ok = True
            else: d1ok = False
            if dice.d2 > 0 and 1 <= moves[0] - 2*dice.d1 and (curr_color == columns[moves[0]-1 - 2*dice.d1].color or 0 <= columns[moves[0]-1 - 2*dice.d1].size <= 1) and d1ok:
                moves.append(columns[moves[0]-1 - 2*dice.d1])
            if dice.d3 > 0 and 1 <= moves[0] - 3*dice.d1 and (curr_color == columns[moves[0]-1 - 3*dice.d1].color or 0 <= columns[moves[0]-1 - 3*dice.d1].size <= 1) and d1ok:
                moves.append(columns[moves[0]-1 - 3*dice.d1])
            if dice.d4 > 0 and 1 <= moves[0] - 4*dice.d1 and (curr_color == columns[moves[0]-1 - 4*dice.d1].color or 0 <= columns[moves[0]-1 - 4*dice.d1].size <= 1) and d1ok:
                moves.append(columns[moves[0]-1 - 4*dice.d1])
        else:
            #  not out of bounds         and source color = destination color                     or destination is empty or has 1 puck                       
            if dice.d1 > 0 and 1 <= moves[0] - dice.d1 and (curr_color == columns[moves[0]-1 - dice.d1].color or 0 <= columns[moves[0]-1 - dice.d1].size <= 1):
                moves.append(columns[moves[0]-1 - dice.d1])
                d1ok = True
            else: d1ok = False
            # same for d2
            if dice.d2 > 0 and 1 <= moves[0] - dice.d2 and (curr_color == columns[moves[0]-1 - dice.d2].color or 0 <= columns[moves[0]-1 - dice.d2].size <= 1):
                moves.append(columns[moves[0]-1 - dice.d2])
                d2ok = True
            else: d2ok = False
            # same for d1+d2
            if dice.d1 > 0 and dice.d2 > 0 and 1 <= moves[0] - dice.d1 - dice.d2 and (curr_color == columns[moves[0]-1 - (dice.d1 + dice.d2)].color or 0 <= columns[moves[0]-1 - (dice.d1 + dice.d2)].size <= 1) and (d1ok or d2ok):
                moves.append(columns[moves[0]-1 - (dice.d1 + dice.d2)])

def update_moves(dist):
    distance = []
    index = 0
    if not dice.doubles:
        if dist == dice.d1:
            dice.d1 = 0
        elif dist == dice.d2:
            dice.d2 = 0
        else:
            dice.d1 = dice.d2 = 0
    else:
        cnt = (dist/dice.d1)
        sum = dice.d1 + dice.d2 + dice.d3 + dice.d4
        if cnt == 4:
            dice.d1 = dice.d2 = dice.d3 = dice.d4 = 0
        elif cnt == 3 and sum == 4*dice.d1:
            dice.d2 = dice.d3 = dice.d4 = 0
        elif cnt == 3 and sum == 3*dice.d1:
            dice.d1 = dice.d2 = dice.d3 = 0
        elif cnt == 2 and sum == 4*dice.d1:
            dice.d3 = dice.d4 = 0
        elif cnt == 2 and sum == 3*dice.d1:
            dice.d2 = dice.d3 = 0
        elif cnt == 2 and sum == 2*dice.d1:
            dice.d1 = dice.d2 = 0    
        elif cnt == 1 and sum == 4*dice.d1:
            dice.d4 = 0
        elif cnt == 1 and sum == 3*dice.d1:
            dice.d3 = 0
        elif cnt == 1 and sum == 2*dice.d1:
            dice.d2 = 0
        else: 
            dice.d1 = 0

            
    print(dice.d1, dice.d2, dice.d3, dice.d4) #debug
    legal_moves(moves[0])

def show_moves():
    for j in moves[1:]:
        if 1<=j.number<=12:
            screen.blit(highlight_col_bot, (j.xpos, j.ypos))
        else:
            screen.blit(highlight_col_top, (j.xpos, j.ypos))

def turn_over():
    if dice.d1 == dice.d2 == dice.d3 == dice.d4 == 0:
        return True
    else:
        return False

def home_check():
    sum_w = sum_b = 0
    if gamemode == None or gamemode == 1:
        # check whites
        for w in columns[17:]: # get columns 17-23
            if w.color == "white":
                sum_w += w.size
        if sum_w + collected_white == 15:
            home_white = True
        else: 
            home_white = False
        # check blacks
        for b in columns[:6]: # get columns 0-5
            if b.color == "black":
                sum_w += b.size
        if sum_b + collected_black == 15:
            home_black = True
        else: 
            home_black = False
    else:
        # check whites
        for w in columns[15:]: # get columns 15-23
            if w.color == "white":
                sum_w += w.size
        if sum_w + collected_white == 15:
            home_white = True
        else: 
            home_white = False
        # check blacks
        for b in columns[:8]: # get columns 0-7
            if b.color == "black":
                sum_w += b.size
        if sum_b + collected_black == 15:
            home_black = True
        else: 
            home_black = False

# columns array 
bot_light_y = 415
top_light_y = 60 
columns = [
    column(1, col1_x, bot_light_y), column(2, col1_x-(col_width+8.5), bot_light_y), column(3, col1_x-2*(col_width+8.5), bot_light_y), column(4, col1_x-3*(col_width+8.5), bot_light_y), column(5, col1_x-4*(col_width+8.5), bot_light_y), column(6, col1_x-5*(col_width+8.5), bot_light_y),
    column(7, col7_x, bot_light_y), column(8, col7_x-(col_width+8.5), bot_light_y), column(9, col7_x-2*(col_width+8.5), bot_light_y), column(10, col7_x-3*(col_width+8.5), bot_light_y), column(11, col7_x-4*(col_width+8.5), bot_light_y), column(12, col7_x-5*(col_width+8.5), bot_light_y),
    column(13, col7_x-5*(col_width+8.5), top_light_y), column(14, col7_x-4*(col_width+8.5), top_light_y), column(15, col7_x-3*(col_width+8.5), top_light_y), column(16, col7_x-2*(col_width+8.5), top_light_y), column(17, col7_x-(col_width+8.5), top_light_y), column(18, col7_x, top_light_y),
    column(19, col1_x-5*(col_width+8.5), top_light_y), column(20, col1_x-4*(col_width+8.5), top_light_y), column(21, col1_x-3*(col_width+8.5), top_light_y), column(22, col1_x-2*(col_width+8.5), top_light_y), column(23, col1_x-(col_width+8.5), top_light_y), column(24, col1_x, top_light_y) 
]

# initialize columns with pucks
columns[0].add_piece(whites[0]); columns[0].add_piece(whites[1])
columns[5].add_piece(blacks[0]); columns[5].add_piece(blacks[1]); columns[5].add_piece(blacks[2]); columns[5].add_piece(blacks[3]); columns[5].add_piece(blacks[4])
columns[7].add_piece(blacks[5]); columns[7].add_piece(blacks[6]); columns[7].add_piece(blacks[7])
columns[11].add_piece(whites[2]); columns[11].add_piece(whites[3]); columns[11].add_piece(whites[4]); columns[11].add_piece(whites[5]); columns[11].add_piece(whites[6])
columns[12].add_piece(blacks[8]); columns[12].add_piece(blacks[9]); columns[12].add_piece(blacks[10]); columns[12].add_piece(blacks[11]); columns[12].add_piece(blacks[12])
columns[16].add_piece(whites[7]); columns[16].add_piece(whites[8]); columns[16].add_piece(whites[9])
columns[18].add_piece(whites[10]); columns[18].add_piece(whites[11]); columns[18].add_piece(whites[12]); columns[18].add_piece(whites[13]); columns[18].add_piece(whites[14])
columns[23].add_piece(blacks[13]); columns[23].add_piece(blacks[14])

# messages
info = font.render("Playing: ", True, (0,255,255))

# # debug space
# for i in whites:
#     print(i.x_coord, i.y_coord)
# for i in blacks:
#     print(i.x_coord, i.y_coord)


while running:

    mouse = pg.mouse.get_pos()
    click = pg.mouse.get_pressed()

    # decide first turn
    while current_turn == None:
        # d3, d4 not used here
        roll(dice)
        if dice.d1 > dice.d2:
            current_turn = "black"
        elif dice.d2 > dice.d1:
            current_turn = "white"
        dice.d1 = dice.d2 = 0
    
    # set background
    screen.fill((0,0,0))
    screen.blit(background, (0,0))
    # pg.display.flip()
    for event in pg.event.get():
        if event.type == pg.QUIT:
            running = False

    out = font.render("playing: " + current_turn,True,(0,255,0), (150,150,150))
    screen.blit(out, (500, 800))

    # set up pieces on board
    for i in whites:
        screen.blit(i.image, (i.x_coord, i.y_coord))
    for i in blacks:
        screen.blit(i.image, (i.x_coord, i.y_coord))

    # screen.blit(roll_button, (bxpos,bypos))

    # if end_of_turn == True:
    if turn_over():
        # change roll button on hover
        if (bxpos <= mouse[0] <= bxpos + bwidth) and (bypos <= mouse[1] <= bypos + bheight):
            screen.blit(active_roll_button, (bxpos,bypos))
            # roll on clikc and start new turn
            if click[0] == 1:
                # end_of_turn = False
                roll(dice)
                print(dice.d1, dice.d2, dice.d3, dice.d4) #debug
                moves.clear
                moves.append(0)
        else:
            screen.blit(roll_button, (bxpos, bypos))

    # a player is playing
    else:
        # listen for mouse click on column to show available moves
        if event.type == pg.MOUSEBUTTONDOWN:# and not show_moves_flag:
            pg.time.wait(100)
            for i in columns:
                if (i.xpos <= mouse[0] <= i.xpos+col_width) and (i.ypos <= mouse[1] <= i.ypos+col_height):
                    active_col = i.number 

                    if show_moves_flag and active_col == moves[0]:
                        show_moves_flag = False
                    elif not show_moves_flag and active_col == moves[0]:
                        show_moves_flag = True
                    else:                        
                        # check if player clicked a valid move fromm the moves list
                        if show_moves_flag and len(moves) > 1:
                            for j in moves[1:]:
                                if j.xpos <= mouse[0] <= j.xpos + col_width and j.ypos <= mouse[1] <= j.ypos + col_height:
                                    move(columns[moves[0]-1], columns[j.number-1])
                                    print(abs(moves[0]-j.number))
                                    update_moves(abs(moves[0]-j.number))
                                    
                        legal_moves(active_col)            
                        show_moves_flag = True

        if show_moves_flag and not turn_over():
            show_moves()    
        # change player turn
        if turn_over() and current_turn == "white":
            current_turn = "black"
            print("turn over")
        elif turn_over() and current_turn == "black":
            current_turn = "white"
            print("turn over")

















    pg.display.update()
    