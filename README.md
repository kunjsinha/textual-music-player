# 🎵 Textual Music Player

A terminal-based MP3 music player built with [Textual](https://github.com/Textualize/textual), [pygame](https://www.pygame.org/), and [mutagen](https://mutagen.readthedocs.io/).  
It lets you create and manage playlists, add songs, shuffle, and control playback - all from a beautiful Textual UI.

---

## ✨ Features

- 🎧 Create and manage playlists  
- ➕ Add MP3 songs using a file picker  
- ▶️ Play / ⏸ Pause / ⏭ Next song controls  
- 🔀 Shuffle mode  
- 📊 Real-time progress bar  
- 🧾 Persistent playlists (saved as `.txt` files)  

---

##  Project Structure
```
textual-music-player/
│
├── music_app.py # Main application
├── appstyles.css # Textual styling file
├── requirements.txt # Dependencies list
├── README.md # Documentation
└── LICENSE #MIT LICENSE
```


---

##  Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/kunjsinha/textual-music-player.git
cd textual-music-player
```

---

### 2. Create and Activate a Virtual Environment
```bash
python -m venv venv
source venv/bin/activate   # macOS / Linux
# or
venv\Scripts\activate      # Windows
```

---

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

---

### 4. Run the App
```bash
python music_app.py
```

---

##  Usage
- Create Playlist: Type a name and click “Create Playlist.”
- Select Playlist: Click a playlist button from the left panel.
- Add Song: Click “Add Song” and pick an MP3 file.
- Play Controls: Use Play, Pause, Next, and Shuffle.
- Quit: Click “Quit” to exit the app.
- All playlists and songs are saved locally in csv and text files.

---

## 🧠 Development Notes
- Playlists are tracked in playlist.csv.
- Each playlist’s songs are stored in separate .txt files.
- The player uses pygame.mixer for playback and mutagen for MP3 duration.
- The app automatically updates the progress bar as the song plays.
