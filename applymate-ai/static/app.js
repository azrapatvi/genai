const chat = document.getElementById("chat");
const form = document.getElementById("form");
const input = document.getElementById("input");
const submitBtn = document.getElementById("submitBtn");
const draftCard = document.getElementById("draftCard");
const changes = document.getElementById("changes");

const threadId = "chat-" + Math.random().toString(36).slice(2, 10);

function addMsg(text, cls) {
  const d = document.createElement("div");
  d.className = "msg " + cls;
  d.textContent = text;
  chat.appendChild(d);
  chat.scrollTop = chat.scrollHeight;
  return d;
}

function showDraft(d) {
  document.getElementById("dTo").textContent = d.recruiter_email;
  document.getElementById("dSubject").textContent = d.subject;
  document.getElementById("dBody").textContent = d.body;
  changes.value = "";
  draftCard.classList.remove("hidden");
  form.classList.add("hidden");
  draftCard.scrollIntoView({ behavior: "smooth", block: "nearest" });
}

function hideDraft() {
  draftCard.classList.add("hidden");
  form.classList.remove("hidden");
  input.focus();
}

function handle(data) {
  if (data.error) {
    addMsg(data.error, "error");
    return;
  }
  if (data.reply) addMsg(data.reply, "bot");
  if (data.pending && data.draft) showDraft(data.draft);
  else hideDraft();
}

async function post(url, body) {
  const typing = addMsg("Thinking...", "bot typing");
  try {
    const r = await fetch(url, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ ...body, thread_id: threadId }),
    });
    const data = await r.json();
    typing.remove();
    handle(data);
  } catch (e) {
    typing.remove();
    addMsg("Network error: " + e.message, "error");
  }
}

form.addEventListener("submit", async (e) => {
  e.preventDefault();
  const text = input.value.trim();
  if (!text) return;
  addMsg(text, "user");
  input.value = "";
  submitBtn.disabled = true;
  await post("/api/chat", { message: text });
  submitBtn.disabled = false;
});

function setBusy(b) {
  draftCard.querySelectorAll("button").forEach((x) => (x.disabled = b));
}

document.getElementById("sendBtn").addEventListener("click", async () => {
  setBusy(true);
  addMsg("Yes, send it.", "user");
  await post("/api/decision", { action: "approve" });
  setBusy(false);
});

document.getElementById("cancelBtn").addEventListener("click", async () => {
  setBusy(true);
  addMsg("Cancel, do not send.", "user");
  await post("/api/decision", { action: "reject" });
  setBusy(false);
});

document.getElementById("changeBtn").addEventListener("click", async () => {
  const instruction = changes.value.trim();
  if (!instruction) {
    changes.focus();
    return;
  }
  setBusy(true);
  addMsg(instruction, "user");
  await post("/api/decision", { action: "rewrite", instruction });
  setBusy(false);
});

// ---------------- setup
const setupCard = document.getElementById("setup");
const setupForm = document.getElementById("setupForm");
const editSetupBtn = document.getElementById("editSetupBtn");
let greeted = false;

function showSetup(info) {
  if (info) {
    document.getElementById("linkedin").value = info.linkedin_url || "";
    document.getElementById("github").value = info.github_url || "";
    document.getElementById("senderEmail").value = info.sender_email || "";
    document.getElementById("resumeNote").textContent = info.resume_filename
      ? "Current resume: " + info.resume_filename + " (choose a file only to replace it)"
      : "";
  }
  document.getElementById("appPassword").value = "";
  setupCard.classList.remove("hidden");
  chat.classList.add("hidden");
  draftCard.classList.add("hidden");
  form.classList.add("hidden");
}

function showChat() {
  setupCard.classList.add("hidden");
  chat.classList.remove("hidden");
  if (draftCard.classList.contains("hidden")) form.classList.remove("hidden");
  editSetupBtn.classList.remove("hidden");
  if (!greeted) {
    greeted = true;
    addMsg("Hi! I'm ApplyMate AI. Tell me which company and role you want to apply for.", "bot");
  }
}

setupForm.addEventListener("submit", async (e) => {
  e.preventDefault();
  const fd = new FormData();
  const f = document.getElementById("resume").files[0];
  if (f) fd.append("resume", f);
  fd.append("linkedin_url", document.getElementById("linkedin").value);
  fd.append("github_url", document.getElementById("github").value);
  fd.append("sender_email", document.getElementById("senderEmail").value);
  fd.append("app_password", document.getElementById("appPassword").value);
  const btn = document.getElementById("setupBtn");
  btn.disabled = true;
  btn.textContent = "Saving...";
  try {
    const r = await fetch("/api/setup", { method: "POST", body: fd });
    const data = await r.json();
    if (data.error) alert(data.error);
    else showChat();
  } catch (err) {
    alert("Network error: " + err.message);
  }
  btn.disabled = false;
  btn.textContent = "Save and start";
});

editSetupBtn.addEventListener("click", async () => {
  const info = await (await fetch("/api/status")).json();
  showSetup(info);
});

(async () => {
  const info = await (await fetch("/api/status")).json();
  if (info.configured) showChat();
  else showSetup(info);
})();