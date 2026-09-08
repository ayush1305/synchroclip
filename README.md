# SynchroClip — AI Audio-Synced Stock Video Studio

A web application that combines multiple stock video clips from the **Pexels API** synchronized to an uploaded audio track and transcript, featuring smooth transitions and **zero hardcoded captions**.

---

## 🌟 Key Features

1. **Audio Track Upload & Waveform Analysis**:
   - Upload any voiceover, speech, or music file (`.mp3`, `.wav`, `.m4a`, `.ogg`, `.flac`, `.aac`).
   - Visual waveform generator and audio playhead with millisecond-accurate timing via `ffprobe`.

2. **Smart Script Segmentation & Keyword Extraction**:
   - Analyzes your transcript and breaks it into timed visual scenes matching the audio's duration.
   - Automatically extracts contextual keywords (nouns, action verbs, scene descriptors).

3. **Pexels Stock Video Search & Matching**:
   - Automatically queries the Pexels Video API for high-resolution 1080p clips matching each scene's keywords.
   - Interactive **Swap Clip** drawer: search any query on Pexels and pick alternative footage with 1 click.
   - Built-in curated stock video library for instant testing out-of-the-box.

4. **Cinematic Transitions & Normalization**:
   - Employs FFmpeg's `xfade` filter (smooth dissolve, crossfade, dip to black/white, smooth wipe, circle iris).
   - Normalizes all clips to identical resolution (1080p 16:9 or 9:16 vertical shorts), 30fps, and subtle color tone so transitions feel like one cohesive video.
   - Scene timings are mathematically calibrated with transition overlaps to match the exact audio duration.

5. **No Subtitles / Captions Added**:
   - The visual video canvas is kept 100% clean without burnt-in captions, so you can add your custom captions and typography yourself.

6. **Preserved Uploaded Audio**:
   - Muxes your uploaded audio track in high-fidelity AAC directly onto the final stitched video.

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
   http://localhost:8000
   ```

---

## 🖥️ How to Use

1. **Upload Audio**: Drag and drop your audio file or click "Try Demo Sample" to load a preconfigured audio & script.
2. **Paste Transcript**: Paste the transcript or text of your audio in the script box.
3. **Configure Settings**:
   - Choose **Aspect Ratio** (16:9 for YouTube or 9:16 for Shorts/Reels).
   - Choose **Transition Type** (Smooth Dissolve, Crossfade, Dip to Black, etc.) and transition duration (e.g. 0.8s).
4. **Click "Analyze & Auto-Match Clips"**:
   - The app will automatically split the script into timed scenes and find matching Pexels clips.
5. **Review Storyboard**:
   - Hover over any clip to preview video playback.
   - Click **Swap Clip** to search Pexels for alternative clips.
   - Use the arrow buttons to reorder scenes.
6. **Click "Render Final Video"**:
   - FFmpeg will stitch the clips with seamless crossfades and mux your uploaded audio.
   - Watch real-time progress and download the completed master MP4!
