import tkinter as tk
from tkinter import ttk
import threading,time,chessbot
from functools import wraps
from PIL import Image, ImageTk

def memoize(func): # optimizing the code to work faster with saving cache
    cache = {}
    @wraps(func)
    def wrapper(*args,**kwargs):
        key = str(args) + str(kwargs)

        if key not in cache:
            cache[key] = func(*args,**kwargs)
        return cache[key]
    return wrapper


class mainScr(tk.Tk):   # the main tk window

    def __init__(self):
        super().__init__()
        self.mainPage = tk.Frame(self,bg = 'Ghost White',width=450,height=450)  #Main frame
        self.chessboardl = tk.Label(self.mainPage,image=self.returnimg(r"Board/chessboardpng.png"))#the lable that holds the board image
        self.autoup = threading.Thread(name='autoupdate',target=self.updatebestmove,daemon=True) #running thread to contantly update the image while using the cheat mode
        self.bthread = threading.Thread(name='updatingboard',target=self.updateboardimg,daemon=True) # running thread to update the image inside the label



        self.var1 = tk.IntVar() #storing the value of the checkbox
        self.container = tk.Label(self.mainPage)
        self.addbtn = tk.Button(self.container,text='add move',command=self.mmoves)
        self.scnbtn = tk.Button(self.container,text='Scan',command=lambda:chessbot.updateboard())
        self.combobx = ttk.Combobox(self.container,values=["White","Black"])
        self.bestmov = tk.Label(self.container,text='')
        self.tickauto = tk.Checkbutton(self.container,variable=self.var1)
        self.bestmovbtn = tk.Button(self.container,text='Cheat',command=self.bestmove)
        self.mainPage.grid()

        #grid the objects
        self.combobx.grid(row=0,column=0)
        self.tickauto.grid(row=0,column=1)
        self.bestmov.grid(row=0,column=2)
        self.scnbtn.grid(row=0,column=3)
        self.addbtn.grid(row=0,column=4)
        self.bestmovbtn.grid(row=0,column=5)


        self.container.grid(row=1,column=0)
        self.chessboardl.grid(row=0,column=0)
        self.autoup.start()
        self.bthread.start()

# Returnds an ImageTk photo from the specified path
    def returnimg(self,fpath):
        self.opemimg = Image.open(fpath)
        tkimg = ImageTk.PhotoImage(self.opemimg)
        return tkimg

    def mmoves(self): #saving new moves to the text file

        def writef(fen, move):
            with open("moves/mainmoves.txt", "a") as mf:
                mf.write(f'\n' + fen + ' : ' + move)

        def showf():
            with open('moves/mainmoves.txt', "r") as mf:
                for x in mf:
                    print(x)

        mwin = tk.Toplevel()
        fen = tk.Entry(mwin, width=25)
        move = tk.Entry(mwin, width=25)
        tk.Button(mwin, text='Show', command=showf).grid(row=2, column=1)
        tk.Button(mwin, text='Update', command=lambda: writef(fen.get(), move.get())).grid(row=2, column=0)
        fen.grid(row=0, column=0)
        move.grid(row=1, column=0)

    def bestmove(self):
        x = chessbot.cheating()
        self.bestmov.configure(text=x)
        print(x)

    @memoize
    def updateboardimg(self):
        while True: # automatically  refreshes the image inside the label
            try:
                xfile = self.returnimg(r"Board/chessboardpng.png")
                self.chessboardl.configure(image=xfile)
                self.chessboardl.image = xfile
            except:
                pass
            time.sleep(0.5)

    def updatebestmove(self):
        while True:  #using a thread to constantly check if the tickbox is marked
            while self.var1.get()  == 1:

                x = chessbot.cheating()
                self.bestmov.configure(text=x)
                time.sleep(7)

            time.sleep(0.5)

if __name__ == "__main__":
    app = mainScr()
    app.attributes('-topmost',True)
   # subprocess.Popen(['python', 'chessbot.py'])
    app.mainloop()
