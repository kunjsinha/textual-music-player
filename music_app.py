from textual.app import App
from textual.widgets import Button, Header, Footer, Static, Input, ProgressBar, ListView, ListItem
from textual.containers import Horizontal, Vertical
from pathlib import Path
from pygame import mixer as m
from mutagen.mp3 import MP3
import csv
import tkinter as tk
from tkinter import filedialog
import time
import random

def select_file():
    root = tk.Tk()
    root.withdraw()  # hide tkinter window so only song selector comes
    file_path = filedialog.askopenfilename(
        title="Select a song",
        filetypes=[("MP3 files", "*.mp3"), ("All files", "*.*")]
    )
    root.destroy()
    return file_path

selected_playlist = ""

playlist = "playlist.csv"
Path(playlist).touch(exist_ok=True)
first_song_played = False


class MusicApp(App):
    CSS_PATH = "appstyles.css" 

    def compose(self):
        yield Header()
        with Horizontal(id="main"):
            with Vertical(id="left_panel"):
                yield Static("Playlists", id="playlists_label")
                self.playlist_container = Vertical(id="playlist_container")
                yield self.playlist_container
                self.input_box = Input("Enter Playlist Name", id="input_pname")
                yield self.input_box
                yield Button("Create Playlist", id="create_playlist")

            with Vertical(id="right_panel"):
                yield Static("Songs in Playlist")
                
                self.song_list = ListView(id="song_list")
                yield self.song_list
                yield Static("Controls")
                with Horizontal(id="controls"):
                    self.play_btn = Button("Play", id="play")
                    self.pause_btn = Button("Pause", id="pause")
                    self.next_btn = Button("Next", id="next")
                    self.shuffle_btn = Button("Shuffle", id="shuffle")
                    yield self.play_btn
                    yield self.pause_btn
                    yield self.next_btn
                    yield self.shuffle_btn
                self.progress = ProgressBar(total=100, id="progress")
                yield self.progress
                yield Button("Add Song", id="add_song")
                yield Button("Quit", id="exit_prog")
        yield Footer()

    def on_mount(self):
        self.load_playlists()
        global selected_playlist
        selected_playlist = None
        self.playing = False
        self.paused = False
        self.current_index = 0
        self.current_duration = 0
        self.playlist_songs = []
        self.shuffle_play = False
        


    def load_playlists(self):
        #load playlists as buttons
        for child in list(self.playlist_container.children):
            child.remove()
        with open(playlist, "r", newline="") as f:
            reader = csv.reader(f)
            for row in reader:
                pname = row[0]
                btn = Button(pname, id=f"playlist_{pname}")
                self.playlist_container.mount(btn)

    def load_playlist_songs(self, pname: str):
        #load songs into playlist
        self.song_list.clear()
        if not pname:  #safety check
            return
        playlist_file = str(pname) + ".txt"
        try:
            with open(playlist_file, "r") as f:
                songs = [line.strip() for line in f.readlines() if line.strip()]
            for song in songs:
                item = ListItem(Static(Path(song).name))
                self.song_list.append(item)
        except FileNotFoundError:
            self.notify("No songs found in this playlist.")


    def on_button_pressed(self, event):
        global selected_playlist
        #create new playlist
        if event.button.id == "create_playlist":
            pname = self.input_box.value.strip()
            if pname:
                with open(playlist, "a", newline='') as f:
                    writer = csv.writer(f)
                    writer.writerow([pname])
                with open(pname + ".txt", 'w', newline='') as f:
                    pass
                btn = Button(pname, id=f"playlist_{pname}")
                self.playlist_container.mount(btn)
                self.input_box.value = ""

        #add new song
        elif event.button.id == "add_song":
            if not selected_playlist:
                self.notify("Select a playlist first!")
                return
            song_path = select_file()
            song_name = Path(song_path).name
            pstr = str(selected_playlist)
            with open(pstr + ".txt", 'a') as f:
                f.write(f"{song_path}\n")
            self.notify(f"Added: {song_name}")
            self.load_playlist_songs(selected_playlist)
            with open(pstr + ".txt", 'r') as f:
                self.playlist_songs = [line.strip() for line in f.readlines() if line.strip()]

        #check if a playlist button is clicked
        elif event.button.id.startswith("playlist_"):
            selected_playlist = event.button.label
            self.notify(f"Selected playlist: {selected_playlist}")
            self.load_playlist_songs(selected_playlist)
            pstr = str(selected_playlist)
            self.current_index = 0
            self.shuffle_play = False
            with open(pstr + ".txt", 'r') as f:
                self.playlist_songs = [line.strip() for line in f.readlines() if line.strip()]
                if not self.playlist_songs:
                    self.notify("No songs in playlist!")
                    return
        
        #shuffle songs
        elif event.button.id == "shuffle":
            if self.shuffle_play == False:
                m.init()
                self.shuffle_play = True
                self.notify("Shuffle has been enabled")
                self.current_index = random.randint(0,len(self.playlist_songs)-1)
                self.play_song(self.playlist_songs[self.current_index])


            elif self.shuffle_play == True:
                self.shuffle_play = False
                self.notify("Shuffle play has been disabled")


        #play song
        elif event.button.id == "play":
            if not m.get_init():
                m.init()

            if not selected_playlist:
                self.notify("Select a playlist first!")
                return

            pstr = str(selected_playlist)
            try:
            
                #resume if paused
                if self.paused:
                    m.music.unpause()
                    self.paused = False
                    self.notify(f"Resumed: {self.song_name}")
                    return
            
                self.current_index = 0
                
                self.play_song(self.playlist_songs[self.current_index])
                self.set_interval(1, self.upd_song)

            except FileNotFoundError:
                self.notify("Add a song first!")

        #pause current song
        elif event.button.id == "pause":
            if self.playing and not self.paused:
                m.music.pause()
                self.paused = True
                self.last_pause_start = time.time()      
                self.notify(f"Paused: {self.song_name}")
            elif self.paused:
                m.music.unpause()
                if self.last_pause_start:
                    
                    self.paused_time += time.time() - self.last_pause_start
                    self.last_pause_start = None
                self.paused = False
                self.notify(f"Resumed: {self.song_name}")

        #go to next song
        elif event.button.id == "next":
            if not self.playlist_songs:
                self.notify("No songs loaded!")
                return
            if self.shuffle_play == True:
                self.current_index = random.randint(0,len(self.playlist_songs)-1)
                self.play_song(self.playlist_songs[self.current_index])
            else:    
                self.current_index += 1
            if self.current_index < len(self.playlist_songs):
                self.play_song(self.playlist_songs[self.current_index])
            else:
                self.notify("End of playlist!")

        
        elif event.button.id == "exit_prog":
            self.exit()

    #song player
    def play_song(self, path: str):
        p = Path(path)
        if not p.exists():
            self.notify(f"File not found: {p}")
            return
        
        try:
            audio = MP3(str(p))
            self.current_duration = audio.info.length
        except Exception:
            self.current_duration = 0

        self.song_name = p.name
        self.progress.update(progress=0)

        self.playing = True
        self.paused = False
        self.song_start_time = time.time()       
        self.paused_time = 0
        m.music.load(str(p))
        m.music.play()                    
        self.last_pause_start = None             
        self.notify(f"🎶 Playing: {self.song_name}")

    #thing so other buttons can be clicked while song is playing
    def upd_song(self):
        if not self.playing or self.paused:
            return

        #check time playing
        elapsed = time.time() - self.song_start_time - self.paused_time

        #upd prog bar
        if self.current_duration > 0:
            percent = min((elapsed / self.current_duration) * 100, 100)
            self.progress.update(progress=percent)
        else:
            self.progress.update(progress=0)

        #if song ended
        if not m.music.get_busy():
            if self.shuffle_play and self.playlist_songs:
                self.current_index = random.randint(0, len(self.playlist_songs) - 1)
                self.play_song(self.playlist_songs[self.current_index])
            else:
                self.current_index += 1
                if self.current_index < len(self.playlist_songs):
                    self.play_song(self.playlist_songs[self.current_index])
                else:
                    self.notify("Playlist finished")
                    self.playing = False
                    self.progress.update(progress=100)
                    

if __name__ == "__main__":
    MusicApp().run()
