const API = "";
let currentWhitelist = [];
let currentStatus = {};

const STEPS = [
  { n: 1, label: "Kết nối" },
  { n: 2, label: "Whitelist" },
  { n: 3, label: "Xem lại" },
];

function renderStepper(activeStep) {
  const ol = document.getElementById("stepper");
  ol.innerHTML = STEPS.map((s) => {
    const done = s.n < activeStep;
    const active = s.n === activeStep;
    const circle = done
      ? `<div class="w-8 h-8 rounded-full bg-primary text-on-primary flex items-center justify-center"><span class="material-symbols-outlined text-[16px]">check</span></div>`
      : active
      ? `<div class="w-8 h-8 rounded-full bg-primary-container text-on-primary-container flex items-center justify-center border-2 border-primary"><span class="text-xs font-bold">${s.n}</span></div>`
      : `<div class="w-8 h-8 rounded-full bg-surface-container-high text-on-surface-variant flex items-center justify-center border border-outline-variant"><span class="text-xs">${s.n}</span></div>`;
    return `<li class="flex items-start">
      <div class="flex flex-col items-center mr-md relative z-10">${circle}${
      s.n < STEPS.length ? `<div class="w-px h-8 bg-outline-variant mt-1"></div>` : ""
    }</div>
      <div class="pt-1 pb-md">
        <span class="text-xs text-primary block">Bước ${s.n}</span>
        <span class="text-sm font-medium ${active ? "text-on-surface" : "text-on-surface-variant"}">${s.label}</span>
      </div>
    </li>`;
  }).join("");
}

function goToStep(n) {
  document.querySelectorAll(".step-panel").forEach((p) => p.classList.remove("active"));
  document.getElementById(`panel-${n}`).classList.add("active");
  renderStepper(n);
  if (n === 2) loadWhitelist();
  if (n === 3) loadReview();
}

function statusChip(ok, textOk, textNo) {
  return ok
    ? `<span class="bg-[#e6f4ea] text-[#137333] px-sm py-xs rounded-full">${textOk}</span>`
    : `<span class="bg-surface-container-high text-on-surface-variant px-sm py-xs rounded-full">${textNo}</span>`;
}

async function loadStatus() {
  const res = await fetch(`${API}/setup/status`);
  currentStatus = await res.json();
  document.getElementById("gmail-status").innerHTML = statusChip(
    currentStatus.gmail_connected, "Đã kết nối", "Chưa kết nối"
  );
  document.getElementById("wealify-status").innerHTML = statusChip(
    currentStatus.wealify_configured, "Hợp lệ", "Chưa cấu hình"
  );
  if (currentStatus.gmail_account) {
    document.getElementById("gmailClientId").placeholder = currentStatus.gmail_account;
  }
  if (currentStatus.wealify_username) {
    document.getElementById("wealifyUsername").value = currentStatus.wealify_username;
  }
  currentWhitelist = currentStatus.whitelist || [];
}

async function connectGmail() {
  const clientId = document.getElementById("gmailClientId").value.trim();
  const clientSecret = document.getElementById("gmailClientSecret").value.trim();
  const resultEl = document.getElementById("gmailResult");
  if (!clientId || !clientSecret) {
    resultEl.textContent = "⚠️ Nhập đủ Client ID và Client Secret.";
    resultEl.classList.remove("hidden");
    return;
  }
  resultEl.textContent = "⏳ Đang mở trình duyệt để xác nhận quyền truy cập Gmail...";
  resultEl.classList.remove("hidden");
  const btn = document.getElementById("gmailConnectBtn");
  btn.disabled = true;
  try {
    const res = await fetch(`${API}/setup/gmail`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ client_id: clientId, client_secret: clientSecret }),
    });
    const data = await res.json();
    if (data.success) {
      resultEl.textContent = `✅ Đã kết nối: ${data.connected_account}`;
    } else {
      resultEl.textContent = `❌ Lỗi: ${data.error}`;
    }
  } catch (e) {
    resultEl.textContent = `❌ Lỗi: ${e}`;
  }
  btn.disabled = false;
  loadStatus();
}

async function connectWealify() {
  const username = document.getElementById("wealifyUsername").value.trim();
  const password = document.getElementById("wealifyPassword").value.trim();
  const resultEl = document.getElementById("wealifyResult");
  if (!username || !password) {
    resultEl.textContent = "⚠️ Nhập đủ email và mật khẩu.";
    resultEl.classList.remove("hidden");
    return;
  }
  resultEl.textContent = "⏳ Đang xác thực...";
  resultEl.classList.remove("hidden");
  try {
    const res = await fetch(`${API}/setup/wealify`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ username, password }),
    });
    const data = await res.json();
    resultEl.textContent = data.success ? "✅ Xác thực thành công." : `❌ Lỗi: ${data.error}`;
  } catch (e) {
    resultEl.textContent = `❌ Lỗi: ${e}`;
  }
  loadStatus();
}

function domainIcon() {
  return `<span class="material-symbols-outlined text-[16px] text-on-surface-variant">domain</span>`;
}

function renderWhitelist() {
  document.getElementById("whitelistCount").textContent = currentWhitelist.length;
  const list = document.getElementById("whitelistList");
  if (currentWhitelist.length === 0) {
    list.innerHTML = `<li class="text-center text-sm text-on-surface-variant py-lg">Chưa có domain nào được chọn.</li>`;
    return;
  }
  list.innerHTML = currentWhitelist
    .map(
      (d) => `<li class="flex items-center justify-between p-sm rounded-lg hover:bg-surface-container-low group">
      <div class="flex items-center gap-sm">
        <div class="w-8 h-8 rounded-full bg-surface-variant flex items-center justify-center">${domainIcon()}</div>
        <span class="text-sm font-mono">${d}</span>
      </div>
      <button onclick="removeDomain('${d}')" class="w-8 h-8 rounded-full flex items-center justify-center text-outline hover:text-error hover:bg-error-container opacity-0 group-hover:opacity-100" aria-label="Remove">
        <span class="material-symbols-outlined text-[18px]">close</span>
      </button>
    </li>`
    )
    .join("");
}

function renderSuggestions(suggestions) {
  const container = document.getElementById("suggestedDomains");
  container.innerHTML = suggestions
    .map(
      (d) => `<button class="flex items-center gap-xs px-3 py-1.5 bg-surface-container rounded-full border border-outline-variant/50 hover:border-primary text-sm" onclick="addDomain('${d}')">
      <span>${d}</span><span class="material-symbols-outlined text-[16px]">add_circle</span>
    </button>`
    )
    .join("");
}

async function loadWhitelist() {
  const res = await fetch(`${API}/setup/whitelist`);
  const data = await res.json();
  currentWhitelist = data.whitelist;
  renderWhitelist();
  renderSuggestions(data.suggested);
}

async function addDomain(domain) {
  domain = (domain || "").trim().toLowerCase();
  if (!domain) return;
  const res = await fetch(`${API}/setup/whitelist`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ domain }),
  });
  const data = await res.json();
  currentWhitelist = data.whitelist;
  renderWhitelist();
  loadWhitelist();
}

async function removeDomain(domain) {
  const res = await fetch(`${API}/setup/whitelist/${encodeURIComponent(domain)}`, { method: "DELETE" });
  const data = await res.json();
  currentWhitelist = data.whitelist;
  renderWhitelist();
  loadWhitelist();
}

async function loadReview() {
  await loadStatus();
  document.getElementById("review-gmail").textContent = currentStatus.gmail_account || "Chưa kết nối";
  document.getElementById("review-wealify").textContent = currentStatus.wealify_username || "Chưa cấu hình";
  document.getElementById("review-count").textContent = currentWhitelist.length;
  document.getElementById("review-whitelist").innerHTML = currentWhitelist
    .map((d) => `<span class="border border-outline-variant px-md py-sm rounded-lg font-mono text-sm bg-white">${d}</span>`)
    .join("");
}

async function finalizeSetup() {
  await fetch(`${API}/setup/finalize`, { method: "POST" });
  window.location.href = "/";
}

renderStepper(1);
loadStatus();
