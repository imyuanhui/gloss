// =======================
// Config
// =======================
const API_URL = "https://gloss.onrender.com/lookup";
// const API_URL = "http://127.0.0.1:8000/lookup";
const AUTH_TOKEN = "";

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
const sendSpinner = document.getElementById("sendSpinner");

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

  if (sendSpinner) {
    sendSpinner.style.display = isSending ? "inline-block" : "none";
  }

  const textEl = sendBtn.querySelector(".btn-text");
  if (textEl) textEl.textContent = isSending ? "Sending..." : "Send";

  // disable/enable clarification choice buttons if present
  document.querySelectorAll(".choice-btn").forEach((b) => {
    b.disabled = isSending;
  });
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
  // Clear the chat and only show the final card + saved message
  messagesEl.innerHTML = "";

  const domains = Array.isArray(payload.domain)
    ? payload.domain.join(", ")
    : "";
  const related = Array.isArray(payload.related_words)
    ? payload.related_words.join(", ")
    : "";

  addBotHTML(`
    <div class="card">
      <h3 class="card-title">${escapeHtml(payload.word)}</h3>
      <div class="card-content">
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
      </div>
  `);

  addMessage("Glossed and saved", "bot");
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
      // ignore clicks if already disabled
      if (btn.disabled) return;

      // disable all choice buttons immediately to prevent double-clicks
      lastBubble.querySelectorAll(".choice-btn").forEach((b) => {
        b.disabled = true;
        b.classList.add("disabled");
      });

      // visually mark the clicked button and add a small spinner
      btn.classList.add("selected");
      const spinner = document.createElement("span");
      spinner.className = "choice-spinner";
      spinner.setAttribute("aria-hidden", "true");
      btn.appendChild(spinner);

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
      // stop the sending state so buttons are clickable
      setSending(false);
      renderClarification(data);
      return;
    }

    const finalPayload = normalizeFinalPayload(data);
    if (finalPayload) {
      renderFinal(finalPayload);
      return;
    }

    // Fallback: Notion raw response dict
    addMessage("Glossed and saved.", "bot");
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
    // Send the actual chosen text back to the backend as part of the context
    // and also include the numeric option for backward compatibility.
    const idx = Number(selected_option);
    const selected_text =
      lastClarification && Array.isArray(lastClarification.choices)
        ? lastClarification.choices[idx - 1]
        : String(idx);

    const body = {
      term: lastRequest.term,
      // append the chosen text to the previous context (with a space)
      context: lastRequest.context
        ? `${lastRequest.context} ${selected_text}`
        : selected_text,
    };

    const data = await postLookup(body);

    if (data && data.type === "clarification_request") {
      // If backend asks again, render again — re-enable UI before rendering
      setSending(false);
      renderClarification(data);
      return;
    }

    const finalPayload = normalizeFinalPayload(data);
    if (finalPayload) {
      renderFinal(finalPayload);
      return;
    }

    addMessage("Glossed and saved.", "bot");
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
    "Hello, this is Gloss.\nI help you understand and use real English vocabulary.\nEnter a word or short phrase to look up. Context is optional.\nEvery lookup will be saved to your Notion vocabulary database.",
    "bot"
  );
}

greet();
