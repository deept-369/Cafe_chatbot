// ── Brewed Awakening Chatbot JS ────────────────────────────────────
const chatMessages = document.getElementById('chatMessages');
const userInput    = document.getElementById('userInput');
const sendBtn      = document.getElementById('sendBtn');

// Welcome message on load
window.addEventListener('DOMContentLoaded', () => {
  setTimeout(() => {
    appendBot("👋 Welcome to **Brewed Awakening Café**! I'm your virtual barista assistant, available 24/7.\n\nI can help you with:\n• ☕ Menu & prices\n• 🕐 Hours & location\n• 📶 WiFi & parking\n• 🎉 Loyalty rewards & gift cards\n• 🗓️ Reservations & catering\n• 🌱 Vegan & dietary options\n\nHow can I help you today? Feel free to type or pick a question on the left!");
  }, 400);
});

// ── Render helpers ─────────────────────────────────────────────────
function formatBubbleText(text) {
  // Bold: **text** → <strong>
  return text.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
}

function appendUser(text) {
  const wrap = document.createElement('div');
  wrap.className = 'msg user';
  wrap.innerHTML = `
    <div class="bubble">${escapeHtml(text)}</div>
    <div class="bubble-av">🙂</div>
  `;
  chatMessages.appendChild(wrap);
  scrollBottom();
}

function appendBot(text) {
  const wrap = document.createElement('div');
  wrap.className = 'msg bot';
  wrap.innerHTML = `
    <div class="bubble-av">☕</div>
    <div class="bubble">${formatBubbleText(escapeHtml(text))}</div>
  `;
  chatMessages.appendChild(wrap);
  scrollBottom();
}

function showTyping() {
  const wrap = document.createElement('div');
  wrap.className = 'msg bot';
  wrap.id = 'typingIndicator';
  wrap.innerHTML = `
    <div class="bubble-av">☕</div>
    <div class="bubble typing-dots">
      <span></span><span></span><span></span>
    </div>
  `;
  chatMessages.appendChild(wrap);
  scrollBottom();
}

function removeTyping() {
  const el = document.getElementById('typingIndicator');
  if (el) el.remove();
}

function scrollBottom() {
  chatMessages.scrollTop = chatMessages.scrollHeight;
}

function escapeHtml(str) {
  return str
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}

// ── Send logic ─────────────────────────────────────────────────────
async function sendMessage() {
  const text = userInput.value.trim();
  if (!text) return;

  appendUser(text);
  userInput.value = '';
  sendBtn.disabled = true;

  showTyping();

  try {
    const res = await fetch('/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message: text }),
    });
    const data = await res.json();
    removeTyping();
    appendBot(data.reply || "I'm sorry, I couldn't get a response. Please try again!");
  } catch (err) {
    removeTyping();
    appendBot("Oops! Something went wrong on my end. Please try again or call us at +1 (718) 555-0192. ☕");
  } finally {
    sendBtn.disabled = false;
    userInput.focus();
  }
}

function sendChip(btn) {
  userInput.value = btn.textContent;
  sendMessage();
}

// Enter key
userInput.addEventListener('keydown', (e) => {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault();
    sendMessage();
  }
});
