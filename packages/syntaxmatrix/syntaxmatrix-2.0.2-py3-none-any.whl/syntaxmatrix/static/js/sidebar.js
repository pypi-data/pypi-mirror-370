function setSession(sessionId, elem) {
    document.querySelectorAll('#sidebar .session-item').forEach(function(el) {
      el.classList.remove('active');
    });
    if (elem && elem.parentElement && elem.parentElement.tagName.toLowerCase() === 'li') {
      elem.parentElement.classList.add('active');
    }
    var currentDiv = document.querySelector('#sidebar > div.session-item');
    if(currentDiv) {
        currentDiv.classList.remove('active');
    }
    fetch('/load_session', {
      method: 'POST',
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      body: 'session_id=' + encodeURIComponent(sessionId)
    })
    .then(response => response.json())
    .then(data =>   {
      document.getElementById("chat-history").innerHTML = data.chat_html;
      document.getElementById("sidebar-container").innerHTML = data.sidebar_html;

      // ——— RE-APPLY SIDEBAR OPEN/CLOSED STATE ———
      (function(){
        const sidebar = document.getElementById("sidebar");
        const state   = localStorage.getItem("sidebarState");
        if (!sidebar) return;
        if (state === "open") {
          sidebar.classList.add("open");
        } else {
          sidebar.classList.remove("open");
        }
      })();

    })
    .catch(() => alert('Failed to load session.'));
}
  
function toggleSessionMenu(sessionId) {
    var menu = document.getElementById("menu-" + sessionId);
    if(menu.style.display === "block") {
        menu.style.display = "none";
    } else {
        menu.style.display = "block";
    }
}

// ────────── RENAME MODAL ──────────
function openRenameModal(sessionId, currentTitle) {
  const modal = document.createElement("div");
  modal.id = "rename-modal";
  Object.assign(modal.style, {
    position: "fixed",
    inset: 0,
    background: "rgba(0,0,0,0.5)",
    display: "flex",
    justifyContent: "center",
    alignItems: "center",
    zIndex: 9999
  });

  // Build shell *without* the title string
  modal.innerHTML = `
    <div style="background:#fff;padding:20px;border-radius:8px;min-width:300px;">
      <h3>Rename session</h3>
      <input type="text" id="new-session-name" style="width:100%;padding:5px;" />
      <div style="margin-top:10px;text-align:right;">
        <button style="cursor:pointer;" onclick="submitRenameModal('${sessionId}')">Rename</button>
        <button style="cursor:pointer;" onclick="document.getElementById('rename-modal').remove()">
          Cancel
        </button>
      </div>
    </div>
  `;
  document.body.appendChild(modal);

  // Safely inject the text *after* the element exists
  const inp = document.getElementById("new-session-name");
  inp.value = currentTitle;
  inp.focus();
}

function submitRenameModal(sessionId) {
  const newName = document.getElementById("new-session-name").value.trim();
  if (!newName) return;
  fetch("/rename_session", {
    method: "POST",
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
    body:
      "session_id=" + encodeURIComponent(sessionId) +
      "&new_title=" + encodeURIComponent(newName)
  })
  .then(r => r.json())
  .then(data => {
    document.getElementById("rename-modal").remove();
    const span = document.querySelector(
      `#sidebar li.session-item[data-session-id="${sessionId}"] .session-title`
    );
    if (span) {
      const t = data.new_title;
      span.textContent = t.length <= 15 ? t : t.slice(0, 15) + "…";
      span.title = data.new_title;
    }
  });
}

// Ensure the inline onclick="" handlers can see them
window.openRenameModal   = openRenameModal;
window.submitRenameModal = submitRenameModal;

function openDeleteModal(sessionId) {
    var modal = document.createElement("div");
    modal.id = "delete-modal";
    modal.style.position = "fixed";
    modal.style.top = "0";
    modal.style.left = "0";
    modal.style.width = "100%";
    modal.style.height = "100%";
    modal.style.backgroundColor = "rgba(0,0,0,0.5)";
    modal.style.display = "flex";
    modal.style.justifyContent = "center";
    modal.style.alignItems = "center";
    modal.innerHTML = `
      <div style="background: #fff; padding: 20px; border-radius: 8px; min-width: 300px;">
        <h3>Confirm Deletion</h3>
        <p>Are you sure you want to delete this chat session?</p>
        <div style="margin-top: 10px; text-align: right;">
          <button style="cursor:pointer;" onclick="submitDeleteModal('` + sessionId + `')">Yes</button>
          <button style="cursor:pointer;" onclick="document.getElementById('delete-modal').remove()">No</button>
        </div>
      </div>
    `;
    document.body.appendChild(modal);
}

function submitDeleteModal(sessionId) {
    fetch('/delete_session', {
      method: 'POST',
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      body: 'session_id=' + encodeURIComponent(sessionId)
    })
    .then(r => r.json())
    .then(data => {
      document.getElementById('delete-modal').remove();
      const li = document.querySelector(
        `#sidebar li.session-item[data-session-id="${sessionId}"]`
      );
      const wasActive = li?.classList.contains('active');
      if (li) li.remove();

      if (wasActive) {
        // mark “Current” as active again
        document.querySelectorAll('#sidebar .session-item').forEach(el => el.classList.remove('active'));
        const currentDiv = document.querySelector('#sidebar > div.session-item');
        if (currentDiv) currentDiv.classList.add('active');
        // and replace the chat area
        document.getElementById('chat-history').innerHTML = data.chat_html;
      }}
    );
}
  
document.addEventListener("click", function(e) {
    var menus = document.getElementsByClassName("session-menu");
    for (var i = 0; i < menus.length; i++) {
        menus[i].style.display = "none";
    }
});

// Read the icon URLs off the toggle button's data attributes
const toggleBtn = document.getElementById("sidebar-toggle-btn");
const sidebarIcon = document.getElementById("sidebar-toggle-icon");
const iconOpen = toggleBtn.dataset.iconOpen;
const iconClose = toggleBtn.dataset.iconClose;

// A helper to apply the stored open/closed state
function applySidebarState() {
  const sidebar = document.getElementById("sidebar");
  if (!sidebar) return;
  const isOpen = localStorage.getItem("sidebarState") === "open";
  sidebar.classList.toggle("open", isOpen);
  sidebarIcon.src = isOpen ? iconClose : iconOpen;
  toggleBtn.title = isOpen ? "Close sidebar" : "Open sidebar";
  sidebarIcon.alt = toggleBtn.title;
  document.body.classList.toggle("sidebar-open", isOpen);
}

// Run once at load
applySidebarState();

// Wire up the toggle button to always hit the *current* #sidebar
toggleBtn.addEventListener("click", () => {
  const sidebar = document.getElementById("sidebar");
  if (!sidebar) return;
  // flip it
  const newState = sidebar.classList.toggle("open") ? "open" : "closed";
  localStorage.setItem("sidebarState", newState);
  sidebarIcon.src = newState === "open" ? iconClose : iconOpen;

   toggleBtn.title   = newState === "open"
                     ? "Close sidebar"
                     : "Open sidebar";
  sidebarIcon.alt   = toggleBtn.title;
  document.body.classList.toggle("sidebar-open", newState === "open");
});


// And also after every sidebar redraw
window.addEventListener("sidebar:redraw", applySidebarState);
