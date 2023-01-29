from PIL import ImageGrab, ImageTk
import tkinter as tk
import time,pip


pip.main(['install','--user','chess','cairosvg','pyautogui','Pillow','Stockfish'])

def scanBoard(name=''):
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
        saveimg = scrShot.crop(canvas.coords([rect_id]))
        saveimg.save('pieces/' + name + ".png", 'PNG')
        window.destroy()
        time.sleep(1.5)

    try:
        window = tk.Tk()
        window.title(name)
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

def get_files():
    for file in piece_names.keys():
        scanBoard(file)
        time.sleep(1)

