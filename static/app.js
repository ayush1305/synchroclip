/**
 * SynchroClip — Free AI Video Editor Studio (CapCut Style)
 * Professional client-side NLE engine with multi-track timeline,
 * Pexels stock integration, AI audio-to-video workflow, and real-time canvas preview.
 */

// Global NLE State
const state = {
  projectTitle: 'Untitled Project',
  aspectRatio: '9:16', // 16:9, 9:16, 1:1, 4:5
  playheadTime: 0.0,
  duration: 15.0,
  zoom: 60, // pixels per second
  isPlaying: false,
  isSnapEnabled: true,
  selectedClipId: null,
  activeTab: 'media',
  undoStack: [],
  redoStack: [],
  mediaBin: [],
  captionPresets: [],
  activeAudioElement: null,

  // Multi-Track Timeline
  timeline: {
    duration: 15.0,
    aspectRatio: '9:16',
    tracks: [
      { id: 'T1', name: 'Text & Captions', type: 'text', clips: [] },
      { id: 'V2', name: 'Overlay / PiP', type: 'video', clips: [] },
      { id: 'V1', name: 'Main Video', type: 'video', clips: [] },
      { id: 'A1', name: 'Voiceover', type: 'audio', clips: [] },
      { id: 'A2', name: 'Background Music', type: 'audio', clips: [] }
    ]
  }
};

// DOM Elements
const el = {
  projectTitleInput: document.getElementById('projectTitleInput'),
  btnUndo: document.getElementById('btnUndo'),
  btnRedo: document.getElementById('btnRedo'),
  btnRatio16x9: document.getElementById('btnRatio16x9'),
  btnRatio9x16: document.getElementById('btnRatio9x16'),
  btnRatio1x1: document.getElementById('btnRatio1x1'),
  btnRatio4x5: document.getElementById('btnRatio4x5'),
  btnTrySampleDemo: document.getElementById('btnTrySampleDemo'),
  btnOpenExportModal: document.getElementById('btnOpenExportModal'),

  // Left Asset Tabs
  assetTabBtns: document.querySelectorAll('.asset-tab-btn'),
  tabPanes: document.querySelectorAll('.tab-pane'),
  mediaDropzone: document.getElementById('mediaDropzone'),
  mediaFileInput: document.getElementById('mediaFileInput'),
  mediaGrid: document.getElementById('mediaGrid'),
  mediaItemCount: document.getElementById('mediaItemCount'),

  // Stock (Pexels)
  pexelsSearchInput: document.getElementById('pexelsSearchInput'),
  btnPexelsSearch: document.getElementById('btnPexelsSearch'),
  stockChips: document.querySelectorAll('.stock-chip'),
  stockVideosGrid: document.getElementById('stockVideosGrid'),

  // Audio & AI Modal
  btnOpenAIAudioWizard: document.getElementById('btnOpenAIAudioWizard'),
  audioLibraryList: document.getElementById('audioLibraryList'),
  aiAudioModal: document.getElementById('aiAudioModal'),
  btnCloseAIModal: document.getElementById('btnCloseAIModal'),
  aiAudioDropzone: document.getElementById('aiAudioDropzone'),
  aiAudioFileInput: document.getElementById('aiAudioFileInput'),
  aiAudioFileName: document.getElementById('aiAudioFileName'),
  btnUseDemoAudioInModal: document.getElementById('btnUseDemoAudioInModal'),
  aiAnalysisBox: document.getElementById('aiAnalysisBox'),
  aiKeywordsContainer: document.getElementById('aiKeywordsContainer'),
  aiTranscriptSnippet: document.getElementById('aiTranscriptSnippet'),
  aiDurationBadge: document.getElementById('aiDurationBadge'),
  btnOptionAGenerate: document.getElementById('btnOptionAGenerate'),
  btnOptionBUseAudioOnly: document.getElementById('btnOptionBUseAudioOnly'),

  // Text & Captions
  btnAddDefaultText: document.getElementById('btnAddDefaultText'),
  textPresetsGrid: document.getElementById('textPresetsGrid'),
  btnAutoGenerateCaptions: document.getElementById('btnAutoGenerateCaptions'),
  captionPresetsList: document.getElementById('captionPresetsList'),

  // Canvas & Monitor
  viewportContainer: document.getElementById('viewportContainer'),
  programCanvas: document.getElementById('programCanvas'),
  safeGuidesOverlay: document.getElementById('safeGuidesOverlay'),
  toggleSafeGuides: document.getElementById('toggleSafeGuides'),
  mediaPool: document.getElementById('mediaPool'),
  monitorResolutionBadge: document.getElementById('monitorResolutionBadge'),

  // Transport
  btnTransportFirst: document.getElementById('btnTransportFirst'),
  btnTransportBack: document.getElementById('btnTransportBack'),
  btnTransportPlayPause: document.getElementById('btnTransportPlayPause'),
  iconPlayPause: document.getElementById('iconPlayPause'),
  btnTransportForward: document.getElementById('btnTransportForward'),
  btnTransportLast: document.getElementById('btnTransportLast'),
  timecodeCurrent: document.getElementById('timecodeCurrent'),
  timecodeTotal: document.getElementById('timecodeTotal'),
  btnTransportMute: document.getElementById('btnTransportMute'),
  iconTransportVolume: document.getElementById('iconTransportVolume'),
  btnTransportFullscreen: document.getElementById('btnTransportFullscreen'),

  // Inspector
  inspectorHeaderTitle: document.getElementById('inspectorHeaderTitle'),
  inspectorItemTypeBadge: document.getElementById('inspectorItemTypeBadge'),
  inspectorContent: document.getElementById('inspectorContent'),

  // Timeline
  btnTimelineSplit: document.getElementById('btnTimelineSplit'),
  btnTimelineDelete: document.getElementById('btnTimelineDelete'),
  btnTimelineDuplicate: document.getElementById('btnTimelineDuplicate'),
  btnToggleSnap: document.getElementById('btnToggleSnap'),
  btnZoomOut: document.getElementById('btnZoomOut'),
  btnZoomIn: document.getElementById('btnZoomIn'),
  timelineZoomSlider: document.getElementById('timelineZoomSlider'),
  timelineScrollArea: document.getElementById('timelineScrollArea'),
  btnScrollTimelineLeft: document.getElementById('btnScrollTimelineLeft'),
  btnScrollTimelineRight: document.getElementById('btnScrollTimelineRight'),
  btnScrollToTimeline: document.getElementById('btnScrollToTimeline'),
  bottomTimelineSection: document.getElementById('bottomTimelineSection'),
  timelineRuler: document.getElementById('timelineRuler'),
  timelineLanes: document.getElementById('timelineLanes'),
  playheadNeedle: document.getElementById('playheadNeedle'),
  playheadHead: document.getElementById('playheadHead'),

  // Export Modal
  exportModal: document.getElementById('exportModal'),
  btnCloseExportModal: document.getElementById('btnCloseExportModal'),
  exportResBtns: document.querySelectorAll('.export-res-btn'),
  exportAspectRatioSelect: document.getElementById('exportAspectRatioSelect'),
  exportFpsSelect: document.getElementById('exportFpsSelect'),
  btnStartExportRender: document.getElementById('btnStartExportRender'),
  renderProgressBox: document.getElementById('renderProgressBox'),
  renderStatusLabel: document.getElementById('renderStatusLabel'),
  renderPercentLabel: document.getElementById('renderPercentLabel'),
  renderProgressBar: document.getElementById('renderProgressBar'),
  renderFinishedBox: document.getElementById('renderFinishedBox'),
  btnDownloadRenderedVideo: document.getElementById('btnDownloadRenderedVideo')
};

// Canvas Context
let ctx = null;
let animationFrameId = null;
let lastPlayTimestamp = null;
let currentAIAnalysis = null;

// ================= INITIALIZATION =================
function init() {
  ctx = el.programCanvas.getContext('2d');
  bindEvents();
  setAspectRatio('16:9');
  fetchCaptionPresets();
  fetchInitialStockVideos('technology');
  renderTimeline();
  updateTimecodeDisplays();
  renderInspector();
  renderCanvas();
  if (window.lucide) lucide.createIcons();
}

// ================= EVENT BINDINGS =================
function bindEvents() {
  // Title
  el.projectTitleInput.addEventListener('input', (e) => {
    state.projectTitle = e.target.value.trim() || 'Untitled Project';
  });

  // Undo / Redo
  el.btnUndo.addEventListener('click', undo);
  el.btnRedo.addEventListener('click', redo);

  // Aspect Ratios
  el.btnRatio16x9.addEventListener('click', () => setAspectRatio('16:9'));
  el.btnRatio9x16.addEventListener('click', () => setAspectRatio('9:16'));
  el.btnRatio1x1.addEventListener('click', () => setAspectRatio('1:1'));
  el.btnRatio4x5.addEventListener('click', () => setAspectRatio('4:5'));

  // Quick Demo
  el.btnTrySampleDemo.addEventListener('click', handleLoadDemoSample);

  // Export Modal
  el.btnOpenExportModal.addEventListener('click', () => {
    el.exportModal.classList.remove('hidden');
    el.renderProgressBox.classList.add('hidden');
    el.renderFinishedBox.classList.add('hidden');
    el.btnStartExportRender.disabled = false;
  });
  el.btnCloseExportModal.addEventListener('click', () => el.exportModal.classList.add('hidden'));

  el.exportResBtns.forEach(b => {
    b.addEventListener('click', () => {
      el.exportResBtns.forEach(x => {
        x.classList.remove('active', 'bg-brand-600', 'text-white');
        x.classList.add('bg-surface-950', 'text-slate-300');
      });
      b.classList.add('active', 'bg-brand-600', 'text-white');
      b.classList.remove('bg-surface-950', 'text-slate-300');
    });
  });

  el.btnStartExportRender.addEventListener('click', handleStartExportRender);

  // Asset Tabs
  el.assetTabBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      el.assetTabBtns.forEach(b => b.classList.remove('active', 'text-white', 'bg-surface-800'));
      btn.classList.add('active', 'text-white', 'bg-surface-800');
      const tab = btn.dataset.tab;
      state.activeTab = tab;

      el.tabPanes.forEach(pane => pane.classList.add('hidden'));
      const targetPane = document.getElementById(`tabContent${capitalize(tab)}`) ||
                         document.getElementById(`tabContent${tab}`) ||
                         (tab === 'aigenerator' ? document.getElementById('tabContentAiGenerator') : null);
      if (targetPane) targetPane.classList.remove('hidden');
    });
  });

  // Media Upload
  el.mediaDropzone.addEventListener('click', () => el.mediaFileInput.click());
  el.mediaFileInput.addEventListener('change', (e) => {
    if (e.target.files && e.target.files.length) {
      Array.from(e.target.files).forEach(f => uploadMediaFile(f));
    }
  });

  // Pexels Search
  el.btnPexelsSearch.addEventListener('click', () => {
    const q = el.pexelsSearchInput.value.trim() || 'cinematic';
    searchPexelsStock(q);
  });
  el.pexelsSearchInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter') el.btnPexelsSearch.click();
  });
  el.stockChips.forEach(chip => {
    chip.addEventListener('click', () => {
      const cat = chip.dataset.cat;
      el.pexelsSearchInput.value = cat;
      searchPexelsStock(cat);
    });
  });

  // Transport Controls
  el.btnTransportPlayPause.addEventListener('click', togglePlayback);
  el.btnTransportFirst.addEventListener('click', () => seekTo(0));
  el.btnTransportLast.addEventListener('click', () => seekTo(state.timeline.duration));
  el.btnTransportBack.addEventListener('click', () => seekTo(Math.max(0, state.playheadTime - 1.0)));
  el.btnTransportForward.addEventListener('click', () => seekTo(Math.min(state.timeline.duration, state.playheadTime + 1.0)));

  // Timeline Tools
  el.btnTimelineSplit.addEventListener('click', splitClipAtPlayhead);
  el.btnTimelineDelete.addEventListener('click', deleteSelectedClip);
  el.btnTimelineDuplicate.addEventListener('click', duplicateSelectedClip);
  el.btnToggleSnap.addEventListener('click', () => {
    state.isSnapEnabled = !state.isSnapEnabled;
    el.btnToggleSnap.className = state.isSnapEnabled
      ? 'px-2 py-1 rounded bg-brand-600/30 text-brand-300 border border-brand-500/30 flex items-center space-x-1 text-[11px]'
      : 'px-2 py-1 rounded bg-surface-800 text-slate-400 border border-slate-700 flex items-center space-x-1 text-[11px]';
  });

  // Timeline Zoom Slider
  el.timelineZoomSlider.addEventListener('input', (e) => {
    state.zoom = parseInt(e.target.value);
    renderTimeline();
  });
  el.btnZoomIn.addEventListener('click', () => {
    state.zoom = Math.min(150, state.zoom + 15);
    el.timelineZoomSlider.value = state.zoom;
    renderTimeline();
  });
  el.btnZoomOut.addEventListener('click', () => {
    state.zoom = Math.max(20, state.zoom - 15);
    el.timelineZoomSlider.value = state.zoom;
    renderTimeline();
  });

  // Timeline Horizontal Scroll Buttons & Shortcuts
  if (el.btnScrollTimelineLeft) {
    el.btnScrollTimelineLeft.addEventListener('click', () => {
      if (el.timelineScrollArea) {
        el.timelineScrollArea.scrollBy({ left: -260, behavior: 'smooth' });
      }
    });
  }
  if (el.btnScrollTimelineRight) {
    el.btnScrollTimelineRight.addEventListener('click', () => {
      if (el.timelineScrollArea) {
        el.timelineScrollArea.scrollBy({ left: 260, behavior: 'smooth' });
      }
    });
  }
  if (el.btnScrollToTimeline) {
    el.btnScrollToTimeline.addEventListener('click', () => {
      const target = document.getElementById('bottomTimelineSection') || el.timelineScrollArea;
      if (target) {
        target.scrollIntoView({ behavior: 'smooth', block: 'end' });
      }
    });
  }

  // Timeline Ruler & Playhead Dragging
  bindPlayheadDragging();

  // Text & Captions
  el.btnAddDefaultText.addEventListener('click', addDefaultTextToTimeline);
  document.querySelectorAll('.text-preset-card').forEach(card => {
    card.addEventListener('click', () => addPresetTextToTimeline(card.dataset.preset));
  });
  el.btnAutoGenerateCaptions.addEventListener('click', () => {
    openAIAudioWizard();
  });

  // AI Video Buttons (Header, Media, Monitor, Sidebar)
  const btnHeaderGen = document.getElementById('btnHeaderGenerateVideo');
  if (btnHeaderGen) btnHeaderGen.addEventListener('click', openAIAudioWizard);

  const btnMediaGen = document.getElementById('btnMediaGenerateAiVideo');
  if (btnMediaGen) btnMediaGen.addEventListener('click', openAIAudioWizard);

  const btnMonitorGen = document.getElementById('btnMonitorGenerateVideo');
  if (btnMonitorGen) btnMonitorGen.addEventListener('click', openAIAudioWizard);

  const btnMonitorImport = document.getElementById('btnMonitorImportMedia');
  if (btnMonitorImport) btnMonitorImport.addEventListener('click', () => el.mediaFileInput.click());

  const btnSidebarOpen = document.getElementById('btnSidebarOpenAiWizard');
  if (btnSidebarOpen) btnSidebarOpen.addEventListener('click', openAIAudioWizard);

  const btnSidebarDemo = document.getElementById('btnSidebarLoadDemoAudio');
  if (btnSidebarDemo) btnSidebarDemo.addEventListener('click', () => {
    openAIAudioWizard();
    handleLoadDemoAudioInModal();
  });

  const sidebarAudioDrop = document.getElementById('sidebarAudioDropzone');
  if (sidebarAudioDrop) sidebarAudioDrop.addEventListener('click', () => {
    openAIAudioWizard();
    el.aiAudioFileInput.click();
  });

  // AI Audio Modal
  if (el.btnOpenAIAudioWizard) el.btnOpenAIAudioWizard.addEventListener('click', openAIAudioWizard);
  el.btnCloseAIModal.addEventListener('click', () => el.aiAudioModal.classList.add('hidden'));
  el.aiAudioDropzone.addEventListener('click', () => el.aiAudioFileInput.click());
  el.aiAudioFileInput.addEventListener('change', (e) => {
    if (e.target.files && e.target.files[0]) handleAIAudioUpload(e.target.files[0]);
  });
  el.btnUseDemoAudioInModal.addEventListener('click', handleLoadDemoAudioInModal);
  el.btnOptionAGenerate.addEventListener('click', handleExecuteOptionAGenerate);
  el.btnOptionBUseAudioOnly.addEventListener('click', handleExecuteOptionBUseAudioOnly);

  // Safe Guides
  el.toggleSafeGuides.addEventListener('change', (e) => {
    el.safeGuidesOverlay.style.display = e.target.checked ? 'flex' : 'none';
  });

  // Keyboard Shortcuts
  window.addEventListener('keydown', handleGlobalKeydown);
}

// ================= KEYBOARD SHORTCUTS =================
function handleGlobalKeydown(e) {
  if (['INPUT', 'TEXTAREA'].includes(document.activeElement.tagName)) return;

  if (e.code === 'Space') {
    e.preventDefault();
    togglePlayback();
  } else if ((e.ctrlKey || e.metaKey) && e.key === 'z') {
    e.preventDefault();
    undo();
  } else if ((e.ctrlKey || e.metaKey) && e.key === 'y') {
    e.preventDefault();
    redo();
  } else if ((e.ctrlKey || e.metaKey) && e.key === 'b') {
    e.preventDefault();
    splitClipAtPlayhead();
  } else if (e.key === 'Delete' || e.key === 'Backspace') {
    e.preventDefault();
    deleteSelectedClip();
  } else if ((e.ctrlKey || e.metaKey) && e.key === 'd') {
    e.preventDefault();
    duplicateSelectedClip();
  } else if (e.key === 's') {
    e.preventDefault();
    el.btnToggleSnap.click();
  }
}

// ================= ASPECT RATIO =================
function setAspectRatio(ratio) {
  state.aspectRatio = ratio;
  state.timeline.aspectRatio = ratio;

  const buttons = [
    { btn: el.btnRatio16x9, key: '16:9' },
    { btn: el.btnRatio9x16, key: '9:16' },
    { btn: el.btnRatio1x1, key: '1:1' },
    { btn: el.btnRatio4x5, key: '4:5' }
  ];

  buttons.forEach(item => {
    if (item.key === ratio) {
      item.btn.className = 'px-2.5 py-1 rounded-md font-semibold transition bg-brand-600 text-white shadow';
    } else {
      item.btn.className = 'px-2.5 py-1 rounded-md font-semibold transition text-slate-400 hover:text-white';
    }
  });

  // Viewport aspect ratio container
  if (ratio === '16:9') {
    el.viewportContainer.className = 'relative bg-black rounded-lg overflow-hidden shadow-2xl border border-slate-800 aspect-[16/9] w-full max-w-[850px] max-h-full flex items-center justify-center transition-all';
    el.monitorResolutionBadge.textContent = '1920x1080 (16:9)';
    el.programCanvas.width = 1920;
    el.programCanvas.height = 1080;
  } else if (ratio === '9:16') {
    el.viewportContainer.className = 'relative bg-black rounded-lg overflow-hidden shadow-2xl border border-slate-800 aspect-[9/16] h-[250px] max-h-[75%] flex items-center justify-center transition-all';
    el.monitorResolutionBadge.textContent = '1080x1920 (9:16)';
    el.programCanvas.width = 1080;
    el.programCanvas.height = 1920;
  } else if (ratio === '1:1') {
    el.viewportContainer.className = 'relative bg-black rounded-lg overflow-hidden shadow-2xl border border-slate-800 aspect-square h-[250px] max-h-[75%] flex items-center justify-center transition-all';
    el.monitorResolutionBadge.textContent = '1080x1080 (1:1)';
    el.programCanvas.width = 1080;
    el.programCanvas.height = 1080;
  } else if (ratio === '4:5') {
    el.viewportContainer.className = 'relative bg-black rounded-lg overflow-hidden shadow-2xl border border-slate-800 aspect-[4/5] h-[250px] max-h-[75%] flex items-center justify-center transition-all';
    el.monitorResolutionBadge.textContent = '1080x1350 (4:5)';
    el.programCanvas.width = 1080;
    el.programCanvas.height = 1350;
  }

  renderCanvas();
}

// ================= TIMELINE ENGINE =================
function saveState() {
  state.undoStack.push(JSON.stringify(state.timeline));
  if (state.undoStack.length > 30) state.undoStack.shift();
  state.redoStack = [];
}

function undo() {
  if (!state.undoStack.length) return;
  state.redoStack.push(JSON.stringify(state.timeline));
  state.timeline = JSON.parse(state.undoStack.pop());
  renderTimeline();
  renderInspector();
  renderCanvas();
}

function redo() {
  if (!state.redoStack.length) return;
  state.undoStack.push(JSON.stringify(state.timeline));
  state.timeline = JSON.parse(state.redoStack.pop());
  renderTimeline();
  renderInspector();
  renderCanvas();
}

function updateTimelineDuration() {
  let maxTime = 10.0;
  state.timeline.tracks.forEach(track => {
    track.clips.forEach(clip => {
      const end = clip.startTime + clip.duration;
      if (end > maxTime) maxTime = end;
    });
  });
  state.timeline.duration = Math.ceil(maxTime + 2.0);
  state.duration = state.timeline.duration;
  updateTimecodeDisplays();
}

function addClipToTrack(trackId, clipData, atTime = null) {
  saveState();
  const track = state.timeline.tracks.find(t => t.id === trackId);
  if (!track) return;

  let insertTime = atTime !== null ? atTime : state.playheadTime;
  if (atTime === null && track.clips.length) {
    const lastClip = track.clips[track.clips.length - 1];
    insertTime = lastClip.startTime + lastClip.duration;
  }

  const newClip = {
    id: `clip_${Date.now()}_${Math.random().toString(36).substr(2, 5)}`,
    trackId: trackId,
    type: clipData.type || (trackId.startsWith('V') ? 'video' : trackId.startsWith('A') ? 'audio' : 'text'),
    title: clipData.title || 'Untitled Clip',
    url: clipData.url || '',
    thumbnail_url: clipData.thumbnail_url || '',
    startTime: insertTime,
    duration: clipData.duration || 4.0,
    sourceStart: clipData.sourceStart || 0.0,
    sourceDuration: clipData.sourceDuration || clipData.duration || 10.0,
    text: clipData.text || '',
    words: clipData.words || [],
    properties: Object.assign({
      scale: 1.0,
      opacity: 1.0,
      rotation: 0,
      speed: 1.0,
      volume: 1.0,
      brightness: 0,
      contrast: 0,
      saturation: 0,
      blur: 0,
      templateId: 'tiktok_bold',
      highlightColor: '#ffe600',
      fontFamily: 'Montserrat',
      fontSize: 48,
      color: '#ffffff',
      animation: 'pop',
      positionY: 80
    }, clipData.properties || {})
  };

  track.clips.push(newClip);
  track.clips.sort((a, b) => a.startTime - b.startTime);
  state.selectedClipId = newClip.id;

  updateTimelineDuration();
  renderTimeline();
  renderInspector();
  renderCanvas();
}

function splitClipAtPlayhead() {
  const t = state.playheadTime;
  let splitOccurred = false;

  saveState();
  state.timeline.tracks.forEach(track => {
    const targetClip = track.clips.find(c => t > c.startTime + 0.1 && t < c.startTime + c.duration - 0.1);
    if (targetClip) {
      const firstPartDuration = t - targetClip.startTime;
      const secondPartDuration = targetClip.duration - firstPartDuration;

      const secondPart = JSON.parse(JSON.stringify(targetClip));
      secondPart.id = `clip_${Date.now()}_split`;
      secondPart.startTime = t;
      secondPart.duration = secondPartDuration;
      secondPart.sourceStart = targetClip.sourceStart + (firstPartDuration * (targetClip.properties.speed || 1.0));

      targetClip.duration = firstPartDuration;

      track.clips.push(secondPart);
      track.clips.sort((a, b) => a.startTime - b.startTime);
      state.selectedClipId = secondPart.id;
      splitOccurred = true;
    }
  });

  if (splitOccurred) {
    renderTimeline();
    renderInspector();
    renderCanvas();
  }
}

function deleteSelectedClip() {
  if (!state.selectedClipId) return;
  saveState();

  state.timeline.tracks.forEach(track => {
    track.clips = track.clips.filter(c => c.id !== state.selectedClipId);
  });

  state.selectedClipId = null;
  updateTimelineDuration();
  renderTimeline();
  renderInspector();
  renderCanvas();
}

function duplicateSelectedClip() {
  if (!state.selectedClipId) return;
  const clip = findClipById(state.selectedClipId);
  if (!clip) return;

  saveState();
  const dup = JSON.parse(JSON.stringify(clip));
  dup.id = `clip_${Date.now()}_dup`;
  dup.startTime = clip.startTime + clip.duration;

  const track = state.timeline.tracks.find(t => t.id === clip.trackId);
  if (track) {
    track.clips.push(dup);
    track.clips.sort((a, b) => a.startTime - b.startTime);
    state.selectedClipId = dup.id;
  }

  updateTimelineDuration();
  renderTimeline();
  renderInspector();
  renderCanvas();
}

function findClipById(id) {
  for (const track of state.timeline.tracks) {
    const found = track.clips.find(c => c.id === id);
    if (found) return found;
  }
  return null;
}

// ================= TIMELINE UI RENDERING =================
function renderTimeline() {
  const z = state.zoom;
  const totalWidth = Math.max(state.timeline.duration * z, el.timelineScrollArea.clientWidth);

  // 1. Ruler
  el.timelineRuler.style.width = `${totalWidth}px`;
  el.timelineRuler.innerHTML = '';
  const secondsCount = Math.ceil(state.timeline.duration);

  for (let s = 0; s <= secondsCount; s++) {
    const mark = document.createElement('div');
    mark.className = 'absolute top-0 bottom-0 border-l border-slate-800 text-[9px] font-mono text-slate-500 pl-1 select-none pointer-events-none';
    mark.style.left = `${s * z}px`;
    mark.textContent = formatTimeSec(s);
    el.timelineRuler.appendChild(mark);
  }

  // 2. Lanes
  el.timelineLanes.style.width = `${totalWidth}px`;

  state.timeline.tracks.forEach(track => {
    const lane = document.getElementById(`lane${track.id}`);
    if (!lane) return;
    lane.innerHTML = '';

    track.clips.forEach(clip => {
      const clipBlock = document.createElement('div');
      const leftPx = clip.startTime * z;
      const widthPx = Math.max(16, clip.duration * z);

      clipBlock.className = `timeline-clip clip-${clip.type} ${clip.id === state.selectedClipId ? 'selected' : ''}`;
      clipBlock.style.left = `${leftPx}px`;
      clipBlock.style.width = `${widthPx}px`;
      clipBlock.dataset.id = clip.id;

      // Inner Label
      const titleSpan = document.createElement('span');
      titleSpan.className = 'truncate pointer-events-none select-none';
      titleSpan.textContent = clip.text ? `"${clip.text}"` : clip.title;
      clipBlock.appendChild(titleSpan);

      // Duration badge
      const durBadge = document.createElement('span');
      durBadge.className = 'text-[9px] opacity-70 font-mono pointer-events-none pl-1 select-none';
      durBadge.textContent = `${clip.duration.toFixed(1)}s`;
      clipBlock.appendChild(durBadge);

      // Left & Right Trim Handles
      const handleLeft = document.createElement('div');
      handleLeft.className = 'trim-handle trim-handle-left';
      handleLeft.title = 'Trim Start';
      clipBlock.appendChild(handleLeft);

      const handleRight = document.createElement('div');
      handleRight.className = 'trim-handle trim-handle-right';
      handleRight.title = 'Trim End';
      clipBlock.appendChild(handleRight);

      // Trim Handle Dragging
      handleLeft.addEventListener('mousedown', (e) => startTrimming(e, clip, 'left'));
      handleRight.addEventListener('mousedown', (e) => startTrimming(e, clip, 'right'));

      // Clip Dragging / Moving
      clipBlock.addEventListener('mousedown', (e) => {
        if (e.target.classList.contains('trim-handle')) return;
        selectClip(clip.id);
        startMovingClip(e, clip);
      });

      lane.appendChild(clipBlock);
    });
  });

  // 3. Playhead Position
  updatePlayheadPosition();

  // 4. Update Empty Monitor Overlay
  const totalClips = state.timeline.tracks.reduce((sum, tr) => sum + tr.clips.length, 0);
  const emptyMonitor = document.getElementById('emptyMonitorPlaceholder');
  if (emptyMonitor) {
    if (totalClips === 0) {
      emptyMonitor.classList.remove('hidden');
    } else {
      emptyMonitor.classList.add('hidden');
    }
  }
}

function selectClip(id) {
  state.selectedClipId = id;
  document.querySelectorAll('.timeline-clip').forEach(el => {
    if (el.dataset.id === id) el.classList.add('selected');
    else el.classList.remove('selected');
  });
  renderInspector();
}

function updatePlayheadPosition() {
  const left = state.playheadTime * state.zoom;
  el.playheadNeedle.style.left = `${left}px`;
}

function bindPlayheadDragging() {
  let isDragging = false;

  const seekFromClientX = (clientX) => {
    const rect = el.timelineScrollArea.getBoundingClientRect();
    const scrollX = el.timelineScrollArea.scrollLeft;
    const x = clientX - rect.left + scrollX;
    const time = Math.max(0, Math.min(state.timeline.duration, x / state.zoom));
    seekTo(time);
  };

  el.timelineRuler.addEventListener('mousedown', (e) => {
    isDragging = true;
    seekFromClientX(e.clientX);
  });

  el.playheadHead.addEventListener('mousedown', (e) => {
    isDragging = true;
    e.stopPropagation();
  });

  window.addEventListener('mousemove', (e) => {
    if (isDragging) {
      seekFromClientX(e.clientX);
    }
  });

  window.addEventListener('mouseup', () => {
    if (isDragging) isDragging = false;
  });
}

function seekTo(time) {
  state.playheadTime = Math.max(0, Math.min(state.timeline.duration, time));
  updatePlayheadPosition();
  updateTimecodeDisplays();
  renderCanvas();
}

function startTrimming(e, clip, edge) {
  e.stopPropagation();
  saveState();
  const startX = e.clientX;
  const origStart = clip.startTime;
  const origDur = clip.duration;
  const z = state.zoom;

  const onMouseMove = (ev) => {
    const deltaSec = (ev.clientX - startX) / z;
    if (edge === 'left') {
      const newStart = Math.max(0, origStart + deltaSec);
      const newDur = Math.max(0.5, origDur - (newStart - origStart));
      clip.startTime = Number(newStart.toFixed(2));
      clip.duration = Number(newDur.toFixed(2));
    } else {
      const newDur = Math.max(0.5, origDur + deltaSec);
      clip.duration = Number(newDur.toFixed(2));
    }
    updateTimelineDuration();
    renderTimeline();
    renderCanvas();
  };

  const onMouseUp = () => {
    window.removeEventListener('mousemove', onMouseMove);
    window.removeEventListener('mouseup', onMouseUp);
  };

  window.addEventListener('mousemove', onMouseMove);
  window.addEventListener('mouseup', onMouseUp);
}

function startMovingClip(e, clip) {
  e.stopPropagation();
  saveState();
  const startX = e.clientX;
  const origStart = clip.startTime;
  const z = state.zoom;

  const onMouseMove = (ev) => {
    const deltaSec = (ev.clientX - startX) / z;
    let newStart = Math.max(0, origStart + deltaSec);
    if (state.isSnapEnabled) {
      // Snap to whole seconds or adjacent clip edges
      const rounded = Math.round(newStart);
      if (Math.abs(newStart - rounded) < 0.2) newStart = rounded;
    }
    clip.startTime = Number(newStart.toFixed(2));
    updateTimelineDuration();
    renderTimeline();
    renderCanvas();
  };

  const onMouseUp = () => {
    window.removeEventListener('mousemove', onMouseMove);
    window.removeEventListener('mouseup', onMouseUp);
  };

  window.addEventListener('mousemove', onMouseMove);
  window.addEventListener('mouseup', onMouseUp);
}

// ================= REAL-TIME CANVAS COMPOSITOR =================
function renderCanvas() {
  if (!ctx) return;
  const t = state.playheadTime;
  const cw = el.programCanvas.width;
  const ch = el.programCanvas.height;

  // Clear background
  ctx.fillStyle = '#020617';
  ctx.fillRect(0, 0, cw, ch);

  // 1. Render Video Track V1
  const v1Track = state.timeline.tracks.find(tr => tr.id === 'V1');
  if (v1Track) {
    const activeClip = v1Track.clips.find(c => t >= c.startTime && t < c.startTime + c.duration);
    if (activeClip) {
      drawClipToCanvas(activeClip, t - activeClip.startTime, cw, ch);
    }
  }

  // 2. Render Overlay Track V2
  const v2Track = state.timeline.tracks.find(tr => tr.id === 'V2');
  if (v2Track) {
    const activeOverlay = v2Track.clips.find(c => t >= c.startTime && t < c.startTime + c.duration);
    if (activeOverlay) {
      drawClipToCanvas(activeOverlay, t - activeOverlay.startTime, cw, ch, true);
    }
  }

  // 3. Render Text & Captions Track T1
  const t1Track = state.timeline.tracks.find(tr => tr.id === 'T1');
  if (t1Track) {
    const activeText = t1Track.clips.find(c => t >= c.startTime && t < c.startTime + c.duration);
    if (activeText) {
      drawTextToCanvas(activeText, t - activeText.startTime, cw, ch);
    }
  }
}

function drawClipToCanvas(clip, clipOffset, cw, ch, isOverlay = false) {
  let mediaEl = document.getElementById(`media_${clip.id}`);
  if (!mediaEl) {
    if (clip.type === 'video') {
      mediaEl = document.createElement('video');
      mediaEl.id = `media_${clip.id}`;
      mediaEl.src = clip.url;
      mediaEl.muted = true;
      mediaEl.preload = 'auto';
      mediaEl.playsInline = true;
      el.mediaPool.appendChild(mediaEl);
    } else if (clip.type === 'image') {
      mediaEl = document.createElement('img');
      mediaEl.id = `media_${clip.id}`;
      mediaEl.src = clip.url;
      el.mediaPool.appendChild(mediaEl);
    }
  }

  if (!mediaEl) return;

  // Sync video time
  if (clip.type === 'video' && mediaEl.readyState >= 2) {
    const targetVideoTime = (clip.sourceStart || 0) + (clipOffset * (clip.properties.speed || 1.0));
    if (Math.abs(mediaEl.currentTime - targetVideoTime) > 0.3) {
      mediaEl.currentTime = targetVideoTime;
    }
    if (state.isPlaying && mediaEl.paused) {
      mediaEl.play().catch(() => {});
    } else if (!state.isPlaying && !mediaEl.paused) {
      mediaEl.pause();
    }
  }

  ctx.save();
  const props = clip.properties || {};

  // Opacity & Filters
  ctx.globalAlpha = props.opacity !== undefined ? props.opacity : 1.0;
  let filterStr = '';
  if (props.brightness) filterStr += `brightness(${100 + props.brightness}%) `;
  if (props.contrast) filterStr += `contrast(${100 + props.contrast}%) `;
  if (props.saturation) filterStr += `saturate(${100 + props.saturation}%) `;
  if (props.blur) filterStr += `blur(${props.blur}px) `;
  ctx.filter = filterStr || 'none';

  // Transform
  const scale = props.scale !== undefined ? props.scale : 1.0;
  const rot = (props.rotation || 0) * Math.PI / 180;

  ctx.translate(cw / 2, ch / 2);
  ctx.rotate(rot);
  ctx.scale(scale, scale);

  const drawW = isOverlay ? cw * 0.4 : cw;
  const drawH = isOverlay ? ch * 0.4 : ch;

  try {
    if (mediaEl.readyState >= 2 || clip.type === 'image') {
      ctx.drawImage(mediaEl, -drawW / 2, -drawH / 2, drawW, drawH);
    } else if (clip.thumbnail_url) {
      // Draw thumbnail while loading
      let thumb = document.getElementById(`thumb_${clip.id}`);
      if (!thumb) {
        thumb = new Image();
        thumb.id = `thumb_${clip.id}`;
        thumb.src = clip.thumbnail_url;
      }
      if (thumb.complete) {
        ctx.drawImage(thumb, -drawW / 2, -drawH / 2, drawW, drawH);
      }
    }
  } catch (err) {}

  ctx.restore();
}

function drawTextToCanvas(clip, offset, cw, ch) {
  const props = clip.properties || {};
  const fontFam = props.fontFamily || 'Montserrat';
  const fontSize = Math.round((props.fontSize || 48) * (cw / 1080));
  const posY = ch * ((props.positionY || 80) / 100);

  ctx.save();
  ctx.textAlign = 'center';
  ctx.textBaseline = 'middle';
  ctx.font = `900 ${fontSize}px '${fontFam}', sans-serif`;

  // Draw word-by-word karaoke highlight if words present
  if (clip.words && clip.words.length > 0) {
    const totalWords = clip.words;
    const activeWordIdx = totalWords.findIndex(w => (clip.startTime + offset) >= w.start && (clip.startTime + offset) <= w.end + 0.1);

    const fullText = clip.text || totalWords.map(w => w.word).join(' ');
    const words = fullText.split(' ');
    const spaceWidth = ctx.measureText(' ').width;
    const totalW = words.reduce((acc, w) => acc + ctx.measureText(w).width, 0) + (spaceWidth * (words.length - 1));

    let curX = (cw / 2) - (totalW / 2);

    words.forEach((w, idx) => {
      const wWidth = ctx.measureText(w).width;
      const isHighlighted = idx === activeWordIdx;

      ctx.fillStyle = isHighlighted ? (props.highlightColor || '#ffe600') : (props.color || '#ffffff');
      ctx.shadowColor = 'rgba(0, 0, 0, 0.9)';
      ctx.shadowBlur = isHighlighted ? 12 : 4;
      ctx.shadowOffsetX = 0;
      ctx.shadowOffsetY = 2;

      ctx.fillText(w, curX + (wWidth / 2), posY);
      curX += wWidth + spaceWidth;
    });
  } else {
    // Static Text Layer
    ctx.fillStyle = props.color || '#ffffff';
    ctx.shadowColor = 'rgba(0, 0, 0, 0.9)';
    ctx.shadowBlur = 6;
    ctx.fillText(clip.text || 'Heading Text', cw / 2, posY);
  }

  ctx.restore();
}

// ================= PLAYBACK TRANSPORT LOOP =================
function togglePlayback() {
  state.isPlaying = !state.isPlaying;
  if (state.isPlaying) {
    el.iconPlayPause.setAttribute('data-lucide', 'pause');
    lastPlayTimestamp = performance.now();
    playbackLoop(performance.now());
  } else {
    el.iconPlayPause.setAttribute('data-lucide', 'play');
    if (animationFrameId) cancelAnimationFrame(animationFrameId);
    pauseAllMediaElements();
  }
  if (window.lucide) lucide.createIcons();
}

function playbackLoop(timestamp) {
  if (!state.isPlaying) return;
  const delta = (timestamp - lastPlayTimestamp) / 1000;
  lastPlayTimestamp = timestamp;

  state.playheadTime += delta;
  if (state.playheadTime >= state.timeline.duration) {
    state.playheadTime = state.timeline.duration;
    togglePlayback();
  }

  updatePlayheadPosition();
  updateTimecodeDisplays();
  renderCanvas();

  animationFrameId = requestAnimationFrame(playbackLoop);
}

function pauseAllMediaElements() {
  document.querySelectorAll('#mediaPool video').forEach(v => v.pause());
}

// ================= PROPERTIES INSPECTOR UI =================
function renderInspector() {
  const clip = findClipById(state.selectedClipId);

  if (!clip) {
    el.inspectorHeaderTitle.textContent = 'Project Settings';
    el.inspectorItemTypeBadge.textContent = 'Canvas';
    el.inspectorContent.innerHTML = `
      <div class="space-y-3">
        <div>
          <label class="block text-xs font-semibold text-slate-300 mb-1">Canvas Aspect Ratio</label>
          <div class="text-xs font-mono text-brand-400 bg-surface-950 p-2 rounded border border-slate-800">${state.aspectRatio}</div>
        </div>
        <div>
          <label class="block text-xs font-semibold text-slate-300 mb-1">Total Duration</label>
          <div class="text-xs font-mono text-slate-300 bg-surface-950 p-2 rounded border border-slate-800">${state.timeline.duration.toFixed(1)} seconds</div>
        </div>
        <div class="p-3 bg-surface-950 rounded-xl border border-slate-800 text-[11px] text-slate-400">
          Click any clip on the timeline to edit its transform, speed, filters, and caption typography.
        </div>
      </div>
    `;
    return;
  }

  el.inspectorHeaderTitle.textContent = clip.title || 'Clip Properties';
  el.inspectorItemTypeBadge.textContent = clip.type.toUpperCase();

  const props = clip.properties || {};

  if (clip.type === 'video' || clip.type === 'image') {
    el.inspectorContent.innerHTML = `
      <div class="space-y-4">
        <!-- Scale / Zoom -->
        <div>
          <div class="flex justify-between text-xs font-semibold text-slate-300 mb-1">
            <span>Scale</span>
            <span class="font-mono text-brand-400" id="inspScaleVal">${Math.round((props.scale || 1.0) * 100)}%</span>
          </div>
          <input type="range" id="inspScaleInput" min="0.5" max="2.0" step="0.05" value="${props.scale || 1.0}" class="w-full accent-brand-500 h-1 bg-slate-800 rounded">
        </div>

        <!-- Opacity -->
        <div>
          <div class="flex justify-between text-xs font-semibold text-slate-300 mb-1">
            <span>Opacity</span>
            <span class="font-mono text-brand-400" id="inspOpacityVal">${Math.round((props.opacity !== undefined ? props.opacity : 1.0) * 100)}%</span>
          </div>
          <input type="range" id="inspOpacityInput" min="0" max="1" step="0.05" value="${props.opacity !== undefined ? props.opacity : 1.0}" class="w-full accent-brand-500 h-1 bg-slate-800 rounded">
        </div>

        <!-- Speed -->
        <div>
          <div class="flex justify-between text-xs font-semibold text-slate-300 mb-1">
            <span>Speed</span>
            <span class="font-mono text-brand-400" id="inspSpeedVal">${(props.speed || 1.0).toFixed(1)}x</span>
          </div>
          <input type="range" id="inspSpeedInput" min="0.25" max="3.0" step="0.25" value="${props.speed || 1.0}" class="w-full accent-brand-500 h-1 bg-slate-800 rounded">
        </div>

        <!-- Color Adjustments -->
        <div class="pt-2 border-t border-slate-800 space-y-3">
          <span class="text-xs font-bold uppercase tracking-wider text-slate-400 block">Color Adjustments</span>
          <div>
            <div class="flex justify-between text-[11px] text-slate-300 mb-1">
              <span>Brightness</span>
              <span class="font-mono text-brand-400" id="inspBrightVal">${props.brightness || 0}</span>
            </div>
            <input type="range" id="inspBrightInput" min="-50" max="50" value="${props.brightness || 0}" class="w-full accent-brand-500 h-1 bg-slate-800 rounded">
          </div>
          <div>
            <div class="flex justify-between text-[11px] text-slate-300 mb-1">
              <span>Contrast</span>
              <span class="font-mono text-brand-400" id="inspContrastVal">${props.contrast || 0}</span>
            </div>
            <input type="range" id="inspContrastInput" min="-50" max="50" value="${props.contrast || 0}" class="w-full accent-brand-500 h-1 bg-slate-800 rounded">
          </div>
          <div>
            <div class="flex justify-between text-[11px] text-slate-300 mb-1">
              <span>Saturation</span>
              <span class="font-mono text-brand-400" id="inspSatVal">${props.saturation || 0}</span>
            </div>
            <input type="range" id="inspSatInput" min="-50" max="50" value="${props.saturation || 0}" class="w-full accent-brand-500 h-1 bg-slate-800 rounded">
          </div>
        </div>
      </div>
    `;

    // Bind inputs
    document.getElementById('inspScaleInput').addEventListener('input', (e) => {
      clip.properties.scale = parseFloat(e.target.value);
      document.getElementById('inspScaleVal').textContent = `${Math.round(clip.properties.scale * 100)}%`;
      renderCanvas();
    });
    document.getElementById('inspOpacityInput').addEventListener('input', (e) => {
      clip.properties.opacity = parseFloat(e.target.value);
      document.getElementById('inspOpacityVal').textContent = `${Math.round(clip.properties.opacity * 100)}%`;
      renderCanvas();
    });
    document.getElementById('inspSpeedInput').addEventListener('input', (e) => {
      clip.properties.speed = parseFloat(e.target.value);
      document.getElementById('inspSpeedVal').textContent = `${clip.properties.speed.toFixed(1)}x`;
      renderCanvas();
    });
    document.getElementById('inspBrightInput').addEventListener('input', (e) => {
      clip.properties.brightness = parseInt(e.target.value);
      document.getElementById('inspBrightVal').textContent = clip.properties.brightness;
      renderCanvas();
    });
    document.getElementById('inspContrastInput').addEventListener('input', (e) => {
      clip.properties.contrast = parseInt(e.target.value);
      document.getElementById('inspContrastVal').textContent = clip.properties.contrast;
      renderCanvas();
    });
    document.getElementById('inspSatInput').addEventListener('input', (e) => {
      clip.properties.saturation = parseInt(e.target.value);
      document.getElementById('inspSatVal').textContent = clip.properties.saturation;
      renderCanvas();
    });

  } else if (clip.type === 'text' || clip.type === 'caption') {
    el.inspectorContent.innerHTML = `
      <div class="space-y-4">
        <div>
          <label class="block text-xs font-semibold text-slate-300 mb-1">Text Content</label>
          <textarea id="inspTextInput" rows="2" class="w-full bg-surface-950 border border-slate-800 rounded-lg p-2 text-xs text-slate-200 outline-none focus:border-brand-500 font-sans resize-none">${clip.text || ''}</textarea>
        </div>

        <div>
          <label class="block text-xs font-semibold text-slate-300 mb-1">Font Family</label>
          <select id="inspFontFamilySelect" class="w-full bg-surface-950 border border-slate-800 rounded-lg px-2 py-1.5 text-xs text-slate-200 outline-none focus:border-brand-500">
            <option value="Montserrat" ${props.fontFamily === 'Montserrat' ? 'selected' : ''}>Montserrat (Bold Viral)</option>
            <option value="Inter" ${props.fontFamily === 'Inter' ? 'selected' : ''}>Inter (Clean Modern)</option>
            <option value="Bebas Neue" ${props.fontFamily === 'Bebas Neue' ? 'selected' : ''}>Bebas Neue (Punch Title)</option>
            <option value="Poppins" ${props.fontFamily === 'Poppins' ? 'selected' : ''}>Poppins (Friendly Bold)</option>
            <option value="Playfair Display" ${props.fontFamily === 'Playfair Display' ? 'selected' : ''}>Playfair Display (Serif)</option>
            <option value="Oswald" ${props.fontFamily === 'Oswald' ? 'selected' : ''}>Oswald (Condensed)</option>
          </select>
        </div>

        <div>
          <div class="flex justify-between text-xs font-semibold text-slate-300 mb-1">
            <span>Font Size</span>
            <span class="font-mono text-brand-400" id="inspFontSizeVal">${props.fontSize || 48}px</span>
          </div>
          <input type="range" id="inspFontSizeInput" min="24" max="96" value="${props.fontSize || 48}" class="w-full accent-brand-500 h-1 bg-slate-800 rounded">
        </div>

        <div>
          <label class="block text-xs font-semibold text-slate-300 mb-1.5">Word Highlight Color</label>
          <div class="flex items-center space-x-2">
            <input type="color" id="inspHighlightColorPicker" value="${props.highlightColor || '#ffe600'}" class="w-8 h-8 rounded bg-transparent border-0 cursor-pointer">
            <span class="text-xs font-mono text-slate-300" id="inspHighlightHexLabel">${props.highlightColor || '#ffe600'}</span>
          </div>
        </div>

        <div>
          <div class="flex justify-between text-xs font-semibold text-slate-300 mb-1">
            <span>Vertical Position</span>
            <span class="font-mono text-brand-400" id="inspPosYVal">${props.positionY || 80}%</span>
          </div>
          <input type="range" id="inspPosYInput" min="10" max="90" value="${props.positionY || 80}" class="w-full accent-brand-500 h-1 bg-slate-800 rounded">
        </div>
      </div>
    `;

    document.getElementById('inspTextInput').addEventListener('input', (e) => {
      clip.text = e.target.value;
      renderTimeline();
      renderCanvas();
    });
    document.getElementById('inspFontFamilySelect').addEventListener('change', (e) => {
      clip.properties.fontFamily = e.target.value;
      renderCanvas();
    });
    document.getElementById('inspFontSizeInput').addEventListener('input', (e) => {
      clip.properties.fontSize = parseInt(e.target.value);
      document.getElementById('inspFontSizeVal').textContent = `${clip.properties.fontSize}px`;
      renderCanvas();
    });
    document.getElementById('inspHighlightColorPicker').addEventListener('input', (e) => {
      clip.properties.highlightColor = e.target.value;
      document.getElementById('inspHighlightHexLabel').textContent = e.target.value;
      renderCanvas();
    });
    document.getElementById('inspPosYInput').addEventListener('input', (e) => {
      clip.properties.positionY = parseInt(e.target.value);
      document.getElementById('inspPosYVal').textContent = `${clip.properties.positionY}%`;
      renderCanvas();
    });

  } else if (clip.type === 'audio') {
    el.inspectorContent.innerHTML = `
      <div class="space-y-4">
        <div>
          <div class="flex justify-between text-xs font-semibold text-slate-300 mb-1">
            <span>Volume</span>
            <span class="font-mono text-brand-400" id="inspVolVal">${Math.round((props.volume !== undefined ? props.volume : 1.0) * 100)}%</span>
          </div>
          <input type="range" id="inspVolInput" min="0" max="2" step="0.05" value="${props.volume !== undefined ? props.volume : 1.0}" class="w-full accent-brand-500 h-1 bg-slate-800 rounded">
        </div>
        <div>
          <div class="flex justify-between text-xs font-semibold text-slate-300 mb-1">
            <span>Fade In</span>
            <span class="font-mono text-brand-400">${props.fadeIn || 0}s</span>
          </div>
          <input type="range" id="inspFadeInInput" min="0" max="3" step="0.2" value="${props.fadeIn || 0}" class="w-full accent-brand-500 h-1 bg-slate-800 rounded">
        </div>
      </div>
    `;

    document.getElementById('inspVolInput').addEventListener('input', (e) => {
      clip.properties.volume = parseFloat(e.target.value);
      document.getElementById('inspVolVal').textContent = `${Math.round(clip.properties.volume * 100)}%`;
    });
  }
}

// ================= MEDIA BIN & UPLOAD =================
async function uploadMediaFile(file) {
  const formData = new FormData();
  formData.append('file', file);

  try {
    const resp = await fetch('/api/upload-media', {
      method: 'POST',
      body: formData
    });
    if (!resp.ok) throw new Error('Upload failed');
    const data = await resp.json();
    const media = data.media;

    state.mediaBin.push(media);
    renderMediaBin();

    // Auto-place on timeline
    if (media.type === 'video') {
      addClipToTrack('V1', media);
    } else if (media.type === 'audio') {
      addClipToTrack('A1', media);
    } else if (media.type === 'image') {
      addClipToTrack('V2', media);
    }
  } catch (err) {
    alert('Media import error: ' + err.message);
  }
}

function renderMediaBin() {
  el.mediaGrid.innerHTML = '';
  el.mediaItemCount.textContent = `${state.mediaBin.length} items`;

  state.mediaBin.forEach(item => {
    const card = document.createElement('div');
    card.className = 'relative aspect-video rounded-lg overflow-hidden bg-surface-950 border border-slate-800 hover:border-brand-500 cursor-pointer group transition';

    const thumb = item.thumbnail_url || 'https://images.unsplash.com/photo-1506744038136-46273834b3fb?w=640&q=80';
    card.innerHTML = `
      <img src="${thumb}" class="w-full h-full object-cover">
      <div class="absolute inset-0 bg-black/60 opacity-0 group-hover:opacity-100 flex items-center justify-center space-x-2 transition">
        <button class="p-1 rounded bg-brand-600 text-white text-[10px] font-bold shadow">+ Add</button>
      </div>
      <span class="absolute bottom-1 left-1 bg-black/70 px-1 py-0.5 rounded text-[9px] font-mono text-slate-300 truncate max-w-[80%]">${item.name}</span>
    `;

    card.querySelector('button').addEventListener('click', (e) => {
      e.stopPropagation();
      const targetTrack = item.type === 'audio' ? 'A1' : 'V1';
      addClipToTrack(targetTrack, item);
    });

    el.mediaGrid.appendChild(card);
  });
}

// ================= STOCK (PEXELS) INTEGRATION =================
async function searchPexelsStock(query) {
  el.stockVideosGrid.innerHTML = '<div class="col-span-2 py-8 text-center text-xs text-slate-400">Searching Pexels footage...</div>';

  try {
    const orientation = state.aspectRatio === '9:16' ? 'portrait' : 'landscape';
    const resp = await fetch(`/api/search-pexels?query=${encodeURIComponent(query)}&orientation=${orientation}&per_page=12`);
    if (!resp.ok) throw new Error('Search failed');
    const data = await resp.json();
    const videos = data.videos || [];

    el.stockVideosGrid.innerHTML = '';
    if (!videos.length) {
      el.stockVideosGrid.innerHTML = '<div class="col-span-2 py-8 text-center text-xs text-slate-400">No stock videos found.</div>';
      return;
    }

    videos.forEach(v => {
      const card = document.createElement('div');
      card.className = 'stock-card group relative';
      card.innerHTML = `
        <img src="${v.image}" class="w-full h-full object-cover transition group-hover:opacity-0">
        ${v.preview_url ? `<video src="${v.preview_url}" muted loop preload="none" class="absolute inset-0 w-full h-full object-cover opacity-0 group-hover:opacity-100 transition"></video>` : ''}
        <div class="absolute inset-0 bg-black/50 opacity-0 group-hover:opacity-100 flex items-center justify-center transition">
          <button class="px-2 py-1 rounded bg-brand-600 hover:bg-brand-500 text-white text-[11px] font-bold shadow flex items-center space-x-1">
            <i data-lucide="plus" class="w-3 h-3"></i>
            <span>Add to V1</span>
          </button>
        </div>
        <span class="absolute bottom-1 right-1 bg-black/80 px-1 py-0.5 rounded text-[9px] font-mono text-amber-400">${v.duration}s</span>
      `;

      card.querySelector('button').addEventListener('click', (e) => {
        e.stopPropagation();
        addClipToTrack('V1', {
          type: 'video',
          title: v.title,
          url: v.video_url || v.preview_url,
          thumbnail_url: v.image,
          duration: Math.min(6.0, v.duration || 5.0),
          sourceDuration: v.duration
        });
      });

      el.stockVideosGrid.appendChild(card);
    });

    if (window.lucide) lucide.createIcons();
  } catch (err) {
    el.stockVideosGrid.innerHTML = `<div class="col-span-2 py-8 text-center text-xs text-rose-400">Pexels error: ${err.message}</div>`;
  }
}

function fetchInitialStockVideos(cat) {
  searchPexelsStock(cat);
}

// ================= AI VIDEO FROM AUDIO WIZARD =================
function openAIAudioWizard() {
  el.aiAudioModal.classList.remove('hidden');
  currentAIAnalysis = null;
  el.aiAnalysisBox.classList.add('hidden');
  el.aiAudioFileName.textContent = 'Click to select audio file or sample';
}

async function handleAIAudioUpload(file) {
  el.aiAudioFileName.textContent = `Analyzing: ${file.filename || file.name}...`;

  const formData = new FormData();
  formData.append('file', file);

  try {
    const resp = await fetch('/api/upload-media', {
      method: 'POST',
      body: formData
    });
    if (!resp.ok) throw new Error('Audio upload failed');
    const data = await resp.json();
    const media = data.media;

    // Run AI analysis
    await triggerAudioAnalysis(media.id);
  } catch (err) {
    alert('Audio analysis error: ' + err.message);
  }
}

async function handleLoadDemoAudioInModal() {
  el.aiAudioFileName.textContent = 'Loading demo audio...';
  try {
    const resp = await fetch('/api/sample-demo');
    const data = await resp.json();
    await triggerAudioAnalysis(data.audio_id, data.script);
  } catch (err) {
    alert('Demo load error: ' + err.message);
  }
}

async function triggerAudioAnalysis(audioId, optionalScript = '') {
  try {
    const resp = await fetch('/api/analyze-audio', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        audio_id: audioId,
        script_text: optionalScript
      })
    });
    if (!resp.ok) throw new Error('Analysis failed');
    const analysis = await resp.json();
    currentAIAnalysis = analysis;

    // Display keywords and transcript summary
    el.aiAnalysisBox.classList.remove('hidden');
    el.aiDurationBadge.textContent = `${analysis.duration.toFixed(1)}s`;
    el.aiTranscriptSnippet.textContent = `"${analysis.transcript}"`;
    el.aiKeywordsContainer.innerHTML = '';
    (analysis.keywords || []).forEach(kw => {
      const pill = document.createElement('span');
      pill.className = 'px-2 py-0.5 rounded bg-brand-600/30 text-brand-300 text-[10px] font-bold';
      pill.textContent = kw;
      el.aiKeywordsContainer.appendChild(pill);
    });
  } catch (err) {
    alert('Analysis error: ' + err.message);
  }
}

// Option A: Automatically Generate Multi-Clip Video from Audio
async function handleExecuteOptionAGenerate() {
  if (!currentAIAnalysis) {
    el.btnOptionAGenerate.disabled = true;
    el.btnOptionAGenerate.innerHTML = '<span class="flex items-center space-x-2"><i data-lucide="loader" class="w-4 h-4 animate-spin"></i><span>Loading demo audio & analyzing speech...</span></span>';
    if (window.lucide) lucide.createIcons();
    await handleLoadDemoAudioInModal();
    if (!currentAIAnalysis) {
      el.btnOptionAGenerate.disabled = false;
      resetOptionAGenerateButton();
      alert('Please select or upload an audio file first.');
      return;
    }
  }

  const aspectSel = document.getElementById('aiAspectSelect');
  const themeSel = document.getElementById('aiThemeSelect');
  const pacingSel = document.getElementById('aiPacingSelect');
  const captionSel = document.getElementById('aiCaptionTemplateSelect');

  const aspect = aspectSel ? aspectSel.value : state.aspectRatio;
  const visualTheme = themeSel ? themeSel.value : 'auto';
  const pacing = pacingSel ? pacingSel.value : 'medium';
  const templateId = captionSel ? captionSel.value : 'tiktok_bold';

  el.btnOptionAGenerate.disabled = true;
  el.btnOptionAGenerate.innerHTML = '<span class="flex items-center space-x-2"><i data-lucide="loader" class="w-4 h-4 animate-spin"></i><span>Analyzing rhythm, sourcing multiple clips & assembling video...</span></span>';
  if (window.lucide) lucide.createIcons();

  try {
    const resp = await fetch('/api/ai-generate-timeline', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        audio_id: currentAIAnalysis.audio_id,
        aspect_ratio: aspect,
        script_text: currentAIAnalysis.transcript,
        template_id: templateId,
        visual_theme: visualTheme,
        pacing: pacing
      })
    });
    if (!resp.ok) throw new Error('AI Timeline generation failed');
    const data = await resp.json();

    saveState();
    state.timeline = data.timeline;
    state.duration = data.timeline.duration;
    if (aspect !== state.aspectRatio) {
      setAspectRatio(aspect);
    }

    el.aiAudioModal.classList.add('hidden');
    renderTimeline();
    seekTo(0);
    renderCanvas();

    const v1Track = data.timeline.tracks.find(t => t.id === 'V1');
    const clipCount = v1Track ? v1Track.clips.length : 'multiple';
    showToast(`✨ Generated video with ${clipCount} matching clips & subtitles!`);
  } catch (err) {
    alert('Failed to generate video: ' + err.message);
  } finally {
    el.btnOptionAGenerate.disabled = false;
    resetOptionAGenerateButton();
  }
}

function resetOptionAGenerateButton() {
  el.btnOptionAGenerate.innerHTML = `
    <div class="flex items-center justify-between">
      <span class="font-bold text-xs sm:text-sm text-white flex items-center space-x-2">
        <i data-lucide="wand-2" class="w-4 h-4 text-amber-300"></i>
        <span>Generate Multi-Clip Video from Audio</span>
      </span>
      <span class="px-2 py-0.5 rounded bg-white/20 text-[9px] font-bold text-white uppercase tracking-wider">AI Multi-Clip</span>
    </div>
    <p class="text-[11px] text-purple-100 mt-1 leading-snug">
      Analyzes rhythm & pauses, auto-selects multiple matching HD clips for Track V1, adds crossfades, and generates word-timed animated captions on Track T1.
    </p>
  `;
  if (window.lucide) lucide.createIcons();
}

function showToast(msg) {
  let toast = document.getElementById('globalToast');
  if (!toast) {
    toast = document.createElement('div');
    toast.id = 'globalToast';
    toast.className = 'fixed bottom-6 right-6 z-50 px-4 py-3 rounded-xl bg-surface-900 border border-purple-500/50 text-white text-xs font-semibold shadow-2xl backdrop-blur-md flex items-center space-x-2 transition-all duration-300 transform translate-y-12 opacity-0 pointer-events-none';
    document.body.appendChild(toast);
  }
  toast.innerHTML = `<i data-lucide="check-circle" class="w-4 h-4 text-emerald-400 shrink-0"></i><span>${msg}</span>`;
  if (window.lucide) lucide.createIcons();

  toast.classList.remove('translate-y-12', 'opacity-0');
  toast.classList.add('translate-y-0', 'opacity-100');

  clearTimeout(toast._timeout);
  toast._timeout = setTimeout(() => {
    toast.classList.remove('translate-y-0', 'opacity-100');
    toast.classList.add('translate-y-12', 'opacity-0');
  }, 3500);
}

// Option B: Just Use Audio Only
function handleExecuteOptionBUseAudioOnly() {
  if (!currentAIAnalysis) {
    alert('Please select or upload an audio file first.');
    return;
  }

  addClipToTrack('A1', {
    type: 'audio',
    title: 'Voiceover Audio',
    url: `/api/audio/${currentAIAnalysis.audio_id}`,
    duration: currentAIAnalysis.duration
  }, 0.0);

  el.aiAudioModal.classList.add('hidden');
  seekTo(0);
}

// ================= CAPTIONS & PRESETS =================
async function fetchCaptionPresets() {
  try {
    const resp = await fetch('/api/caption-presets');
    const data = await resp.json();
    state.captionPresets = data.presets || [];

    el.captionPresetsList.innerHTML = '';
    state.captionPresets.forEach(preset => {
      const row = document.createElement('div');
      row.className = 'p-2 rounded-lg bg-surface-950 border border-slate-800 hover:border-brand-500 cursor-pointer flex items-center justify-between transition';
      row.innerHTML = `
        <div>
          <p class="text-xs font-bold text-white font-sans">${preset.name}</p>
          <span class="text-[10px] text-slate-400 font-mono">${preset.category} • ${preset.font}</span>
        </div>
        <div class="w-4 h-4 rounded-full border border-white/20" style="background-color: ${preset.highlight};"></div>
      `;

      row.addEventListener('click', () => {
        applyCaptionPresetToSelectedOrAll(preset);
      });

      el.captionPresetsList.appendChild(row);
    });
  } catch (err) {}
}

function applyCaptionPresetToSelectedOrAll(preset) {
  saveState();
  const t1 = state.timeline.tracks.find(t => t.id === 'T1');
  if (!t1) return;

  t1.clips.forEach(clip => {
    clip.properties.templateId = preset.id;
    clip.properties.fontFamily = preset.font;
    clip.properties.highlightColor = preset.highlight;
    clip.properties.animation = preset.anim;
  });

  renderCanvas();
  renderInspector();
}

function addDefaultTextToTimeline() {
  addClipToTrack('T1', {
    type: 'text',
    title: 'Heading Text',
    text: 'YOUR TITLE HERE',
    duration: 3.5,
    properties: {
      fontSize: 56,
      fontFamily: 'Montserrat',
      color: '#ffffff',
      positionY: 50
    }
  });
}

function addPresetTextToTimeline(presetKey) {
  let text = 'TITLE';
  let font = 'Montserrat';
  let color = '#ffffff';

  if (presetKey === 'bold_title') {
    text = 'BOLD HEADING';
    font = 'Bebas Neue';
    color = '#facc15';
  } else if (presetKey === 'neon_sign') {
    text = 'NEON NIGHTS';
    font = 'Montserrat';
    color = '#06b6d4';
  } else if (presetKey === 'clean_serif') {
    text = 'Cinematic Moment';
    font = 'Playfair Display';
    color = '#f43f5e';
  }

  addClipToTrack('T1', {
    type: 'text',
    title: text,
    text: text,
    duration: 3.5,
    properties: {
      fontSize: 52,
      fontFamily: font,
      color: color,
      positionY: 50
    }
  });
}

// ================= EXPORT RENDER PIPELINE =================
async function handleStartExportRender() {
  const activeResBtn = document.querySelector('.export-res-btn.active');
  const res = activeResBtn ? activeResBtn.dataset.res : '1080p';
  const ratio = el.exportAspectRatioSelect.value;
  const fps = parseInt(el.exportFpsSelect.value);

  el.renderProgressBox.classList.remove('hidden');
  el.renderFinishedBox.classList.add('hidden');
  el.btnStartExportRender.disabled = true;
  el.renderStatusLabel.textContent = 'Preparing render job...';
  el.renderProgressBar.style.width = '10%';
  el.renderPercentLabel.textContent = '10%';

  try {
    const resp = await fetch('/api/render-timeline', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        timeline: state.timeline,
        aspect_ratio: ratio,
        resolution: res,
        fps: fps,
        caption_template: 'tiktok_bold',
        highlight_color: '#ffe600'
      })
    });
    if (!resp.ok) throw new Error('Render initiation failed');
    const data = await resp.json();
    const jobId = data.job_id;

    pollRenderJob(jobId);
  } catch (err) {
    el.renderStatusLabel.textContent = 'Render error: ' + err.message;
    el.btnStartExportRender.disabled = false;
  }
}

function pollRenderJob(jobId) {
  const timer = setInterval(async () => {
    try {
      const resp = await fetch(`/api/render-status/${jobId}`);
      if (!resp.ok) return;
      const status = await resp.json();

      el.renderProgressBar.style.width = `${status.progress}%`;
      el.renderPercentLabel.textContent = `${status.progress}%`;
      el.renderStatusLabel.textContent = status.message || 'Rendering...';

      if (status.status === 'done') {
        clearInterval(timer);
        el.renderProgressBar.style.width = '100%';
        el.renderPercentLabel.textContent = '100%';
        el.renderStatusLabel.textContent = 'Render Complete! Zero watermark applied.';
        el.btnDownloadRenderedVideo.href = status.download_url;
        el.renderFinishedBox.classList.remove('hidden');
      } else if (status.status === 'error') {
        clearInterval(timer);
        el.renderStatusLabel.textContent = 'Render failed: ' + status.message;
        el.btnStartExportRender.disabled = false;
      }
    } catch (e) {
      console.error('Polling error:', e);
    }
  }, 1000);
}

// ================= DEMO SAMPLE =================
async function handleLoadDemoSample() {
  openAIAudioWizard();
  await handleLoadDemoAudioInModal();
}

// ================= HELPERS =================
function formatTimeSec(sec) {
  const m = Math.floor(sec / 60);
  const s = Math.floor(sec % 60);
  return `${String(m).padStart(2, '0')}:${String(s).padStart(2, '0')}`;
}

function updateTimecodeDisplays() {
  const cur = state.playheadTime;
  const tot = state.timeline.duration;

  const curM = Math.floor(cur / 60);
  const curS = Math.floor(cur % 60);
  const curF = Math.floor((cur % 1) * 30);
  el.timecodeCurrent.textContent = `00:${String(curM).padStart(2, '0')}:${String(curS).padStart(2, '0')}:${String(curF).padStart(2, '0')}`;

  const totM = Math.floor(tot / 60);
  const totS = Math.floor(tot % 60);
  const totF = Math.floor((tot % 1) * 30);
  el.timecodeTotal.textContent = `00:${String(totM).padStart(2, '0')}:${String(totS).padStart(2, '0')}:${String(totF).padStart(2, '0')}`;
}

function capitalize(s) {
  return s.charAt(0).toUpperCase() + s.slice(1);
}

// Bootstrap on DOM Ready
document.addEventListener('DOMContentLoaded', init);
