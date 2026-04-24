/* ============================================
   RAG Chat — Frontend (stub/demo mode)
   US-01..US-09 визуальные заглушки
   ============================================ */
'use strict';

// ── State ──────────────────────────────────────
const state = {
  sessionId: 'demo-' + Math.random().toString(36).slice(2, 8),
  documents: [],
  messages: [],
  llm: { provider: 'openai', model: 'gpt-4o-mini' },
  apiKey: null,
  isLoading: false,
};

// ── Demo stub responses ─────────────────────────
const STUB_RESPONSES = [
  { text: 'Согласно загруженному документу, основная концепция RAG (Retrieval-Augmented Generation) заключается в дополнении языковой модели релевантным контекстом из базы знаний.', sources: [{ file: 'document.pdf', page: 3, snippet: '...RAG нивелирует эффект галлюцинаций за счёт поиска по подготовленной векторной БД...' }] },
  { text: 'В документе описаны три ключевые функции: выбор LLM, загрузка файлов с созданием эмбеддингов, и диалоговый интерфейс для работы с документами.', sources: [{ file: 'spec.md', page: 1, snippet: '...MVP включает минимум 3 функции: выбор LLM, загрузка файла, пользовательский интерфейс...' }] },
  { text: 'Целевая аудитория приложения — пользователи ПК и мобильных устройств, которым необходимо быстро находить информацию в больших документах.', sources: [{ file: 'requirements.pdf', page: 2, snippet: '...сокращает время на изучение документов для аналитиков и разработчиков...' }] },
];
let stubIdx = 0;

// ── DOM refs ────────────────────────────────────
const $ = id => document.getElementById(id);
const chatMessages  = $('chatMessages');
const queryInput    = $('queryInput');
const sendBtn       = $('sendBtn');
const documentList  = $('documentList');
const fileInput     = $('fileInput');
const dropZone      = $('dropZone');
const welcomeScreen = $('welcomeScreen');
const toastContainer = $('toastContainer');

// ── Init ────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
  bindEvents();
  updateLLMDisplay();
});

function bindEvents() {
  sendBtn.addEventListener('click', sendQuery);
  queryInput.addEventListener('keydown', e => {
    if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); sendQuery(); }
  });
  queryInput.addEventListener('input', autoResize);
  fileInput.addEventListener('change', e => handleFileSelect(e.target.files[0]));

  // Drag & drop
  dropZone.addEventListener('dragover', e => { e.preventDefault(); dropZone.classList.add('drag-over'); });
  dropZone.addEventListener('dragleave', () => dropZone.classList.remove('drag-over'));
  dropZone.addEventListener('drop', e => {
    e.preventDefault();
    dropZone.classList.remove('drag-over');
    handleFileSelect(e.dataTransfer.files[0]);
  });
  dropZone.addEventListener('click', () => fileInput.click());

  // Close modals on overlay click
  $('llmModal').addEventListener('click', e => { if (e.target === $('llmModal')) closeLLMModal(); });
  $('apiKeyModal').addEventListener('click', e => { if (e.target === $('apiKeyModal')) closeApiKeyModal(); });
}

function autoResize() {
  queryInput.style.height = 'auto';
  queryInput.style.height = Math.min(queryInput.scrollHeight, 120) + 'px';
}

// ── File handling ───────────────────────────────
function handleFileSelect(file) {
  if (!file) return;

  // US-01: Validation
  const allowed = ['.pdf', '.docx', '.txt', '.md'];
  const ext = '.' + file.name.split('.').pop().toLowerCase();
  if (!allowed.includes(ext)) {
    showToast('error', '❌ Формат не поддерживается. Допустимые: PDF, DOCX, TXT, MD');
    return;
  }
  if (file.size > 50 * 1024 * 1024) {
    showToast('error', '❌ Файл превышает допустимый размер 50 МБ');
    return;
  }
  if (state.documents.length >= 10) {
    showToast('error', '❌ Достигнут лимит: максимум 10 документов');
    return;
  }

  addDocument(file);
  fileInput.value = '';
}

function addDocument(file) {
  const doc = {
    id: 'doc-' + Date.now(),
    name: file.name,
    size: formatSize(file.size),
    ext: file.name.split('.').pop().toUpperCase(),
    status: 'processing',
    chunks: 0,
    pages: 0,
    selected: true,
  };
  state.documents.push(doc);
  renderDocuments();
  showToast('info', `📤 Загрузка: ${file.name}`);

  // Simulate processing
  setTimeout(() => {
    doc.status = 'ready';
    doc.chunks = Math.floor(Math.random() * 80) + 20;
    doc.pages  = Math.floor(Math.random() * 30) + 5;
    renderDocuments();
    showToast('success', `✅ ${file.name} готов (${doc.chunks} чанков)`);
    hideWelcome();
  }, 2000);
}

function formatSize(bytes) {
  if (bytes < 1024) return bytes + ' B';
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
  return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
}

// ── Render documents ────────────────────────────
function renderDocuments() {
  if (state.documents.length === 0) {
    documentList.innerHTML = `
      <div class="empty-state">
        <div class="empty-state-icon">📄</div>
        <p>Загрузите документ<br>для начала работы</p>
      </div>`;
    return;
  }

  documentList.innerHTML = state.documents.map(doc => `
    <div class="document-item ${doc.selected ? 'selected' : ''}" id="${doc.id}">
      <input type="checkbox" class="doc-checkbox" ${doc.selected ? 'checked' : ''}
             onchange="toggleDoc('${doc.id}', this.checked)">
      <div class="doc-icon">${docIcon(doc.ext)}</div>
      <div class="doc-info">
        <div class="doc-name" title="${doc.name}">${doc.name}</div>
        <div class="doc-meta">
          <span>${doc.size}</span>
          ${doc.status === 'ready' ? `<span>${doc.chunks} чанков · ${doc.pages} стр.</span>` : ''}
        </div>
        ${doc.status === 'processing' ? `
          <div class="progress-bar"><div class="progress-fill" style="width:60%;animation:progress 1.5s infinite alternate"></div></div>
        ` : ''}
      </div>
      <span class="doc-status ${doc.status}">${doc.status === 'ready' ? '✓ Готов' : '⏳'}</span>
      <button class="doc-delete" onclick="deleteDoc('${doc.id}')" title="Удалить">✕</button>
    </div>
  `).join('');
}

function docIcon(ext) {
  const icons = { PDF: '📕', DOCX: '📘', TXT: '📄', MD: '📝' };
  return icons[ext] || '📄';
}

function toggleDoc(id, selected) {
  const doc = state.documents.find(d => d.id === id);
  if (doc) { doc.selected = selected; renderDocuments(); }
}

function deleteDoc(id) {
  state.documents = state.documents.filter(d => d.id !== id);
  renderDocuments();
  if (state.documents.length === 0) {
    state.messages = [];
    renderMessages();
    showWelcome();
    showToast('info', 'ℹ️ Все документы удалены, история очищена');
  } else {
    showToast('success', '🗑️ Документ удалён');
  }
}

// ── Chat ────────────────────────────────────────
function sendQuery() {
  const text = queryInput.value.trim();
  if (!text || state.isLoading) return;

  // US-03: No documents check
  const ready = state.documents.filter(d => d.selected && d.status === 'ready');
  if (ready.length === 0) {
    showToast('error', '⚠️ Загрузите документ для начала работы');
    return;
  }

  hideWelcome();
  addMessage('user', text);
  queryInput.value = '';
  queryInput.style.height = 'auto';
  state.isLoading = true;
  sendBtn.disabled = true;

  // Typing indicator
  const typingId = addTyping();

  // Simulate LLM response (US-03)
  const delay = 1200 + Math.random() * 800;
  setTimeout(() => {
    removeTyping(typingId);
    const resp = STUB_RESPONSES[stubIdx % STUB_RESPONSES.length];
    stubIdx++;
    addMessage('assistant', resp.text, resp.sources);
    state.isLoading = false;
    sendBtn.disabled = false;
  }, delay);
}

function addMessage(role, text, sources = []) {
  const msg = { id: 'msg-' + Date.now(), role, text, sources, time: now() };
  state.messages.push(msg);
  renderMessages();
  scrollBottom();
}

function renderMessages() {
  // Keep welcome or messages
  const existing = chatMessages.querySelectorAll('.message, .typing-wrap');
  existing.forEach(el => el.remove());

  state.messages.forEach(msg => {
    const el = document.createElement('div');
    el.className = `message ${msg.role}`;
    el.id = msg.id;

    const sourcesHtml = msg.sources.length ? `
      <div class="sources-block">
        ${msg.sources.map(s => `
          <div class="source-card" onclick="toggleSnippet(this)">
            <div class="source-header">📎 ${s.file} · стр. ${s.page}</div>
            <div class="source-snippet">${s.snippet}</div>
          </div>
        `).join('')}
      </div>` : '';

    el.innerHTML = `
      <div class="message-avatar">${msg.role === 'user' ? '👤' : '🤖'}</div>
      <div class="message-body">
        <div class="message-bubble">${escHtml(msg.text)}${sourcesHtml}</div>
        <div class="message-time">${msg.time}</div>
      </div>`;
    chatMessages.appendChild(el);
  });
}

function addTyping() {
  const id = 'typing-' + Date.now();
  const el = document.createElement('div');
  el.className = 'message assistant typing-wrap';
  el.id = id;
  el.innerHTML = `
    <div class="message-avatar">🤖</div>
    <div class="message-body">
      <div class="typing-indicator">
        <div class="typing-dot"></div>
        <div class="typing-dot"></div>
        <div class="typing-dot"></div>
      </div>
    </div>`;
  chatMessages.appendChild(el);
  scrollBottom();
  return id;
}

function removeTyping(id) {
  const el = $(id);
  if (el) el.remove();
}

function toggleSnippet(card) {
  const snippet = card.querySelector('.source-snippet');
  snippet.style.webkitLineClamp = snippet.style.webkitLineClamp === 'unset' ? '2' : 'unset';
}

// ── LLM Modal ───────────────────────────────────
function openLLMModal() { $('llmModal').classList.remove('hidden'); }
function closeLLMModal() { $('llmModal').classList.add('hidden'); }

function onProviderChange() {
  const p = $('llmProvider').value;
  const modelSel = $('llmModel');
  const ollamaStatus = $('ollamaStatus');

  if (p === 'openai') {
    modelSel.innerHTML = `
      <option value="gpt-4o-mini">GPT-4o-mini</option>
      <option value="gpt-4o">GPT-4o</option>`;
    ollamaStatus.style.display = 'none';
  } else {
    modelSel.innerHTML = `
      <option value="llama2">Llama 2</option>
      <option value="mistral">Mistral</option>
      <option value="gemma">Gemma</option>`;
    ollamaStatus.style.display = 'block'; // US-02: show unavailable warning
  }
}

function saveLLMConfig() {
  state.llm.provider = $('llmProvider').value;
  state.llm.model    = $('llmModel').value;
  updateLLMDisplay();
  closeLLMModal();
  showToast('success', `✅ Модель: ${state.llm.model}`);
}

function updateLLMDisplay() {
  $('llmNameDisplay').textContent = state.llm.model;
  const dot = $('llmDot');
  dot.style.background = state.llm.provider === 'openai' ? '#22d3a0' : '#fbbf24';
  dot.style.boxShadow  = `0 0 6px ${state.llm.provider === 'openai' ? '#22d3a0' : '#fbbf24'}`;
}

// ── API Key Modal ────────────────────────────────
function openApiKeyModal() { $('apiKeyModal').classList.remove('hidden'); }
function closeApiKeyModal() { $('apiKeyModal').classList.add('hidden'); }

function saveApiKey() {
  const key = $('apiKeyInput').value.trim();
  if (key && !key.startsWith('sk-')) {
    showToast('error', '❌ Неверный формат API-ключа');
    return;
  }
  state.apiKey = key || null;
  closeApiKeyModal();
  showToast('success', key ? '🔑 API-ключ сохранён (только в памяти сессии)' : '🔑 API-ключ очищен');
}

// ── Toast ────────────────────────────────────────
function showToast(type, msg, duration = 3500) {
  const el = document.createElement('div');
  el.className = `toast ${type}`;
  el.textContent = msg;
  toastContainer.appendChild(el);
  setTimeout(() => { el.style.opacity = '0'; el.style.transition = 'opacity 0.3s'; setTimeout(() => el.remove(), 300); }, duration);
}

// ── Helpers ──────────────────────────────────────
function hideWelcome() {
  if (welcomeScreen) welcomeScreen.style.display = 'none';
}
function showWelcome() {
  if (welcomeScreen) welcomeScreen.style.display = 'flex';
}
function scrollBottom() {
  chatMessages.scrollTop = chatMessages.scrollHeight;
}
function now() {
  return new Date().toLocaleTimeString('ru-RU', { hour: '2-digit', minute: '2-digit' });
}
function escHtml(s) {
  return s.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/\n/g,'<br>');
}
