// State management
const state = {
  audioId: null,
  audioDuration: 0,
  audioFileName: '',
  waveformPeaks: [],
  scenes: [],
  aspectRatio: '16:9',
  transitionType: 'dissolve',
  transitionDuration: 0.8,
  selectedTemplate: 'capcut_classic',
  selectedHighlightColor: 'yellow',
  captionTemplates: [],
  highlightColors: {},
  captionCards: [],
  timedWords: [],
  activeCategory: 'All',
  pexelsApiKey: localStorage.getItem('synchro_pexels_api_key') || '',
  activeSwapSceneIndex: null,
  currentPlayingAudio: false,
  renderPollInterval: null
};

// DOM Elements
const elements = {
  audioDropzone: document.getElementById('audioDropzone'),
  audioFileInput: document.getElementById('audioFileInput'),
  audioPlayerCard: document.getElementById('audioPlayerCard'),
  audioDurationBadge: document.getElementById('audioDurationBadge'),
  audioFileName: document.getElementById('audioFileName'),
  waveformBars: document.getElementById('waveformBars'),
  waveformPlayhead: document.getElementById('waveformPlayhead'),
  btnAudioPlayPause: document.getElementById('btnAudioPlayPause'),
  audioCurrentTime: document.getElementById('audioCurrentTime'),
  audioTotalTime: document.getElementById('audioTotalTime'),
  htmlAudio: document.getElementById('htmlAudioElement'),
  btnRemoveAudio: document.getElementById('btnRemoveAudio'),
  scriptInput: document.getElementById('scriptInput'),
  scriptWordCount: document.getElementById('scriptWordCount'),
  btnAutoTranscribe: document.getElementById('btnAutoTranscribe'),
  captionStatusIndicator: document.getElementById('captionStatusIndicator'),
  selectAspectRatio: document.getElementById('selectAspectRatio'),
  selectTransition: document.getElementById('selectTransition'),
  sliderTransitionDur: document.getElementById('sliderTransitionDur'),
  transitionDurLabel: document.getElementById('transitionDurLabel'),
  btnGenerateScenes: document.getElementById('btnGenerateScenes'),
  // Caption Template Section
  highlightColorPills: document.getElementById('highlightColorPills'),
  captionTemplatesGrid: document.getElementById('captionTemplatesGrid'),
  captionCatTabs: document.querySelectorAll('.caption-cat-tab'),
  // Storyboard & Live Preview
  storyboardSection: document.getElementById('storyboardSection'),
  storyboardGrid: document.getElementById('storyboardGrid'),
  timelineSegmentsBar: document.getElementById('timelineSegmentsBar'),
  timelineTotalDuration: document.getElementById('timelineTotalDuration'),
  btnAutoMatchAllAgain: document.getElementById('btnAutoMatchAllAgain'),
  btnRenderVideo: document.getElementById('btnRenderVideo'),
  btnLoadDemo: document.getElementById('btnLoadDemo'),
  livePreviewVideo: document.getElementById('livePreviewVideo'),
  liveCaptionOverlay: document.getElementById('liveCaptionOverlay'),
  activeTemplateBadge: document.getElementById('activeTemplateBadge'),
  // GitHub & Download
  btnGitHub: document.getElementById('btnGitHub'),
  gitHubModal: document.getElementById('gitHubModal'),
  btnCloseGitHubModal: document.getElementById('btnCloseGitHubModal'),
  // Pexels Key Modal
  btnApiKeyToggle: document.getElementById('btnApiKeyToggle'),
  apiKeyModal: document.getElementById('apiKeyModal'),
  btnCloseApiKeyModal: document.getElementById('btnCloseApiKeyModal'),
  inputPexelsKey: document.getElementById('inputPexelsKey'),
  btnSaveApiKey: document.getElementById('btnSaveApiKey'),
  apiKeyStatusDot: document.getElementById('apiKeyStatusDot'),
  apiKeyLabel: document.getElementById('apiKeyLabel'),
  // Swap Clip Modal
  swapClipModal: document.getElementById('swapClipModal'),
  btnCloseSwapModal: document.getElementById('btnCloseSwapModal'),
  swapModalSubtitle: document.getElementById('swapModalSubtitle'),
  swapSearchInput: document.getElementById('swapSearchInput'),
  btnExecuteSearch: document.getElementById('btnExecuteSearch'),
  swapSuggestedChips: document.getElementById('swapSuggestedChips'),
  swapResultsGrid: document.getElementById('swapResultsGrid'),
  // Render Progress Modal
  renderProgressModal: document.getElementById('renderProgressModal'),
  renderProgressBar: document.getElementById('renderProgressBar'),
  renderPercentText: document.getElementById('renderPercentText'),
  renderPhaseText: document.getElementById('renderPhaseText'),
  renderResultBox: document.getElementById('renderResultBox'),
  renderedVideoPlayer: document.getElementById('renderedVideoPlayer'),
  btnDownloadVideo: document.getElementById('btnDownloadVideo'),
  btnCloseRenderModal: document.getElementById('btnCloseRenderModal')
};

// Initialize UI
async function init() {
  updateApiKeyStatusUI();
  setupEventListeners();
  await loadCaptionTemplates();
  lucide.createIcons();
}

function updateApiKeyStatusUI() {
  if (state.pexelsApiKey) {
    elements.apiKeyStatusDot.className = 'w-2 h-2 rounded-full bg-emerald-400';
    elements.apiKeyLabel.textContent = 'Pexels API: Active';
    elements.inputPexelsKey.value = state.pexelsApiKey;
  } else {
    elements.apiKeyStatusDot.className = 'w-2 h-2 rounded-full bg-amber-400';
    elements.apiKeyLabel.textContent = 'Pexels API (Free)';
  }
}

async function loadCaptionTemplates() {
  try {
    const resp = await fetch('/api/caption-templates');
    const data = await resp.json();
    state.captionTemplates = data.templates || [];
    state.highlightColors = data.colors || {};

    renderHighlightColors();
    renderCaptionTemplates();
  } catch (e) {
    console.error('Failed to load caption templates:', e);
  }
}

function renderHighlightColors() {
  elements.highlightColorPills.innerHTML = '';
  Object.entries(state.highlightColors).forEach(([key, info]) => {
    const btn = document.createElement('button');
    btn.className = `w-5 h-5 rounded-full border-2 transition ${state.selectedHighlightColor === key ? 'border-white scale-110 shadow' : 'border-transparent hover:scale-105'}`;
    btn.style.backgroundColor = info.hex;
    btn.title = info.name;
    btn.addEventListener('click', () => {
      state.selectedHighlightColor = key;
      renderHighlightColors();
      updateLiveKaraokeCaption(elements.htmlAudio.currentTime || 0);
    });
    elements.highlightColorPills.appendChild(btn);
  });
}

function renderCaptionTemplates() {
  elements.captionTemplatesGrid.innerHTML = '';

  const filtered = state.captionTemplates.filter(tpl => {
    if (state.activeCategory === 'All') return true;
    return tpl.category.toLowerCase() === state.activeCategory.toLowerCase();
  });

  filtered.forEach(tpl => {
    const isSelected = state.selectedTemplate === tpl.id;
    const card = document.createElement('div');
    card.className = `caption-card relative bg-surface-850 border border-slate-800 rounded-xl p-3 flex flex-col justify-between h-28 select-none ${isSelected ? 'active-tpl' : ''}`;
    
    // Top badge
    const badgeText = tpl.badge || 'Pro';
    const badgeColor = tpl.id === 'none' ? 'bg-slate-700 text-slate-300' : 'bg-brand-500/20 text-brand-400 border border-brand-500/30';

    card.innerHTML = `
      <div class="flex items-center justify-between">
        <span class="text-[9px] uppercase font-bold px-1.5 py-0.5 rounded ${badgeColor}">${badgeText}</span>
        ${isSelected ? '<i data-lucide="check-circle-2" class="w-3.5 h-3.5 text-brand-400"></i>' : ''}
      </div>

      <!-- Preview Text Display Styled Like Reference Image -->
      <div class="flex-1 flex items-center justify-center text-center px-1 my-1 overflow-hidden">
        ${getTemplatePreviewHtml(tpl)}
      </div>

      <div class="text-[10px] text-slate-400 font-medium truncate text-center">
        ${tpl.name}
      </div>
    `;

    card.addEventListener('click', () => {
      state.selectedTemplate = tpl.id;
      elements.activeTemplateBadge.textContent = tpl.name;
      renderCaptionTemplates();
      updateLiveKaraokeCaption(elements.htmlAudio.currentTime || 0);
    });

    elements.captionTemplatesGrid.appendChild(card);
  });

  lucide.createIcons();
}

function getTemplatePreviewHtml(tpl) {
  if (tpl.id === 'none') {
    return '<span class="text-xs text-slate-500 italic">No Captions</span>';
  }

  const highlightHex = state.highlightColors[state.selectedHighlightColor]?.hex || '#facc15';

  if (tpl.id === 'capcut_classic') {
    return `
      <span class="font-extrabold uppercase text-[11px] tracking-tight leading-tight" style="font-family: Impact, Arial Black; color: #ffffff; text-shadow: 0 2px 4px #000;">
        THE <span style="color: ${highlightHex};">${tpl.preview_highlight}</span>
      </span>
    `;
  } else if (tpl.id === 'neon_fox') {
    return `
      <span class="font-extrabold uppercase text-xs tracking-wider" style="color: #ffffff; text-shadow: 0 0 8px #ff00ea, 0 0 15px #00ffff;">
        ${tpl.preview_highlight}
      </span>
    `;
  } else if (tpl.id === 'red_fire') {
    return `
      <span class="font-extrabold uppercase text-[11px] tracking-tight" style="color: #ff2a2a; text-shadow: 0 0 10px #ff0000;">
        THE <span style="color: ${highlightHex};">${tpl.preview_highlight}</span>
      </span>
    `;
  } else if (tpl.id === 'cinematic_serif') {
    return `
      <span class="font-serif italic text-[11px] leading-tight" style="color: #ffffff; text-shadow: 0 1px 4px rgba(0,0,0,0.8);">
        The <span style="color: ${highlightHex};">${tpl.preview_highlight}</span> fox
      </span>
    `;
  } else if (tpl.id === 'word_pop') {
    return `
      <span class="font-extrabold uppercase text-base" style="font-family: Impact; color: ${highlightHex}; text-shadow: 0 3px 6px #000;">
        ${tpl.preview_highlight}
      </span>
    `;
  } else if (tpl.id === 'minimal_monoline') {
    return `
      <span class="text-[10px] bg-black/60 px-2 py-0.5 rounded-full text-slate-100">
        ${tpl.preview_highlight}
      </span>
    `;
  }

  return `<span class="text-xs font-bold uppercase text-white">${tpl.preview_highlight}</span>`;
}

function setupEventListeners() {
  // Script input word count
  elements.scriptInput.addEventListener('input', () => {
    const text = elements.scriptInput.value.trim();
    const words = text ? text.split(/\s+/).length : 0;
    elements.scriptWordCount.textContent = `${words} word${words === 1 ? '' : 's'}`;
  });

  // Auto-transcribe button
  elements.btnAutoTranscribe.addEventListener('click', handleAutoTranscribe);

  // Category filter tabs
  elements.captionCatTabs.forEach(tab => {
    tab.addEventListener('click', () => {
      elements.captionCatTabs.forEach(t => t.classList.remove('active', 'bg-brand-600', 'text-white'));
      elements.captionCatTabs.forEach(t => t.classList.add('bg-surface-850', 'text-slate-300'));
      tab.classList.add('active', 'bg-brand-600', 'text-white');
      tab.classList.remove('bg-surface-850', 'text-slate-300');

      state.activeCategory = tab.dataset.cat;
      renderCaptionTemplates();
    });
  });

  // Aspect ratio & transition
  elements.selectAspectRatio.addEventListener('change', (e) => {
    state.aspectRatio = e.target.value;
  });
  elements.selectTransition.addEventListener('change', (e) => {
    state.transitionType = e.target.value;
  });
  elements.sliderTransitionDur.addEventListener('input', (e) => {
    state.transitionDuration = parseFloat(e.target.value);
    elements.transitionDurLabel.textContent = `${state.transitionDuration.toFixed(1)}s`;
  });

  // Audio drag & drop
  elements.audioDropzone.addEventListener('dragover', (e) => {
    e.preventDefault();
    elements.audioDropzone.classList.add('border-brand-500');
  });
  elements.audioDropzone.addEventListener('dragleave', () => {
    elements.audioDropzone.classList.remove('border-brand-500');
  });
  elements.audioDropzone.addEventListener('drop', (e) => {
    e.preventDefault();
    elements.audioDropzone.classList.remove('border-brand-500');
    if (e.dataTransfer.files.length) {
      handleAudioUpload(e.dataTransfer.files[0]);
    }
  });
  elements.audioFileInput.addEventListener('change', (e) => {
    if (e.target.files.length) {
      handleAudioUpload(e.target.files[0]);
    }
  });

  // Audio player controls
  elements.btnAudioPlayPause.addEventListener('click', toggleAudioPlayback);
  elements.btnRemoveAudio.addEventListener('click', resetAudio);
  elements.htmlAudio.addEventListener('timeupdate', updateAudioPlayhead);
  elements.htmlAudio.addEventListener('ended', () => {
    state.currentPlayingAudio = false;
    updateAudioPlayButtonIcon();
    elements.waveformPlayhead.style.left = '0%';
    elements.liveCaptionOverlay.innerHTML = '';
  });

  // Generate scenes button
  elements.btnGenerateScenes.addEventListener('click', handleGenerateScenes);
  elements.btnAutoMatchAllAgain.addEventListener('click', () => handleAutoMatchAll(state.scenes));

  // Render video
  elements.btnRenderVideo.addEventListener('click', handleRenderVideo);

  // Demo loader
  elements.btnLoadDemo.addEventListener('click', handleLoadDemo);

  // GitHub Modal
  elements.btnGitHub.addEventListener('click', () => {
    elements.gitHubModal.classList.remove('hidden');
  });
  elements.btnCloseGitHubModal.addEventListener('click', () => {
    elements.gitHubModal.classList.add('hidden');
  });

  // API Key Modal
  elements.btnApiKeyToggle.addEventListener('click', () => {
    elements.apiKeyModal.classList.remove('hidden');
  });
  elements.btnCloseApiKeyModal.addEventListener('click', () => {
    elements.apiKeyModal.classList.add('hidden');
  });
  elements.btnSaveApiKey.addEventListener('click', () => {
    const key = elements.inputPexelsKey.value.trim();
    state.pexelsApiKey = key;
    if (key) {
      localStorage.setItem('synchro_pexels_api_key', key);
    } else {
      localStorage.removeItem('synchro_pexels_api_key');
    }
    updateApiKeyStatusUI();
    elements.apiKeyModal.classList.add('hidden');
  });

  // Swap Clip Modal
  elements.btnCloseSwapModal.addEventListener('click', () => {
    elements.swapClipModal.classList.add('hidden');
  });
  elements.btnExecuteSearch.addEventListener('click', executeSwapSearch);
  elements.swapSearchInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter') executeSwapSearch();
  });

  // Render progress modal close
  elements.btnCloseRenderModal.addEventListener('click', () => {
    elements.renderProgressModal.classList.add('hidden');
  });
}

// Audio Upload Handler
async function handleAudioUpload(file) {
  const formData = new FormData();
  formData.append('file', file);

  elements.audioDropzone.classList.add('opacity-50', 'pointer-events-none');
  const originalText = elements.audioDropzone.querySelector('p').textContent;
  elements.audioDropzone.querySelector('p').textContent = 'Analyzing audio duration & waveforms...';

  try {
    const resp = await fetch('/api/upload-audio', {
      method: 'POST',
      body: formData
    });
    if (!resp.ok) {
      const err = await resp.json();
      throw new Error(err.detail || 'Failed to upload audio');
    }

    const data = await resp.json();
    setAudioState(data);
  } catch (err) {
    alert('Upload error: ' + err.message);
  } finally {
    elements.audioDropzone.classList.remove('opacity-50', 'pointer-events-none');
    elements.audioDropzone.querySelector('p').textContent = originalText;
  }
}

function setAudioState(data) {
  state.audioId = data.audio_id;
  state.audioDuration = data.duration;
  state.audioFileName = data.filename;
  state.waveformPeaks = data.waveform || [];

  // Update UI
  elements.audioDropzone.classList.add('hidden');
  elements.audioPlayerCard.classList.remove('hidden');
  elements.audioDurationBadge.classList.remove('hidden');
  elements.audioDurationBadge.textContent = data.formatted_duration;
  elements.audioFileName.textContent = data.filename;
  elements.audioTotalTime.textContent = formatTime(data.duration);
  elements.audioCurrentTime.textContent = '00:00';

  // Audio source
  elements.htmlAudio.src = `/api/audio/${data.audio_id}`;
  elements.htmlAudio.load();

  // Render waveform
  renderWaveform(state.waveformPeaks);
}

function resetAudio() {
  state.audioId = null;
  state.audioDuration = 0;
  elements.htmlAudio.pause();
  elements.htmlAudio.src = '';
  elements.audioPlayerCard.classList.add('hidden');
  elements.audioDropzone.classList.remove('hidden');
  elements.audioDurationBadge.classList.add('hidden');
  elements.liveCaptionOverlay.innerHTML = '';
}

function renderWaveform(peaks) {
  elements.waveformBars.innerHTML = '';
  peaks.forEach((peak, i) => {
    const bar = document.createElement('div');
    bar.className = 'waveform-bar w-1 bg-slate-700 rounded-full cursor-pointer hover:bg-brand-400';
    bar.style.height = `${Math.max(12, peak * 100)}%`;
    bar.dataset.index = i;
    bar.addEventListener('click', () => {
      const progress = i / peaks.length;
      elements.htmlAudio.currentTime = progress * state.audioDuration;
      if (!state.currentPlayingAudio) toggleAudioPlayback();
    });
    elements.waveformBars.appendChild(bar);
  });
}

function toggleAudioPlayback() {
  if (elements.htmlAudio.paused) {
    elements.htmlAudio.play();
    state.currentPlayingAudio = true;
    if (elements.livePreviewVideo.src) {
      elements.livePreviewVideo.currentTime = elements.htmlAudio.currentTime;
      elements.livePreviewVideo.play().catch(() => {});
    }
  } else {
    elements.htmlAudio.pause();
    state.currentPlayingAudio = false;
    elements.livePreviewVideo.pause();
  }
  updateAudioPlayButtonIcon();
}

function updateAudioPlayButtonIcon() {
  elements.btnAudioPlayPause.innerHTML = state.currentPlayingAudio
    ? '<i data-lucide="pause" class="w-4 h-4 fill-current"></i>'
    : '<i data-lucide="play" class="w-4 h-4 fill-current"></i>';
  lucide.createIcons();
}

function updateAudioPlayhead() {
  const current = elements.htmlAudio.currentTime;
  const total = state.audioDuration || 1;
  const percent = (current / total) * 100;
  
  elements.audioCurrentTime.textContent = formatTime(current);
  elements.waveformPlayhead.style.left = `${Math.min(100, percent)}%`;

  // Highlight active waveform bars
  const totalBars = elements.waveformBars.children.length;
  const activeCount = Math.floor((percent / 100) * totalBars);
  Array.from(elements.waveformBars.children).forEach((bar, idx) => {
    if (idx <= activeCount) {
      bar.classList.add('active');
    } else {
      bar.classList.remove('active');
    }
  });

  // Sync live video preview
  syncLiveVideoScene(current);

  // Sync live CapCut karaoke captions
  updateLiveKaraokeCaption(current);
}

function syncLiveVideoScene(currentTime) {
  if (!state.scenes.length) return;
  const activeScene = state.scenes.find(s => currentTime >= s.start_time && currentTime < s.end_time) || state.scenes[0];
  if (activeScene && activeScene.selected_clip) {
    const videoUrl = activeScene.selected_clip.preview_url || activeScene.selected_clip.video_url;
    if (elements.livePreviewVideo.dataset.src !== videoUrl) {
      elements.livePreviewVideo.dataset.src = videoUrl;
      elements.livePreviewVideo.src = videoUrl;
      elements.livePreviewVideo.load();
      if (state.currentPlayingAudio) {
        elements.livePreviewVideo.play().catch(() => {});
      }
    }
  }
}

// Real-time CapCut word-by-word highlight in player
function updateLiveKaraokeCaption(currentTime) {
  if (state.selectedTemplate === 'none' || !state.captionCards.length) {
    elements.liveCaptionOverlay.innerHTML = '';
    return;
  }

  // Find active caption card
  const activeCard = state.captionCards.find(c => currentTime >= c.start_time && currentTime <= c.end_time + 0.1);
  if (!activeCard) {
    elements.liveCaptionOverlay.innerHTML = '';
    return;
  }

  const highlightHex = state.highlightColors[state.selectedHighlightColor]?.hex || '#facc15';
  const tplClass = `tpl-${state.selectedTemplate}`;

  elements.liveCaptionOverlay.className = `absolute inset-x-4 bottom-6 flex flex-wrap items-center justify-center text-center pointer-events-none transition duration-150 ${tplClass}`;

  const wordsHtml = activeCard.words.map(w => {
    const isSpoken = currentTime >= w.start && currentTime <= w.end;
    const highlightStyle = isSpoken
      ? `color: ${highlightHex}; text-shadow: 0 0 16px ${highlightHex}, 0 2px 4px #000; font-weight: 900;`
      : '';
    return `
      <span class="karaoke-word ${isSpoken ? 'active-word' : ''}" style="${highlightStyle}">
        ${w.word}
      </span>
    `;
  }).join(' ');

  elements.liveCaptionOverlay.innerHTML = wordsHtml;
}

// Auto-transcribe audio via SpeechRecognition
async function handleAutoTranscribe() {
  if (!state.audioId) {
    alert('Please upload an audio file first.');
    return;
  }

  elements.btnAutoTranscribe.disabled = true;
  elements.btnAutoTranscribe.innerHTML = '<i data-lucide="loader-2" class="w-3 h-3 animate-spin"></i><span>Transcribing...</span>';
  lucide.createIcons();

  try {
    const resp = await fetch('/api/generate-captions', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        audio_id: state.audioId,
        script_text: '',
        template_id: state.selectedTemplate
      })
    });
    if (!resp.ok) throw new Error('Speech recognition failed');
    const data = await resp.json();

    if (data.transcript) {
      elements.scriptInput.value = data.transcript;
      elements.scriptInput.dispatchEvent(new Event('input'));
    }

    state.captionCards = data.cards || [];
    state.timedWords = data.words || [];
    elements.captionStatusIndicator.textContent = `Aligned ${state.timedWords.length} words`;
  } catch (err) {
    alert('Speech recognition error: ' + err.message);
  } finally {
    elements.btnAutoTranscribe.disabled = false;
    elements.btnAutoTranscribe.innerHTML = '<i data-lucide="mic" class="w-3 h-3"></i><span>Auto-Transcribe Audio</span>';
    lucide.createIcons();
  }
}

// Demo Sample Loader
async function handleLoadDemo() {
  elements.btnLoadDemo.disabled = true;
  elements.btnLoadDemo.innerHTML = '<i data-lucide="loader-2" class="w-3.5 h-3.5 animate-spin"></i><span>Loading Demo...</span>';
  lucide.createIcons();

  try {
    const resp = await fetch('/api/sample-demo');
    const data = await resp.json();

    setAudioState(data);
    elements.scriptInput.value = data.script;
    elements.scriptInput.dispatchEvent(new Event('input'));

    await handleGenerateScenes();
  } catch (e) {
    alert('Failed to load demo: ' + e.message);
  } finally {
    elements.btnLoadDemo.disabled = false;
    elements.btnLoadDemo.innerHTML = '<i data-lucide="sparkles" class="w-3.5 h-3.5 text-amber-400"></i><span>Try Demo Sample</span>';
    lucide.createIcons();
  }
}

// Generate Scenes & Storyboard
async function handleGenerateScenes() {
  if (!state.audioId) {
    alert('Please upload an audio file first.');
    return;
  }

  const script = elements.scriptInput.value.trim();
  if (!script) {
    alert('Please enter or paste the transcript text corresponding to the audio.');
    return;
  }

  elements.btnGenerateScenes.disabled = true;
  elements.btnGenerateScenes.innerHTML = '<i data-lucide="loader-2" class="w-4 h-4 animate-spin"></i><span>Analyzing Script Pacing...</span>';
  lucide.createIcons();

  try {
    // 1. Segment script
    const segmentResp = await fetch('/api/segment-script', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        audio_id: state.audioId,
        script_text: script
      })
    });
    if (!segmentResp.ok) throw new Error('Segmentation failed');
    const segmentData = await segmentResp.json();
    
    // 2. Align word-level karaoke timestamps for CapCut captions
    elements.btnGenerateScenes.innerHTML = '<i data-lucide="loader-2" class="w-4 h-4 animate-spin"></i><span>Aligning Word Highlights...</span>';
    lucide.createIcons();

    const captionResp = await fetch('/api/generate-captions', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        audio_id: state.audioId,
        script_text: script,
        template_id: state.selectedTemplate
      })
    });
    if (captionResp.ok) {
      const captionData = await captionResp.json();
      state.captionCards = captionData.cards || [];
      state.timedWords = captionData.words || [];
      elements.captionStatusIndicator.textContent = `Aligned ${state.timedWords.length} words`;
    }

    // 3. Auto-match clips for each scene
    elements.btnGenerateScenes.innerHTML = '<i data-lucide="loader-2" class="w-4 h-4 animate-spin"></i><span>Matching Pexels Footage...</span>';
    lucide.createIcons();

    await handleAutoMatchAll(segmentData.scenes);

    // Scroll to storyboard
    elements.storyboardSection.classList.remove('hidden');
    elements.storyboardSection.scrollIntoView({ behavior: 'smooth' });

  } catch (err) {
    alert('Error generating scenes: ' + err.message);
  } finally {
    elements.btnGenerateScenes.disabled = false;
    elements.btnGenerateScenes.innerHTML = '<i data-lucide="wand-2" class="w-4 h-4"></i><span>Analyze, Match & Style</span>';
    lucide.createIcons();
  }
}

async function handleAutoMatchAll(scenes) {
  try {
    const matchResp = await fetch('/api/auto-match-all', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        scenes: scenes,
        api_key: state.pexelsApiKey,
        orientation: state.aspectRatio === '9:16' ? 'portrait' : 'landscape'
      })
    });
    if (!matchResp.ok) throw new Error('Auto-match failed');
    const matchData = await matchResp.json();

    state.scenes = matchData.scenes;
    renderStoryboard();
    renderTimelineOverview();

    // Init live preview video with scene 1
    if (state.scenes.length && state.scenes[0].selected_clip) {
      const firstUrl = state.scenes[0].selected_clip.preview_url || state.scenes[0].selected_clip.video_url;
      elements.livePreviewVideo.dataset.src = firstUrl;
      elements.livePreviewVideo.src = firstUrl;
    }
  } catch (e) {
    alert('Auto match error: ' + e.message);
  }
}

// Render Storyboard Grid
function renderStoryboard() {
  elements.storyboardGrid.innerHTML = '';

  state.scenes.forEach((scene, index) => {
    const card = document.createElement('div');
    card.className = 'storyboard-card bg-surface-900 border border-slate-800 rounded-2xl overflow-hidden flex flex-col justify-between shadow-lg relative group';
    
    const clip = scene.selected_clip || {};
    const thumbUrl = clip.image || 'https://images.unsplash.com/photo-1506744038136-46273834b3fb?w=640&q=80';
    const previewVideoUrl = clip.preview_url || clip.video_url || '';

    card.innerHTML = `
      <div>
        <!-- Video Preview Container -->
        <div class="video-preview-wrapper relative aspect-video bg-black overflow-hidden group/video">
          <img src="${thumbUrl}" alt="Scene Preview" class="w-full h-full object-cover transition duration-300 group-hover/video:opacity-0">
          ${previewVideoUrl ? `
            <video src="${previewVideoUrl}" muted loop preload="none" class="absolute inset-0 w-full h-full object-cover opacity-0 group-hover/video:opacity-100 transition duration-300"></video>
          ` : ''}
          <div class="absolute top-2 left-2 bg-black/70 backdrop-blur-sm text-[11px] font-mono font-semibold text-white px-2 py-0.5 rounded-md border border-white/10">
            Scene #${index + 1}
          </div>
          <div class="absolute top-2 right-2 bg-brand-500/80 backdrop-blur-sm text-[11px] font-mono font-semibold text-white px-2 py-0.5 rounded-md border border-brand-400/30">
            ${scene.duration.toFixed(1)}s
          </div>
          <div class="absolute bottom-2 left-2 right-2 flex items-center justify-between pointer-events-none opacity-0 group-hover/video:opacity-100 transition text-[10px] text-white/90">
            <span class="bg-black/60 px-1.5 py-0.5 rounded truncate max-w-[140px]">${clip.author || 'Pexels'}</span>
            <span class="bg-black/60 px-1.5 py-0.5 rounded">Hover to play</span>
          </div>
        </div>

        <!-- Scene Content -->
        <div class="p-4 space-y-2.5">
          <div class="flex items-center justify-between text-[11px] text-slate-400 font-mono">
            <span>${scene.formatted_time}</span>
            <span class="text-brand-400 capitalize truncate max-w-[110px]" title="${scene.primary_query}">🔍 ${scene.primary_query}</span>
          </div>

          <p class="text-xs text-slate-200 line-clamp-3 leading-relaxed" title="${scene.text}">
            "${scene.text}"
          </p>
        </div>
      </div>

      <!-- Card Actions -->
      <div class="p-3 bg-surface-850 border-t border-slate-800/80 flex items-center justify-between">
        <div class="flex items-center space-x-1">
          <button class="btn-move-left p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-slate-700/60 transition ${index === 0 ? 'opacity-30 pointer-events-none' : ''}" title="Move Earlier">
            <i data-lucide="chevron-left" class="w-4 h-4"></i>
          </button>
          <button class="btn-move-right p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-slate-700/60 transition ${index === state.scenes.length - 1 ? 'opacity-30 pointer-events-none' : ''}" title="Move Later">
            <i data-lucide="chevron-right" class="w-4 h-4"></i>
          </button>
        </div>

        <button class="btn-swap-clip text-xs px-2.5 py-1.5 rounded-lg bg-surface-900 hover:bg-slate-800 text-brand-400 hover:text-brand-300 border border-slate-700 flex items-center space-x-1.5 transition">
          <i data-lucide="refresh-ccw" class="w-3 h-3"></i>
          <span>Swap Clip</span>
        </button>
      </div>
    `;

    // Hover-to-play video event listeners
    const videoEl = card.querySelector('video');
    if (videoEl) {
      const wrapper = card.querySelector('.video-preview-wrapper');
      wrapper.addEventListener('mouseenter', () => videoEl.play().catch(() => {}));
      wrapper.addEventListener('mouseleave', () => {
        videoEl.pause();
        videoEl.currentTime = 0;
      });
    }

    // Move left/right handlers
    card.querySelector('.btn-move-left').addEventListener('click', () => moveScene(index, index - 1));
    card.querySelector('.btn-move-right').addEventListener('click', () => moveScene(index, index + 1));
    
    // Swap clip handler
    card.querySelector('.btn-swap-clip').addEventListener('click', () => openSwapModal(index));

    elements.storyboardGrid.appendChild(card);
  });

  lucide.createIcons();
}

function renderTimelineOverview() {
  elements.timelineSegmentsBar.innerHTML = '';
  const total = state.audioDuration || 1;
  elements.timelineTotalDuration.textContent = `Total: ${formatTime(total)}`;

  const colors = [
    'bg-indigo-600', 'bg-violet-600', 'bg-purple-600', 'bg-blue-600', 'bg-sky-600', 'bg-teal-600'
  ];

  state.scenes.forEach((scene, i) => {
    const widthPct = (scene.duration / total) * 100;
    const color = colors[i % colors.length];

    const block = document.createElement('div');
    block.className = `${color} h-full border-r border-slate-900 flex items-center justify-center text-[10px] font-mono text-white font-medium truncate px-1 transition hover:brightness-125 cursor-pointer`;
    block.style.width = `${widthPct}%`;
    block.textContent = `#${i+1} (${scene.duration.toFixed(1)}s)`;
    block.title = `Scene #${i+1}: ${scene.text} (${scene.formatted_time})`;

    block.addEventListener('click', () => {
      elements.htmlAudio.currentTime = scene.start_time;
      if (elements.htmlAudio.paused) toggleAudioPlayback();
    });

    elements.timelineSegmentsBar.appendChild(block);
  });
}

function moveScene(fromIndex, toIndex) {
  if (toIndex < 0 || toIndex >= state.scenes.length) return;
  const temp = state.scenes[fromIndex];
  state.scenes[fromIndex] = state.scenes[toIndex];
  state.scenes[toIndex] = temp;

  let cur = 0;
  state.scenes.forEach((s, idx) => {
    s.id = idx + 1;
    s.start_time = round(cur, 2);
    s.end_time = round(cur + s.duration, 2);
    s.formatted_time = `${formatTime(s.start_time)} - ${formatTime(s.end_time)}`;
    cur = s.end_time;
  });

  renderStoryboard();
  renderTimelineOverview();
}

// Swap Clip Modal Logic
function openSwapModal(sceneIndex) {
  state.activeSwapSceneIndex = sceneIndex;
  const scene = state.scenes[sceneIndex];

  elements.swapModalSubtitle.textContent = `Replacing footage for Scene #${sceneIndex + 1}: "${scene.text.substring(0, 60)}..."`;
  elements.swapSearchInput.value = scene.primary_query;

  elements.swapSuggestedChips.innerHTML = '';
  const queries = [scene.primary_query, ...(scene.suggested_queries || [])];
  queries.forEach(q => {
    const chip = document.createElement('button');
    chip.className = 'px-2.5 py-1 rounded-lg bg-surface-850 hover:bg-brand-600/30 text-slate-300 hover:text-brand-300 border border-slate-700 transition flex items-center space-x-1';
    chip.innerHTML = `<span>${q}</span>`;
    chip.addEventListener('click', () => {
      elements.swapSearchInput.value = q;
      executeSwapSearch();
    });
    elements.swapSuggestedChips.appendChild(chip);
  });

  elements.swapClipModal.classList.remove('hidden');
  executeSwapSearch();
}

async function executeSwapSearch() {
  const query = elements.swapSearchInput.value.trim();
  if (!query) return;

  elements.swapResultsGrid.innerHTML = `
    <div class="col-span-full py-12 flex flex-col items-center justify-center text-slate-400 space-y-2">
      <i data-lucide="loader-2" class="w-6 h-6 animate-spin text-brand-400"></i>
      <p class="text-xs">Searching Pexels for "${query}"...</p>
    </div>
  `;
  lucide.createIcons();

  try {
    const resp = await fetch('/api/search-pexels', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        query: query,
        api_key: state.pexelsApiKey,
        orientation: state.aspectRatio === '9:16' ? 'portrait' : 'landscape',
        per_page: 12
      })
    });
    const data = await resp.json();
    renderSwapResults(data.videos || []);
  } catch (e) {
    elements.swapResultsGrid.innerHTML = `
      <div class="col-span-full py-8 text-center text-rose-400 text-xs">
        Failed to fetch video clips: ${e.message}
      </div>
    `;
  }
}

function renderSwapResults(videos) {
  elements.swapResultsGrid.innerHTML = '';

  if (!videos.length) {
    elements.swapResultsGrid.innerHTML = `
      <div class="col-span-full py-12 text-center text-slate-400 text-xs">
        No stock videos found for this query. Try different keywords.
      </div>
    `;
    return;
  }

  videos.forEach(v => {
    const card = document.createElement('div');
    card.className = 'group relative rounded-xl overflow-hidden border border-slate-800 hover:border-brand-500 bg-surface-850 flex flex-col justify-between transition cursor-pointer';

    card.innerHTML = `
      <div class="relative aspect-video bg-black overflow-hidden">
        <img src="${v.image}" class="w-full h-full object-cover group-hover:opacity-0 transition duration-300">
        <video src="${v.preview_url || v.video_url}" muted loop preload="none" class="absolute inset-0 w-full h-full object-cover opacity-0 group-hover:opacity-100 transition duration-300"></video>
        <span class="absolute top-1.5 right-1.5 bg-black/70 text-[10px] font-mono text-white px-1.5 py-0.5 rounded">
          ${v.duration}s
        </span>
      </div>
      <div class="p-2.5 flex items-center justify-between">
        <span class="text-[11px] text-slate-400 truncate max-w-[120px]">${v.author}</span>
        <button class="px-2 py-1 bg-brand-600 hover:bg-brand-500 text-white rounded text-[10px] font-medium transition">
          Select
        </button>
      </div>
    `;

    const videoEl = card.querySelector('video');
    card.addEventListener('mouseenter', () => videoEl.play().catch(() => {}));
    card.addEventListener('mouseleave', () => {
      videoEl.pause();
      videoEl.currentTime = 0;
    });

    card.addEventListener('click', () => {
      if (state.activeSwapSceneIndex !== null) {
        state.scenes[state.activeSwapSceneIndex].selected_clip = v;
        renderStoryboard();
        elements.swapClipModal.classList.add('hidden');
      }
    });

    elements.swapResultsGrid.appendChild(card);
  });
}

// Render Video with FFmpeg
async function handleRenderVideo() {
  if (!state.audioId || !state.scenes.length) {
    alert('Please prepare audio and scenes first.');
    return;
  }

  // Open render modal
  elements.renderProgressModal.classList.remove('hidden');
  elements.renderResultBox.classList.add('hidden');
  elements.renderProgressBar.style.width = '5%';
  elements.renderPercentText.textContent = '5%';
  elements.renderPhaseText.textContent = 'Initializing video render engine...';

  try {
    const resp = await fetch('/api/render', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        audio_id: state.audioId,
        scenes: state.scenes,
        transition_type: state.transitionType,
        transition_duration: state.transitionDuration,
        aspect_ratio: state.aspectRatio,
        caption_template: state.selectedTemplate,
        highlight_color: state.selectedHighlightColor,
        caption_cards: state.captionCards
      })
    });

    if (!resp.ok) {
      const err = await resp.json();
      throw new Error(err.detail || 'Rendering initiation failed');
    }

    const { job_id } = await resp.json();
    pollRenderStatus(job_id);

  } catch (e) {
    alert('Render failed: ' + e.message);
    elements.renderProgressModal.classList.add('hidden');
  }
}

function pollRenderStatus(jobId) {
  if (state.renderPollInterval) clearInterval(state.renderPollInterval);

  state.renderPollInterval = setInterval(async () => {
    try {
      const resp = await fetch(`/api/render-status/${jobId}`);
      if (!resp.ok) return;

      const data = await resp.json();
      elements.renderProgressBar.style.width = `${data.progress}%`;
      elements.renderPercentText.textContent = `${data.progress}%`;
      elements.renderPhaseText.textContent = data.message;

      if (data.status === 'done') {
        clearInterval(state.renderPollInterval);
        showRenderSuccess(data.video_url, data.download_url);
      } else if (data.status === 'error') {
        clearInterval(state.renderPollInterval);
        elements.renderPhaseText.textContent = 'Error: ' + data.message;
        elements.renderProgressBar.classList.add('bg-rose-500');
      }
    } catch (err) {
      console.error('Polling error:', err);
    }
  }, 1200);
}

function showRenderSuccess(videoUrl, downloadUrl) {
  elements.renderResultBox.classList.remove('hidden');
  elements.renderedVideoPlayer.src = videoUrl;
  elements.renderedVideoPlayer.load();
  elements.btnDownloadVideo.href = downloadUrl;
}

// Helpers
function formatTime(seconds) {
  const m = Math.floor(seconds / 60);
  const s = Math.floor(seconds % 60);
  return `${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`;
}

function round(val, dec) {
  return Number(Math.round(val + 'e' + dec) + 'e-' + dec);
}

// Start application
window.addEventListener('DOMContentLoaded', init);
