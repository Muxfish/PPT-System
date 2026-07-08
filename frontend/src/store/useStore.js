import { create } from 'zustand';

const useStore = create((set, get) => ({
  // Generation state
  topic: '',
  style: 'style-b',
  theme: 'ikb-blue',
  audience: '',
  slideCount: 10,
  language: 'zh-CN',
  tone: '',
  additionalRequirements: '',
  includeImages: false,
  bgType: 'gradient', // gradient | photo | pattern | none

  // Generated result
  outline: null,
  htmlContent: null,

  // UI state
  step: 'input', // input | generating | outline | preview | html
  loading: false,
  error: null,
  streamMessages: [],

  // Actions
  setField: (field, value) => set({ [field]: value }),

  setOutline: (outline) => set({ outline, step: 'outline' }),

  setHtmlContent: (html) => set({ htmlContent: html, step: 'html' }),

  setStep: (step) => set({ step }),

  setLoading: (loading) => set({ loading }),

  setError: (err) => {
    if (err === null || err === undefined) { set({ error: null }); return; }
    if (typeof err === 'string') { set({ error: err }); return; }
    if (err.message) { set({ error: err.message }); return; }
    if (err.detail) { set({ error: err.detail }); return; }
    try { set({ error: JSON.stringify(err) }); } catch { set({ error: String(err) }); }
  },

  addStreamMessage: (msg) =>
    set((state) => ({
      streamMessages: [...state.streamMessages, msg],
    })),

  clearStreamMessages: () => set({ streamMessages: [] }),

  reset: () =>
    set({
      outline: null,
      htmlContent: null,
      step: 'input',
      loading: false,
      error: null,
      streamMessages: [],
    }),

  // Update a specific slide
  updateSlide: (index, slideData) =>
    set((state) => {
      if (!state.outline) return state;
      const slides = [...state.outline.slides];
      slides[index] = { ...slides[index], ...slideData };
      return { outline: { ...state.outline, slides } };
    }),

  // Get current theme info
  getThemeColors: () => {
    const { style, theme } = get();
    const colorMap = {
      'style-a': {
        'ink-classic': { bg: '#faf8f5', text: '#1a1a1a', accent: '#c41e3a' },
        'indigo-porcelain': { bg: '#f5f7fa', text: '#1e2a3a', accent: '#3b5998' },
        'forest-ink': { bg: '#f6f8f4', text: '#1a2e1a', accent: '#4a7c59' },
        'kraft-paper': { bg: '#fdf8f0', text: '#3d2b1f', accent: '#c4732e' },
        'sand-dune': { bg: '#fbf9f6', text: '#2e261e', accent: '#c4945a' },
      },
      'style-b': {
        'ikb-blue': { bg: '#ffffff', text: '#1a1a1a', accent: '#0015ff' },
        'lemon-yellow': { bg: '#ffffff', text: '#1a1a1a', accent: '#ffe600' },
        'lemon-green': { bg: '#ffffff', text: '#1a1a1a', accent: '#00ff62' },
        'safety-orange': { bg: '#ffffff', text: '#1a1a1a', accent: '#ff5f00' },
      },
    };
    return colorMap[style]?.[theme] || colorMap['style-b']['ikb-blue'];
  },
}));

export default useStore;
