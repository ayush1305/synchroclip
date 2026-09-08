// Color 1 Presets (Base text colors)
const PRIMARY_COLORS = {
  white: { name: 'Pure White', hex: '#ffffff' },
  cream: { name: 'Warm Cream', hex: '#fef08a' },
  silver: { name: 'Slate Silver', hex: '#cbd5e1' },
  ice_blue: { name: 'Ice Blue', hex: '#bae6fd' },
  mint: { name: 'Pastel Mint', hex: '#a7f3d0' },
  pink: { name: 'Pastel Pink', hex: '#fbcfe8' },
  peach: { name: 'Warm Peach', hex: '#fed7aa' }
};

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
  selectedTemplate: 'smooth_cross',
  selectedPrimaryColor: '#ffffff',
  selectedHighlightColor: '#facc15',
  selectedFontFamily: '',
  selectedHeroFont: '',
  studioMode: 'generate', // 'generate' | 'direct'
  directVideo: null,
  templateSearchTerm: '',
  captionTemplates: [],
  highlightColors: {},
  famousFonts: [],
  captionCards: [],
  timedWords: [],
  activeCategory: 'All',
  userClips: [],
  pexelsApiKey: localStorage.getItem('synchro_pexels_api_key') || '',
  activeSwapSceneIndex: null,
  currentPlayingAudio: false,
  renderPollInterval: null
};

// DOM Elements
const elements = {
  // Mode Switcher
  modeBtnGenerate: document.getElementById('modeBtnGenerate'),
  modeBtnDirect: document.getElementById('modeBtnDirect'),
  modeDescriptionText: document.getElementById('modeDescriptionText'),
  sectionModeA: document.getElementById('sectionModeA'),
  sectionModeB: document.getElementById('sectionModeB'),
  // Mode A: Audio Dropzone & Player
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
  // Mode B: Direct Video Dropzone & Player
  directVideoDropzone: document.getElementById('directVideoDropzone'),
  directVideoFileInput: document.getElementById('directVideoFileInput'),
  directVideoUploading: document.getElementById('directVideoUploading'),
  directVideoPlayerCard: document.getElementById('directVideoPlayerCard'),
  directVideoDurationBadge: document.getElementById('directVideoDurationBadge'),
  directVideoFileName: document.getElementById('directVideoFileName'),
  directVideoResBadge: document.getElementById('directVideoResBadge'),
  directWaveformBars: document.getElementById('directWaveformBars'),
  directWaveformPlayhead: document.getElementById('directWaveformPlayhead'),
  btnDirectAudioPlayPause: document.getElementById('btnDirectAudioPlayPause'),
  directAudioCurrentTime: document.getElementById('directAudioCurrentTime'),
  directAudioTotalTime: document.getElementById('directAudioTotalTime'),
  btnRemoveDirectVideo: document.getElementById('btnRemoveDirectVideo'),
  directScriptInput: document.getElementById('directScriptInput'),
  directScriptWordCount: document.getElementById('directScriptWordCount'),
  btnDirectAutoTranscribe: document.getElementById('btnDirectAutoTranscribe'),
  directCaptionStatusIndicator: document.getElementById('directCaptionStatusIndicator'),
  btnDirectSyncCaptions: document.getElementById('btnDirectSyncCaptions'),
  // Caption Template Section & Dual Colors
  color1Pills: document.getElementById('color1Pills'),
  customColor1Picker: document.getElementById('customColor1Picker'),
  customColor1Preview: document.getElementById('customColor1Preview'),
  customColor1Hex: document.getElementById('customColor1Hex'),
  color2Pills: document.getElementById('color2Pills'),
  customColor2Picker: document.getElementById('customColor2Picker'),
  customColor2Preview: document.getElementById('customColor2Preview'),
  customColor2Hex: document.getElementById('customColor2Hex'),
  captionTemplatesGrid: document.getElementById('captionTemplatesGrid'),
  captionCatTabs: document.querySelectorAll('.caption-cat-tab'),
  selectFontFamily: document.getElementById('selectFontFamily'),
  selectHeroFont: document.getElementById('selectHeroFont'),
  captionTemplateSearch: document.getElementById('captionTemplateSearch'),
  templateCountBadge: document.getElementById('templateCountBadge'),
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
  // Swap Clip Modal & Video Upload
  swapClipModal: document.getElementById('swapClipModal'),
  btnCloseSwapModal: document.getElementById('btnCloseSwapModal'),
  swapModalTitle: document.getElementById('swapModalTitle'),
  swapModalSubtitle: document.getElementById('swapModalSubtitle'),
  tabBtnPexels: document.getElementById('tabBtnPexels'),
  tabBtnUpload: document.getElementById('tabBtnUpload'),
  tabContentPexels: document.getElementById('tabContentPexels'),
  tabContentUpload: document.getElementById('tabContentUpload'),
  swapSearchInput: document.getElementById('swapSearchInput'),
  btnExecuteSearch: document.getElementById('btnExecuteSearch'),
  swapSuggestedChips: document.getElementById('swapSuggestedChips'),
  swapResultsGrid: document.getElementById('swapResultsGrid'),
  videoUploadDropzone: document.getElementById('videoUploadDropzone'),
  userVideoFileInput: document.getElementById('userVideoFileInput'),
  videoUploadLoading: document.getElementById('videoUploadLoading'),
  userClipsGrid: document.getElementById('userClipsGrid'),
  userClipsCount: document.getElementById('userClipsCount'),
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
  renderColor1Pills();
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
    state.famousFonts = data.famous_fonts || [];

    // If active template is not in list, fallback to first
    if (state.captionTemplates.length && !state.captionTemplates.find(t => t.id === state.selectedTemplate)) {
      state.selectedTemplate = state.captionTemplates[0].id;
    }

    renderColor1Pills();
    renderColor2Pills();
    renderCaptionTemplates();
  } catch (e) {
    console.error('Failed to load caption templates:', e);
  }
}

function getActivePrimaryHex() {
  if (state.selectedPrimaryColor && state.selectedPrimaryColor.startsWith('#')) {
    return state.selectedPrimaryColor;
  }
  return PRIMARY_COLORS[state.selectedPrimaryColor]?.hex || '#ffffff';
}

function getActiveHighlightHex() {
  if (state.selectedHighlightColor && state.selectedHighlightColor.startsWith('#')) {
    return state.selectedHighlightColor;
  }
  return state.highlightColors[state.selectedHighlightColor]?.hex || '#facc15';
}

function renderColor1Pills() {
  if (!elements.color1Pills) return;
  elements.color1Pills.innerHTML = '';
  const currentHex = getActivePrimaryHex().toLowerCase();

  Object.entries(PRIMARY_COLORS).forEach(([key, info]) => {
    const isSelected = currentHex === info.hex.toLowerCase() || state.selectedPrimaryColor === key;
    const btn = document.createElement('button');
    btn.className = `w-5 h-5 rounded-full border-2 transition ${isSelected ? 'border-brand-400 scale-125 shadow-lg ring-2 ring-brand-500/50' : 'border-transparent hover:scale-110'}`;
    btn.style.backgroundColor = info.hex;
    btn.title = info.name;
    btn.addEventListener('click', () => {
      state.selectedPrimaryColor = info.hex;
      if (elements.customColor1Picker) elements.customColor1Picker.value = info.hex;
      if (elements.customColor1Preview) elements.customColor1Preview.style.backgroundColor = info.hex;
      if (elements.customColor1Hex) elements.customColor1Hex.textContent = info.hex;
      renderColor1Pills();
      renderCaptionTemplates();
      updateLiveKaraokeCaption(elements.htmlAudio.currentTime || 0);
    });
    elements.color1Pills.appendChild(btn);
  });

  if (elements.customColor1Picker) elements.customColor1Picker.value = currentHex;
  if (elements.customColor1Preview) elements.customColor1Preview.style.backgroundColor = currentHex;
  if (elements.customColor1Hex) elements.customColor1Hex.textContent = currentHex;
}

function renderColor2Pills() {
  if (!elements.color2Pills) return;
  elements.color2Pills.innerHTML = '';
  const currentHex = getActiveHighlightHex().toLowerCase();

  Object.entries(state.highlightColors).forEach(([key, info]) => {
    const isSelected = currentHex === info.hex.toLowerCase() || state.selectedHighlightColor === key;
    const btn = document.createElement('button');
    btn.className = `w-5 h-5 rounded-full border-2 transition ${isSelected ? 'border-white scale-125 shadow-lg ring-2 ring-brand-500/50' : 'border-transparent hover:scale-110'}`;
    btn.style.backgroundColor = info.hex;
    btn.title = info.name;
    btn.addEventListener('click', () => {
      state.selectedHighlightColor = info.hex;
      if (elements.customColor2Picker) elements.customColor2Picker.value = info.hex;
      if (elements.customColor2Preview) elements.customColor2Preview.style.backgroundColor = info.hex;
      if (elements.customColor2Hex) elements.customColor2Hex.textContent = info.hex;
      renderColor2Pills();
      renderCaptionTemplates();
      updateLiveKaraokeCaption(elements.htmlAudio.currentTime || 0);
    });
    elements.color2Pills.appendChild(btn);
  });

  if (elements.customColor2Picker) elements.customColor2Picker.value = currentHex;
  if (elements.customColor2Preview) elements.customColor2Preview.style.backgroundColor = currentHex;
  if (elements.customColor2Hex) elements.customColor2Hex.textContent = currentHex;
}

function renderCaptionTemplates() {
  elements.captionTemplatesGrid.innerHTML = '';

  const search = (state.templateSearchTerm || '').toLowerCase();
  const category = state.activeCategory;

  const filtered = state.captionTemplates.filter(tpl => {
    // Category match
    const catMatch = (category === 'All') || (tpl.category && tpl.category.toLowerCase() === category.toLowerCase());
    if (!catMatch) return false;

    // Search match
    if (search) {
      const nameMatch = (tpl.name || '').toLowerCase().includes(search);
      const catNameMatch = (tpl.category || '').toLowerCase().includes(search);
      const animMatch = (tpl.animation || '').toLowerCase().includes(search);
      const badgeMatch = (tpl.badge || '').toLowerCase().includes(search);
      return nameMatch || catNameMatch || animMatch || badgeMatch;
    }
    return true;
  });

  if (elements.templateCountBadge) {
    elements.templateCountBadge.textContent = `${filtered.length} template${filtered.length === 1 ? '' : 's'}`;
  }

  if (!filtered.length) {
    elements.captionTemplatesGrid.innerHTML = `
      <div class="col-span-full py-8 text-center text-xs text-slate-500">
        No templates found matching "${search}". Try another keyword or select "All".
      </div>
    `;
    return;
  }

  filtered.forEach(tpl => {
    const isSelected = state.selectedTemplate === tpl.id;
    const card = document.createElement('div');
    card.className = `caption-card relative bg-surface-850 border border-slate-800 rounded-xl p-2.5 flex flex-col justify-between h-28 select-none transition ${isSelected ? 'active-tpl' : 'hover:border-slate-700'}`;
    
    // Top badge
    const badgeText = tpl.badge || tpl.category || 'Pro';
    const badgeColor = tpl.id === 'none' ? 'bg-slate-700 text-slate-300' : 'bg-brand-500/20 text-brand-400 border border-brand-500/30';

    card.innerHTML = `
      <div class="flex items-center justify-between pointer-events-none">
        <span class="text-[9px] uppercase font-bold px-1.5 py-0.2 rounded ${badgeColor}">${badgeText}</span>
        ${isSelected ? '<i data-lucide="check-circle-2" class="w-3.5 h-3.5 text-brand-400"></i>' : ''}
      </div>

      <!-- Preview Text Display -->
      <div class="flex-1 flex items-center justify-center text-center px-1 my-1 overflow-hidden pointer-events-none">
        ${getTemplatePreviewHtml(tpl)}
      </div>

      <div class="text-[10px] text-slate-400 font-medium truncate text-center pointer-events-none" title="${tpl.name}">
        ${tpl.name}
      </div>
    `;

    card.addEventListener('click', () => {
      state.selectedTemplate = tpl.id;
      if (elements.activeTemplateBadge) elements.activeTemplateBadge.textContent = tpl.name;
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

  const primaryHex = getActivePrimaryHex();
  const highlightHex = getActiveHighlightHex();
  
  // Font resolution
  const bodyFont = state.selectedFontFamily || tpl.body_font || tpl.fontname || 'Montserrat';
  const heroFont = state.selectedHeroFont || tpl.hero_font || bodyFont;
  const isItalic = tpl.italic || tpl.hero_italic;
  const anim = tpl.animation || 'bounce';

  const previewText = tpl.preview_text || 'AMAZING VIDEO';
  const highlightWord = tpl.preview_highlight || previewText.split(' ')[0] || 'VIDEO';

  let extraShadow = 'text-shadow: 0 2px 4px rgba(0,0,0,0.8);';
  if (['glow_pulse', 'neon_glow', 'aura', 'laser'].includes(anim)) {
    extraShadow = `text-shadow: 0 0 8px ${highlightHex}, 0 0 14px #00ffff;`;
  } else if (['fire_pulse', 'firestorm'].includes(anim)) {
    extraShadow = `text-shadow: 0 0 8px #ff4500, 0 0 14px #ff0000;`;
  }

  // Multi-font hybrid templates display
  if (tpl.category === 'Hybrid' || tpl.hero_font || state.selectedHeroFont) {
    if (tpl.id === 'creator_hierarchy') {
      return `
        <div class="flex flex-col items-center justify-center space-y-0.5 pointer-events-none leading-none">
          <span class="text-[8px] uppercase tracking-widest font-semibold" style="font-family: '${bodyFont}', sans-serif; color: ${primaryHex}; opacity: 0.85;">WATCH THIS</span>
          <span class="text-[13px] uppercase font-black tracking-wide" style="font-family: '${heroFont}', sans-serif; color: ${highlightHex}; filter: drop-shadow(0 0 8px ${highlightHex});">GAME CHANGER</span>
          <span class="text-[8px] uppercase tracking-wider font-semibold" style="font-family: '${bodyFont}', sans-serif; color: ${primaryHex}; opacity: 0.85;">TODAY</span>
        </div>
      `;
    }

    if (tpl.id === 'devin_jatho_fx') {
      return `
        <div class="flex flex-col items-center justify-center pointer-events-none leading-tight">
          <span class="text-[9px] uppercase tracking-widest font-semibold" style="font-family: '${bodyFont}', sans-serif; color: ${primaryHex};">DEVIN JATHO</span>
          <span class="text-[12px] uppercase font-black" style="font-family: '${heroFont}', sans-serif; color: ${highlightHex}; text-shadow: 0 0 10px ${highlightHex};">TEXT EFFECT</span>
        </div>
      `;
    }

    // Two-tone / multi-font word pair (e.g. Smooth Cross, Serif Punch, MrBeast Duo, Apple Clean Duo)
    const words = previewText.split(' ');
    const firstWord = words[0] || 'SMOOTH';
    const secondWord = words.slice(1).join(' ') || 'CROSS';

    return `
      <div class="flex items-center justify-center space-x-1.5 pointer-events-none ${extraShadow}">
        <span class="text-[11px] font-bold" style="font-family: '${bodyFont}', sans-serif; color: ${primaryHex};">
          ${firstWord}
        </span>
        <span class="text-[13px] ${isItalic ? 'italic' : ''} font-black" style="font-family: '${heroFont}', cursive, sans-serif; color: ${highlightHex}; filter: drop-shadow(0 0 6px ${highlightHex});">
          ${secondWord}
        </span>
      </div>
    `;
  }

  // Standard templates (Color 1 for non-highlight words, Color 2 for highlight word)
  let formattedHtml = '';
  if (previewText.includes(highlightWord)) {
    const parts = previewText.split(highlightWord);
    formattedHtml = `
      <span style="font-family: '${bodyFont}', sans-serif; color: ${primaryHex};">${parts[0]}</span><span style="font-family: '${heroFont}', sans-serif; color: ${highlightHex}; filter: drop-shadow(0 0 6px ${highlightHex}); font-weight: 900;">${highlightWord}</span><span style="font-family: '${bodyFont}', sans-serif; color: ${primaryHex};">${parts.slice(1).join(highlightWord)}</span>
    `;
  } else {
    formattedHtml = `<span style="font-family: '${heroFont}', sans-serif; color: ${highlightHex};">${previewText}</span>`;
  }

  return `
    <span class="uppercase text-[11px] leading-tight tracking-tight line-clamp-2" style="${tpl.bold ? 'font-weight: 800;' : 'font-weight: 600;'} ${tpl.italic ? 'font-style: italic;' : ''} ${extraShadow}">
      ${formattedHtml}
    </span>
  `;
}

function setupEventListeners() {
  // Mode Switcher tabs
  if (elements.modeBtnGenerate) {
    elements.modeBtnGenerate.addEventListener('click', () => switchStudioMode('generate'));
  }
  if (elements.modeBtnDirect) {
    elements.modeBtnDirect.addEventListener('click', () => switchStudioMode('direct'));
  }

  // Script input word count
  elements.scriptInput.addEventListener('input', () => {
    const text = elements.scriptInput.value.trim();
    const words = text ? text.split(/\s+/).length : 0;
    elements.scriptWordCount.textContent = `${words} word${words === 1 ? '' : 's'}`;
  });

  // Direct video script input word count
  if (elements.directScriptInput) {
    elements.directScriptInput.addEventListener('input', () => {
      const text = elements.directScriptInput.value.trim();
      const words = text ? text.split(/\s+/).length : 0;
      elements.directScriptWordCount.textContent = `${words} word${words === 1 ? '' : 's'}`;
    });
  }

  // Auto-transcribe buttons
  elements.btnAutoTranscribe.addEventListener('click', handleAutoTranscribe);
  if (elements.btnDirectAutoTranscribe) {
    elements.btnDirectAutoTranscribe.addEventListener('click', handleDirectAutoTranscribe);
  }
  if (elements.btnDirectSyncCaptions) {
    elements.btnDirectSyncCaptions.addEventListener('click', handleDirectSyncCaptions);
  }

  // Color 1 Custom Color Picker
  if (elements.customColor1Picker) {
    elements.customColor1Picker.addEventListener('input', (e) => {
      const hex = e.target.value.toLowerCase();
      state.selectedPrimaryColor = hex;
      if (elements.customColor1Preview) elements.customColor1Preview.style.backgroundColor = hex;
      if (elements.customColor1Hex) elements.customColor1Hex.textContent = hex;
      renderColor1Pills();
      renderCaptionTemplates();
      updateLiveKaraokeCaption(elements.htmlAudio.currentTime || 0);
    });
  }

  // Color 2 Custom Color Picker
  if (elements.customColor2Picker) {
    elements.customColor2Picker.addEventListener('input', (e) => {
      const hex = e.target.value.toLowerCase();
      state.selectedHighlightColor = hex;
      if (elements.customColor2Preview) elements.customColor2Preview.style.backgroundColor = hex;
      if (elements.customColor2Hex) elements.customColor2Hex.textContent = hex;
      renderColor2Pills();
      renderCaptionTemplates();
      updateLiveKaraokeCaption(elements.htmlAudio.currentTime || 0);
    });
  }

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

  // Base Font Selector
  if (elements.selectFontFamily) {
    elements.selectFontFamily.addEventListener('change', (e) => {
      state.selectedFontFamily = e.target.value;
      renderCaptionTemplates();
      updateLiveKaraokeCaption(elements.htmlAudio.currentTime || 0);
    });
  }

  // Hero Font Selector
  if (elements.selectHeroFont) {
    elements.selectHeroFont.addEventListener('change', (e) => {
      state.selectedHeroFont = e.target.value;
      renderCaptionTemplates();
      updateLiveKaraokeCaption(elements.htmlAudio.currentTime || 0);
    });
  }

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

  // Audio drag & drop (Mode A)
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

  // Direct Video drag & drop (Mode B)
  if (elements.directVideoDropzone) {
    elements.directVideoDropzone.addEventListener('dragover', (e) => {
      e.preventDefault();
      elements.directVideoDropzone.classList.add('border-emerald-500');
    });
    elements.directVideoDropzone.addEventListener('dragleave', () => {
      elements.directVideoDropzone.classList.remove('border-emerald-500');
    });
    elements.directVideoDropzone.addEventListener('drop', (e) => {
      e.preventDefault();
      elements.directVideoDropzone.classList.remove('border-emerald-500');
      if (e.dataTransfer.files.length) {
        handleDirectVideoUpload(e.dataTransfer.files[0]);
      }
    });
  }
  if (elements.directVideoFileInput) {
    elements.directVideoFileInput.addEventListener('change', (e) => {
      if (e.target.files.length) {
        handleDirectVideoUpload(e.target.files[0]);
      }
    });
  }

  // Audio player controls
  elements.btnAudioPlayPause.addEventListener('click', toggleAudioPlayback);
  elements.btnRemoveAudio.addEventListener('click', resetAudio);
  if (elements.btnDirectAudioPlayPause) {
    elements.btnDirectAudioPlayPause.addEventListener('click', toggleAudioPlayback);
  }
  if (elements.btnRemoveDirectVideo) {
    elements.btnRemoveDirectVideo.addEventListener('click', resetDirectVideo);
  }

  elements.htmlAudio.addEventListener('timeupdate', updateAudioPlayhead);
  elements.htmlAudio.addEventListener('ended', () => {
    state.currentPlayingAudio = false;
    updateAudioPlayButtonIcon();
    elements.waveformPlayhead.style.left = '0%';
    if (elements.directWaveformPlayhead) elements.directWaveformPlayhead.style.left = '0%';
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

  // Creator Font Style Selector
  if (elements.selectFontFamily) {
    elements.selectFontFamily.addEventListener('change', (e) => {
      state.selectedFontFamily = e.target.value;
      renderCaptionTemplates();
      updateLiveKaraokeCaption(elements.htmlAudio.currentTime || 0);
    });
  }

  // Template Search Bar
  if (elements.captionTemplateSearch) {
    elements.captionTemplateSearch.addEventListener('input', (e) => {
      state.templateSearchTerm = e.target.value;
      renderCaptionTemplates();
    });
  }

  // Swap Clip Modal Tabs
  if (elements.tabBtnPexels) {
    elements.tabBtnPexels.addEventListener('click', () => switchSwapModalTab('pexels'));
  }
  if (elements.tabBtnUpload) {
    elements.tabBtnUpload.addEventListener('click', () => switchSwapModalTab('upload'));
  }

  // Custom Video Upload file input & dropzone
  if (elements.userVideoFileInput) {
    elements.userVideoFileInput.addEventListener('change', (e) => {
      if (e.target.files.length) {
        handleCustomVideoUpload(e.target.files[0]);
      }
    });
  }

  if (elements.videoUploadDropzone) {
    elements.videoUploadDropzone.addEventListener('dragover', (e) => {
      e.preventDefault();
      elements.videoUploadDropzone.classList.add('dragover', 'border-brand-500');
    });
    elements.videoUploadDropzone.addEventListener('dragleave', () => {
      elements.videoUploadDropzone.classList.remove('dragover', 'border-brand-500');
    });
    elements.videoUploadDropzone.addEventListener('drop', (e) => {
      e.preventDefault();
      elements.videoUploadDropzone.classList.remove('dragover', 'border-brand-500');
      if (e.dataTransfer.files.length) {
        handleCustomVideoUpload(e.dataTransfer.files[0]);
      }
    });
  }

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

  if (elements.directAudioCurrentTime) elements.directAudioCurrentTime.textContent = formatTime(current);
  if (elements.directWaveformPlayhead) elements.directWaveformPlayhead.style.left = `${Math.min(100, percent)}%`;

  // Highlight active waveform bars (Mode A)
  const totalBars = elements.waveformBars.children.length;
  const activeCount = Math.floor((percent / 100) * totalBars);
  Array.from(elements.waveformBars.children).forEach((bar, idx) => {
    if (idx <= activeCount) {
      bar.classList.add('active');
    } else {
      bar.classList.remove('active');
    }
  });

  // Highlight active waveform bars (Mode B)
  if (elements.directWaveformBars && elements.directWaveformBars.children.length) {
    const totalDirectBars = elements.directWaveformBars.children.length;
    const activeDirectCount = Math.floor((percent / 100) * totalDirectBars);
    Array.from(elements.directWaveformBars.children).forEach((bar, idx) => {
      if (idx <= activeDirectCount) {
        bar.classList.add('active');
      } else {
        bar.classList.remove('active');
      }
    });
  }

  // Sync live video preview
  if (state.studioMode === 'direct' && elements.livePreviewVideo.src) {
    if (Math.abs(elements.livePreviewVideo.currentTime - current) > 0.3) {
      elements.livePreviewVideo.currentTime = current;
    }
  } else {
    syncLiveVideoScene(current);
  }

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

// Mode Switcher function
function switchStudioMode(mode) {
  state.studioMode = mode;
  if (mode === 'direct') {
    elements.modeBtnDirect.className = 'px-4 py-2 rounded-lg text-xs font-semibold flex items-center space-x-2 transition bg-emerald-600 text-white shadow';
    elements.modeBtnGenerate.className = 'px-4 py-2 rounded-lg text-xs font-semibold flex items-center space-x-2 transition bg-transparent hover:bg-slate-800 text-slate-300';
    elements.modeDescriptionText.innerHTML = `
      <i data-lucide="video" class="w-3.5 h-3.5 text-emerald-400 shrink-0"></i>
      <span>Upload your full video directly. Auto-extract audio, generate timestamps, and burn styled multi-font captions.</span>
    `;
    elements.sectionModeA.classList.add('hidden');
    elements.sectionModeB.classList.remove('hidden');

    if (state.directVideo) {
      elements.storyboardSection.classList.remove('hidden');
      if (elements.timelineSegmentsBar) elements.timelineSegmentsBar.parentElement.classList.add('hidden');
      if (elements.storyboardGrid) elements.storyboardGrid.classList.add('hidden');
      if (elements.btnAutoMatchAllAgain) elements.btnAutoMatchAllAgain.classList.add('hidden');
      if (elements.btnRenderVideo) elements.btnRenderVideo.innerHTML = '<i data-lucide="film" class="w-4 h-4"></i><span>Burn Captions & Export Video</span>';
    }
  } else {
    elements.modeBtnGenerate.className = 'px-4 py-2 rounded-lg text-xs font-semibold flex items-center space-x-2 transition bg-brand-600 text-white shadow';
    elements.modeBtnDirect.className = 'px-4 py-2 rounded-lg text-xs font-semibold flex items-center space-x-2 transition bg-transparent hover:bg-slate-800 text-slate-300';
    elements.modeDescriptionText.innerHTML = `
      <i data-lucide="sparkles" class="w-3.5 h-3.5 text-amber-400 shrink-0"></i>
      <span>Upload audio, auto-match visual scenes from Pexels, and add CapCut animated captions.</span>
    `;
    elements.sectionModeB.classList.add('hidden');
    elements.sectionModeA.classList.remove('hidden');

    if (elements.timelineSegmentsBar) elements.timelineSegmentsBar.parentElement.classList.remove('hidden');
    if (elements.storyboardGrid) elements.storyboardGrid.classList.remove('hidden');
    if (elements.btnAutoMatchAllAgain) elements.btnAutoMatchAllAgain.classList.remove('hidden');
    if (elements.btnRenderVideo) elements.btnRenderVideo.innerHTML = '<i data-lucide="film" class="w-4 h-4"></i><span>Render Final Video</span>';
  }
  lucide.createIcons();
}

// Direct Video Upload Handler
async function handleDirectVideoUpload(file) {
  if (!elements.directVideoUploading || !elements.directVideoDropzone) return;
  elements.directVideoUploading.classList.remove('hidden');
  elements.directVideoDropzone.classList.add('opacity-50', 'pointer-events-none');

  const formData = new FormData();
  formData.append('file', file);

  try {
    const resp = await fetch('/api/upload-direct-video', {
      method: 'POST',
      body: formData
    });
    if (!resp.ok) {
      const err = await resp.json();
      throw new Error(err.detail || 'Failed to process video');
    }

    const data = await resp.json();
    setDirectVideoState(data);
  } catch (err) {
    alert('Video upload error: ' + err.message);
  } finally {
    elements.directVideoUploading.classList.add('hidden');
    elements.directVideoDropzone.classList.remove('opacity-50', 'pointer-events-none');
  }
}

function setDirectVideoState(data) {
  state.directVideo = data;
  state.audioId = data.audio_id;
  state.audioDuration = data.duration;
  state.audioFileName = data.filename;
  state.waveformPeaks = data.waveform || [];

  // Update Direct UI
  elements.directVideoDropzone.classList.add('hidden');
  elements.directVideoPlayerCard.classList.remove('hidden');
  elements.directVideoDurationBadge.classList.remove('hidden');
  elements.directVideoDurationBadge.textContent = data.formatted_duration;
  elements.directVideoFileName.textContent = data.filename;
  elements.directVideoResBadge.textContent = `${data.width}x${data.height}`;
  elements.directAudioTotalTime.textContent = formatTime(data.duration);
  elements.directAudioCurrentTime.textContent = '00:00';

  // Audio element source
  elements.htmlAudio.src = `/api/audio/${data.audio_id}`;
  elements.htmlAudio.load();

  // Live video preview
  elements.livePreviewVideo.dataset.src = data.video_url;
  elements.livePreviewVideo.src = data.video_url;
  elements.livePreviewVideo.load();

  // Render direct waveform bars
  renderDirectWaveform(state.waveformPeaks);

  // Show storyboard section in direct mode
  elements.storyboardSection.classList.remove('hidden');
  if (elements.timelineSegmentsBar) elements.timelineSegmentsBar.parentElement.classList.add('hidden');
  if (elements.storyboardGrid) elements.storyboardGrid.classList.add('hidden');
  if (elements.btnAutoMatchAllAgain) elements.btnAutoMatchAllAgain.classList.add('hidden');
  if (elements.btnRenderVideo) elements.btnRenderVideo.innerHTML = '<i data-lucide="film" class="w-4 h-4"></i><span>Burn Captions & Export Video</span>';
  lucide.createIcons();
}

function resetDirectVideo() {
  state.directVideo = null;
  state.audioId = null;
  state.audioDuration = 0;
  elements.htmlAudio.pause();
  elements.htmlAudio.src = '';
  elements.livePreviewVideo.pause();
  elements.livePreviewVideo.src = '';
  elements.directVideoPlayerCard.classList.add('hidden');
  elements.directVideoDropzone.classList.remove('hidden');
  elements.directVideoDurationBadge.classList.add('hidden');
  elements.liveCaptionOverlay.innerHTML = '';
}

function renderDirectWaveform(peaks) {
  if (!elements.directWaveformBars) return;
  elements.directWaveformBars.innerHTML = '';
  peaks.forEach((peak, i) => {
    const bar = document.createElement('div');
    bar.className = 'waveform-bar w-1 bg-slate-700 rounded-full cursor-pointer hover:bg-emerald-400';
    bar.style.height = `${Math.max(12, peak * 100)}%`;
    bar.dataset.index = i;
    bar.addEventListener('click', () => {
      const progress = i / peaks.length;
      elements.htmlAudio.currentTime = progress * state.audioDuration;
      if (elements.livePreviewVideo) {
        elements.livePreviewVideo.currentTime = elements.htmlAudio.currentTime;
      }
      if (!state.currentPlayingAudio) toggleAudioPlayback();
    });
    elements.directWaveformBars.appendChild(bar);
  });
}

async function handleDirectAutoTranscribe() {
  if (!state.audioId) {
    alert('Please upload a video file first.');
    return;
  }

  elements.btnDirectAutoTranscribe.disabled = true;
  elements.btnDirectAutoTranscribe.innerHTML = '<i data-lucide="loader-2" class="w-3 h-3 animate-spin"></i><span>Transcribing...</span>';
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
      elements.directScriptInput.value = data.transcript;
      elements.directScriptInput.dispatchEvent(new Event('input'));
    }

    state.captionCards = data.cards || [];
    state.timedWords = data.words || [];
    elements.directCaptionStatusIndicator.textContent = `Aligned ${state.timedWords.length} words`;
    updateLiveKaraokeCaption(elements.htmlAudio.currentTime || 0);
  } catch (err) {
    alert('Speech recognition error: ' + err.message);
  } finally {
    elements.btnDirectAutoTranscribe.disabled = false;
    elements.btnDirectAutoTranscribe.innerHTML = '<i data-lucide="mic" class="w-3 h-3"></i><span>Auto-Transcribe Video Audio</span>';
    lucide.createIcons();
  }
}

async function handleDirectSyncCaptions() {
  if (!state.audioId) {
    alert('Please upload a video file first.');
    return;
  }

  const scriptText = elements.directScriptInput.value.trim();
  if (!scriptText) {
    alert('Please enter or transcribe a script for caption alignment.');
    return;
  }

  elements.btnDirectSyncCaptions.disabled = true;
  elements.btnDirectSyncCaptions.innerHTML = '<i data-lucide="loader-2" class="w-4 h-4 animate-spin"></i><span>Aligning Word Timestamps...</span>';
  lucide.createIcons();

  try {
    const resp = await fetch('/api/generate-captions', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        audio_id: state.audioId,
        script_text: scriptText,
        template_id: state.selectedTemplate
      })
    });
    if (!resp.ok) throw new Error('Failed to align captions');
    const data = await resp.json();

    state.captionCards = data.cards || [];
    state.timedWords = data.words || [];
    elements.directCaptionStatusIndicator.textContent = `Aligned ${state.timedWords.length} words`;

    // Ensure player is ready
    elements.storyboardSection.classList.remove('hidden');
    elements.livePreviewVideo.dataset.src = state.directVideo.video_url;
    elements.livePreviewVideo.src = state.directVideo.video_url;
    elements.livePreviewVideo.currentTime = 0;
    elements.htmlAudio.currentTime = 0;
    updateLiveKaraokeCaption(0);

    // Scroll to player
    elements.storyboardSection.scrollIntoView({ behavior: 'smooth' });
  } catch (err) {
    alert('Alignment error: ' + err.message);
  } finally {
    elements.btnDirectSyncCaptions.disabled = false;
    elements.btnDirectSyncCaptions.innerHTML = '<i data-lucide="subtitles" class="w-4 h-4"></i><span>Align Speech & Preview Captions</span>';
    lucide.createIcons();
  }
}

// Real-time CapCut word-by-word highlight in player with Multi-Font and Dual-Colors
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

  const tpl = state.captionTemplates.find(t => t.id === state.selectedTemplate) || {};
  const primaryHex = getActivePrimaryHex();
  const highlightHex = getActiveHighlightHex();
  const bodyFont = state.selectedFontFamily || tpl.body_font || tpl.fontname || 'Montserrat';
  const heroFont = state.selectedHeroFont || tpl.hero_font || bodyFont;
  const anim = tpl.animation || 'bounce';

  // Map anim name to CSS anim class
  let animClass = 'anim-bounce';
  if (['word_zoom', 'mega_zoom', 'stomp'].includes(anim)) animClass = 'anim-zoom';
  else if (['glow_pulse', 'neon_glow', 'aura', 'laser'].includes(anim)) animClass = 'anim-glow';
  else if (['fire_pulse', 'firestorm'].includes(anim)) animClass = 'anim-fire';
  else if (['comic_pop', 'boom'].includes(anim)) animClass = 'anim-pop';
  else if (['slide_up', 'drift_left', 'elevator', 'wave'].includes(anim)) animClass = 'anim-slide';
  else if (['glitch', 'pixel', 'retro_vhs', 'matrix'].includes(anim)) animClass = 'anim-glitch';

  const isItalic = (tpl.italic || tpl.hero_italic) ? 'italic' : '';
  const isBold = tpl.bold ? 'font-black' : 'font-bold';

  elements.liveCaptionOverlay.className = `absolute inset-x-4 bottom-6 flex flex-wrap items-center justify-center text-center pointer-events-none transition duration-150`;

  const wordsHtml = activeCard.words.map(w => {
    const isSpoken = currentTime >= w.start && currentTime <= w.end;
    if (isSpoken) {
      return `
        <span class="karaoke-word ${isBold} ${isItalic} active-word ${animClass}" style="font-family: '${heroFont}', cursive, sans-serif; color: ${highlightHex}; text-shadow: 0 0 16px ${highlightHex}, 0 2px 6px #000; transform: scale(1.18);">
          ${w.word}
        </span>
      `;
    } else {
      return `
        <span class="karaoke-word ${isBold}" style="font-family: '${bodyFont}', sans-serif; color: ${primaryHex}; text-shadow: 0 2px 5px rgba(0,0,0,0.9);">
          ${w.word}
        </span>
      `;
    }
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

        <div class="flex items-center space-x-1.5">
          <button class="btn-upload-clip text-xs px-2.5 py-1.5 rounded-lg bg-surface-900 hover:bg-slate-800 text-slate-300 hover:text-white border border-slate-700 flex items-center space-x-1 transition" title="Upload your own video clip for this scene">
            <i data-lucide="upload-cloud" class="w-3.5 h-3.5 text-brand-400"></i>
            <span>Upload</span>
          </button>
          <button class="btn-swap-clip text-xs px-2.5 py-1.5 rounded-lg bg-surface-900 hover:bg-slate-800 text-brand-400 hover:text-brand-300 border border-slate-700 flex items-center space-x-1 transition" title="Search Pexels stock video">
            <i data-lucide="refresh-ccw" class="w-3.5 h-3.5"></i>
            <span>Pexels</span>
          </button>
        </div>
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
    
    // Upload custom clip handler
    card.querySelector('.btn-upload-clip').addEventListener('click', () => openSwapModal(index, 'upload'));

    // Swap clip handler (Pexels)
    card.querySelector('.btn-swap-clip').addEventListener('click', () => openSwapModal(index, 'pexels'));

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
function openSwapModal(sceneIndex, initialTab = 'pexels') {
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
  switchSwapModalTab(initialTab);
}

function switchSwapModalTab(tab) {
  if (tab === 'pexels') {
    elements.tabBtnPexels.className = 'px-3.5 py-1.5 rounded-lg text-xs font-semibold bg-brand-600 text-white flex items-center space-x-1.5 transition';
    elements.tabBtnUpload.className = 'px-3.5 py-1.5 rounded-lg text-xs font-semibold bg-surface-850 hover:bg-slate-800 text-slate-300 flex items-center space-x-1.5 transition';
    elements.tabContentPexels.classList.remove('hidden');
    elements.tabContentUpload.classList.add('hidden');
    executeSwapSearch();
  } else {
    elements.tabBtnUpload.className = 'px-3.5 py-1.5 rounded-lg text-xs font-semibold bg-brand-600 text-white flex items-center space-x-1.5 transition';
    elements.tabBtnPexels.className = 'px-3.5 py-1.5 rounded-lg text-xs font-semibold bg-surface-850 hover:bg-slate-800 text-slate-300 flex items-center space-x-1.5 transition';
    elements.tabContentUpload.classList.remove('hidden');
    elements.tabContentPexels.classList.add('hidden');
    renderUserClipsGrid();
  }
  lucide.createIcons();
}

// Custom User Video Upload Handler
async function handleCustomVideoUpload(file) {
  if (!file) return;

  const validTypes = ['video/mp4', 'video/quicktime', 'video/webm', 'video/x-matroska', 'video/avi'];
  if (!file.type.startsWith('video/') && !validTypes.includes(file.type)) {
    alert('Please select a valid video file (.mp4, .mov, .webm, .mkv).');
    return;
  }

  elements.videoUploadLoading.classList.remove('hidden');
  const formData = new FormData();
  formData.append('file', file);

  try {
    const resp = await fetch('/api/upload-video', {
      method: 'POST',
      body: formData
    });

    if (!resp.ok) {
      const err = await resp.json();
      throw new Error(err.detail || 'Upload failed');
    }

    const data = await resp.json();
    const clip = data.clip;

    // Add to local user clips session store
    if (!state.userClips.some(c => c.id === clip.id)) {
      state.userClips.unshift(clip);
    }

    // Assign to active scene
    if (state.activeSwapSceneIndex !== null && state.scenes[state.activeSwapSceneIndex]) {
      state.scenes[state.activeSwapSceneIndex].selected_clip = clip;
      renderStoryboard();
      renderTimelineOverview();
      syncLiveVideoScene(elements.htmlAudio.currentTime || 0);
      elements.swapClipModal.classList.add('hidden');
    }

    renderUserClipsGrid();

  } catch (e) {
    alert('Failed to upload video: ' + e.message);
  } finally {
    elements.videoUploadLoading.classList.add('hidden');
    if (elements.userVideoFileInput) elements.userVideoFileInput.value = '';
  }
}

function renderUserClipsGrid() {
  if (!elements.userClipsGrid) return;
  elements.userClipsGrid.innerHTML = '';
  if (elements.userClipsCount) {
    elements.userClipsCount.textContent = `${state.userClips.length} clip${state.userClips.length === 1 ? '' : 's'}`;
  }

  if (!state.userClips.length) {
    elements.userClipsGrid.innerHTML = `
      <div class="col-span-full py-8 text-center text-xs text-slate-500">
        No custom videos uploaded yet. Drag & drop a video above to use it in this scene!
      </div>
    `;
    return;
  }

  state.userClips.forEach(clip => {
    const card = document.createElement('div');
    card.className = 'group relative rounded-xl overflow-hidden border border-slate-800 hover:border-brand-500 bg-surface-850 flex flex-col justify-between transition cursor-pointer';

    card.innerHTML = `
      <div class="relative aspect-video bg-black overflow-hidden">
        <img src="${clip.preview_url || clip.image}" class="w-full h-full object-cover group-hover:opacity-0 transition duration-300">
        <video src="${clip.video_url}" muted loop preload="none" class="absolute inset-0 w-full h-full object-cover opacity-0 group-hover:opacity-100 transition duration-300"></video>
        <span class="absolute top-1.5 right-1.5 bg-brand-600/90 text-[10px] font-mono font-semibold text-white px-1.5 py-0.5 rounded">
          ${clip.duration}s
        </span>
      </div>
      <div class="p-2.5 flex items-center justify-between">
        <span class="text-[11px] text-slate-300 font-medium truncate max-w-[130px]">${clip.title}</span>
        <button class="btn-select-clip px-2.5 py-1 bg-brand-600 hover:bg-brand-500 text-white rounded text-[10px] font-semibold transition">
          Use
        </button>
      </div>
    `;

    const videoEl = card.querySelector('video');
    card.addEventListener('mouseenter', () => videoEl.play().catch(() => {}));
    card.addEventListener('mouseleave', () => {
      videoEl.pause();
      videoEl.currentTime = 0;
    });

    card.querySelector('.btn-select-clip').addEventListener('click', () => {
      if (state.activeSwapSceneIndex !== null && state.scenes[state.activeSwapSceneIndex]) {
        state.scenes[state.activeSwapSceneIndex].selected_clip = clip;
        renderStoryboard();
        renderTimelineOverview();
        syncLiveVideoScene(elements.htmlAudio.currentTime || 0);
        elements.swapClipModal.classList.add('hidden');
      }
    });

    elements.userClipsGrid.appendChild(card);
  });
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
  // Mode B: Direct Video Mode
  if (state.studioMode === 'direct') {
    if (!state.directVideo || !state.audioId) {
      alert('Please upload your video file first.');
      return;
    }

    if (!state.captionCards.length) {
      const text = elements.directScriptInput ? elements.directScriptInput.value.trim() : '';
      if (text) {
        await handleDirectSyncCaptions();
      } else {
        alert('Please auto-transcribe or enter a script to generate animated captions.');
        return;
      }
    }

    elements.renderProgressModal.classList.remove('hidden');
    elements.renderResultBox.classList.add('hidden');
    elements.renderProgressBar.style.width = '5%';
    elements.renderPercentText.textContent = '5%';
    elements.renderPhaseText.textContent = 'Burning styled captions directly onto video with FFmpeg...';

    try {
      const isVertical = state.directVideo.height > state.directVideo.width;
      const resp = await fetch('/api/render', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          audio_id: state.audioId,
          scenes: [],
          is_direct_video: true,
          direct_video_path: state.directVideo.local_video_path,
          caption_template: state.selectedTemplate,
          primary_color: getActivePrimaryHex(),
          highlight_color: getActiveHighlightHex(),
          font_family: state.selectedFontFamily || null,
          hero_font: state.selectedHeroFont || null,
          caption_cards: state.captionCards,
          aspect_ratio: isVertical ? '9:16' : '16:9'
        })
      });

      if (!resp.ok) {
        const err = await resp.json();
        throw new Error(err.detail || 'Direct rendering failed');
      }

      const { job_id } = await resp.json();
      pollRenderStatus(job_id);

    } catch (e) {
      alert('Render failed: ' + e.message);
      elements.renderProgressModal.classList.add('hidden');
    }
    return;
  }

  // Mode A: Generated Scenes Mode
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
        primary_color: getActivePrimaryHex(),
        highlight_color: getActiveHighlightHex(),
        font_family: state.selectedFontFamily || null,
        hero_font: state.selectedHeroFont || null,
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
