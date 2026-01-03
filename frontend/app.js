// =======================
// Config
// =======================
const API_URL = "http://127.0.0.1:8000/lookup"; // update when deployed
const AUTH_TOKEN = ""; // optional: set to "your_token" if backend requires Bearer auth

// =======================
// State
// =======================
let lastRequest = { term: "", context: "" };
let lastClarification = null;

// =======================
// DOM
// =======================
const messagesEl = document.getElementById("messages");
const termInput = document.getElementById("termInput");
const contextInput = document.getElementById("contextInput");
const sendBtn = document.getElementById("sendBtn");
const resetBtn = document.getElementById("resetBtn");

// =======================
// UI helpers
// =======================
function scrollToBottom() {
  messagesEl.scrollTop = messagesEl.scrollHeight;
}

function addMessage(text, who = "bot") {
  const row = document.createElement("div");
  row.className = `msg ${who}`;
  const bubble = document.createElement("div");
  bubble.className = "bubble";
  bubble.textContent = text;
  row.appendChild(bubble);
  messagesEl.appendChild(row);
  scrollToBottom();
}

function addBotHTML(html) {
  const row = document.createElement("div");
  row.className = "msg bot";
  const bubble = document.createElement("div");
  bubble.className = "bubble";
  bubble.innerHTML = html;
  row.appendChild(bubble);
  messagesEl.appendChild(row);
  scrollToBottom();
}

function setSending(isSending) {
  sendBtn.disabled = isSending;
  termInput.disabled = isSending;
  contextInput.disabled = isSending;
}

// =======================
// Networking
// =======================
async function postLookup(body) {
  const headers = { "Content-Type": "application/json" };
  if (AUTH_TOKEN) headers["Authorization"] = `Bearer ${AUTH_TOKEN}`;

  const res = await fetch(API_URL, {
    method: "POST",
    headers,
    body: JSON.stringify(body),
  });

  // Handle non-2xx with readable error
  if (!res.ok) {
    const txt = await res.text().catch(() => "");
    throw new Error(`HTTP ${res.status}: ${txt || res.statusText}`);
  }
  return res.json();
}

// =======================
// Response handling
// =======================
function normalizeFinalPayload(data) {
  // Your backend might return:
  // 1) NotionPagePayload directly: {word, core_meaning, ...}
  // 2) wrapped: {status_code: 200, response: {word, core_meaning, ...}}
  if (data && typeof data === "object") {
    if (data.word && data.core_meaning) return data;
    if (data.response && data.response.word && data.response.core_meaning)
      return data.response;
  }
  return null;
}

function renderFinal(payload) {
  const domains = Array.isArray(payload.domain)
    ? payload.domain.join(", ")
    : "";
  const related = Array.isArray(payload.related_words)
    ? payload.related_words.join(", ")
    : "";

  addBotHTML(`
    <div class="card">
      <h3>${escapeHtml(payload.word)}</h3>
      <div>${escapeHtml(payload.core_meaning)}</div>

      <div class="kv"><span>Meaning type:</span> ${escapeHtml(
        payload.meaning_type || ""
      )}</div>
      <div class="kv"><span>Domain:</span> ${escapeHtml(domains)}</div>
      ${
        payload.usage_notes
          ? `<div class="kv"><span>Usage notes:</span> ${escapeHtml(
              payload.usage_notes
            )}</div>`
          : ""
      }
      <div class="kv"><span>Example:</span> ${escapeHtml(
        payload.example || ""
      )}</div>
      <div class="kv"><span>Related:</span> ${escapeHtml(related)}</div>
    </div>
  `);

  addMessage(
    "Saved to your Notion database. You can look up another word whenever you're ready.",
    "bot"
  );
}

function renderClarification(req) {
  lastClarification = req;

  const choicesHtml = req.choices
    .map((c, idx) => {
      const i = idx + 1; // 1-based
      return `<button class="choice-btn" data-choice="${i}">${escapeHtml(
        c
      )}</button>`;
    })
    .join("");

  addBotHTML(`
    <div>${escapeHtml(req.question)}</div>
    <div class="choices">${choicesHtml}</div>
    <div class="meta">Click one option to continue.</div>
  `);

  // attach listeners for the buttons we just created
  const lastBubble = messagesEl.lastElementChild.querySelector(".bubble");
  lastBubble.querySelectorAll(".choice-btn").forEach((btn) => {
    btn.addEventListener("click", async () => {
      const selected = Number(btn.getAttribute("data-choice"));
      await submitChoice(selected);
    });
  });
}

function escapeHtml(s) {
  return String(s ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

// =======================
// Actions
// =======================
async function submitLookup() {
  const term = termInput.value.trim();
  const context = contextInput.value.trim();

  if (!term) return;

  lastRequest = { term, context };
  lastClarification = null;

  addMessage(`Term: ${term}${context ? `\nContext: ${context}` : ""}`, "user");
  setSending(true);

  try {
    // Your backend currently accepts {"term","context"}.
    const data = await postLookup({ term, context });

    if (data && data.type === "clarification_request") {
      renderClarification(data);
      return;
    }

    const finalPayload = normalizeFinalPayload(data);
    if (finalPayload) {
      renderFinal(finalPayload);
      return;
    }

    // Fallback: Notion raw response dict
    addMessage("Saved to your Notion database.", "bot");
  } catch (err) {
    addMessage(`Error: ${err.message}`, "bot");
  } finally {
    setSending(false);
  }
}

async function submitChoice(selected_option) {
  if (!lastClarification) return;

  setSending(true);

  try {
    // IMPORTANT:
    // This assumes your backend supports selected_option for the follow-up call.
    // If it doesn't yet, add it to your LookupRequest schema.
    const body = {
      term: lastRequest.term,
      context: lastRequest.context,
      selected_option,
    };

    const data = await postLookup(body);

    if (data && data.type === "clarification_request") {
      // If backend asks again, render again
      renderClarification(data);
      return;
    }

    const finalPayload = normalizeFinalPayload(data);
    if (finalPayload) {
      renderFinal(finalPayload);
      return;
    }

    addMessage("Saved to your Notion database.", "bot");
  } catch (err) {
    addMessage(`Error: ${err.message}`, "bot");
  } finally {
    setSending(false);
  }
}

function resetChat() {
  messagesEl.innerHTML = "";
  lastRequest = { term: "", context: "" };
  lastClarification = null;
  greet();
}

// =======================
// Events
// =======================
sendBtn.addEventListener("click", submitLookup);
resetBtn.addEventListener("click", resetChat);

termInput.addEventListener("keydown", (e) => {
  if (e.key === "Enter" && !e.shiftKey) {
    e.preventDefault();
    submitLookup();
  }
});

function greet() {
  addMessage(
    "Hello. Enter a word or phrase to look up. Add context if you have it (optional).",
    "bot"
  );
}

greet();
