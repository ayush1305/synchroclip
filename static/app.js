/**
 * SynchroClip — AI Audio-to-Video Multi-Clip Studio
 * Clean, lightweight, reliable multi-clip video generator and player.
 */

// Application State
const state = {
  audioId: null,
  audioDuration: 0,
  audioFileName: '',
  waveformPeaks: [],
  scenes: [],
  captionCards: [],
  timedWords: [],
  aspectRatio: '9:16',
  selectedTemplate: 'hormozi_classic',
  highlightColor: '#ffe600',
  enableShine: false,
  isPlaying: false,
  currentSceneIndex: 0,
  activeSwappingSceneIndex: null,
  isMuted: false
};

// DOM Elements
const el = {
  // Top controls
  btnAspectPortrait: document.getElementById('btnAspectPortrait'),
  btnAspectLandscape: document.getElementById('btnAspectLandscape'),
  btnQuickDemo: document.getElementById('btnQuickDemo'),
  btnTopExport: document.getElementById('btnTopExport'),
  btnRenderVideo: document.getElementById('btnRenderVideo'),

  // Audio source
  audioDropzone: document.getElementById('audioDropzone'),
  audioFileInput: document.getElementById('audioFileInput'),
  audioPlayerCard: document.getElementById('audioPlayerCard'),
  audioStatusBadge: document.getElementById('audioStatusBadge'),
  btnAudioPlayPause: document.getElementById('btnAudioPlayPause'),
  audioFileName: document.getElementById('audioFileName'),
  audioCurrentTime: document.getElementById('audioCurrentTime'),
  audioTotalTime: document.getElementById('audioTotalTime'),
  btnChangeAudio: document.getElementById('btnChangeAudio'),
  waveformContainer: document.getElementById('waveformContainer'),
  htmlAudio: document.getElementById('htmlAudio'),
  btnAnalyzeAndGenerate: document.getElementById('btnAnalyzeAndGenerate'),

  // Script accordion
  btnToggleScriptAccordion: document.getElementById('btnToggleScriptAccordion'),
  iconScriptChevron: document.getElementById('iconScriptChevron'),
  scriptAccordionContent: document.getElementById('scriptAccordionContent'),
  scriptInput: document.getElementById('scriptInput'),

  // Storyboard
  storyboardSection: document.getElementById('storyboardSection'),
  storyboardEmptyState: document.getElementById('storyboardEmptyState'),
  storyboardGrid: document.getElementById('storyboardGrid'),
  sceneCountBadge: document.getElementById('sceneCountBadge'),

  // Program Monitor
  playerContainer: document.getElementById('playerContainer'),
  liveVideoPlayer: document.getElementById('liveVideoPlayer'),
  liveCaptionOverlay: document.getElementById('liveCaptionOverlay'),
  playerClickOverlay: document.getElementById('playerClickOverlay'),
  iconMonitorCenterPlay: document.getElementById('iconMonitorCenterPlay'),
  playerActiveClipBadge: document.getElementById('playerActiveClipBadge'),
  btnTransportPrev: document.getElementById('btnTransportPrev'),
  btnTransportPlay: document.getElementById('btnTransportPlay'),
  iconTransportPlay: document.getElementById('iconTransportPlay'),
  btnTransportNext: document.getElementById('btnTransportNext'),
  monitorCurrentTime: document.getElementById('monitorCurrentTime'),
  monitorTotalTime: document.getElementById('monitorTotalTime'),
  btnMuteToggle: document.getElementById('btnMuteToggle'),
  iconVolume: document.getElementById('iconVolume'),

  // Captions & Styling
  captionTemplateSelect: document.getElementById('captionTemplateSelect'),
  colorSwatches: document.querySelectorAll('.color-swatch-btn'),
  toggleShineGlow: document.getElementById('toggleShineGlow'),

  // Swap Clip Modal
  swapClipModal: document.getElementById('swapClipModal'),
  swapModalSubtitle: document.getElementById('swapModalSubtitle'),
  swapSearchInput: document.getElementById('swapSearchInput'),
  btnSwapSearch: document.getElementById('btnSwapSearch'),
  swapClipsGrid: document.getElementById('swapClipsGrid'),
  btnCloseSwapModal: document.getElementById('btnCloseSwapModal'),

  // Render Modal
  renderProgressModal: document.getElementById('renderProgressModal'),
  renderStatusMessage: document.getElementById('renderStatusMessage'),
  renderProgressBar: document.getElementById('renderProgressBar'),
  renderProgressPercent: document.getElementById('renderProgressPercent'),
  renderSuccessContainer: document.getElementById('renderSuccessContainer'),
  btnDownloadFinishedVideo: document.getElementById('btnDownloadFinishedVideo'),
  btnCloseRenderModal: document.getElementById('btnCloseRenderModal')
};

// Initialize Application
function initApp() {
  bindEventListeners();
  updateHighlightColor(state.highlightColor);
  if (window.lucide) lucide.createIcons();
}

// Event Listeners
function bindEventListeners() {
  // Aspect ratio switcher
  el.btnAspectPortrait.addEventListener('click', () => setAspectRatio('9:16'));
  el.btnAspectLandscape.addEventListener('click', () => setAspectRatio('16:9'));

  // Quick Demo
  el.btnQuickDemo.addEventListener('click', handleQuickDemo);

  // Audio Dropzone & File Input
  el.audioDropzone.addEventListener('click', () => el.audioFileInput.click());
  el.audioFileInput.addEventListener('change', (e) => {
    if (e.target.files && e.target.files[0]) handleAudioUpload(e.target.files[0]);
  });

  el.audioDropzone.addEventListener('dragover', (e) => {
    e.preventDefault();
    el.audioDropzone.classList.add('border-brand-500', 'bg-brand-500/10');
  });

  el.audioDropzone.addEventListener('dragleave', () => {
    el.audioDropzone.classList.remove('border-brand-500', 'bg-brand-500/10');
  });

  el.audioDropzone.addEventListener('drop', (e) => {
    e.preventDefault();
    el.audioDropzone.classList.remove('border-brand-500', 'bg-brand-500/10');
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleAudioUpload(e.dataTransfer.files[0]);
    }
  });

  // Audio Play/Pause
  el.btnAudioPlayPause.addEventListener('click', togglePlayPause);
  el.btnChangeAudio.addEventListener('click', resetAudio);

  // Script Accordion
  el.btnToggleScriptAccordion.addEventListener('click', () => {
    const isHidden = el.scriptAccordionContent.classList.toggle('hidden');
    el.iconScriptChevron.style.transform = isHidden ? 'rotate(0deg)' : 'rotate(180deg)';
  });

  // Analyze & Generate Action
  el.btnAnalyzeAndGenerate.addEventListener('click', handleAnalyzeAndGenerate);

  // Player controls
  el.playerClickOverlay.addEventListener('click', togglePlayPause);
  el.btnTransportPlay.addEventListener('click', togglePlayPause);
  el.btnTransportPrev.addEventListener('click', () => seekToScene(state.currentSceneIndex - 1));
  el.btnTransportNext.addEventListener('click', () => seekToScene(state.currentSceneIndex + 1));

  el.btnMuteToggle.addEventListener('click', toggleMute);

  // HTML Audio Events
  el.htmlAudio.addEventListener('timeupdate', onAudioTimeUpdate);
  el.htmlAudio.addEventListener('ended', onAudioEnded);

  // Caption Template Select
  el.captionTemplateSelect.addEventListener('change', (e) => {
    state.selectedTemplate = e.target.value;
    updateLiveCaption(el.htmlAudio.currentTime || 0);
  });

  // Color swatches
  el.colorSwatches.forEach(btn => {
    btn.addEventListener('click', () => {
      const hex = btn.dataset.hex;
      updateHighlightColor(hex);
      el.colorSwatches.forEach(b => b.classList.replace('border-white', 'border-transparent'));
      btn.classList.replace('border-transparent', 'border-white');
      updateLiveCaption(el.htmlAudio.currentTime || 0);
    });
  });

  // Shine glow toggle
  el.toggleShineGlow.addEventListener('change', (e) => {
    state.enableShine = e.target.checked;
    if (state.enableShine) {
      el.liveCaptionOverlay.classList.add('shine-glow-active');
    } else {
      el.liveCaptionOverlay.classList.remove('shine-glow-active');
    }
    updateLiveCaption(el.htmlAudio.currentTime || 0);
  });

  // Render buttons
  el.btnTopExport.addEventListener('click', handleRenderVideo);
  el.btnRenderVideo.addEventListener('click', handleRenderVideo);

  // Swap modal listeners
  el.btnCloseSwapModal.addEventListener('click', () => el.swapClipModal.classList.add('hidden'));
  el.btnSwapSearch.addEventListener('click', handleSwapSearch);
  el.swapSearchInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter') handleSwapSearch();
  });

  // Render modal close
  el.btnCloseRenderModal.addEventListener('click', () => el.renderProgressModal.classList.add('hidden'));
}

// Set Aspect Ratio
function setAspectRatio(ratio) {
  state.aspectRatio = ratio;
  if (ratio === '9:16') {
    el.btnAspectPortrait.className = 'px-3 py-1.5 rounded-lg text-xs font-semibold flex items-center space-x-1.5 transition bg-brand-600 text-white shadow';
    el.btnAspectLandscape.className = 'px-3 py-1.5 rounded-lg text-xs font-semibold flex items-center space-x-1.5 transition text-slate-400 hover:text-white';
    el.playerContainer.className = 'relative bg-black rounded-xl overflow-hidden border border-slate-800 shadow-2xl flex items-center justify-center w-full max-w-[340px] aspect-[9/16] transition-all';
  } else {
    el.btnAspectLandscape.className = 'px-3 py-1.5 rounded-lg text-xs font-semibold flex items-center space-x-1.5 transition bg-brand-600 text-white shadow';
    el.btnAspectPortrait.className = 'px-3 py-1.5 rounded-lg text-xs font-semibold flex items-center space-x-1.5 transition text-slate-400 hover:text-white';
    el.playerContainer.className = 'relative bg-black rounded-xl overflow-hidden border border-slate-800 shadow-2xl flex items-center justify-center w-full max-w-[540px] aspect-[16/9] transition-all';
  }
}

// Update Highlight Color
function updateHighlightColor(hex) {
  state.highlightColor = hex;
  document.documentElement.style.setProperty('--highlight-color', hex);
}

// Audio Upload Handler
async function handleAudioUpload(file) {
  const formData = new FormData();
  formData.append('file', file);

  try {
    el.audioStatusBadge.classList.remove('hidden');
    el.audioStatusBadge.textContent = 'Uploading...';
    el.audioStatusBadge.className = 'px-2.5 py-1 rounded-full text-xs font-medium bg-amber-500/20 text-amber-300 border border-amber-500/30';

    const resp = await fetch('/api/upload-audio', {
      method: 'POST',
      body: formData
    });
    if (!resp.ok) throw new Error('Failed to upload audio');
    const data = await resp.json();

    setAudioData(data);
  } catch (err) {
    alert('Audio upload failed: ' + err.message);
    el.audioStatusBadge.classList.add('hidden');
  }
}

// Quick Demo Loader
async function handleQuickDemo() {
  try {
    el.btnQuickDemo.disabled = true;
    el.btnQuickDemo.innerHTML = '<i data-lucide="loader-2" class="w-3.5 h-3.5 animate-spin"></i><span>Loading Demo...</span>';
    if (window.lucide) lucide.createIcons();

    const resp = await fetch('/api/sample-demo');
    if (!resp.ok) throw new Error('Demo fetch failed');
    const data = await resp.json();

    setAudioData(data);
    if (data.script) {
      el.scriptInput.value = data.script;
    }

    // Automatically trigger scene generation for instant demo magic
    await handleAnalyzeAndGenerate();
  } catch (err) {
    alert('Could not load demo: ' + err.message);
  } finally {
    el.btnQuickDemo.disabled = false;
    el.btnQuickDemo.innerHTML = '<i data-lucide="sparkles" class="w-3.5 h-3.5 text-amber-400"></i><span>Try Demo Audio</span>';
    if (window.lucide) lucide.createIcons();
  }
}

// Set Audio Data
function setAudioData(data) {
  state.audioId = data.audio_id;
  state.audioDuration = data.duration;
  state.audioFileName = data.filename;
  state.waveformPeaks = data.waveform || [];

  // Update UI
  el.audioDropzone.classList.add('hidden');
  el.audioPlayerCard.classList.remove('hidden');
  el.audioFileName.textContent = data.filename;
  el.audioTotalTime.textContent = formatTime(data.duration);
  el.audioCurrentTime.textContent = '00:00';
  el.monitorTotalTime.textContent = formatTime(data.duration);

  el.audioStatusBadge.classList.remove('hidden');
  el.audioStatusBadge.textContent = 'Audio Ready';
  el.audioStatusBadge.className = 'px-2.5 py-1 rounded-full text-xs font-medium bg-emerald-500/20 text-emerald-300 border border-emerald-500/30';

  el.htmlAudio.src = `/api/audio/${data.audio_id}`;
  el.htmlAudio.load();

  renderWaveform(state.waveformPeaks);
}

// Reset Audio
function resetAudio() {
  state.audioId = null;
  state.audioDuration = 0;
  state.isPlaying = false;
  el.htmlAudio.pause();
  el.htmlAudio.src = '';
  el.liveVideoPlayer.pause();
  el.liveVideoPlayer.src = '';

  el.audioPlayerCard.classList.add('hidden');
  el.audioDropzone.classList.remove('hidden');
  el.audioStatusBadge.classList.add('hidden');
  el.storyboardGrid.innerHTML = '';
  el.storyboardGrid.classList.add('hidden');
  el.storyboardEmptyState.classList.remove('hidden');
  el.sceneCountBadge.textContent = '0 Scenes';
  el.liveCaptionOverlay.innerHTML = '';
}

// Render Waveform
function renderWaveform(peaks) {
  el.waveformContainer.innerHTML = '';
  peaks.forEach((peak, i) => {
    const bar = document.createElement('div');
    bar.className = 'waveform-bar';
    bar.style.height = `${Math.max(12, peak * 100)}%`;
    bar.addEventListener('click', () => {
      const progress = i / peaks.length;
      seekToTime(progress * state.audioDuration);
    });
    el.waveformContainer.appendChild(bar);
  });
}

// Core Action: Analyze Audio & Generate Multi-Clip Video
async function handleAnalyzeAndGenerate() {
  if (!state.audioId) {
    alert('Please upload an audio file first.');
    return;
  }

  el.btnAnalyzeAndGenerate.disabled = true;
  el.btnAnalyzeAndGenerate.innerHTML = '<i data-lucide="loader-2" class="w-4 h-4 animate-spin text-amber-300"></i><span>Analyzing Pauses & Matching Multiple Clips...</span>';
  if (window.lucide) lucide.createIcons();

  try {
    const scriptText = el.scriptInput.value.trim();
    const resp = await fetch('/api/analyze-and-generate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        audio_id: state.audioId,
        script_text: scriptText,
        aspect_ratio: state.aspectRatio,
        template_id: state.selectedTemplate
      })
    });

    if (!resp.ok) throw new Error('Scene generation failed');
    const data = await resp.json();

    state.scenes = data.scenes || [];
    state.captionCards = data.caption_cards || [];
    state.timedWords = data.timed_words || [];

    if (data.transcript && !el.scriptInput.value.trim()) {
      el.scriptInput.value = data.transcript;
    }

    renderStoryboard(state.scenes);

    // Prepare first scene in player
    if (state.scenes.length > 0) {
      loadSceneIntoPlayer(0);
    }
  } catch (err) {
    alert('Error analyzing audio: ' + err.message);
  } finally {
    el.btnAnalyzeAndGenerate.disabled = false;
    el.btnAnalyzeAndGenerate.innerHTML = '<i data-lucide="sparkles" class="w-4 h-4 text-amber-300"></i><span>✨ Analyze Audio & Generate Multi-Clip Video</span>';
    if (window.lucide) lucide.createIcons();
  }
}

// Render Storyboard Scenes
function renderStoryboard(scenes) {
  el.storyboardGrid.innerHTML = '';
  el.sceneCountBadge.textContent = `${scenes.length} Scenes`;

  if (!scenes.length) {
    el.storyboardEmptyState.classList.remove('hidden');
    el.storyboardGrid.classList.add('hidden');
    return;
  }

  el.storyboardEmptyState.classList.add('hidden');
  el.storyboardGrid.classList.remove('hidden');

  scenes.forEach((scene, index) => {
    const card = document.createElement('div');
    card.className = `scene-card p-3 flex flex-col justify-between cursor-pointer ${index === 0 ? 'active-scene' : ''}`;
    card.dataset.index = index;

    const clip = scene.selected_clip || {};
    const thumbUrl = clip.image || 'https://images.unsplash.com/photo-1506744038136-46273834b3fb?w=640&q=80';
    const videoUrl = clip.preview_url || clip.video_url || '';

    card.innerHTML = `
      <div>
        <!-- Clip Thumbnail with Hover Preview -->
        <div class="relative aspect-video rounded-lg overflow-hidden bg-black mb-2.5 group">
          <img src="${thumbUrl}" class="w-full h-full object-cover transition group-hover:opacity-0" alt="Clip">
          ${videoUrl ? `<video src="${videoUrl}" muted loop preload="none" class="absolute inset-0 w-full h-full object-cover opacity-0 group-hover:opacity-100 transition"></video>` : ''}
          <span class="absolute top-1.5 left-1.5 bg-black/70 backdrop-blur text-[10px] font-mono px-1.5 py-0.5 rounded text-slate-200">
            Scene #${index + 1}
          </span>
          <span class="absolute bottom-1.5 right-1.5 bg-black/70 backdrop-blur text-[10px] font-mono px-1.5 py-0.5 rounded text-amber-300">
            ${formatTime(scene.start_time)} - ${formatTime(scene.end_time)}
          </span>
        </div>

        <!-- Scene Visual Query / Mood -->
        <div class="flex items-center justify-between mb-1">
          <span class="text-xs font-bold text-white capitalize truncate">${scene.primary_query || 'Cinematic Scenery'}</span>
          <span class="text-[10px] text-slate-400 font-mono">${scene.duration}s</span>
        </div>

        <!-- Spoken Text Snippet -->
        <p class="text-[11px] text-slate-300 line-clamp-2 italic mb-3">"${scene.text}"</p>
      </div>

      <!-- Action Buttons -->
      <div class="flex items-center space-x-2 pt-2 border-t border-slate-800">
        <button type="button" class="btn-play-scene flex-1 py-1 px-2 rounded-lg bg-surface-800 hover:bg-slate-700 text-xs font-semibold text-slate-200 flex items-center justify-center space-x-1 transition">
          <i data-lucide="play" class="w-3 h-3"></i>
          <span>Play Scene</span>
        </button>
        <button type="button" class="btn-swap-scene p-1 px-2 rounded-lg bg-surface-800 hover:bg-brand-600/30 text-xs font-semibold text-brand-300 flex items-center justify-center space-x-1 transition" title="Swap visual clip">
          <i data-lucide="refresh-cw" class="w-3 h-3"></i>
          <span>Swap</span>
        </button>
      </div>
    `;

    // Click on card seeks player to scene start
    card.querySelector('.btn-play-scene').addEventListener('click', (e) => {
      e.stopPropagation();
      seekToScene(index);
      if (!state.isPlaying) togglePlayPause();
    });

    card.querySelector('.btn-swap-scene').addEventListener('click', (e) => {
      e.stopPropagation();
      openSwapModal(index);
    });

    card.addEventListener('click', () => {
      seekToScene(index);
    });

    el.storyboardGrid.appendChild(card);
  });

  if (window.lucide) lucide.createIcons();
}

// Load Scene into Live Video Player
function loadSceneIntoPlayer(sceneIndex) {
  if (!state.scenes[sceneIndex]) return;
  state.currentSceneIndex = sceneIndex;
  const scene = state.scenes[sceneIndex];
  const clip = scene.selected_clip || {};
  const videoUrl = clip.preview_url || clip.video_url || '';

  if (videoUrl && el.liveVideoPlayer.dataset.src !== videoUrl) {
    el.liveVideoPlayer.dataset.src = videoUrl;
    el.liveVideoPlayer.src = videoUrl;
    el.liveVideoPlayer.load();
  }

  el.playerActiveClipBadge.textContent = `Clip: Scene #${sceneIndex + 1} (${scene.primary_query || 'Visual'})`;

  // Highlight active scene in storyboard
  document.querySelectorAll('.scene-card').forEach((card, idx) => {
    if (idx === sceneIndex) {
      card.classList.add('active-scene');
    } else {
      card.classList.remove('active-scene');
    }
  });
}

// Seek to a specific Scene
function seekToScene(sceneIndex) {
  if (sceneIndex < 0) sceneIndex = 0;
  if (sceneIndex >= state.scenes.length) sceneIndex = state.scenes.length - 1;
  const scene = state.scenes[sceneIndex];
  if (!scene) return;

  seekToTime(scene.start_time);
}

// Seek to specific timestamp (seconds)
function seekToTime(timeSec) {
  el.htmlAudio.currentTime = timeSec;
  onAudioTimeUpdate();
}

// Play / Pause Toggle
function togglePlayPause() {
  if (!state.audioId) return;

  if (el.htmlAudio.paused) {
    el.htmlAudio.play();
    state.isPlaying = true;
    el.iconTransportPlay.setAttribute('data-lucide', 'pause');
    el.iconMonitorCenterPlay.setAttribute('data-lucide', 'pause');
    el.btnAudioPlayPause.innerHTML = '<i data-lucide="pause" class="w-5 h-5"></i>';
    el.liveVideoPlayer.play().catch(() => {});
  } else {
    el.htmlAudio.pause();
    state.isPlaying = false;
    el.iconTransportPlay.setAttribute('data-lucide', 'play');
    el.iconMonitorCenterPlay.setAttribute('data-lucide', 'play');
    el.btnAudioPlayPause.innerHTML = '<i data-lucide="play" class="w-5 h-5 ml-0.5"></i>';
    el.liveVideoPlayer.pause();
  }
  if (window.lucide) lucide.createIcons();
}

// Audio Time Update Callback: Coordinates Video Scene Cutting & Subtitle Highlights
function onAudioTimeUpdate() {
  const current = el.htmlAudio.currentTime;

  // 1. Update time display
  el.audioCurrentTime.textContent = formatTime(current);
  el.monitorCurrentTime.textContent = formatTime(current, true);

  // 2. Update waveform bars
  const total = state.audioDuration || 1;
  const fraction = current / total;
  const bars = el.waveformContainer.children;
  const playedCount = Math.floor(fraction * bars.length);
  for (let i = 0; i < bars.length; i++) {
    if (i <= playedCount) {
      bars[i].classList.add('played');
    } else {
      bars[i].classList.remove('played');
    }
  }

  // 3. Multi-Clip Video Cutting: Find which scene corresponds to current audio time
  if (state.scenes.length > 0) {
    const activeIdx = state.scenes.findIndex(s => current >= s.start_time && current < s.end_time);
    const resolvedIdx = activeIdx !== -1 ? activeIdx : (current >= state.scenes[state.scenes.length - 1].end_time ? state.scenes.length - 1 : 0);

    if (resolvedIdx !== state.currentSceneIndex) {
      loadSceneIntoPlayer(resolvedIdx);
      if (state.isPlaying) {
        el.liveVideoPlayer.play().catch(() => {});
      }
    }

    // Keep video clip in sync with scene start offset
    const activeScene = state.scenes[resolvedIdx];
    if (activeScene && el.liveVideoPlayer.duration) {
      const clipOffset = (current - activeScene.start_time) % el.liveVideoPlayer.duration;
      if (Math.abs(el.liveVideoPlayer.currentTime - clipOffset) > 0.5) {
        el.liveVideoPlayer.currentTime = clipOffset;
      }
    }
  }

  // 4. Update dynamic word-by-word captions
  updateLiveCaption(current);
}

function onAudioEnded() {
  state.isPlaying = false;
  el.iconTransportPlay.setAttribute('data-lucide', 'play');
  el.iconMonitorCenterPlay.setAttribute('data-lucide', 'play');
  el.btnAudioPlayPause.innerHTML = '<i data-lucide="play" class="w-5 h-5 ml-0.5"></i>';
  el.liveVideoPlayer.pause();
  if (window.lucide) lucide.createIcons();
}

// Update Live Caption Overlay
function updateLiveCaption(currentTime) {
  if (state.selectedTemplate === 'none' || !state.captionCards.length) {
    el.liveCaptionOverlay.innerHTML = '';
    return;
  }

  // Find active caption card
  const card = state.captionCards.find(c => currentTime >= c.start_time && currentTime <= c.end_time + 0.1);
  if (!card) {
    el.liveCaptionOverlay.innerHTML = '';
    return;
  }

  // Find active word
  const activeWordIdx = (card.words || []).findIndex(w => currentTime >= w.start_time && currentTime <= w.end_time + 0.05);

  let wordsHtml = '';
  (card.words || []).forEach((w, idx) => {
    const isActive = idx === activeWordIdx;
    wordsHtml += `<span class="caption-word ${isActive ? 'active-word' : ''}">${w.word}</span>`;
  });

  el.liveCaptionOverlay.innerHTML = wordsHtml;
}

// Toggle Mute
function toggleMute() {
  state.isMuted = !state.isMuted;
  el.htmlAudio.muted = state.isMuted;
  el.iconVolume.setAttribute('data-lucide', state.isMuted ? 'volume-x' : 'volume-2');
  if (window.lucide) lucide.createIcons();
}

// Swap Clip Modal Handlers
function openSwapModal(sceneIndex) {
  state.activeSwappingSceneIndex = sceneIndex;
  const scene = state.scenes[sceneIndex];
  if (!scene) return;

  el.swapModalSubtitle.textContent = `Scene #${sceneIndex + 1} (${scene.primary_query || 'Visual'})`;
  el.swapSearchInput.value = scene.primary_query || '';
  el.swapClipModal.classList.remove('hidden');

  handleSwapSearch();
}

async function handleSwapSearch() {
  const query = el.swapSearchInput.value.trim() || 'cinematic';
  el.swapClipsGrid.innerHTML = '<div class="col-span-3 py-10 text-center text-xs text-slate-400">Searching footage...</div>';

  try {
    const resp = await fetch('/api/swap-clip', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        query: query,
        aspect_ratio: state.aspectRatio
      })
    });
    const data = await resp.json();
    const videos = data.videos || [];

    el.swapClipsGrid.innerHTML = '';
    if (!videos.length) {
      el.swapClipsGrid.innerHTML = '<div class="col-span-3 py-10 text-center text-xs text-slate-400">No clips found. Try another query.</div>';
      return;
    }

    videos.forEach(v => {
      const item = document.createElement('div');
      item.className = 'relative aspect-video rounded-lg overflow-hidden bg-black cursor-pointer border border-slate-800 hover:border-brand-500 transition group';
      item.innerHTML = `
        <img src="${v.image}" class="w-full h-full object-cover">
        <div class="absolute inset-0 bg-brand-600/20 opacity-0 group-hover:opacity-100 flex items-center justify-center transition">
          <span class="px-2.5 py-1 rounded bg-brand-600 text-white text-xs font-bold shadow">Select</span>
        </div>
      `;
      item.addEventListener('click', () => {
        if (state.activeSwappingSceneIndex !== null) {
          state.scenes[state.activeSwappingSceneIndex].selected_clip = v;
          renderStoryboard(state.scenes);
          if (state.currentSceneIndex === state.activeSwappingSceneIndex) {
            loadSceneIntoPlayer(state.activeSwappingSceneIndex);
          }
          el.swapClipModal.classList.add('hidden');
        }
      });
      el.swapClipsGrid.appendChild(item);
    });
  } catch (err) {
    el.swapClipsGrid.innerHTML = `<div class="col-span-3 py-10 text-center text-xs text-rose-400">Search error: ${err.message}</div>`;
  }
}

// Render Final MP4 Video
async function handleRenderVideo() {
  if (!state.audioId || !state.scenes.length) {
    alert('Please generate scenes from your audio before exporting.');
    return;
  }

  el.renderProgressModal.classList.remove('hidden');
  el.renderSuccessContainer.classList.add('hidden');
  el.renderStatusMessage.textContent = 'Preparing footage and composing timeline...';
  el.renderProgressBar.style.width = '10%';
  el.renderProgressPercent.textContent = '10%';

  try {
    const resp = await fetch('/api/render', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        audio_id: state.audioId,
        scenes: state.scenes,
        aspect_ratio: state.aspectRatio,
        caption_template: state.selectedTemplate,
        highlight_color: state.highlightColor,
        enable_shine: state.enableShine,
        caption_cards: state.captionCards,
        transition_type: 'fade',
        transition_duration: 0.8
      })
    });

    if (!resp.ok) throw new Error('Render initiation failed');
    const data = await resp.json();
    const jobId = data.job_id;

    pollRenderStatus(jobId);
  } catch (err) {
    el.renderStatusMessage.textContent = 'Render error: ' + err.message;
  }
}

// Poll Render Progress
function pollRenderStatus(jobId) {
  const timer = setInterval(async () => {
    try {
      const resp = await fetch(`/api/render-status/${jobId}`);
      if (!resp.ok) return;
      const status = await resp.json();

      el.renderProgressBar.style.width = `${status.progress}%`;
      el.renderProgressPercent.textContent = `${status.progress}%`;
      el.renderStatusMessage.textContent = status.message || 'Rendering...';

      if (status.status === 'done') {
        clearInterval(timer);
        el.renderProgressBar.style.width = '100%';
        el.renderProgressPercent.textContent = '100%';
        el.renderStatusMessage.textContent = 'Render complete! Your video is ready.';
        el.btnDownloadFinishedVideo.href = status.download_url;
        el.renderSuccessContainer.classList.remove('hidden');
      } else if (status.status === 'error') {
        clearInterval(timer);
        el.renderStatusMessage.textContent = 'Render failed: ' + status.message;
      }
    } catch (e) {
      console.error('Polling error:', e);
    }
  }, 1000);
}

// Helper: Format Time in MM:SS
function formatTime(sec, showSubSec = false) {
  if (!sec || isNaN(sec)) return showSubSec ? '00:00.0' : '00:00';
  const mins = Math.floor(sec / 60);
  const secs = Math.floor(sec % 60);
  const sub = Math.floor((sec % 1) * 10);
  const padM = String(mins).padStart(2, '0');
  const padS = String(secs).padStart(2, '0');
  return showSubSec ? `${padM}:${padS}.${sub}` : `${padM}:${padS}`;
}

// Start app on DOM load
document.addEventListener('DOMContentLoaded', initApp);
