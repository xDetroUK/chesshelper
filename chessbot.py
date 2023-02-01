# packages
import chess,cairosvg,chess.svg,time
import chess.engine
from stockfish import Stockfish
import pyautogui as pg
from PIL import ImageGrab,ImageTk
import tkinter as tk

croploc = [] # saves the cordinates from the function scan board
# constants (modify if needed)
CONFIDENCE = 0.8 # the confidence level for pyauto recognize
DETECTION_NOICE_THRESHOLD = 12 #noice detection
PIECES_PATH = './pieces/' # pieces location

def scanBoard():
    scrShot = ImageGrab.grab()
    topx, topy, botx, boty = 0, 0, 0, 0

    def get_mouse_posn(event):
        global topy, topx
        topx, topy = event.x, event.y

    def update_sel_rect(event):
        global topy, topx, botx, boty
        botx, boty = event.x, event.y
        canvas.coords(rect_id, topx, topy, botx, boty)  # Update selection rect.

    def finalImage(event):
        croploc.append(canvas.coords([rect_id]))
        window.destroy()

    try:
        window = tk.Tk()
        window.attributes('-fullscreen',True)
        img = ImageTk.PhotoImage(scrShot)
        canvas = tk.Canvas(window, width=img.width(), height=img.height(),
                           borderwidth=0, highlightthickness=0)
        canvas.pack(expand=True)
        canvas.img = img  # Keep reference in case this code is put into a function.
        canvas.create_image(0, 0, image=img, anchor=tk.NW)
        rect_id = canvas.create_rectangle(topx, topy, topx, topy, dash=(2, 2), fill='', outline='white')
        canvas.bind('<Button-1>', get_mouse_posn)  # blind to mouse left click
        canvas.bind('<B1-Motion>', update_sel_rect)  # detects the motion of the mouse
        canvas.bind("<ButtonRelease-1>", finalImage)  # if left button is released
        window.mainloop()

    except:
        pass

if not croploc:
    scanBoard()

BOARD_SIZE = 840 #895 works best so far
CELL_SIZE = int(BOARD_SIZE / 8)
BOARD_TOP_COORD = croploc[0][1] # the cordinate of top corner from the screenshot taken
BOARD_LEFT_COORD = croploc[0][0] #

# players
WHITE = 0
BLACK = 1   #currently the black side doesn't work with cheating function, displays wrong side of the board

# side to move
side_to_move = 0

# read argv if available

# square to coords
square_to_coords = []

# array to convert board square indices to coordinates (black)
get_square = [
    'a8', 'b8', 'c8', 'd8', 'e8', 'f8', 'g8', 'h8',
    'a7', 'b7', 'c7', 'd7', 'e7', 'f7', 'g7', 'h7',
    'a6', 'b6', 'c6', 'd6', 'e6', 'f6', 'g6', 'h6',
    'a5', 'b5', 'c5', 'd5', 'e5', 'f5', 'g5', 'h5',
    'a4', 'b4', 'c4', 'd4', 'e4', 'f4', 'g4', 'h4',
    'a3', 'b3', 'c3', 'd3', 'e3', 'f3', 'g3', 'h3',
    'a2', 'b2', 'c2', 'd2', 'e2', 'f2', 'g2', 'h2',
    'a1', 'b1', 'c1', 'd1', 'e1', 'f1', 'g1', 'h1'
]

# map piece names to FEN chars
piece_names = {
    'black_king': 'k',
    'black_queen': 'q',
    'black_rook': 'r',
    'black_bishop': 'b',
    'black_knight': 'n',
    'black_pawn': 'p',
    'white_knight': 'N',
    'white_pawn': 'P',
    'white_king': 'K',
    'white_queen': 'Q',
    'white_rook': 'R',
    'white_bishop': 'B'
}

def timing(f): # python wrap to check how long does it take for a function to execute, using it try to speed up recognition process
    def wrap(*args, **kwargs):
        time1 = time.time()
        ret = f(*args, **kwargs)
        time2 = time.time()
        print('{:s} function took {:.3f} ms'.format(
            f.__name__, (time2-time1)*1000.0))

        return ret
    return wrap


#returns screenshot of the display using PIL and croping the selectede area  croploc[0] has saved cordinates from scanboard function
def scrshotfunc():
    scrn = ImageGrab.grab()
    cropscrn = scrn.crop(croploc[0])
    return cropscrn

# get coordinates of chess pieces
@timing
def recognize_position():
    # piece locations
    piece_locations = {
        'black_king': [],
        'black_queen': [],
        'black_rook': [],
        'black_bishop': [],
        'black_knight': [],
        'black_pawn': [],
        'white_knight': [],
        'white_pawn': [],
        'white_king': [],
        'white_queen': [],
        'white_rook': [],
        'white_bishop': []
    }

    # # loop over piece names
    for piece in piece_names.keys():
        # store piece locations
        for location in pg.locateAllOnScreen(PIECES_PATH + piece + '.png', confidence=CONFIDENCE):
            # false detection flag
            noise = False

            # loop over matched pieces
            for position in piece_locations[piece]:
                # noice detection
                if abs(position.left - location.left) < DETECTION_NOICE_THRESHOLD and \
                        abs(position.top - location.top) < DETECTION_NOICE_THRESHOLD:
                    noise = True
                    break

            # skip noice detections
            if noise: continue

            # detect piece
            piece_locations[piece].append(location)
        #    print('detecting:', piece, location)
    # return piece locations
    return piece_locations


# convert piece coordinates to FEN string

def locations_to_fen(piece_locations):
    # FEN string
    fen = ''

    # board top left corner coords
    x = BOARD_LEFT_COORD
    y = BOARD_TOP_COORD

    # loop over board rows
    for row in range(8):
        # empty square counter
        empty = 0

        # loop over board columns
        for col in range(8):
            # init square
            square = row * 8 + col

            # piece detection
            is_piece = ()

            # loop over piece types
            for piece_type in piece_locations.keys():
                # loop over pieces
                for piece in piece_locations[piece_type]:
                    if abs(piece.left - x) < DETECTION_NOICE_THRESHOLD and \
                            abs(piece.top - y) < DETECTION_NOICE_THRESHOLD:
                        if empty:
                            fen += str(empty)
                            empty = 0

                        fen += piece_names[piece_type]
                        is_piece = (square, piece_names[piece_type])

            if not len(is_piece):
                empty += 1

            # increment x coord by cell size
            x += CELL_SIZE

        if empty: fen += str(empty)
        if row < 7: fen += '/'

        # restore x coord, increment y coordinate by cell size
        x = BOARD_LEFT_COORD
        y += CELL_SIZE

    # add side to move to fen
    fen += ' ' + 'b' if side_to_move else ' w'

    # add placeholders (NO EN PASSANT AND CASTLING are static placeholders)
    fen += ' KQkq - 0 1'

    # return FEN string
    return fen

# board top left corner coords
x = BOARD_LEFT_COORD
y = BOARD_TOP_COORD

# loop over board rows

for row in range(8):
    # loop over board columns
    for col in range(8):
        # init square
        square = row * 8 + col

        # associate square with square center coordinates
        square_to_coords.append((int(x + CELL_SIZE / 2), int(y + CELL_SIZE / 2)))

        # increment x coord by cell size
        x += CELL_SIZE

    # restore x coord, increment y coordinate by cell size
    x = BOARD_LEFT_COORD
    y += CELL_SIZE

def updateboard():  # Updating the board image after scaning the display with fen function
        fen = locations_to_fen(recognize_position()) # using location function together with recognize function to get the fen of the board
        print(fen,'\n')
        try: # writing the image as svg using chess module
            with open(f'Board/chessboardsvg.svg','w') as fh:
                fh.write(chess.svg.board(chess.Board(fen)))
                cairosvg.svg2png(url="Board/chessboardsvg.svg", write_to="Board/chessboardpng.png")#converting the svg to png file so it can be displayed inside tkinter, tkinter SVG doesn't display the pieces
        except:
            pass

def cheating():
        try:
            stockf = Stockfish(path="stockfish/stockfish-windows.exe", depth=10,
                               parameters={"Threads": 1, "Minimum Thinking Time": 2}) #seting up stockfish parameters

            fen = locations_to_fen(recognize_position())
            stockf.set_fen_position(fen) # setting the fen to stockfish
            x = stockf.get_best_move() # getting the best move
            curboard = chess.Board(fen=fen) #using chess module to re-create chessboard
            try:
                with open(f'Board/chessboardsvg.svg', 'w') as fh:
                    fh.write(chess.svg.board(curboard, lastmove=chess.Move.from_uci(x))) # the last played move
                    cairosvg.svg2png(url="Board/chessboardsvg.svg", write_to="Board/chessboardpng.png")
                    stockf.reset_engine_parameters() # reseting the engine at the end so it doesn't crash

                    with chess.engine.SimpleEngine.popen_uci("stockfish/stockfish-windows.exe") as ws:
                        info = ws.analyse(curboard, chess.engine.Limit(time=0.2))
                        f = info["score"].relative.cp

                return x,f,fen
            except:
                pass


        except Exception as e:
            print(e)

