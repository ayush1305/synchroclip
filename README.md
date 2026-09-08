# SynchroClip — AI Audio-Synced Stock Video Studio

A web application that combines multiple stock video clips from the **Pexels API** synchronized to an uploaded audio track, with **CapCut-style animated caption templates**, **word-by-word karaoke highlighting**, smooth cinematic transitions, and 1-click export.

---

## 🌟 Key Features

1. **Audio Track Upload & Waveform Analysis**:
   - Upload voiceovers, speeches, or music (`.mp3`, `.wav`, `.m4a`, `.ogg`, `.flac`, `.aac`).
   - Interactive waveform visualizer and audio playhead with millisecond-accurate timing via `ffprobe`.

2. **CapCut-Style Animated Caption Templates**:
   - **Trending / Classic Hormozi**: Bold uppercase font with bright yellow active word pop, thick outline, and bounce animation.
   - **Neon Glow (Purple / Magenta / Cyan)**: Glowing text with diffused neon drop aura.
   - **Red Fire Glow**: Crimson aura with blazing yellow active word.
   - **Cinematic Serif**: Elegant editorial multiline typography (Playfair / Georgia) with white-to-cyan glow.
   - **Word Pop / Single Focus**: High-impact centered word display with zoom-pop per spoken word.
   - **Minimal Monoline**: Clean white text with translucent rounded pill badge.
   - **No Captions**: 1-click option to keep the video clean without subtitles.

3. **Word-by-Word Karaoke Highlighting**:
   - As audio plays, each word highlights in real-time.
   - Customizable highlight colors: **Neon Yellow**, **Toxic Green**, **Electric Cyan**, **Hot Magenta**, **Fiery Orange**, **Luminous White**.
   - Rendered natively in FFmpeg using Advanced SubStation Alpha (`.ass`) with motion scaling and color styling.

4. **Automated Caption Generation & Alignment**:
   - Speech-to-Text auto-transcription directly from audio via `SpeechRecognition`.
   - Voice activity detection via FFmpeg `silencedetect` to anchor word timestamps to speech energy bursts.

5. **Pexels Stock Video Search & Matching**:
   - Automatically queries Pexels Video API for high-definition 1080p clips matching each scene's keywords.
   - **Swap Clip** modal: search any query on Pexels and pick alternative footage with 1 click.
   - Includes curated stock clips for instant out-of-the-box testing.

6. **Seamless Transitions & Normalization**:
   - Employs FFmpeg's `xfade` filter (smooth dissolve, crossfade, dip to black/white, smooth wipe, circle iris).
   - Normalizes all clips to identical resolution (1080p 16:9 or 9:16 vertical shorts), 30fps, and subtle color tone.

---

## 🚀 How to Run

1. Open your terminal in this directory:
   ```bash
   cd "C:\Users\Ayush\.gemini\antigravity\scratch\video-clip-sync"
   ```

2. Start the studio server:
   ```bash
   python run.py
   ```

3. Open your browser at:
   ```
   http://localhost:8080
   ```

---

## 📦 Publishing to GitHub

The Git repository is already initialized with an initial commit and clean `.gitignore`.

To publish this repository to your GitHub account:

1. Create a new empty repository on [GitHub](https://github.com/new) (e.g. `synchroclip`).
2. Run these commands in terminal:
   ```bash
   git remote add origin https://github.com/<YOUR_USERNAME>/<YOUR_REPO_NAME>.git
   git branch -M main
   git push -u origin main
   ```

You can also download the complete project ZIP anytime by clicking **"Download Project (.ZIP)"** in the top navigation bar of the web app or visiting `http://localhost:8080/api/download-project-zip`.
