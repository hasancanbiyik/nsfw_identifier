const API = "http://127.0.0.1:8000";

chrome.runtime.onInstalled.addListener(() => {
  chrome.contextMenus.create({
    id: "nsfw-check",
    title: "Check image with NSFW Identifier",
    contexts: ["image"]
  });
});

chrome.contextMenus.onClicked.addListener(async (info, tab) => {
  if (info.menuItemId !== "nsfw-check" || !info.srcUrl || !tab?.id) return;
  try {
    const res = await fetch(`${API}/classify?url=${encodeURIComponent(info.srcUrl)}`);
    if (!res.ok) throw new Error(`API error ${res.status}`);
    const data = await res.json();
    await chrome.tabs.sendMessage(tab.id, { type: "NSFW_RESULT", srcUrl: info.srcUrl, data });
  } catch (err) {
    await chrome.tabs.sendMessage(tab.id, { type: "NSFW_ERROR", srcUrl: info.srcUrl, error: String(err) });
  }
});

