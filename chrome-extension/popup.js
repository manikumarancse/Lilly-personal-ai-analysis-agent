const API = "http://127.0.0.1:8765";
let currentTab = null;

async function getCurrentTab() {
  const tabs = await chrome.tabs.query({ active: true, currentWindow: true });
  currentTab = tabs[0] || null;
  document.getElementById("tabTitle").textContent = currentTab?.title || "No active tab";
  document.getElementById("tabUrl").textContent = currentTab?.url || "";
}

async function checkLilly() {
  const el = document.getElementById("connection");
  try {
    const response = await fetch(API + "/health");
    const data = await response.json();
    if (!data.ok) throw new Error("Lilly unavailable");
    el.textContent = data.watching ? "● Lilly connected — watching a tab" : "● Lilly connected";
    el.className = "status online";
    document.getElementById("watch").disabled = false;
    document.getElementById("stop").disabled = !data.watching;
  } catch (error) {
    el.textContent = "● Lilly desktop app is not connected";
    el.className = "status offline";
    document.getElementById("watch").disabled = true;
    document.getElementById("stop").disabled = true;
  }
}

async function post(path, payload = {}) {
  const response = await fetch(API + path, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload)
  });
  if (!response.ok) throw new Error("Lilly returned an error");
  return response.json();
}

document.getElementById("watch").addEventListener("click", async () => {
  const message = document.getElementById("message");
  if (!currentTab) return;
  try {
    await post("/watch", {
      tab_id: currentTab.id,
      title: currentTab.title,
      url: currentTab.url
    });
    message.textContent = "This tab is now selected for Lilly.";
    await checkLilly();
  } catch (error) {
    message.textContent = "Could not connect. Make sure Lilly is running.";
  }
});

document.getElementById("stop").addEventListener("click", async () => {
  const message = document.getElementById("message");
  try {
    await post("/stop");
    message.textContent = "Chrome monitoring stopped.";
    await checkLilly();
  } catch (error) {
    message.textContent = "Could not connect. Make sure Lilly is running.";
  }
});

(async () => {
  await getCurrentTab();
  await checkLilly();
})();
