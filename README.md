# 🎬 SynchroClip — AI Audio-Synced Video Studio & Kinetic Caption Creator

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-0.110%2B-009688?logo=fastapi)
![FFmpeg](https://img.shields.io/badge/FFmpeg-5.0%2B-007808?logo=ffmpeg)
![TailwindCSS](https://img.shields.io/badge/TailwindCSS-3.0-38bdf8?logo=tailwind-css)
![Templates](https://img.shields.io/badge/Caption_Templates-103-ff4081)

**SynchroClip** is a full-featured, AI-powered stock video creation and kinetic caption editing studio. Upload your voiceover, speech, or music track, and SynchroClip automatically matches, synchronizes, and crossfades high-definition stock video clips from **Pexels API** (or your own uploaded footage), burns **CapCut-style kinetic multi-line typography**, renders **word-by-word karaoke animations**, supports **Picture-in-Picture (PiP) logos/stickers**, and exports a finished 1080p video in seconds.

---

## 🚀 Direct App Download (Windows)

No ZIP extraction or Python terminal commands needed! Download the pre-built desktop app directly:

| Download Asset | Description | Direct Download |
| :--- | :--- | :--- |
| **`SynchroClip.exe`** | **Standalone Windows Desktop App** (Double-click to run, opens automatically in browser) | [**⬇️ Download SynchroClip.exe**](https://github.com/ayush1305/synchroclip/releases/download/v1.0.0/SynchroClip.exe) |
| **`Install-Desktop-Shortcut.bat`** | Creates an official Windows Desktop icon shortcut | [**⬇️ Download Desktop Installer**](https://github.com/ayush1305/synchroclip/releases/download/v1.0.0/Install-Desktop-Shortcut.bat) |
| **`SynchroClip-Launcher.bat`** | 1-Click launcher script | [**⬇️ Download Launcher**](https://github.com/ayush1305/synchroclip/releases/download/v1.0.0/SynchroClip-Launcher.bat) |

👉 **[View All GitHub Releases](https://github.com/ayush1305/synchroclip/releases)**

---

### 1. 🎵 Audio-Driven Smart Clip Sync
- Upload any audio track (`.mp3`, `.wav`, `.m4a`, `.ogg`, `.flac`, `.aac`).
- Real-time waveform visualizer with synchronized playback.
- Automatically calculates speech pacing and segments clips to match your audio duration.
- Automated speech transcription with millisecond-accurate word timestamps using SpeechRecognition and voice activity detection (VAD).

### 2. 🎥 Pexels Stock Matching & Custom Video Upload
- Queries the Pexels Video API for HD 1080p clips matching keywords in your transcript.
- **One-Click Clip Swapping**: Browse and switch clips on the fly.
- **Custom Video Mode**: Upload your own raw video footage directly if you don't want AI stock generation.

### 3. 🎨 103+ Professional Caption & Typography Templates
- **15 Viral Hierarchy MOGRT Templates**: Authentic stacked multi-tier typography (Line 1 Context, Line 2 Giant Punch, Line 3 Payoff) matching viral short-form video editors (Hormozi, Ali Abdaal, Steven Bartlett).
- **Multi-Font Hybrid Typography**: Elegant combinations of modern bold sans and italic editorial serifs.
- **60+ Kinetic Word Animations**: Bounce, Pop, Float, Neon Pulse, Letter Reveal, Typewriter, Slide-In, and more.
- **Dual-Color Customizer**: Full hex color palette picker to customize Primary (Context) and Secondary (Accent) colors.
- **Shine & Glow Toggle**: Crisp, clean matte finish by default, with an optional toggle for high-energy glowing neon auras.

### 4. 🔍 Kinetic Word Zoom & Progressive Reveal
- Automatically focuses on the active spoken word in real-time.
- Keeps prior words visible as spoken, progressively revealing the full phrase across tiers.
- **Dynamic Word Markers**: Highlight critical keywords with dynamic **Circle Rings**, **Rounded Boxes**, or **Marker Underlines**.
- **Video Spotlight Focus**: Subtly dims background footage during punch moments to draw maximum audience focus to the captions.

### 5. 🖼️ Picture-in-Picture (PiP) Overlay
- Upload custom watermark logos, brand badges, or sticker images (`.png`, `.jpg`, `.webp`, `.svg`).
- Freely place PiP in any corner or position (Top-Right, Top-Left, Bottom-Right, Bottom-Left, Center) with adjustable scale and opacity.

### 6. 🚀 Hardware-Accelerated FFmpeg Export
- Seamless transition effects (`xfade` dissolve, wipe, slide, fade).
- Pixel-perfect `.ass` subtitle rendering with kerning, drop shadows, and anti-aliasing.
- 1-Click high-speed export to MP4 ready for TikTok, Instagram Reels, and YouTube Shorts.

---

## 🛠️ Prerequisites

1. **Python 3.10+**: Download from [python.org](https://www.python.org/downloads/).
2. **FFmpeg**: Must be installed and accessible in your system `PATH`.
   - **Windows**: `winget install Gyan.FFmpeg` or download from [gyan.dev](https://www.gyan.dev/ffmpeg/builds/)
   - **macOS**: `brew install ffmpeg`
   - **Linux**: `sudo apt install ffmpeg`

---

## 🚀 Quick Start Guide

### 1. Clone the Repository
```bash
git clone https://github.com/ayush1305/synchroclip.git
cd synchroclip
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. (Optional) Configure Pexels API Key
SynchroClip comes with curated fallback stock clips ready for instant use. If you want access to millions of live Pexels clips:
1. Get a free API key at [pexels.com/api](https://www.pexels.com/api/).
2. Set your environment variable:
   ```bash
   # Windows (PowerShell)
   $env:PEXELS_API_KEY="your_api_key_here"

   # Linux / macOS
   export PEXELS_API_KEY="your_api_key_here"
   ```
   Or copy `.env.example` to `.env`.

### 4. Launch the Studio
```bash
python run.py
```
Open your browser and navigate to:
```
http://localhost:8080
```

---

## 📁 Project Structure

```
synchroclip/
├── server/
│   ├── app.py                  # FastAPI server & REST API endpoints
│   ├── caption_templates.py    # 103 typography templates & styling presets
│   ├── caption_generator.py    # Subtitle generator (.ass) with kinetic tiers & markers
│   ├── video_composer.py       # FFmpeg video pipeline, transitions & export
│   ├── pexels_client.py        # Pexels API integration & video cache
│   ├── audio_analyzer.py       # Audio waveform, ffprobe timing & VAD
│   └── text_segmenter.py       # Speech transcription & sentence alignment
├── static/
│   ├── index.html              # Modern dark-mode studio interface
│   ├── app.js                  # Studio controller, live preview & canvas engine
│   └── style.css               # Kinetic animations, MOGRT styles & markers
├── uploads/                    # Uploaded audio, video, and PiP assets
├── output/                     # Generated videos & export deliverables
├── run.py                      # Application launcher
├── requirements.txt            # Python dependencies
└── README.md                   # Documentation
```

---

## 🧪 Testing

Run the automated test suite covering API, video composition, and subtitle generation:
```bash
python test_new_features.py
python test_captions.py
python test_engine.py
```

---

## 📄 License

MIT License — Feel free to use, modify, and distribute for personal and commercial projects.
