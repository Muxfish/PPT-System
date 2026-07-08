/**
 * API service for communicating with the FastAPI backend.
 */
const API_BASE = '/api';

async function request(url, options = {}) {
  const config = {
    headers: { 'Content-Type': 'application/json', ...options.headers },
    ...options,
  };

  const response = await fetch(`${API_BASE}${url}`, config);

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: response.statusText }));
    throw new Error(error.detail || `Request failed: ${response.status}`);
  }

  // For HTML responses
  const contentType = response.headers.get('content-type');
  if (contentType && contentType.includes('text/html')) {
    return response.text();
  }

  return response.json();
}

export const api = {
  /** Get available themes and layouts */
  getThemes: () => request('/themes'),

  /** Generate a PPT outline (JSON structure only, fast) */
  generateOutline: (data) =>
    request('/generate-outline', {
      method: 'POST',
      body: JSON.stringify(data),
    }),

  /** Generate full PPT with detailed content */
  generateFull: (data) =>
    request('/generate-full', {
      method: 'POST',
      body: JSON.stringify(data),
    }),

  /** Enhance slides in an existing outline */
  enhanceSlides: (data) =>
    request('/enhance-slides', {
      method: 'POST',
      body: JSON.stringify(data),
    }),

  /** Render outline to HTML with optional bg_type */
  renderHTML: (outline, bgType = 'gradient') =>
    request(`/render-html?bg_type=${bgType}`, {
      method: 'POST',
      body: JSON.stringify(outline),
    }),

  /** Chat iteration */
  chat: (data) =>
    request('/chat', {
      method: 'POST',
      body: JSON.stringify(data),
    }),

  /** Health check */
  health: () => request('/health'),
};

/**
 * SSE stream for real-time generation progress.
 */
export function streamGenerate(data, callbacks) {
  const { onProgress, onComplete, onError } = callbacks;

  fetch(`${API_BASE}/stream-generate`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  }).then(async (response) => {
    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    let buffer = '';

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      buffer += decoder.decode(value, { stream: true });
      const lines = buffer.split('\n');
      buffer = lines.pop() || '';

      for (const line of lines) {
        if (line.startsWith('data: ')) {
          const data = line.slice(6);
          if (data === '[DONE]') {
            onComplete?.();
            return;
          }
          try {
            const parsed = JSON.parse(data);
            onProgress?.(parsed);
          } catch (e) {
            // Skip malformed JSON
          }
        }
      }
    }
  }).catch((err) => {
    onError?.(err);
  });
}
