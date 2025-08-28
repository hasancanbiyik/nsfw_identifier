// content.js
const THRESHOLD = 0.5;

// Inject a persistent CSS rule with !important
(function ensureStyle() {
  if (document.getElementById("nsfw-style")) return;
  const style = document.createElement("style");
  style.id = "nsfw-style";
  style.textContent = `
    .nsfw-blur { filter: blur(24px) !important; }
    .nsfw-outline-red { outline: 6px solid #b00020 !important; }
    .nsfw-outline-green { outline: 6px solid #1b5e20 !important; }
    .nsfw-badge {
      position: fixed;
      z-index: 2147483647;
      background: #b00020;
      color: #fff;
      font-size: 12px;
      padding: 2px 6px;
      border-radius: 4px;
      box-shadow: 0 1px 4px rgba(0,0,0,0.3);
      pointer-events: none;
    }
    .nsfw-badge.green { background: #1b5e20; }
  `;
  document.head.appendChild(style);
})();

function normalizeUrl(u) {
  try {
    const url = new URL(u);
    // Some sites (Twitter) vary only by size param like &name=small/medium/large.
    url.searchParams.delete("name");
    return url.origin + url.pathname + (url.searchParams.toString() ? "?" + url.searchParams.toString() : "");
  } catch { return u; }
}

function findTargetsByUrl(srcUrl) {
  const targetNorm = normalizeUrl(srcUrl);
  const imgs = Array.from(document.images).filter(im => {
    const s1 = normalizeUrl(im.src || "");
    const s2 = normalizeUrl(im.currentSrc || "");
    return s1 === targetNorm || s2 === targetNorm;
  });

  // Also check background-image elements
  const bgMatches = [];
  const all = document.querySelectorAll("*");
  all.forEach(el => {
    const bg = getComputedStyle(el).backgroundImage; // e.g., url("https://pbs.twimg.com/...")
    if (bg && bg.includes("url(") && bg.includes(srcUrl)) {
      bgMatches.push(el);
    }
  });

  return { imgs, bgMatches };
}

function addBadgeNear(el, text, color) {
  // Avoid stacking duplicates
  const existing = el.dataset.nsfwBadgeId && document.getElementById(el.dataset.nsfwBadgeId);
  if (existing) existing.remove();

  const rect = el.getBoundingClientRect();
  const badge = document.createElement("span");
  const id = "nsfw-badge-" + Math.random().toString(36).slice(2);
  badge.id = id;
  el.dataset.nsfwBadgeId = id;

  badge.className = "nsfw-badge" + (color === "green" ? " green" : "");
  badge.textContent = text;
  badge.style.left = (rect.left + 4) + "px";
  badge.style.top  = (rect.top + 4) + "px";
  document.body.appendChild(badge);
}

chrome.runtime.onMessage.addListener((msg) => {
  if (msg.type === "NSFW_RESULT") {
    const { srcUrl, data } = msg;
    const nsfwScore = (data.nsfw_score ?? (data.label?.toLowerCase() === "nsfw" ? 1 : 0)) || 0;
    const decision = nsfwScore >= THRESHOLD ? "NSFW" : "SFW";

    console.log("[NSFW] result", { srcUrl, nsfwScore, decision, data });

    const { imgs, bgMatches } = findTargetsByUrl(srcUrl);

    // Decorate <img> elements
    imgs.forEach(img => {
      if (decision === "NSFW") {
        img.classList.add("nsfw-blur", "nsfw-outline-red");
        addBadgeNear(img, `NSFW ${(nsfwScore*100).toFixed(1)}%`, "red");
      } else {
        img.classList.remove("nsfw-blur");
        img.classList.add("nsfw-outline-green");
        addBadgeNear(img, "SFW", "green");
      }
    });

    // Decorate background-image elements
    bgMatches.forEach(el => {
      if (decision === "NSFW") {
        el.classList.add("nsfw-blur", "nsfw-outline-red");
        addBadgeNear(el, `NSFW ${(nsfwScore*100).toFixed(1)}%`, "red");
      } else {
        el.classList.remove("nsfw-blur");
        el.classList.add("nsfw-outline-green");
        addBadgeNear(el, "SFW", "green");
      }
    });

    if (imgs.length === 0 && bgMatches.length === 0) {
      console.warn("[NSFW] No matching elements found for URL", srcUrl);
      alert(`Classified (${decision}) but couldn't find the element to decorate.\nTry a different image on the page.`);
    }
  } else if (msg.type === "NSFW_ERROR") {
    console.warn("NSFW Identifier error:", msg.error);
    alert("NSFW Identifier error: " + msg.error);
  }
});

