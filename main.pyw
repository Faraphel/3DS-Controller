from tkinter import *
import socket
from threading import Thread
from PIL import Image, ImageTk, ImageGrab
import os
from pynput import mouse
import time
import pyvjoy

STOP = False

class AppClass():
    def __init__(self):
        self.root = Tk()
        self.root.title("3DS Controller - Faraphel")
        self.root.resizable(False, False)
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # Internet & UDP
        self.port = 8889
        self.key = []
        self.tick = 20
        self.widget_3DS = []
        self.WIN_p1, self.WIN_p2 = (0, 0), (self.root.winfo_screenwidth(), self.root.winfo_screenheight())
        self.mouse = mouse.Controller()

        self.img = {}
        self.imgtk = {}
        for name in os.listdir("./assets/"):
            name = os.path.splitext(name)[0]
            self.img[name] = Image.open(f"./assets/{name}.png")
            self.imgtk[name] = ImageTk.PhotoImage(self.img[name])

        self.Canvas3DS = Canvas(self.root, width=self.img["3DS"].width, height=self.img["3DS"].height)
        self.Canvas3DS.grid(row = 1, column = 1, columnspan = 4)
        
        w, h = self.img["3DS"].width, self.img["3DS"].height
        self.Canvas3DS.create_image(w//2, h//2, image=self.imgtk["3DS"])

        self.label_coordinate = Label(self.root, text="???")
        self.label_coordinate.grid(row = 2, column = 1, sticky = "NEWS")

        self.button_option = Button(self.root, text = "Paramètre", relief = RIDGE, command = self.option_menu)
        self.button_option.grid(row = 2, column = 3, sticky = "EW")

        self.button_option = Button(self.root, text="Quitter", relief=RIDGE, command=self.root.destroy)
        self.button_option.grid(row=2, column=4, sticky="EW")


        self.connect()
        self.root.after(self.tick, self.update_tk)
        self.root.mainloop()


    def option_menu(self):
        optionTL = Toplevel()

        Label(optionTL, text="IP : ").grid(row=1, column=1)
        
        option_ip = Listbox(optionTL, height = 3)
        for ip in socket.gethostbyname_ex(socket.gethostname())[-1]: option_ip.insert(0, ip)
        option_ip.grid(row=1, column=2)


        def get_borderpoint():
            global screentk
            
            screen = ImageGrab.grab()
            screen = screen.convert("L")
            screentk = ImageTk.PhotoImage(screen)

            borderpointTL = Toplevel()
            borderpointTL.overrideredirect(1)
            borderpointTL.geometry(f"{screen.width}x{screen.height}")

            borderpointCvn = Canvas(borderpointTL, borderwidth=0, width=screen.width, height=screen.height)
            borderpointCvn.grid(row=1, column=1, sticky="NEWS")
            screenID = borderpointCvn.create_image(screen.width // 2, screen.height // 2, image = screentk)

            cache_cvn1 = []
            cache_cvn2 = []
            
            def point1(event):
                nonlocal cache_cvn1
                for ID in cache_cvn1:
                    borderpointCvn.delete(ID)
                cache_cvn1 = []
                    
                cache_cvn1.append( borderpointCvn.create_rectangle(event.x-10, event.y-1, event.x+10, event.y+1, fill="red") )
                cache_cvn1.append( borderpointCvn.create_rectangle(event.x-1, event.y-10, event.x+1, event.y+10, fill="red") )
                self.WIN_p1 = (event.x, event.y)
                connect()

            def point2(event):
                nonlocal cache_cvn2
                for ID in cache_cvn2:
                    borderpointCvn.delete(ID)
                cache_cvn2 = []
                cache_cvn2.append( borderpointCvn.create_rectangle(event.x-10, event.y-1, event.x+10, event.y+1, fill="green") )
                cache_cvn2.append( borderpointCvn.create_rectangle(event.x-1, event.y-10, event.x+1, event.y+10, fill="green") )
                self.WIN_p2 = (event.x, event.y)
                connect()

            def connect():
                if cache_cvn1 and cache_cvn2:
                    ID1 = borderpointCvn.create_rectangle(self.WIN_p1[0], self.WIN_p1[1], self.WIN_p2[0], self.WIN_p2[1], outline="red")
                    ID2 = borderpointCvn.create_rectangle(screen.width - 150, screen.height - 70, screen.width - 10, screen.height - 10, fill = "pink")
                    ID3 = borderpointCvn.create_text(screen.width - 80, screen.height - 40, text = "Confirmer", fill = "black", font = ("Purisa", "18"))
                    
                    cache_cvn1.extend([ID1, ID2, ID3])
                    cache_cvn2.extend([ID1, ID2, ID3])

                    borderpointCvn.tag_bind(ID2, "<Button-1>", confirm)
                    borderpointCvn.tag_bind(ID3, "<Button-1>", confirm)

            def confirm(event):
                borderpointTL.destroy()
                option_label_borderpoint.config(text = f"({self.WIN_p1[0]}, {self.WIN_p1[1]}; {self.WIN_p2[0]}, {self.WIN_p2[1]})")

            borderpointCvn.tag_bind(screenID, "<Button-1>", point1)
            borderpointCvn.bind("<Button-3>", point2)
            
            

        option_borderpoint = Button(optionTL, text="Définir les bordures de l'écran tactile", relief=RIDGE, command = get_borderpoint)
        option_borderpoint.grid(row=2, column=1)

        option_label_borderpoint = Label(optionTL, text = f"({self.WIN_p1[0]}, {self.WIN_p1[1]}; {self.WIN_p2[0]}, {self.WIN_p2[1]})")
        option_label_borderpoint.grid(row=2, column=2)
        


    def connect(self):
        self.socket.bind(("", self.port))
        self.vjoy = pyvjoy.VJoyDevice(1)
    
        self.recvThread = Thread(target=self.recv)
        self.recvThread.setDaemon(True)
        self.recvThread.start()


    def update_tk(self):
        while True:
            ox, oy = 0, 0
            widget_3DS = []
            
            if self.key:
                if "L" in self.key: widget_3DS.append( self.Canvas3DS.create_image(30, 234, image=self.imgtk["L"]) )
                if "R" in self.key: widget_3DS.append( self.Canvas3DS.create_image(429, 234, image=self.imgtk["R"]) )

                if "X" in self.key: widget_3DS.append( self.Canvas3DS.create_image(396, 292, image=self.imgtk["X"]) )
                if "Y" in self.key: widget_3DS.append( self.Canvas3DS.create_image(371, 318, image=self.imgtk["Y"]) )
                if "A" in self.key: widget_3DS.append( self.Canvas3DS.create_image(422, 318, image=self.imgtk["A"]) )
                if "B" in self.key: widget_3DS.append( self.Canvas3DS.create_image(395, 344, image=self.imgtk["B"]) )

                if "+Left" in self.key: widget_3DS.append( self.Canvas3DS.create_image(78, 395, image=self.imgtk["hl"]) )
                elif "+Right" in self.key: widget_3DS.append( self.Canvas3DS.create_image(45, 395, image=self.imgtk["hl"]) )
                elif "+Up" in self.key: widget_3DS.append( self.Canvas3DS.create_image(61, 378, image=self.imgtk["vl"]) )
                elif "+Down" in self.key: widget_3DS.append( self.Canvas3DS.create_image(61, 412, image=self.imgtk["vl"]) )

                elif "Select" in self.key: widget_3DS.append( self.Canvas3DS.create_image(158, 446, image=self.imgtk["SELECT"]) )
                elif "Start" in self.key: widget_3DS.append( self.Canvas3DS.create_image(299, 446, image=self.imgtk["START"]) )

                if "oLeft" in self.key: ox = 10
                elif "oRight" in self.key: ox = -10

                if "oUp" in self.key: oy = -10
                elif "oDown" in self.key: oy = 10

            widget_3DS.append( self.Canvas3DS.create_image(63+ox, 312+oy, image=self.imgtk["joystick"]) )

            if "Tap" in self.key:
                DS_X = 122 + (212 / 314) * self.screenX
                DS_Y = 264 + (161 / 117) * self.screenY
                widget_3DS.append( self.Canvas3DS.create_rectangle(DS_X-2, DS_Y-2, DS_X+2, DS_Y+2, outline = "red") )
                self.label_coordinate.config(text = f"x={self.screenX}, y={self.screenY}")

                WIN_X = self.WIN_p1[0] + ((self.WIN_p2[0]-self.WIN_p1[0]) / 314) * self.screenX
                WIN_Y = self.WIN_p1[1] + ((self.WIN_p2[1]-self.WIN_p1[1]) / 117) * self.screenY
                self.mouse.position = (WIN_X, WIN_Y)
                self.mouse.press(mouse.Button.left)

            else:
                self.mouse.release(mouse.Button.left)


            for widget in self.widget_3DS: self.Canvas3DS.delete(widget)
            self.widget_3DS = widget_3DS

            self.Canvas3DS.update()
        

    def update_key(self): pass


    def recv(self):
        while not(STOP):
            data, addr = self.socket.recvfrom(512)
            b = bin(int(data.hex(), base=16))[2:]

            self.screenX = int(b[104] + b[89:97], base=2)
            self.screenY = int(b[105:112], base=2)

            key = []
            
            if b[52] == "1": key.append("oLeft")
            if b[51] == "1": key.append("oRight")
            if b[50] == "1": key.append("oUp")
            if b[49] == "1": key.append("oDown")
            
            if b[44] == "1": key.append("Tap")
            
            if b[40] == "1": key.append("R")
            if b[39] == "1": key.append("L")

            if b[38] == "1": key.append("X")
            if b[37] == "1": key.append("Y")
            if b[32] == "1": key.append("A")
            if b[31] == "1": key.append("B")
            
            if b[30] == "1": key.append("Select")
            if b[29] == "1": key.append("Start")
            
            if b[28] == "1": key.append("+Left")
            if b[27] == "1": key.append("+Right")
            if b[26] == "1": key.append("+Up")
            if b[25] == "1": key.append("+Down")

            if b[8] == "1": key.append("Keyboard")
     
            self.key = key

            
            for key in winKey:
                if key in self.key:
                    if winKey[key][0] == "k":
                        self.vjoy.set_button(winKey[key][1], 1)

                else:
                    if winKey[key][0] == "k":
                        self.vjoy.set_button(winKey[key][1], 0)


  

winKey = {
    "oLeft": ("k", 1),
    "oRight": ("k", 2),
    "oUp": ("k", 3),
    "oDown": ("k", 4),

    "R": ("k", 5),
    "L": ("k", 6),
    "A": ("k", 7),
    "B": ("k", 8),
    "X": ("k", 9),
    "Y": ("k", 10),

    "Select": ("k", 11),
    "Start": ("k", 12),

    "+Left": ("k", 13),
    "+Right": ("k", 14),
    "+Up": ("k", 15),
    "+Down": ("k", 16),
}

App = AppClass()
STOP = True
