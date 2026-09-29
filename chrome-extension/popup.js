const API = "http://127.0.0.1:8765";
let currentTab = null;
let watching = null;

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
    watching = data.watching;
    el.textContent = watching ? "● Lilly connected — chart tab selected" : "● Lilly connected";
    el.className = "status online";
    document.getElementById("watch").disabled = false;
    document.getElementById("capture").disabled = !watching;
    document.getElementById("stop").disabled = !watching;
  } catch (error) {
    watching = null;
    el.textContent = "● Lilly desktop app is not connected";
    el.className = "status offline";
    document.getElementById("watch").disabled = true;
    document.getElementById("capture").disabled = true;
    document.getElementById("stop").disabled = true;
  }
}

async function post(path, payload = {}) {
  const response = await fetch(API + path, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload)
  });
  const data = await response.json();
  if (!response.ok) throw new Error(data.error || "Lilly returned an error");
  return data;
}

async function captureCurrentTab() {
  if (!currentTab || !watching) throw new Error("Select a tab with Watch This Tab first.");
  if (currentTab.id !== watching.tab_id) {
    throw new Error("Open the watched tab before capturing.");
  }
  const imageData = await chrome.tabs.captureVisibleTab(currentTab.windowId, {
    format: "jpeg",
    quality: 85
  });
  return post("/capture", {
    tab_id: currentTab.id,
    title: currentTab.title,
    url: currentTab.url,
    image_data: imageData,
    width: window.screen.width,
    height: window.screen.height
  });
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
    message.textContent = "This tab is selected. You can capture its visible chart.";
    await checkLilly();
  } catch (error) {
    message.textContent = error.message;
  }
});

document.getElementById("capture").addEventListener("click", async () => {
  const message = document.getElementById("message");
  try {
    message.textContent = "Capturing visible chart…";
    const result = await captureCurrentTab();
    message.textContent = "Capture saved by Lilly at " + result.capture.captured_at;
  } catch (error) {
    message.textContent = error.message;
  }
});

document.getElementById("stop").addEventListener("click", async () => {
  const message = document.getElementById("message");
  try {
    await post("/stop");
    message.textContent = "Chrome monitoring stopped.";
    await checkLilly();
  } catch (error) {
    message.textContent = error.message;
  }
});

(async () => {
  await getCurrentTab();
  await checkLilly();
})();
