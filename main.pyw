from tkinter import *
import socket
from threading import Thread
from PIL import Image, ImageTk
import os
import pyautogui
import time

class AppClass():
    def __init__(self):
        self.root = Tk()
        self.root.title("3DS Controller - Faraphel")
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # Internet & UDP
        self.updateThread = None
        self.port = 8889
        self.key = []
        self.old_key = []
        self.tick = 20

        self.img = {}
        self.imgtk = {}
        for name in os.listdir("./assets/"):
            name = os.path.splitext(name)[0]
            self.img[name] = Image.open(f"./assets/{name}.png")
            self.imgtk[name] = ImageTk.PhotoImage(self.img[name])
        
        self.Canvas3DS = Canvas(self.root, width=self.img["3DS"].width, height=self.img["3DS"].height)
        self.Canvas3DS.grid(row = 1, column = 1)

        
        self.connect()
        self.root.after(self.tick, self.update)
        mainloop()


    def connect(self):
        self.socket.bind(("", self.port))

        self.updateThread = Thread(target=self.recv)
        self.updateThread.setDaemon(True)
        self.updateThread.start()


    def update(self):
        self.Canvas3DS.delete(ALL)
        w, h = self.img["3DS"].width, self.img["3DS"].height
        self.Canvas3DS.create_image(w//2, h//2, image=self.imgtk["3DS"])

        if "L" in self.key: self.Canvas3DS.create_image(30, 234, image=self.imgtk["L"])
        if "R" in self.key: self.Canvas3DS.create_image(429, 234, image=self.imgtk["R"])
        
        if "X" in self.key: self.Canvas3DS.create_image(396, 292, image=self.imgtk["X"])
        if "Y" in self.key: self.Canvas3DS.create_image(371, 318, image=self.imgtk["Y"])
        if "A" in self.key: self.Canvas3DS.create_image(422, 318, image=self.imgtk["A"])
        if "B" in self.key: self.Canvas3DS.create_image(395, 344, image=self.imgtk["B"])

        if "+Left" in self.key: self.Canvas3DS.create_image(78, 395, image=self.imgtk["hl"])
        elif "+Right" in self.key: self.Canvas3DS.create_image(45, 395, image=self.imgtk["hl"])
        elif "+Up" in self.key: self.Canvas3DS.create_image(61, 378, image=self.imgtk["vl"])
        elif "+Down" in self.key: self.Canvas3DS.create_image(61, 412, image=self.imgtk["vl"])

        if "oLeft" in self.key: ox = 10
        elif "oRight" in self.key: ox = -10
        else: ox = 0

        if "oUp" in self.key: oy = -10
        elif "oDown" in self.key: oy = 10
        else: oy = 0
        
        self.Canvas3DS.create_image(63+ox, 312+oy, image=self.imgtk["joystick"])
        self.root.after(self.tick, self.update)

        
    
    def recv(self):
        while True:
            data, addr = self.socket.recvfrom(512)
            b = bin(int(data.hex(), base=16))[2:]

            key = []
            
            for i, c in enumerate(b):
                if i in Key and c == "1":
                    key.append(Key[i])

            if self.key != key:
                t1 = time.time()
                self.old_key = self.key
                self.key = key
                for key in winKey:
                    if key in self.key:
                        if winKey[key][0] == "k":
                            pyautogui.keyDown(winKey[key][1])

                
                    elif key in self.old_key:
                        if winKey[key][0] == "k":
                            pyautogui.keyUp(winKey[key][1])

                print(t1 - time.time())


        


Key = {
    52: "oLeft", 51: "oRight", 50: "oUp", 49: "oDown",
    40: "R", 39: "L",
    38: "X", 37: "Y", 32: "A", 31: "B",
    30: "Select", 29: "Start",
    28: "+Left", 27: "+Right", 26: "+Up", 25: "+Down",
    8: "Keyboard"
}

winKey = {
    "oLeft": ("k", "o"),
    "oRight": ("k", "p"),
    "oUp": ("k", "k"),
    "oDown": ("k", "m"),
    
    "R": ("k", "r"),
    "L": ("k", "l"),
    "A": ("k", "a"),
    "B": ("k", "b"),
    "X": ("k", "x"),
    "Y": ("k", "y"),

    "Select": ("k", "i"),
    "Start": ("k", "s"),

    "+Left": ("k", "right"),
    "+Right": ("k", "left"),
    "+Up": ("k", "up"),
    "+Down": ("k", "down"),
}

App = AppClass()
