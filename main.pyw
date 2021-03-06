from tkinter import *
from tkinter import colorchooser, messagebox
import socket
from threading import Thread
from PIL import Image, ImageTk, ImageGrab
import os, sys
from pynput import mouse
import requests
import time
import pyvjoy
import json
import zipfile

VERSION_FILE_URL = "https://raw.githubusercontent.com/Faraphel/3DS-Controller/master/version"
def check_update():
    try:
        gitversion = requests.get(VERSION_FILE_URL, allow_redirects=True).json()
        with open("version", "rb") as f:
            locversion = json.load(f)

        if gitversion["version"] != locversion["version"]:
            if messagebox.askyesno("Mise à jour disponible !", "Une mise à jour est disponible, souhaitez-vous l'installer ?\n\n"+ \
                                f"Version : {locversion['version']}.{locversion['subversion']} -> {gitversion['version']}.{gitversion['subversion']}\n"+\
                                f"Changelog :\n{gitversion['changelog']}"):

                if not(os.path.exists("./Updater/Updater.exe")):
                    dl = requests.get(gitversion["updater_bin"], allow_redirects=True)
                    with open("./download.zip", "wb") as file:
                        print(f"Téléchargement de Updater en cours...")
                        file.write(dl.content)
                        print("fin du téléchargement, début de l'extraction...")

                    with zipfile.ZipFile("./download.zip") as file:
                        file.extractall("./Updater/")
                        print("fin de l'extraction")

                    os.remove("./download.zip")
                    print("lancement de l'application...")
                    os.startfile(os.path.realpath("./Updater/Updater.exe"))
                    sys.exit()

    except Exception as e:
        print(e)


class AppClass():
    def __init__(self):
        self.root = Tk()
        self.STOP = False
        self.root.title("3DS Controller - Faraphel")
        self.root.resizable(False, False)
        try: self.root.iconphoto(True, ImageTk.PhotoImage(file="./icon.ico"))
        except: pass
        self.root.protocol("WM_DELETE_WINDOW", self.quit)

        check_update()

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # Internet & UDP
        self.mouse = mouse.Controller()
        self.connected_3DS = []
        self.Canvas3DS = {}

        self.port = option["port"]
        self.widget_3DS = {}
        self.Tap, self.mousePressed = False, False
        self.joystickX, self.joystickY = {}, {}
        self.WIN_p1 = option["WIN_p1"] if option["WIN_p1"] else (0, 0)
        self.WIN_p2 = option["WIN_p2"] if option["WIN_p2"] else (self.root.winfo_screenwidth(), self.root.winfo_screenheight())
        self.img, self.imgtk = {}, {}
        self.vjoy = {}


        for name in os.listdir("./assets/"):
            name = os.path.splitext(name)[0]
            self.img[name] = Image.open(f"./assets/{name}.png")
            self.imgtk[name] = ImageTk.PhotoImage(self.img[name])



        self.label_coordinate = Label(self.root, text="???")
        self.label_coordinate.grid(row = 2, column = 1, sticky = "NEWS", columnspan=2)

        self.button_option = Button(self.root, text = "Paramètres...", relief = RIDGE, command = self.option_menu)
        self.button_option.grid(row = 2, column = 3, sticky = "EW")

        self.frame_Canvas_3DS = Frame(self.root)
        self.frame_Canvas_3DS.grid(row=1, column=1, columnspan=3)
        #self.init_3DS(ID=0)

        self.socket.bind(("", self.port))

        self.recvThread = Thread(target=self.recv)
        self.recvThread.setDaemon(True)
        self.recvThread.start()

        self.root.after(0, self.update_tk)
        self.root.mainloop()


    def init_3DS(self, addr, ID=None):
        if ID == None: ID = len(self.connected_3DS)
        addr = addr[0]

        self.Canvas3DS[addr] = Canvas(self.frame_Canvas_3DS, width=self.img["3DS"].width + 40, height=self.img["3DS"].height + 40,
                                bg=option["bgcolor"] if option["bgcolor"] else 'SystemButtonFace')
        self.Canvas3DS[addr].grid(row = 1, column = ID)
        self.Canvas3DS[addr].create_image(self.img["3DS"].width // 2 + 20, self.img["3DS"].height // 2 + 20,
                                    image=self.imgtk["3DS"])

        self.widget_3DS[addr] = {}
        self.widget_3DS[addr][iKEY_L] = self.Canvas3DS[addr].create_image(50, 254, image=self.imgtk["L"])
        self.widget_3DS[addr][iKEY_R] = self.Canvas3DS[addr].create_image(449, 254, image=self.imgtk["R"])

        self.widget_3DS[addr][iKEY_X] = self.Canvas3DS[addr].create_image(416, 312, image=self.imgtk["X"])
        self.widget_3DS[addr][iKEY_Y] = self.Canvas3DS[addr].create_image(391, 338, image=self.imgtk["Y"])
        self.widget_3DS[addr][iKEY_A] = self.Canvas3DS[addr].create_image(442, 338, image=self.imgtk["A"])
        self.widget_3DS[addr][iKEY_B] = self.Canvas3DS[addr].create_image(415, 364, image=self.imgtk["B"])

        self.widget_3DS[addr][iKEY_padLeft] = self.Canvas3DS[addr].create_image(98, 415, image=self.imgtk["hl"])
        self.widget_3DS[addr][iKEY_padRight] = self.Canvas3DS[addr].create_image(65, 415, image=self.imgtk["hl"])
        self.widget_3DS[addr][iKEY_padUp] = self.Canvas3DS[addr].create_image(81, 398, image=self.imgtk["vl"])
        self.widget_3DS[addr][iKEY_padDown] = self.Canvas3DS[addr].create_image(81, 432, image=self.imgtk["vl"])

        self.widget_3DS[addr][iKEY_Select] = self.Canvas3DS[addr].create_image(178, 466, image=self.imgtk["SELECT"])
        self.widget_3DS[addr][iKEY_Start] = self.Canvas3DS[addr].create_image(319, 466, image=self.imgtk["START"])

        self.widget_3DS[addr][iKEY_Joystick] = self.Canvas3DS[addr].create_image(0, 0, image=self.imgtk["joystick"])
        self.widget_3DS[addr][iKEY_Tap] = self.Canvas3DS[addr].create_rectangle(-2, -2, 2, 2, outline="red")

        self.vjoy[addr] = pyvjoy.VJoyDevice(ID + 1)
        self.joystickX[addr], self.joystickY[addr] = 64, 64
        self.connected_3DS.append(addr)


    def quit(self):
        self.STOP = True
        self.root.destroy()


    def save_option(self):
        with open("./option.json", "w") as f:
            json.dump(option, f)


    def option_menu(self):
        try: self.optionTL.destroy()
        except: pass
        self.optionTL = Toplevel()

        option_connect = LabelFrame(self.optionTL, text="Connectivité")
        option_connect.grid(row=1, column=1, sticky="NEWS")
        Label(option_connect, text="IP : ").grid(row=1, column=1)
        
        option_ip = Listbox(option_connect, height=3)
        for ip in socket.gethostbyname_ex(socket.gethostname())[-1]: option_ip.insert(0, ip)
        def show_ip():
            option_ip.grid(row=1, column=2)
            button_show_ip.grid_forget()

        button_show_ip = Button(option_connect, text="Afficher l'IP local", command=show_ip, relief=RIDGE)
        button_show_ip.grid(row=1, column=2)


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
                option["WIN_p1"] = self.WIN_p1
                option["WIN_p2"] = self.WIN_p2
                self.save_option()
                option_label_borderpoint.config(text = f"({self.WIN_p1[0]}, {self.WIN_p1[1]}; {self.WIN_p2[0]}, {self.WIN_p2[1]})")

            borderpointCvn.tag_bind(screenID, "<Button-1>", point1)
            borderpointCvn.bind("<Button-3>", point2)

        option_touchscreen = LabelFrame(self.optionTL, text="Ecran tactile")
        option_touchscreen.grid(row=2, column=1)
        button_borderpoint = Button(option_touchscreen, text="Définir les bordures de l'écran tactile", relief=RIDGE, command = get_borderpoint)
        button_borderpoint.grid(row=1, column=1)

        option_label_borderpoint = Label(option_touchscreen, text = f"({self.WIN_p1[0]}, {self.WIN_p1[1]}; {self.WIN_p2[0]}, {self.WIN_p2[1]})")
        option_label_borderpoint.grid(row=1, column=2)

        def select_bgcolor():
            option_bgcolor = colorchooser.askcolor()
            if option_bgcolor:
                self.Canvas3DS.config(bg = option_bgcolor[-1])
                option["bgcolor"] = option_bgcolor[-1]
                self.save_option()

        option_visual = LabelFrame(self.optionTL, text="Visuel")
        option_visual.grid(row=3, column=1, sticky="NEWS")

        option_bgcolor = Button(option_visual, text="Couleur d'arrière plan", relief=RIDGE, command=select_bgcolor)
        option_bgcolor.grid(row=1, column=1)


    def update_tk(self):
        while not(self.STOP):
            self.frame_Canvas_3DS.update()
            time.sleep(0.05)

            for addr in self.connected_3DS:
                try:
                    _lButtons = self.vjoy[addr].data.lButtons

                    for i in range(12):
                        self.Canvas3DS[addr].itemconfigure(self.widget_3DS[addr][i], state="normal" if _lButtons >> i & 1 else "hidden")

                    ox = round((self.joystickX[addr] * 20 / 127) + 48)
                    oy = round((self.joystickY[addr] * 20 / 127) + 297)
                    self.Canvas3DS[addr].moveto(self.widget_3DS[addr][iKEY_Joystick], ox, oy)

                    if self.Tap:
                        WIN_X = self.WIN_p1[0] + ((self.WIN_p2[0]-self.WIN_p1[0]) / 314) * self.screenX
                        WIN_Y = self.WIN_p1[1] + ((self.WIN_p2[1]-self.WIN_p1[1]) / 117) * self.screenY
                        self.mouse.position = (WIN_X, WIN_Y)
                        if not(self.mousePressed): self.mouse.press(mouse.Button.left)

                        DS_X = 142 + (212 / 314) * self.screenX
                        DS_Y = 284 + (161 / 117) * self.screenY
                        self.Canvas3DS[addr].moveto(self.widget_3DS[addr][iKEY_Tap], DS_X, DS_Y)
                        self.label_coordinate.config(text = f"x={self.screenX}, y={self.screenY}")

                        self.mousePressed = True

                    elif self.mousePressed:
                        self.mouse.release(mouse.Button.left)
                        self.mouse.position = (0, 0)
                        self.mousePressed = False


                except Exception as e:
                    print("Erreur dans update_tk:")
                    print(e)




    def recv(self):
        while not(self.STOP):
            try:
                data, addr = self.socket.recvfrom(512)
                if not(addr[0] in self.connected_3DS):
                    print(f"init {addr}")
                    self.init_3DS(addr=addr)
                addr = addr[0]

                b = bin(int(data.hex(), base=16))[2:]
                self.screenX = int(b[104] + b[89:97], base=2)
                self.screenY = int(b[105:112], base=2)

                _lButton = 0

                _x = int(b[57:65], base=2)
                if b[52] == "1": self.joystickX[addr] = (_x) if (_x) < 127 else 127 # la valeur 32 est subjectif, voir pour calibrer
                elif b[51] == "1": self.joystickX[addr] = (_x)-127 if (_x)-127 > 0 else 0
                else: self.joystickX[addr] = 64

                _y = int(b[73:81], base=2)
                if b[50] == "1": self.joystickY[addr] = (_y)-127 if (_y)-127 > 0 else 0
                elif b[49] == "1": self.joystickY[addr] = (_y) if (_y) < 127 else 127 # la valeur 32 est subjectif, voir pour calibrer
                else: self.joystickY[addr] = 64


                self.Tap = True if b[44] == "1" else False

                if b[40] == "1": _lButton += KEY_R
                if b[39] == "1": _lButton += KEY_L

                if b[38] == "1": _lButton += KEY_X
                if b[37] == "1": _lButton += KEY_Y
                if b[32] == "1": _lButton += KEY_A
                if b[31] == "1": _lButton += KEY_B

                if b[30] == "1": _lButton += KEY_Select
                if b[29] == "1": _lButton += KEY_Start

                if b[28] == "1": _lButton += KEY_padLeft
                elif b[27] == "1": _lButton += KEY_padRight
                elif b[26] == "1": _lButton += KEY_padUp
                elif b[25] == "1": _lButton += KEY_padDown

                #if b[8] == "1": key.append(KEY_Keyboard)

                self.vjoy[addr].data.wAxisX = self.joystickX[addr] * 256 # 32768 // 128
                self.vjoy[addr].data.wAxisY = self.joystickY[addr] * 256 # 32768 // 128
                self.vjoy[addr].data.lButtons = _lButton
                self.vjoy[addr].update()

            except pyvjoy.exceptions.vJoyFailedToAcquireException:
                messagebox.showerror("Erreur lors de la connection",
                                     f"Impossible de se connecter à la console {addr}, vérifier que vJoy est bien \n"+\
                                     "configuré pour supporter plusieurs manette avec au moins 12 bouttons.\n\n"+\
                                     "Quitter le logiciel sur votre console.")

            except Exception as e:
                print("Erreur dans recv:")
                print(e)


KEY_Tap = "T"
KEY_Keyboard = "k"

KEY_R, iKEY_R = 2**0, 0
KEY_L, iKEY_L = 2**1, 1
KEY_A, iKEY_A = 2**2, 2
KEY_B, iKEY_B = 2**3, 3
KEY_X, iKEY_X = 2**4, 4
KEY_Y, iKEY_Y = 2**5, 5

KEY_Select, iKEY_Select = 2**6,     6
KEY_Start, iKEY_Start = 2**7, 7

KEY_padLeft, iKEY_padLeft = 2**8, 8
KEY_padRight, iKEY_padRight = 2**9, 9
KEY_padUp, iKEY_padUp = 2**10, 10
KEY_padDown, iKEY_padDown = 2**11, 11

iKEY_Joystick = 12
iKEY_Tap = 13

option = {
    "port": 8889,
    "WIN_p1": False,
    "WIN_p2": False,
    "bgcolor": False
}

if os.path.exists("./option.json"):
    with open("./option.json") as f:
        option = json.load(f)

App = AppClass()
