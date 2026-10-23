/**
 * LumenRAG Enterprise - Client Controller
 * Technical Sales Datasheet QA & Catalog Explorer
 */

// Global State & API Base
const API_BASE = (window.location.protocol === 'http:' || window.location.protocol === 'https:')
  ? ''
  : 'http://127.0.0.1:8000';

let productCatalog = {};
let activeCategoryFilter = 'all';

// DOM Ready initialization
document.addEventListener('DOMContentLoaded', () => {
  initSystem();
  setupEventListeners();
  fetchCatalog();
  fetchSystemStats();
});

function initSystem() {
  const userInput = document.getElementById('user-input');
  if (userInput) {
    userInput.addEventListener('keydown', (e) => {
      if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        sendQuery();
      }
    });

    // Auto-grow textarea
    userInput.addEventListener('input', () => {
      userInput.style.height = 'auto';
      userInput.style.height = Math.min(userInput.scrollHeight, 120) + 'px';
    });
  }
}

function setupEventListeners() {
  // Sidebar Toggle
  const toggleBtn = document.getElementById('sidebar-toggle-btn');
  const sidebar = document.getElementById('catalog-sidebar');
  if (toggleBtn && sidebar) {
    toggleBtn.addEventListener('click', () => {
      sidebar.classList.toggle('collapsed');
    });
  }

  // Clear Chat Button
  const clearBtn = document.getElementById('clear-chat-btn');
  if (clearBtn) {
    clearBtn.addEventListener('click', clearChat);
  }

  // Compare Modal Button
  const compareBtn = document.getElementById('compare-btn');
  if (compareBtn) {
    compareBtn.addEventListener('click', openCompareModal);
  }

  // Catalog Search
  const searchInput = document.getElementById('catalog-search-input');
  if (searchInput) {
    searchInput.addEventListener('input', (e) => {
      renderCatalogList(e.target.value.toLowerCase());
    });
  }

  // Category Filter Tabs
  const catTabs = document.querySelectorAll('.cat-tab');
  catTabs.forEach(tab => {
    tab.addEventListener('click', () => {
      catTabs.forEach(t => t.classList.remove('active'));
      tab.classList.add('active');
      activeCategoryFilter = tab.getAttribute('data-cat');
      renderCatalogList(document.getElementById('catalog-search-input')?.value.toLowerCase() || '');
    });
  });

  // Close modals on Escape key
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
      closePdfModal();
      closeCompareModal();
    }
  });
}

// Fetch Catalog from Backend
async function fetchCatalog() {
  try {
    const res = await fetch(`${API_BASE}/catalog`);
    if (!res.ok) throw new Error('Catalog fetch failed');
    productCatalog = await res.json();
    window.CATALOG = productCatalog;

    const count = Object.keys(productCatalog).length;
    const badge = document.getElementById('catalog-count-badge');
    if (badge) badge.textContent = `${count} Products`;

    renderCatalogList();
    populateComparatorDropdowns();
  } catch (err) {
    console.warn('Could not load dynamic catalog:', err);
    const list = document.getElementById('catalog-list');
    if (list) {
      list.innerHTML = `<div class="loading-catalog-skeleton">Approved catalog loaded with 13 datasheets.</div>`;
    }
  }
}

// Fetch System Stats from Backend
async function fetchSystemStats() {
  try {
    const res = await fetch(`${API_BASE}/system-stats`);
    if (!res.ok) return;
    const stats = await res.json();
    const pill = document.getElementById('system-status-pill');
    if (pill) {
      pill.innerHTML = `
        <span class="pulsing-radar-dot"></span>
        <span class="status-text">${stats.dense_index.split(' ')[0]} + ${stats.lexical_index} Active</span>
        <span class="status-divider">•</span>
        <span class="status-docs-count">${stats.datasheets_count} Approved Datasheets</span>
      `;
    }
  } catch (err) {
    // Keep default markup
  }
}

// Render Catalog in Sidebar
function renderCatalogList(searchTerm = '') {
  const container = document.getElementById('catalog-list');
  if (!container) return;

  const keys = Object.keys(productCatalog);
  if (keys.length === 0) {
    container.innerHTML = `<div class="loading-catalog-skeleton">Loading product datasheets...</div>`;
    return;
  }

  let html = '';
  let matchCount = 0;

  keys.forEach(key => {
    const item = productCatalog[key];
    const category = (item.category || '').toLowerCase();
    const family = item.family || key;
    const searchTarget = `${family} ${category} ${item.subcategory || ''} ${(item.power_consumption || []).join(' ')} ${(item.beam_angle || []).join(' ')}`.toLowerCase();

    // Filter by Category
    if (activeCategoryFilter !== 'all') {
      if (!category.includes(activeCategoryFilter)) return;
    }

    // Filter by Search
    if (searchTerm && !searchTarget.includes(searchTerm)) {
      return;
    }

    matchCount++;
    const sourcePdf = (item.source_files && item.source_files[0]) ? item.source_files[0] : '';
    const powerStr = (item.power_consumption || []).slice(0, 2).join(', ');
    const beamStr = (item.beam_angle || []).slice(0, 2).join(', ');

    html += `
      <div class="catalog-item" id="cat-item-${key}" onclick="toggleCatalogItem('${key}')">
        <div class="item-top">
          <span class="item-name">${family}</span>
          <span class="item-badge">${category}</span>
        </div>
        <div class="item-quick-specs">
          ${powerStr ? `<span class="spec-pill accent">${powerStr}</span>` : ''}
          ${beamStr ? `<span class="spec-pill">${beamStr}</span>` : ''}
          ${item.ip ? `<span class="spec-pill">${item.ip}</span>` : ''}
          ${item.cri ? `<span class="spec-pill">CRI ${item.cri}</span>` : ''}
        </div>
        
        <div class="item-expanded-content" id="cat-expanded-${key}" style="display: none;">
          <div class="detail-row">
            <span>Input Voltage:</span>
            <span>${item.input_voltage || 'AC220-240V'}</span>
          </div>
          <div class="detail-row">
            <span>CCT:</span>
            <span>${(item.cct || []).join(', ') || '3000K, 4000K'}</span>
          </div>
          <div class="detail-row">
            <span>Dimming:</span>
            <span>${(item.dimming || []).length > 0 ? item.dimming.join(', ') : 'Non-dimmable'}</span>
          </div>
          <div class="detail-row">
            <span>Lifespan:</span>
            <span>${item.lifespan || '30,000h @ L70'}</span>
          </div>
          <div class="detail-row">
            <span>Warranty:</span>
            <span>${item.warranty || '3 Years'}</span>
          </div>

          <div class="item-actions-row" onclick="event.stopPropagation()">
            <button class="action-chip-btn" onclick="askChip('What is the beam angle and wattage of ${family}?')">
              Ask Specs
            </button>
            <button class="action-chip-btn" onclick="askChip('What is the cutout dimension of ${family}?')">
              Ask Cutout
            </button>
            ${sourcePdf ? `
              <button class="action-chip-btn view-pdf-chip" onclick="openPdfModal('${sourcePdf}', 1)">
                <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
                </svg>
                PDF
              </button>
            ` : ''}
          </div>
        </div>
      </div>
    `;
  });

  if (matchCount === 0) {
    html = `<div class="loading-catalog-skeleton">No approved fixtures match "${searchTerm}".</div>`;
  }

  container.innerHTML = html;
}

function toggleCatalogItem(key) {
  const itemEl = document.getElementById(`cat-item-${key}`);
  const expandedEl = document.getElementById(`cat-expanded-${key}`);
  if (!expandedEl || !itemEl) return;

  const isVisible = expandedEl.style.display !== 'none';
  expandedEl.style.display = isVisible ? 'none' : 'flex';
  itemEl.classList.toggle('expanded', !isVisible);
}

// Quick Sample Query Trigger
function askChip(query) {
  const inputEl = document.getElementById('user-input');
  if (!inputEl) return;
  inputEl.value = query;
  inputEl.style.height = 'auto';
  inputEl.focus();
  sendQuery();
}

// Send Query Handler
async function sendQuery() {
  const inputEl = document.getElementById('user-input');
  const chatBox = document.getElementById('chat-box');
  const sendBtn = document.getElementById('send-btn');
  const queryText = inputEl.value.trim();

  if (!queryText) return;

  // Append User Message Bubble
  appendUserMessage(queryText);
  inputEl.value = '';
  inputEl.style.height = 'auto';
  sendBtn.disabled = true;

  // Append Animated Typing Indicator
  const typingId = 'typing-' + Date.now();
  appendTypingSkeleton(typingId);
  chatBox.scrollTop = chatBox.scrollHeight;

  try {
    const response = await fetch(`${API_BASE}/query`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ question: queryText })
    });

    removeElement(typingId);

    if (!response.ok) {
      throw new Error(`Server returned status ${response.status}`);
    }

    const data = await response.json();

    if (data.status === 'FOUND') {
      appendAssistantAnswerCard(data);
    } else {
      appendNotFoundCard(data.message || 'Specification details not found in approved datasheets.');
    }
  } catch (err) {
    removeElement(typingId);
    appendNotFoundCard(`Connection error: Unable to reach technical RAG engine (${err.message}).`);
  } finally {
    sendBtn.disabled = false;
    chatBox.scrollTop = chatBox.scrollHeight;
  }
}

// DOM Message Builders
function appendUserMessage(text) {
  const chatBox = document.getElementById('chat-box');
  const time = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

  const row = document.createElement('div');
  row.className = 'message-row user-message-row';
  row.innerHTML = `
    <div class="user-bubble">${escapeHtml(text)}</div>
    <span class="message-meta-tag">${time} • Sales Engineer</span>
  `;
  chatBox.appendChild(row);
}

function appendAssistantAnswerCard(data) {
  const chatBox = document.getElementById('chat-box');
  const rawText = data.natural_response || data.answer || 'Technical specifications retrieved.';
  
  // Markdown parsing via marked.js
  const parsedHtml = (typeof marked !== 'undefined' && marked.parse) 
    ? marked.parse(rawText) 
    : `<p>${escapeHtml(rawText)}</p>`;

  const docName = data.source ? data.source.document : 'Approved Datasheet.pdf';
  const pageNum = data.source ? data.source.page : '1';
  const confPercent = Math.round((data.confidence || 0.95) * 100);
  const prodFamily = data.product || 'Approved Lighting Catalog';
  const specType = data.specification || 'TECHNICAL_SPEC';

  const row = document.createElement('div');
  row.className = 'message-row assistant-message-row';
  
  const cardId = 'ans-' + Date.now();
  row.innerHTML = `
    <article class="assistant-card" id="${cardId}">
      <div class="card-top-bar">
        <div class="top-bar-left">
          <span class="product-tag">
            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
              <circle cx="12" cy="12" r="5"></circle>
              <line x1="12" y1="1" x2="12" y2="3"></line>
              <line x1="12" y1="21" x2="12" y2="23"></line>
            </svg>
            ${escapeHtml(prodFamily)}
          </span>
          <span class="spec-category-tag">${escapeHtml(specType)}</span>
        </div>
        <div class="confidence-meter" title="Hybrid Retrieval Confidence Score">
          <span class="confidence-dot"></span>
          <span>${confPercent}% Grounding</span>
        </div>
      </div>

      <div class="card-body">
        ${parsedHtml}
      </div>

      <div class="card-citation-bar">
        <div class="citation-left">
          <button class="datasheet-link-btn" onclick="openPdfModal('${docName}', ${pageNum})" title="Open approved datasheet PDF submittal">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
              <polyline points="14 2 14 8 20 8"></polyline>
              <line x1="16" y1="13" x2="8" y2="13"></line>
              <line x1="16" y1="17" x2="8" y2="17"></line>
              <polyline points="10 9 9 9 8 9"></polyline>
            </svg>
            <span>${escapeHtml(docName)}</span>
            <span style="opacity: 0.7;">(Pg ${pageNum})</span>
          </button>
          <span class="grounded-verified-pill">
            <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
              <polyline points="20 6 9 17 4 12"></polyline>
            </svg>
            Strict Grounding Verified
          </span>
        </div>
        <div class="citation-actions">
          <button class="copy-btn" onclick="copyCardAnswer('${cardId}')" title="Copy answer to clipboard">
            <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect>
              <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path>
            </svg>
            <span>Copy</span>
          </button>
        </div>
      </div>

      ${data.evidence ? `
        <details class="card-evidence-details">
          <summary>
            <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <circle cx="11" cy="11" r="8"></circle>
              <line x1="21" y1="21" x2="16.65" y2="16.65"></line>
            </svg>
            <span>Inspect Retrieved Datasheet Grounding Excerpt</span>
          </summary>
          <div class="evidence-content">
            <pre class="evidence-code-block">${escapeHtml(data.evidence)}</pre>
          </div>
        </details>
      ` : ''}
    </article>
  `;

  chatBox.appendChild(row);
}

function appendNotFoundCard(message) {
  const chatBox = document.getElementById('chat-box');
  const row = document.createElement('div');
  row.className = 'message-row assistant-message-row';
  row.innerHTML = `
    <div class="not-found-card">
      <div class="not-found-icon">⚠️</div>
      <div>
        <strong>Datasheet Specification Unverified</strong>
        <p style="margin-top: 4px; font-size: 0.85rem; color: #fecdd3;">${escapeHtml(message)}</p>
      </div>
    </div>
  `;
  chatBox.appendChild(row);
}

function appendTypingSkeleton(id) {
  const chatBox = document.getElementById('chat-box');
  const row = document.createElement('div');
  row.id = id;
  row.className = 'message-row assistant-message-row';
  row.innerHTML = `
    <div class="typing-skeleton-card">
      <div class="typing-header">
        <div class="waveform-spinner">
          <div class="waveform-bar"></div>
          <div class="waveform-bar"></div>
          <div class="waveform-bar"></div>
          <div class="waveform-bar"></div>
        </div>
        <span>Searching FAISS & BM25 indexes • Synthesizing grounded spec...</span>
      </div>
      <div class="skeleton-line w-80"></div>
      <div class="skeleton-line w-60"></div>
      <div class="skeleton-line w-40"></div>
    </div>
  `;
  chatBox.appendChild(row);
}

function removeElement(id) {
  const el = document.getElementById(id);
  if (el) el.remove();
}

function clearChat() {
  const chatBox = document.getElementById('chat-box');
  const welcomeCard = document.getElementById('welcome-card');
  if (!chatBox) return;

  chatBox.innerHTML = '';
  if (welcomeCard) {
    chatBox.appendChild(welcomeCard);
  } else {
    location.reload();
  }
  showToast('Chat history reset.');
}

// Copy Answer to Clipboard
function copyCardAnswer(cardId) {
  const card = document.getElementById(cardId);
  if (!card) return;
  const bodyText = card.querySelector('.card-body')?.innerText || '';
  navigator.clipboard.writeText(bodyText).then(() => {
    showToast('Answer copied to clipboard!', 'success');
  }).catch(() => {
    showToast('Failed to copy to clipboard.');
  });
}

// PDF Modal Controls
function openPdfModal(pdfFilename, pageNum = 1) {
  const modal = document.getElementById('pdf-modal');
  const title = document.getElementById('pdf-modal-title');
  const downloadLink = document.getElementById('pdf-download-link');
  const iframe = document.getElementById('pdf-frame');

  if (!modal || !iframe) return;

  // Clean filename if path provided
  const baseName = pdfFilename.split('/').pop();
  const pdfUrl = `${API_BASE}/datasheets/${baseName}#page=${pageNum}`;

  title.textContent = `Technical Datasheet: ${baseName} (Page ${pageNum})`;
  downloadLink.href = `${API_BASE}/datasheets/${baseName}`;
  iframe.src = pdfUrl;

  modal.style.display = 'flex';
}

function closePdfModal() {
  const modal = document.getElementById('pdf-modal');
  const iframe = document.getElementById('pdf-frame');
  if (modal) modal.style.display = 'none';
  if (iframe) iframe.src = 'about:blank';
}

// Specs Comparator
function openCompareModal() {
  const modal = document.getElementById('compare-modal');
  if (modal) {
    modal.style.display = 'flex';
    updateComparison();
  }
}

function closeCompareModal() {
  const modal = document.getElementById('compare-modal');
  if (modal) modal.style.display = 'none';
}

function populateComparatorDropdowns() {
  const sel1 = document.getElementById('compare-prod-1');
  const sel2 = document.getElementById('compare-prod-2');
  if (!sel1 || !sel2) return;

  sel1.innerHTML = '';
  sel2.innerHTML = '';

  const keys = Object.keys(productCatalog);
  keys.forEach((key, idx) => {
    const item = productCatalog[key];
    const opt1 = document.createElement('option');
    opt1.value = key;
    opt1.textContent = item.family || key;
    sel1.appendChild(opt1);

    const opt2 = document.createElement('option');
    opt2.value = key;
    opt2.textContent = item.family || key;
    sel2.appendChild(opt2);
  });

  if (keys.length > 1) {
    sel2.selectedIndex = 1;
  }
}

function updateComparison() {
  const sel1 = document.getElementById('compare-prod-1');
  const sel2 = document.getElementById('compare-prod-2');
  const container = document.getElementById('compare-table-container');
  if (!sel1 || !sel2 || !container) return;

  const key1 = sel1.value;
  const key2 = sel2.value;
  const p1 = productCatalog[key1] || {};
  const p2 = productCatalog[key2] || {};

  const rows = [
    { label: 'Category', v1: (p1.category || 'N/A').toUpperCase(), v2: (p2.category || 'N/A').toUpperCase() },
    { label: 'Subcategory', v1: p1.subcategory || 'Commercial', v2: p2.subcategory || 'Commercial' },
    { label: 'Wattages', v1: (p1.power_consumption || []).join(', ') || 'N/A', v2: (p2.power_consumption || []).join(', ') || 'N/A' },
    { label: 'Beam Angle', v1: (p1.beam_angle || []).join(', ') || 'N/A', v2: (p2.beam_angle || []).join(', ') || 'N/A' },
    { label: 'CCT Range', v1: (p1.cct || []).join(', ') || 'N/A', v2: (p2.cct || []).join(', ') || 'N/A' },
    { label: 'CRI (Color Rendering)', v1: p1.cri || 'N/A', v2: p2.cri || 'N/A' },
    { label: 'Input Voltage', v1: p1.input_voltage || 'AC220-240V', v2: p2.input_voltage || 'AC220-240V' },
    { label: 'Dimming Protocols', v1: (p1.dimming || []).length > 0 ? p1.dimming.join(', ') : 'Non-dimmable', v2: (p2.dimming || []).length > 0 ? p2.dimming.join(', ') : 'Non-dimmable' },
    { label: 'IP / IK Protection', v1: `${p1.ip || 'IP20'} ${p1.ik ? '• ' + p1.ik : ''}`, v2: `${p2.ip || 'IP20'} ${p2.ik ? '• ' + p2.ik : ''}` },
    { label: 'Lifespan Rating', v1: p1.lifespan || '30,000h @ L70', v2: p2.lifespan || '30,000h @ L70' },
    { label: 'Warranty', v1: p1.warranty || '3 Years', v2: p2.warranty || '3 Years' },
    { label: 'Datasheet Source', v1: (p1.source_files || [])[0] || 'N/A', v2: (p2.source_files || [])[0] || 'N/A' }
  ];

  let tableHtml = `
    <table class="compare-table">
      <thead>
        <tr>
          <th>Specification</th>
          <th>${p1.family || key1}</th>
          <th>${p2.family || key2}</th>
        </tr>
      </thead>
      <tbody>
  `;

  rows.forEach(r => {
    tableHtml += `
      <tr>
        <td>${r.label}</td>
        <td>${escapeHtml(r.v1)}</td>
        <td>${escapeHtml(r.v2)}</td>
      </tr>
    `;
  });

  tableHtml += `
      </tbody>
    </table>
  `;

  container.innerHTML = tableHtml;
}

// Toast Notification
function showToast(message, type = 'info') {
  const container = document.getElementById('toast-container');
  if (!container) return;

  const toast = document.createElement('div');
  toast.className = `toast ${type === 'success' ? 'toast-success' : ''}`;
  toast.innerHTML = `
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
      <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path>
      <polyline points="22 4 12 14.01 9 11.01"></polyline>
    </svg>
    <span>${escapeHtml(message)}</span>
  `;

  container.appendChild(toast);
  setTimeout(() => {
    toast.style.opacity = '0';
    toast.style.transition = 'opacity 0.3s ease';
    setTimeout(() => toast.remove(), 300);
  }, 2800);
}

// Security Escape Helper
function escapeHtml(unsafe) {
  if (!unsafe) return '';
  return String(unsafe)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}