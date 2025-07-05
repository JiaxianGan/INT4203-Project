const chatLog = document.getElementById("chat-log");
const chatForm = document.getElementById("chat-form");
const chatInput = document.getElementById("chat-input");
const toggleBtn = document.getElementById("toggle-theme");
const body = document.body;

// Chat form submission logic
chatForm.addEventListener("submit", async (e) => {
  e.preventDefault();
  const userMsg = chatInput.value.trim();
  if (!userMsg) return;

  addMessage("user", userMsg);
  chatInput.value = "";

  // Show temporary bot message
  const botMsgElem = document.createElement("div");
  botMsgElem.classList.add("message", "bot");
  botMsgElem.innerHTML = `<div class="bubble"><div class="avatar">🤖</div><div class="text">Thinking...</div></div>`;
  chatLog.appendChild(botMsgElem);
  chatLog.scrollTop = chatLog.scrollHeight;

  try {
    const res = await fetch("http://localhost:5000/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message: userMsg }),
    });

    const data = await res.json();
    const reply = data.reply || "Sorry, I didn't get a response.";
    botMsgElem.querySelector(".text").textContent = reply;
  } catch (err) {
    botMsgElem.querySelector(".text").textContent = "Error fetching reply.";
  }

  updateChatActiveState();
});


// Helper to set chat-active class when there are messages
function updateChatActiveState() {
  if (chatLog.children.length > 0) {
    document.body.classList.add("chat-active");
  } else {
    document.body.classList.remove("chat-active");
  }
}

function addMessage(sender, text) {
  const msg = document.createElement("div");
  msg.classList.add("message", sender);

  // Create bubble container
  const bubble = document.createElement("div");
  bubble.className = "bubble";

  // Avatar
  const avatar = document.createElement("div");
  avatar.className = "avatar";
  avatar.textContent = sender === "user" ? "🧑" : "🤖";

  // Text
  const textDiv = document.createElement("div");
  textDiv.className = "text";
  textDiv.textContent = text;

  // Arrange bubble
  if (sender === "user") {
    bubble.appendChild(textDiv);
    bubble.appendChild(avatar);
  } else {
    bubble.appendChild(avatar);
    bubble.appendChild(textDiv);
  }

  msg.appendChild(bubble);
  chatLog.appendChild(msg);
  chatLog.scrollTop = chatLog.scrollHeight;
  updateChatActiveState();
}

function generateBotReply(msg) {
  // Simple stock advisory logic simulation
  if (msg.toLowerCase().includes("apple") || msg.includes("AAPL")) {
    return "Apple Inc. (AAPL) is trading at around $178. Consider its historical stability.";
  }
  return "I'm still learning about that stock. Try asking about Apple, Tesla, or Microsoft!";
}

// Sidebar logic
const sidebar = document.getElementById("sidebar");
const sidebarToggleBtn = document.getElementById("sidebar-toggle");
const sidebarOpenBtn = document.getElementById("sidebar-open-btn");
const newChatBtn = document.getElementById("new-chat-btn");
const searchChatInput = document.getElementById("search-chat-input");
const chatHistoryList = document.getElementById("chat-history-list");

// Helper to update body class for sidebar state
function updateSidebarState() {
  if (sidebar.classList.contains("closed")) {
    document.body.classList.add("sidebar-closed");
    sidebar.classList.add("icon-only");
    sidebarOpenBtn.style.display = "inline-block";
  } else {
    document.body.classList.remove("sidebar-closed");
    sidebar.classList.remove("icon-only");
    sidebarOpenBtn.style.display = "none";
  }
}

// Toggle sidebar to icon-only (collapsed)
sidebarToggleBtn.addEventListener("click", () => {
  sidebar.classList.add("closed");
  updateSidebarState();
});

// Toggle sidebar to expanded (open)
sidebarOpenBtn.addEventListener("click", () => {
  sidebar.classList.remove("closed");
  updateSidebarState();
});

// On load, ensure sidebar is open and open button is hidden
document.addEventListener("DOMContentLoaded", () => {
  sidebar.classList.remove("closed");
  updateSidebarState();
  updateChatActiveState();
});

// New Chat button logic
newChatBtn.addEventListener("click", () => {
  chatLog.innerHTML = "";
  updateChatActiveState();
  // Optionally, add logic to start a new chat session
});

// Search Chat logic (simple filter)
searchChatInput.addEventListener("input", () => {
  const filter = searchChatInput.value.toLowerCase();
  Array.from(chatHistoryList.children).forEach(item => {
    item.style.display = item.textContent.toLowerCase().includes(filter) ? "" : "none";
  });
});

// Chat history click logic (stub)
chatHistoryList.addEventListener("click", (e) => {
if (e.target && e.target.matches("li")) {
  // Load chat history for selected chat (stub)
  // Example: chatLog.innerHTML = ...;
}
  if (e.target && e.target.matches("li")) {
    // Load chat history for selected chat (stub)
    // Example: chatLog.innerHTML = ...;
  }
});

function generateBotReply(msg) {
  return "Thinking..."; // Temporary message

  // The actual response will come from the backend
}

