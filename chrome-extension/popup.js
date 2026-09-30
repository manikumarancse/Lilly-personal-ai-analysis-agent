const API = "http://127.0.0.1:8765";
let currentTab = null;
let watching = null;

const el = (id) => document.getElementById(id);

async function getCurrentTab() {
  const tabs = await chrome.tabs.query({ active: true, currentWindow: true });
  currentTab = tabs[0] || null;
  el("tabTitle").textContent = currentTab?.title || "No active tab";
  el("tabUrl").textContent = currentTab?.url || "";
}

async function request(path, options = {}) {
  const response = await fetch(API + path, options);
  const data = await response.json();
  if (!response.ok) throw new Error(data.error || "Lilly returned an error");
  return data;
}

async function post(path, payload = {}) {
  return request(path, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload)
  });
}

function renderTasks(items) {
  const container = el("tasks");
  if (!items.length) {
    container.textContent = "No tasks yet.";
    return;
  }
  container.innerHTML = "";
  items.slice().reverse().forEach((task) => {
    const row = document.createElement("div");
    row.className = "task" + (task.triggered ? " triggered" : "");
    const relation = task.kind === "price_above" ? ">=" : "<=";
    const state = task.triggered ? "TRIGGERED" : task.active ? "ACTIVE" : "INACTIVE";
    row.append(document.createTextNode((task.label || "Price watch") + ": " + relation + " " + task.level + " — " + state));
    const button = document.createElement("button");
    button.className = "delete";
    button.textContent = "Delete";
    button.onclick = async () => {
      await request("/tasks/" + task.id, { method: "DELETE" });
      await refresh();
    };
    row.appendChild(button);
    container.appendChild(row);
  });
}

async function refresh() {
  try {
    const data = await request("/health");
    watching = data.watching;
    el("connection").textContent = watching ? "● Lilly connected — live monitor selected" : "● Lilly connected";
    el("connection").className = "status online";
    el("watch").disabled = false;
    el("capture").disabled = !watching;
    el("stop").disabled = !watching;
    el("livePrice").textContent = data.latest_price ?? "Waiting for TradingView…";
    renderTasks(data.tasks || []);
    const status = await chrome.runtime.sendMessage({ type: "LIVE_STATUS" });
    if (status?.lastPrice != null) el("livePrice").textContent = status.lastPrice;
    el("liveHint").textContent = watching ? "Updates are saved to the current Lilly session." : "Select a TradingView chart tab.";
  } catch (error) {
    el("connection").textContent = "● Lilly desktop app is not connected";
    el("connection").className = "status offline";
    el("watch").disabled = true;
    el("capture").disabled = true;
    el("stop").disabled = true;
  }
}

el("watch").onclick = async () => {
  try {
    if (!currentTab?.url?.includes("tradingview.com")) throw new Error("Automatic price monitoring currently supports TradingView chart tabs.");
    await post("/watch", { tab_id: currentTab.id, title: currentTab.title, url: currentTab.url });
    await chrome.runtime.sendMessage({ type: "START_LIVE_MONITOR", tabId: currentTab.id });
    el("message").textContent = "Live monitoring started.";
    await refresh();
  } catch (error) { el("message").textContent = error.message; }
};

el("stop").onclick = async () => {
  try {
    await chrome.runtime.sendMessage({ type: "STOP_LIVE_MONITOR" });
    await post("/stop");
    el("message").textContent = "Live monitoring stopped.";
    await refresh();
  } catch (error) { el("message").textContent = error.message; }
};

el("capture").onclick = async () => {
  try {
    if (currentTab.id !== watching?.tab_id) throw new Error("Open the watched tab before capturing.");
    const imageData = await chrome.tabs.captureVisibleTab(currentTab.windowId, { format: "jpeg", quality: 85 });
    await post("/capture", { tab_id: currentTab.id, title: currentTab.title, url: currentTab.url, image_data: imageData, width: screen.width, height: screen.height });
    el("message").textContent = "Chart capture saved.";
  } catch (error) { el("message").textContent = error.message; }
};

el("addTask").onclick = async () => {
  try {
    if (!el("level").value) throw new Error("Enter a price level.");
    await post("/tasks", { kind: el("kind").value, level: Number(el("level").value), label: el("label").value });
    el("level").value = "";
    el("label").value = "";
    el("message").textContent = "Watch task added.";
    await refresh();
  } catch (error) { el("message").textContent = error.message; }
};

el("getUpdate").onclick = async () => {
  try {
    const data = await request("/update");
    const update = data.update;
    el("updateBox").style.display = "block";
    if (!update.count) {
      el("updateText").textContent = "No observations in the current session yet.";
      return;
    }
    const change = update.change >= 0 ? "+" + update.change.toFixed(2) : update.change.toFixed(2);
    el("updateText").textContent =
      "Current session | Latest " + update.latest +
      " | High " + update.high +
      " | Low " + update.low +
      " | Change " + change +
      " | " + update.count + " observations" +
      " | " + update.active_tasks + " active task(s)" +
      " | " + update.triggered_tasks + " triggered this session";
  } catch (error) { el("message").textContent = error.message; }
};

el("resetSession").onclick = async () => {
  try {
    await post("/session/reset");
    el("updateBox").style.display = "none";
    el("message").textContent = "New monitoring session started. Old history was kept.";
    await refresh();
  } catch (error) { el("message").textContent = error.message; }
};

(async () => {
  await getCurrentTab();
  await refresh();
  setInterval(refresh, 2000);
})();
