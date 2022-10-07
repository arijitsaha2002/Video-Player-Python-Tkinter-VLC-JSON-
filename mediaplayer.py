import tkinter as tk
import vlc
import tkinter.filedialog as tkf
import tkinter.ttk as ttk
import sys
import json
# from functools import reduce

MAX_VOL = 200
DEF_VOL = 100
DEF_SPEED = 1
MAX_SPEED = 2
MIN_SPEED = .2
DEF_TIME = "00.00.00"


class mediaInformation:
    def __init__(self):
        self.VOL = DEF_VOL
        self.SPEED = DEF_SPEED
        self.TIME = 0
        self.IS_PLAYING = False
        self.PATH = ""
        self.IS_FULLSCREEN = False
        self.subtitleNo = tk.Variable()
        self.audioNo = tk.Variable()


class myPlayer(tk.Tk):

    def __init__(self):
        super().__init__()
        self.title("VideoPlayer")
        self.geometry("1000x800")
        self.minsize(1800, 800)
        self.attributes('-zoomed', True)
        self.resizable(width=True, height=True)
        self.frame = tk.Frame(self)
        self.frame.pack(fill="both", expand=True)
        self.display = tk.Frame(self.frame, bd=0, background='black')
        self.display.place(relwidth=1, relheight=1)
        self.info = mediaInformation()
        self.player = vlc.MediaPlayer()
        self.topbar = tk.Menu(self)
        self.subtitle = tk.Menu(self.topbar)
        self.audio = tk.Menu(self.topbar)
        self.control = tk.Canvas(self, height=20, width=1500)
        self.control.pack(side="bottom", padx=20, pady=20)
        self.totalLenght = "00.00.00"
        self.fileMenus()
        self.buttomMenus()
        self.keybindings()

    def selectFile(self):
        path = tkf.askopenfilename(filetypes=[["media", "*.m*"], ["all files", "*"]])
        if path == "": return
        self.info.PATH = path
        self.openFile()        


    def openFile(self):
        if self.info.PATH == "": return
        self.player = vlc.MediaPlayer(self.info.PATH)
        self.player.set_xwindow(self.display.winfo_id())
        self.player.set_rate(self.info.SPEED)
        self.player.audio_set_volume(self.info.VOL)
        self.player.play()
        self.title(self.info.PATH)
        self.control.after(5000,self.oneTime)        



    def updateTime(self,A = None):
        if self.info.PATH == "" or not self.player.is_playing() or self.info.IS_FULLSCREEN: return
        time = self.player.get_time() // 1000;
        currTimeString = f"{ time // 3600}.{ (time%3600) // 60}.{ time % 60}"
        self.time.config(text= f"{currTimeString} / {self.totalLenght}")
        self.time.after(1000,self.updateTime)
        self.slider.config(value = 100 * self.player.get_time() / self.player.get_length())


    def oneTime(self,A = None):
        time = self.player.get_length() // 1000
        self.totalLenght = f"{ time // 3600}.{ (time%3600) // 60}.{ time % 60}"
        self.subtitleaudioMenu()
        self.updateTime()

    def subtitleaudioMenu(self, A=None):
        if self.info.PATH == "": return
        self.info.subtitleNo.set(self.player.video_get_spu())
        self.info.audioNo.set(self.player.audio_get_track())
        for i in self.player.video_get_spu_description():
            self.subtitle.add_radiobutton(label=i[1], variable=self.info.subtitleNo, value=i[0],command=self.set_Subtitle)
        for i in self.player.audio_get_track_description():
            self.audio.add_radiobutton(label=i[1], variable=self.info.audioNo, value=i[0],command=self.set_Audio)

    def fullscreenOn(self, A=None):
        if self.info.PATH == "" or self.info.IS_FULLSCREEN: return
        emptyMenu = tk.Menu(self)
        self.config(menu=emptyMenu)
        self.control.pack_forget()
        self.attributes('-fullscreen', True)
        self.info.IS_FULLSCREEN = True
    
    def fullscreenOff(self, A=None):
        if self.info.PATH == "" or not self.info.IS_FULLSCREEN: return
        self.config(menu=self.topbar)
        self.control.pack(side="bottom", padx=20, pady=20)
        self.attributes('-fullscreen', False)
        self.info.IS_FULLSCREEN = False
        self.updateTime()

    def toggleFullscreen(self, A = None):
        if self.info.PATH == "": return
        if self.info.IS_FULLSCREEN : self.fullscreenOff()
        elif not self.info.IS_FULLSCREEN : self.fullscreenOn()


    def changeSlider(self, A=None):
        self.player.set_time(int(self.player.get_length()*self.slider.get()/100))

    def play(self, A=None):
        if self.info.PATH == "": return
        if not self.player.is_playing() : self.player.play()
        self.updateTime()

    def pause(self, A=None):
        if self.info.PATH == "": return
        if self.player.is_playing(): self.player.pause()

    def togglePlay(self, A = None):
        if self.info.PATH == "": return
        if self.player.is_playing(): self.pause()
        elif not self.player.is_playing(): self.play()


    def stop(self, A=None):
        self.player.stop()
        self.info.PATH = ""
        self.totalLenght = DEF_TIME
        self.slider.set(0)


    def volInc(self, A=None):
        if self.info.PATH == "": return
        if (self.player.audio_get_volume() < MAX_VOL):
            self.player.audio_set_volume(self.player.audio_get_volume() + 10)
        self.volume.config(text=f"Volume : {self.player.audio_get_volume()} / {MAX_VOL}")


    def volDec(self, A=None):
        if self.info.PATH == "": return
        if (self.player.audio_get_volume() > 0):
            self.player.audio_set_volume(self.player.audio_get_volume() - 10)
        self.volume.config(text=f"Volume : {self.player.audio_get_volume()} / {MAX_VOL}")


    def speedInc(self, A=None):
        if self.info.PATH == "": return
        if (self.player.get_rate() < MAX_SPEED):
            self.player.set_rate(self.player.get_rate() + .2)
        self.speed.config(text=f"Speed : {round(self.player.get_rate(),2)} / {MAX_SPEED}")


    def speedDec(self, A=None):
        if self.info.PATH == "": return
        if (self.player.get_rate() > MIN_SPEED):
            self.player.set_rate(self.player.get_rate() - .2)
        self.speed.config(text=f"Speed : {round(self.player.get_rate(),2)} / {MAX_SPEED}")


    def set_Subtitle(self):
        if self.info.PATH == "": return
        self.player.video_set_spu(self.info.subtitileNo.get())

    def set_Audio(self):
        if self.info.PATH == "": return
        self.player.audio_set_track(self.info.audioNo.get())

    def seekRight(self, A = None):
        if self.info.PATH == "": return
        self.player.set_time(self.player.get_time()+10000)

    def seekLeft(self, A = None):
        if self.info.PATH == "": return
        self.player.set_time(self.player.get_time()-10000)

    def buttomMenus(self):
        self.time = tk.Label(self.control, text=f"Time : 00.00.00 / {self.totalLenght}")
        self.time.grid(row=0, column=0, padx=30)
        self.slider = ttk.Scale(self.control, from_=0, to=100, orient="horizontal", command=self.changeSlider, length=800)
        self.slider.grid(row=0, column=1, padx=30,)
        self.volume = tk.Label(self.control, text=f"Volume : {DEF_VOL} / {MAX_VOL}")
        self.volume.grid(row=0, column=2, padx=30)
        self.speed = tk.Label(self.control, text=f"Speed : {self.info.SPEED} / {MAX_SPEED}")
        self.speed.grid(row=0, column=3, padx=30)

    def fileMenus(self):
        self.topbar.add_command(label="open", command=self.selectFile)
        self.topbar.add_command(label="play", command=self.play)
        self.topbar.add_command(label="pause", command=self.pause)
        self.topbar.add_command(label="stop", command=self.stop)
        self.topbar.add_command(label="Vol+", command=self.volInc)
        self.topbar.add_command(label="Vol-", command=self.volDec)
        self.topbar.add_cascade(label="Subtitle", menu=self.subtitle)
        self.topbar.add_cascade(label="Audio", menu=self.audio)
        self.topbar.add_command(label="FullScreen", command=self.fullscreenOn)
        self.config(menu=self.topbar)
    def QUIT(self,A = None):
        exit(0)

    def keybindings(self):
        AllFunctions = { 
            "selectFile": self.selectFile,
            "openFile": self.openFile,
            "speedInc": self.speedInc,
            "speedDec": self.speedDec,
            "fullscreenOn": self.fullscreenOn,
            "fullscreenOff": self.fullscreenOff,
            "seekLeft": self.seekLeft,
            "seekRight": self.seekRight,
            "stop": self.stop,
            "volInc": self.volInc,  
            "volDec": self.volDec,
            "play": self.play,
            "pause": self.pause,
            "togglePlay": self.togglePlay,
            "toggleFullscreen": self.toggleFullscreen,
            "quit": self.QUIT
        }

        keys = json.load(open("keybindings.json"))
        for i , j in keys.items():
            self.bind(i,AllFunctions[j])


A = myPlayer()
if len(sys.argv) > 1: 
    A.info.PATH = sys.argv[1]
    A.openFile()
A.mainloop()