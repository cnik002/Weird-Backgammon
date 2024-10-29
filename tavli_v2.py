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
puck_w = 50
puck_h = 20
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
rolled = False
current_turn = None # specifies current turn as "white" or "black"
end_of_turn = True  # flag to signify end of turn
show_moves_flag = False # flag to turn on or off available moves indicator
active_col = None   # variable specifying selected column
active_puck = None  # variable specifying selected puck
home_white = False  # flag checking if whites can be collected
home_black = False  # flag checking if blacks can be collected

# images
roll_button = pg.image.load("img/roll_b_inactive.png")
active_roll_button = pg.image.load("img/roll_b_active.png")
w_puck = pg.image.load("img/white_puck.png")
b_puck = pg.image.load("img/black_puck.png")
w_coll = pg.image.load("img/white_side.png")
b_coll = pg.image.load("img/black_side.png")
selected_white_puck = pg.image.load("img/white_highlight.png")
selected_black_puck = pg.image.load("img/black_highlight.png")
highlight_col_bot = pg.image.load("img/col_light_bot.png")
highlight_col_top = pg.image.load("img/col_light_top.png")
highlight_tower = pg.image.load("img/image1-3.png")

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
    if dice.d1 == dice.d2:
        dice.doubles = True
        dice.d3 = dice.d1
        dice.d4 = dice.d1
    else: 
        dice.doubles = False
        dice.d3 = 0
        dice.d4 = 0

    return dice

# puck class 
# used for init and getting puck coordinates
class puck:
    def __init__(self, color, id):
        self.color = color
        self.hit = False
        self.id = id
        # get image
        if self.color == "white":
            self.image = w_puck
        else:
            self.image = b_puck

    # during normal gameplay
    def get_coords(self, col, sz):    
        # reduce size to stack puck in columns > 5
        if sz >= 5:
            sz = sz - 4.5
        # bottom half of board
        # get y
        if 1 <= col <= 12 or col == 25:
            self.y_coord = low_y - sz * puck_size
            # get x
            if col == 25: # column for black hit pucks
                self.x_coord = columns[25].xpos
                self.y_coord = columns[25].ypos + sz * puck_size
            elif 1 <= col <= 6:
                self.x_coord = col1_x - (col-1) * col_dist
            else:
                self.x_coord = col7_x - (col-7) * col_dist
        # upper half of board
        else: 
            self.y_coord = high_y + sz * puck_size
            # get x
            if col == 0: # column for white hit pucks
                self.x_coord = columns[0].xpos
                self.y_coord = columns[0].ypos - sz * puck_size
            elif 19 <= col <= 24:
                self.x_coord = col1_x - (24-col) * col_dist
            else:
                self.x_coord = col7_x - (18-col) * col_dist

    # used to stack pucks when collected
    def get_t_coords(self, color, sz):
        if color == "black": 
            self.x_coord = black_tower.xpos - 2
            self.y_coord = black_tower.ypos + 50 + col_height - sz * puck_h
        else:
            self.x_coord = white_tower.xpos - 2
            self.y_coord = 35 + sz * puck_h

# array of white pucks
whites = [
    puck("white",0), puck("white",1), puck("white",2), puck("white",3), puck("white",4), 
    puck("white",5), puck("white",6), puck("white",7), puck("white",8), puck("white",9), 
    puck("white",10), puck("white",11), puck("white",12), puck("white",13), puck("white",14)
]

# array of black pucks
blacks = [
    puck("black",0), puck("black",1), puck("black",2), puck("black",3), puck("black",4), 
    puck("black",5), puck("black",6), puck("black",7), puck("black",8), puck("black",9), 
    puck("black",10), puck("black",11), puck("black",12), puck("black",13), puck("black",14)
]

# array of collected pucks
collected = []

# for column stack class
class column:
    def __init__(self, number, xpos, ypos):
        self.pucks = []
        self.number = number
        self.color = None
        self.size = 0
        self.xpos = xpos
        self.ypos = ypos

    # removing a puck from a column
    # reduce col size, check if empty after removal and return the puck
    def remove_piece(self): #poping
        if len(self.pucks) > 0:
            self.size -= 1
            if self.size == 0:
                self.color = None
            return self.pucks.pop()

    # add a puck to a column
    def add_piece(self, piece_to_add): #pushing
        # if move is pwerformed then validity was already checked -> make col color  = puck color
        self.color = piece_to_add.color
        self.pucks.append(piece_to_add)
        # call to get the new coordinates of the puck
        piece_to_add.get_coords(self.number, self.size)
        self.size += 1

    # add a puck to the collected column - similar to add_piece but no coloring needed
    def add_tower(self, add):
        self.pucks.append(add)
        add.get_t_coords(add.color, self.size)
        self.size += 1

    # used to highlight the top puck of the active column
    def highlight_puck(self):
        # unhilight all pucks just in case
        unhilight_pucks("w")
        unhilight_pucks("b")
        if not turn_over() and self.size > 0:
            # remove top puck to change its image (to highlighted) and then put it back
            tpuck = self.remove_piece()
            if tpuck.color == "white" == current_turn:
                tpuck.image = selected_white_puck
            elif tpuck.color == "black" == current_turn:
                tpuck.image = selected_black_puck
            self.add_piece(tpuck)

# opposite function of highlight puck - makes all pucks not highlighted
def unhilight_pucks(color):
    if color == "w":
        for w in whites:
            w.image = w_puck
    elif color == "b":
        for b in blacks:
            b.image = b_puck
    else:
        for w in whites:
            w.image = w_puck
        for b in blacks:
            b.image = b_puck

# check if a move is legal (check target column's color and size)
def is_legal(FROM,TO):
    if FROM.color == TO.color or 0 <= TO.size <= 1:
        return True
    return False

# check and automate hit puck in case player moves to the sum of dice
# in game description, write that the game tries to play the smallest die first
def split_dice(FROM, TO):
    dist = abs(FROM.number-TO.number)
    # separate moves
    # set move1 as smallest die
    if dice.d1 <= dice.d2:
        move1 = dice.d1
        move2 = dist - dice.d1
    else:
        move1 = dice.d2
        move2 = dist - dice.d2  

    # for whites, try to do small move first
    if current_turn == "white" and is_legal(FROM,columns[FROM.number + move1]):
        move(FROM, columns[FROM.number + move1])
        move(columns[FROM.number + move1], columns[FROM.number + move1 + move2])
    elif current_turn == "white" and is_legal(FROM,columns[FROM.number + move2]):
        move(FROM, columns[FROM.number + move2])
        move(columns[FROM.number + move2], columns[FROM.number + move2 + move1])

    # for blacks, try to do small move first
    elif current_turn == "black" and is_legal(FROM,columns[FROM.number - move1]): 
        if is_legal(FROM,columns[FROM.number - move1]):
            move(FROM, columns[FROM.number - move1])
            move(columns[FROM.number - move1], columns[FROM.number - move1 - move2])
    elif current_turn == "black" and is_legal(FROM,columns[FROM.number - move2]):
        move(FROM, columns[FROM.number - move2])
        move(columns[FROM.number - move2], columns[FROM.number - move2 - move1])

# to move piece (from and to refer to columns)
def move(FROM, TO):
    # global w_coll, b_coll, whites, blacks ,collected
    dist = abs(FROM.number-TO.number)
    # if move is bigger than a single die + puck is not hit or collected
    if (dist > dice.d1 and dist > dice.d2) and (0 < TO.number < 25):
        split_dice(FROM, TO)
        return
    pg.mixer.Sound.play(move_sound)
    pg.mixer.Sound.play(move_sound)
    # check if puck is collected
    # MUST ADD CODE TO COLLECT WITH A BIGGER NUMBER - TODO
    if TO.number == 30 or TO.number == 60:
        print("FROM - TO: " , FROM.number, TO.number)
        # remove puck to be collected and change image accordingly
        to_add = FROM.remove_piece()
        if TO.number == 30: # collect black
            print(to_add.image) #debug
            to_add.image = b_coll
            print(to_add.image) #debug
        else: # collect white
            print(whites[to_add.id].image) # debug
            whites[to_add.id].image = w_coll
            print(to_add.image) #debug
        # put in list to be shown and collect puck
        collected.append(to_add)
        TO.add_tower(to_add)
    else:    
        # check if a puck is hit
        if TO.color != current_turn and TO.size == 1 and (0 < TO.number < 25):
            # move to corresponding middle
            if current_turn == "white":
                move(TO, columns[25])
            else:
                move(TO, columns[0])
        # perform original move
        TO.add_piece(FROM.remove_piece())

# flags to help in legal_moves
d1ok = False
d2ok = False
d3ok = False

# call appropriate functions to calculate legal moves for active puck/column
def legal_moves(col):
    # clear list
    moves.clear()
    if col == -1: # exit default
        moves.append(-10)
    else:
        # moves[0] stores number of active column
        moves.append(col)
        home_check() # perform home_check before branching
        if current_turn == "white" and columns[0].size == 0:
            legal_moves_white()
        elif current_turn == "black" and columns[25].size == 0:
            legal_moves_black()
        elif current_turn == "white" and columns[0].size > 0:
            seat_white()
        else:
            seat_black()

# find available moves for white after being hit
def seat_white():
        # if dice.doubles:
        #                   if destination color is white     or destination is empty or has 1 puck
        if dice.d1 > 0 and (columns[dice.d1].color == "white" or 0 <= columns[dice.d1].size <= 1):
            moves.append(columns[dice.d1])
            d1ok = True
        else:
            d1ok = False
        # same for d2
        if not dice.doubles and dice.d2 > 0 and (columns[dice.d2].color == "white" or 0 <= columns[dice.d2].size <= 1):
            moves.append(columns[dice.d2])
            d2ok = True
        else:
            d2ok = False
        if dice.doubles:
            d2ok = d1ok
        # same for d1 + d2 if only 1 puck is hit
        if columns[0] == 1 and (d1ok or d2ok) and (columns[dice.d1+dice.d2].color == "white" or 0 <= columns[dice.d1+dice.d2].size <= 1):
            moves.append(columns[dice.d1+dice.d2])
            # if d1+d2 is valid check if doubles and if it has valid moves
            if dice.doubles:
                if (columns[3*dice.d1].color == "white" or 0 <= columns[3*dice.d1].size <= 1):
                    moves.append(columns[3*dice.d1])
                    if (columns[4*dice.d1].color == "white" or 0 <= columns[4*dice.d1].size <= 1):
                        moves.append(columns[4*dice.d1])
        # end turn if no moves found
        if not d1ok and not d2ok:
            dice.d1 = dice.d2 = dice.d3 = dice.d4 = 0

# find available moves for black after being hit
def seat_black():
        # if dice.doubles:
        #  if destination color is black       or destination is empty or has 1 puck
        if dice.d1 > 0 and (columns[25-dice.d1].color == "black" or 0 <= columns[25-dice.d1].size <= 1):
            moves.append(columns[25-dice.d1])
            d1ok = True
        else:
            d1ok = False
        # same for d2
        if not dice.doubles and dice.d2 > 0 and (columns[25-dice.d2].color == "black" or 0 <= columns[25-dice.d2].size <= 1):
            moves.append(columns[25-dice.d2])
            d2ok = True
        else:
            d2ok = False
        if dice.doubles:
            d2ok = d1ok
        # same for d1 + d2
        if columns[25] == 1 and (d1ok or d2ok) and (columns[25-(dice.d1+dice.d2)].color == "black" or 0 <= columns[25-(dice.d1+dice.d2)].size <= 1):
            moves.append(columns[25-(dice.d1+dice.d2)])
            # if d1+d2 is valid check if doubles and if it has valid moves
            if dice.doubles:
                if (columns[25-(3*dice.d1)].color == "black" or 0 <= columns[25-(3*dice.d1)].size <= 1):
                    moves.append(columns[(25-3*dice.d1)])
                    if (columns[25-(4*dice.d1)].color == "black" or 0 <= columns[(25-4*dice.d1)].size <= 1):
                        moves.append(columns[25-(4*dice.d1)])
        # end turn if no moves found
        if not d1ok and not d2ok:
            dice.d1 = dice.d2 = dice.d3 = dice.d4 = 0

# find available moves for collecting pucks
def collecting_moves(color):
    global home_black, home_white
    coll_flag = False
    # check if pucks can be collected
    if color == "white":
        # collecting exact dice roll
        if 25-dice.d1 == moves[0]:
            coll_flag = True
        if 25-dice.d2 == moves[0]:
            coll_flag = True
        # collect sum roll
        if 25-(dice.d1+dice.d2) == moves[0]:
            coll_flag = True
        if dice.doubles and 25-(3*dice.d1) == moves[0]:
            coll_flag = True
        if dice.doubles and 25-(4*dice.d1) == moves[0]:
            coll_flag = True
        # if a move is found add the collect tower to moves
        if coll_flag:
            moves.append(white_tower)
        # check if a bigger number can collect a smaller column (eg collect 5 with a 6)
        big_flag = None
        if 25-dice.d1 < moves[0]:
            big_flag = True
            for c in columns[17:moves[0]]:
                if c.size > 0:
                    big_flag = False
        # if a move is found add the collect tower to moves
        if big_flag and not coll_flag:
            moves.append(white_tower)
        big_flag = None
        if 25-dice.d2 < moves[0]:
            coll_flag = True
            for c in columns[17:moves[0]]:
                if c.size > 0:
                    big_flag = False
        # if a move is found add the collect tower to moves
        if big_flag:
            moves.append(white_tower)
    
    # same for black
    elif color == "black":
        # collecting exact dice roll
        if dice.d1 == moves[0]:
            coll_flag = True
        if dice.d2 == moves[0]:
            coll_flag = True
        # collect sum roll
        if (dice.d1+dice.d2) == moves[0]:
            coll_flag = True
        if dice.doubles and (3*dice.d1) == moves[0]:
            coll_flag = True
        if dice.doubles and (4*dice.d1) == moves[0]:
            coll_flag = True
        # if a move is found add the collect tower to moves
        if coll_flag:
            moves.append(black_tower)
        # check if a bigger number can collect a smaller column (eg collect 5 with a 6)
        big_flag = None
        if dice.d1 > moves[0]:
            big_flag = True
            for c in columns[moves[0]:9]:
                if c.size > 0:
                    big_flag = False
        if big_flag:
            moves.append(black_tower)
        big_flag = None
        if dice.d2 > moves[0]:
            big_flag = True
            for c in columns[moves[0]:9]:
                if c.size > 0:
                    big_flag = False
        if big_flag:
            moves.append(black_tower)
        
# find available moves for white pucks
def legal_moves_white():
    global home_white
    # color of curernt column 
    curr_color = columns[moves[0]].color
    if curr_color == "white" and dice.d1+dice.d2+dice.d3+dice.d4 > 0:
        # check if pucks can be collected
        if home_white:
            collecting_moves("white")
        # for doubles
        if dice.doubles:
            if moves[0] + dice.d1 <= 24 and (curr_color == columns[moves[0] + dice.d1].color or 0 <= columns[moves[0] + dice.d1].size <= 1):
                moves.append(columns[moves[0] + dice.d1])
                d1ok = True
            else: d1ok = False
            if d1ok and dice.d2 > 0 and moves[0] + 2*dice.d1 <= 24 and (curr_color == columns[moves[0] + 2*dice.d1].color or 0 <= columns[moves[0] + 2*dice.d1].size <= 1):
                moves.append(columns[moves[0] + 2*dice.d1])
                d2ok = True
            else: d2ok = False
            if d1ok and d2ok and dice.d3 > 0 and moves[0] + 3*dice.d1 <= 24 and (curr_color == columns[moves[0] + 3*dice.d1].color or 0 <= columns[moves[0] + 3*dice.d1].size <= 1):
                moves.append(columns[moves[0] + 3*dice.d1])
                d3ok = True
            else: d3ok = False
            if d1ok and d2ok and d3ok and dice.d4 > 0 and moves[0] + 4*dice.d1 <= 24 and (curr_color == columns[moves[0] + 4*dice.d1].color or 0 <= columns[moves[0] + 4*dice.d1].size <= 1):
                moves.append(columns[moves[0] + 4*dice.d1])
        else:
            #  not out of bounds                         if source color = destination color                   or destination is empty or has 1 puck                       
            if dice.d1 > 0 and moves[0] + dice.d1 <= 24 and (curr_color == columns[moves[0] + dice.d1].color or 0 <= columns[moves[0] + dice.d1].size <= 1):
                moves.append(columns[moves[0] + dice.d1])
                d1ok = True
            else: d1ok = False
            # same for d2
            if dice.d2 > 0 and moves[0] + dice.d2 <= 24 and (curr_color == columns[moves[0] + dice.d2].color or 0 <= columns[moves[0] + dice.d2].size <= 1):
                moves.append(columns[moves[0] + dice.d2])
                d2ok = True
            else: d2ok = False
            # same for d1+d2
            if  (d1ok or d2ok) and moves[0] + dice.d1 + dice.d2 <= 24 and (curr_color == columns[moves[0] + dice.d1 + dice.d2].color or 0 <= columns[moves[0] + dice.d1 + dice.d2].size <= 1):
                moves.append(columns[moves[0] + dice.d1 + dice.d2])

# find available moves for black pucks        
def legal_moves_black():
    global home_black
    # color of curernt column 
    curr_color = columns[moves[0]].color
    if curr_color == "black" and dice.d1+dice.d2+dice.d3+dice.d4 > 0:
        # check if pucks can be collected
        if home_black:
            collecting_moves("black")
        # for doubles
        if dice.doubles:
            if 1 <= moves[0] - dice.d1 and (curr_color == columns[moves[0] - dice.d1].color or 0 <= columns[moves[0] - dice.d1].size <= 1):
                moves.append(columns[moves[0] - dice.d1])
                d1ok = True
            else: d1ok = False
            if d1ok and dice.d2 > 0 and 1 <= moves[0] - 2*dice.d1 and (curr_color == columns[moves[0] - 2*dice.d1].color or 0 <= columns[moves[0] - 2*dice.d1].size <= 1):
                moves.append(columns[moves[0] - 2*dice.d1])
                d2ok = True
            else: d2ok = False
            if d1ok and d2ok and dice.d3 > 0 and 1 <= moves[0] - 3*dice.d1 and (curr_color == columns[moves[0] - 3*dice.d1].color or 0 <= columns[moves[0] - 3*dice.d1].size <= 1):
                moves.append(columns[moves[0] - 3*dice.d1])
                d3ok = True
            else: d3ok = False
            if d1ok and d2ok and d3ok and dice.d4 > 0 and 1 <= moves[0] - 4*dice.d1 and (curr_color == columns[moves[0] - 4*dice.d1].color or 0 <= columns[moves[0] - 4*dice.d1].size <= 1):
                moves.append(columns[moves[0] - 4*dice.d1])
        else:
            #  not out of bounds         and source color = destination color                     or destination is empty or has 1 puck                       
            if dice.d1 > 0 and 1 <= moves[0] - dice.d1 and (curr_color == columns[moves[0] - dice.d1].color or 0 <= columns[moves[0] - dice.d1].size <= 1):
                moves.append(columns[moves[0] - dice.d1])
                d1ok = True
            else: d1ok = False
            # same for d2
            if dice.d2 > 0 and 1 <= moves[0] - dice.d2 and (curr_color == columns[moves[0] - dice.d2].color or 0 <= columns[moves[0] - dice.d2].size <= 1):
                moves.append(columns[moves[0] - dice.d2])
                d2ok = True
            else: d2ok = False
            # same for d1+d2
            if (d1ok or d2ok) and 1 <= moves[0] - dice.d1 - dice.d2 and (curr_color == columns[moves[0] - (dice.d1 + dice.d2)].color or 0 <= columns[moves[0] - (dice.d1 + dice.d2)].size <= 1):
                moves.append(columns[moves[0] - (dice.d1 + dice.d2)])

# removes used dice and calls legal_moves to get updated moves with remaining dice
def update_moves(dist, col_flag):
    if not dice.doubles:
        # moved by d1 or collected with a bigger number
        if dist == dice.d1 or (col_flag and dist > dice.d1 and dist > dice.d2 and dice.d1>=dice.d2):
            dice.d1 = 0
        elif dist == dice.d2 or (col_flag and dist > dice.d1 and dist > dice.d2 and dice.d2>dice.d1):
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
    legal_moves(active_col)

# highlight columns of possible moves
def show_moves():
    for j in moves[1:]:
        if 1<=j.number<=12:
            screen.blit(highlight_col_bot, (j.xpos, j.ypos))
        elif 13<=j.number<=24:
            screen.blit(highlight_col_top, (j.xpos, j.ypos))
        elif j.number == 30 or j.number == 60:
            screen.blit(highlight_tower, (j.xpos, j.ypos))

def turn_over():
    if dice.d1 == dice.d2 == dice.d3 == dice.d4 == 0:
        return True
    else:
        # checks for a possible move in every column and returns if even 1 is found
        for i in columns[1:25]:
            if current_turn == "white":
                if i.color == current_turn:
                    # checks if target is in legal range and if its free
                    if dice.d1 != 0 and 1 <= i.number + dice.d1 <= 24  and (columns[i.number+dice.d1].color == current_turn or columns[i.number+dice.d1].size <= 1):
                        return False
                    elif dice.d2 != 0 and 1 <= i.number + dice.d2 <= 24 and (columns[i.number+dice.d2].color == current_turn or columns[i.number+dice.d2].size <= 1):
                        return False
                    elif dice.d3 != 0 and 1 <= i.number + dice.d3 <= 24 and (columns[i.number+dice.d3].color == current_turn or columns[i.number+dice.d3].size <= 1):
                        return False
                    elif dice.d4 != 0 and 1 <= i.number + dice.d4 <= 24 and (columns[i.number+dice.d4].color == current_turn or columns[i.number+dice.d4].size <= 1):
                        return False
            else:
                if i.color == current_turn:# and i.size > 0:
                        if dice.d1 != 0 and 1 <= i.number - dice.d1 <= 24  and (columns[i.number-dice.d1].color == current_turn or columns[i.number-dice.d1].size <= 1):
                            return False
                        elif dice.d2 != 0 and 1 <= i.number - dice.d2 <= 24 and (columns[i.number-dice.d2].color == current_turn or columns[i.number-dice.d2].size <= 1):
                            return False
                        elif dice.d3 != 0 and 1 <= i.number - dice.d3 <= 24 and (columns[i.number-dice.d3].color == current_turn or columns[i.number-dice.d3].size <= 1):
                            return False
                        elif dice.d4 != 0 and 1 <= i.number - dice.d4 <= 24 and (columns[i.number-dice.d4].color == current_turn or columns[i.number-dice.d4].size <= 1):
                            return False
    dice.d1 = dice.d2 = dice.d3 = dice.d4 = 0
    return True

def home_check():
    sum_w = sum_b = 0
    global home_white, home_black
    # home is 1:6 and 19:24
    if gamemode == None or gamemode == 1:
        # check whites
        for w in columns[19:25]: # get columns 19-24
            if w.color == "white":
                sum_w += w.size
        if sum_w + white_tower.size == 15:
            home_white = True
        else: 
            home_white = False
        # check blacks
        for b in columns[1:7]: # get columns 1-6
            if b.color == "black":
                sum_b += b.size
        if sum_b + black_tower.size == 15:
            home_black = True
        else: 
            home_black = False
    # home is 1:8 and 17:24
    else:
        # check whites
        for w in columns[17:25]: # get columns 17-24
            if w.color == "white":
                sum_w += w.size
        if sum_w + white_tower.size == 15:
            home_white = True
        else: 
            home_white = False
        # check blacks
        for b in columns[1:9]: # get columns 1-8
            if b.color == "black":
                sum_b += b.size
        if sum_b + black_tower.size == 15:
            home_black = True
        else: 
            home_black = False

# check if game over
def game_over():
    if black_tower.size == 15 or white_tower.size == 15:
        return True
    return False

# columns array 
bot_light_y = 415
top_light_y = 60 

columns = [
    column(0, 485, 322),
    column(1, col1_x, bot_light_y), column(2, col1_x-(col_width+8.5), bot_light_y), column(3, col1_x-2*(col_width+8.5), bot_light_y), column(4, col1_x-3*(col_width+8.5), bot_light_y), column(5, col1_x-4*(col_width+8.5), bot_light_y), column(6, col1_x-5*(col_width+8.5), bot_light_y),
    column(7, col7_x, bot_light_y), column(8, col7_x-(col_width+8.5), bot_light_y), column(9, col7_x-2*(col_width+8.5), bot_light_y), column(10, col7_x-3*(col_width+8.5), bot_light_y), column(11, col7_x-4*(col_width+8.5), bot_light_y), column(12, col7_x-5*(col_width+8.5), bot_light_y),
    column(13, col7_x-5*(col_width+8.5), top_light_y), column(14, col7_x-4*(col_width+8.5), top_light_y), column(15, col7_x-3*(col_width+8.5), top_light_y), column(16, col7_x-2*(col_width+8.5), top_light_y), column(17, col7_x-(col_width+8.5), top_light_y), column(18, col7_x, top_light_y),
    column(19, col1_x-5*(col_width+8.5), top_light_y), column(20, col1_x-4*(col_width+8.5), top_light_y), column(21, col1_x-3*(col_width+8.5), top_light_y), column(22, col1_x-2*(col_width+8.5), top_light_y), column(23, col1_x-(col_width+8.5), top_light_y), column(24, col1_x, top_light_y),
    column(25, 485, 398)
]

white_tower = column(60,958,29)
black_tower = column(30,958,424)

columns[0].color = white_tower.color = "white"
columns[25].color = black_tower.color = "black"

# initialize columns with pucks
columns[1].add_piece(whites[0]); columns[1].add_piece(whites[1])
columns[6].add_piece(blacks[0]); columns[6].add_piece(blacks[1]); columns[6].add_piece(blacks[2]); columns[6].add_piece(blacks[3]); columns[6].add_piece(blacks[4])
columns[8].add_piece(blacks[5]); columns[8].add_piece(blacks[6]); columns[8].add_piece(blacks[7])
columns[12].add_piece(whites[2]); columns[12].add_piece(whites[3]); columns[12].add_piece(whites[4]); columns[12].add_piece(whites[5]); columns[12].add_piece(whites[6])
columns[13].add_piece(blacks[8]); columns[13].add_piece(blacks[9]); columns[13].add_piece(blacks[10]); columns[13].add_piece(blacks[11]); columns[13].add_piece(blacks[12])
columns[17].add_piece(whites[7]); columns[17].add_piece(whites[8]); columns[17].add_piece(whites[9])
columns[19].add_piece(whites[10]); columns[19].add_piece(whites[11]); columns[19].add_piece(whites[12]); columns[19].add_piece(whites[13]); columns[19].add_piece(whites[14])
columns[24].add_piece(blacks[13]); columns[24].add_piece(blacks[14])

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

    # print messages in border
    out = font.render("playing: " + current_turn,True,(0,255,0), (150,150,150))
    rollinfo = font.render("d1: " + str(dice.d1) + "\nd2: " + str(dice.d2), True,(0,255,0))
    screen.blit(out, (400, 800))
    screen.blit(rollinfo, (600, 800))

    whome = font.render("white: " + str(home_white) + "   tower sz: " + str(white_tower.size), True,(0,255,0))
    bhome = font.render("black: " + str(home_black) + "   tower sz: " + str(black_tower.size), True,(0,255,0))
    screen.blit(whome, (800, 800))
    screen.blit(bhome, (800, 820))

    # set up pieces on board
    for i in reversed(whites):
        screen.blit(i.image, (i.x_coord, i.y_coord))
    for i in blacks:
        screen.blit(i.image, (i.x_coord, i.y_coord))
    for i in collected:
        screen.blit(i.image, (i.x_coord, i.y_coord))

    # screen.blit(roll_button, (bxpos,bypos))

    # when turn is over show roll button until pressed
    if turn_over():
        # change roll button on hover
        if (bxpos <= mouse[0] <= bxpos + bwidth) and (bypos <= mouse[1] <= bypos + bheight):
            screen.blit(active_roll_button, (bxpos,bypos))
            # roll on click and start new turn
            if click[0] == 1:
                roll(dice)
                print(dice.d1, dice.d2, dice.d3, dice.d4) #debug
                moves.clear
                moves.append(-1)
        else:
            screen.blit(roll_button, (bxpos, bypos))

    # a player is playing
    else:
        # in case current player has hit pucks
        if (columns[0].size > 0 and current_turn == "white") or (columns[25].size > 0 and current_turn == "black"):
            if current_turn == "white":
                active_col = 0
            else:
                active_col = 25
            show_moves_flag = True
            legal_moves(active_col)
            if show_moves_flag and len(moves) > 1:
                # listen for mouse click to place hit puck
                if event.type == pg.MOUSEBUTTONDOWN:
                    pg.time.wait(100)
                    for j in moves[1:]:
                        if j.xpos <= mouse[0] <= j.xpos + col_width and j.ypos <= mouse[1] <= j.ypos + col_height:
                            move(columns[moves[0]], columns[j.number])
                            update_moves(abs(moves[0]-j.number), False)
                            show_moves_flag = False
                            active_col = j.number

        # listen for mouse click on column to show available moves
        elif event.type == pg.MOUSEBUTTONDOWN:
            pg.time.wait(100)
            if ((white_tower.xpos <= mouse[0] <= white_tower.xpos+col_width) and (white_tower.ypos <= mouse[1] <= white_tower.ypos+col_height)):
                active_col = white_tower.number
            elif ((black_tower.xpos <= mouse[0] <= black_tower.xpos+col_width) and (black_tower.ypos <= mouse[1] <= black_tower.ypos+col_height)):
                active_col = black_tower.number
            for i in columns:
                # check mouse in columns
                if (i.xpos <= mouse[0] <= i.xpos+col_width) and (i.ypos <= mouse[1] <= i.ypos+col_height):
                    active_col = i.number 

                    if show_moves_flag and active_col == moves[0]:
                        show_moves_flag = False
                    elif not show_moves_flag and active_col == moves[0]:
                        show_moves_flag = True
                    else:                        
                        # check if player clicked a valid move from the moves list
                        if show_moves_flag and len(moves) > 1:
                            # moved = False
                            for j in moves[1:]:
                                if j.xpos <= mouse[0] <= j.xpos + col_width and j.ypos <= mouse[1] <= j.ypos + col_height:
                                    # print(j.number) #debug
                                    if j.number == 30:# and not moved: # black
                                        print("moves[0] sent to move before collecting", moves[0])
                                        move(columns[moves[0]], black_tower) # was move()
                                        print("moves[0] sent to update moves after collecting", moves[0])
                                        update_moves(moves[0], True)
                                        # active_col = -1
                                    elif j.number == 60:# and not moved: # white
                                        print("moves[0] sent to move before collecting", moves[0])
                                        move(columns[moves[0]], white_tower) # was move()
                                        print("25-moves[0] sent to update moves after collecting", 25-moves[0])
                                        update_moves(25-moves[0], True)
                                        # active_col = -1
                                    elif j.number <= 25:
                                        move(columns[moves[0]], columns[j.number]) # was move()
                                        update_moves(abs(moves[0]-j.number), False)
                                        active_col = temp_col

                        if 0<=active_col<=25:
                            legal_moves(active_col)
                            show_moves_flag = True
                            temp_col = active_col 
                        else: 
                            legal_moves(-1) 
                            show_moves_flag = False

        if show_moves_flag and not turn_over():
            show_moves()
            columns[active_col].highlight_puck()

        elif not show_moves_flag:
            unhilight_pucks("all") 
        # change player turn
        if not game_over():
            if turn_over() and current_turn == "white":
                current_turn = "black"
                unhilight_pucks("all")
                show_moves_flag = False
            elif turn_over() and current_turn == "black":
                current_turn = "white"
                unhilight_pucks("all")
                show_moves_flag = False
        else:
            screen.blit(font.render(current_turn + "wins", True,(0,255,0)), (250, 830))
















    pg.display.update()
    