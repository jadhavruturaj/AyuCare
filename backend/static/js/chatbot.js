/**
 * आयुCare (AyuCare) - AyuBot Floating Healthcare Chatbot
 */

document.addEventListener("DOMContentLoaded", () => {
  const launcher = document.getElementById("ayubot-launcher");
  const chatWindow = document.getElementById("ayubot-window");
  const closeBtn = document.getElementById("ayubot-close-btn");
  const minimizeBtn = document.getElementById("ayubot-min-btn");
  const chatBody = document.getElementById("ayubot-messages");
  const chatInput = document.getElementById("ayubot-input");
  const sendBtn = document.getElementById("ayubot-send-btn");
  const chipsContainer = document.getElementById("ayubot-chips-container");
  const typingIndicator = document.getElementById("ayubot-typing");

  if (!launcher || !chatWindow) return;

  // Toggle Chatbot Window
  launcher.addEventListener("click", () => {
    chatWindow.classList.toggle("open");
    if (chatWindow.classList.contains("open")) {
      chatInput?.focus();
      scrollChatToBottom();
    }
  });

  closeBtn?.addEventListener("click", () => chatWindow.classList.remove("open"));
  minimizeBtn?.addEventListener("click", () => chatWindow.classList.remove("open"));

  // Suggested Questions
  const defaultQuestions = [
    "How does AyuCare work?",
    "How do I check my symptoms?",
    "Which specialist should I consult?",
    "What information should I enter?",
    "How can I request a consultation?",
    "Is AyuCare a diagnosis tool?"
  ];

  renderSuggestedChips(defaultQuestions);

  function renderSuggestedChips(questions) {
    if (!chipsContainer) return;
    chipsContainer.innerHTML = "";
    questions.forEach(q => {
      const chip = document.createElement("button");
      chip.type = "button";
      chip.className = "chip-btn";
      chip.textContent = q;
      chip.addEventListener("click", () => {
        if (chatInput) chatInput.value = q;
        sendMessage();
      });
      chipsContainer.appendChild(chip);
    });
  }

  // Handle Send Message
  sendBtn?.addEventListener("click", sendMessage);
  chatInput?.addEventListener("keypress", (e) => {
    if (e.key === "Enter") sendMessage();
  });

  async function sendMessage() {
    const text = chatInput ? chatInput.value.trim() : "";
    if (!text) return;

    // Add user bubble
    appendMessage(text, "user");
    if (chatInput) chatInput.value = "";

    // Show typing
    if (typingIndicator) typingIndicator.style.display = "flex";
    scrollChatToBottom();

    try {
      const res = await AyuAPI.sendChatbotMessage(text);
      if (typingIndicator) typingIndicator.style.display = "none";

      if (res.success && res.data) {
        const d = res.data;
        appendMessage(d.message, "bot", d.is_emergency, d.action_link);
        if (d.suggested_questions && d.suggested_questions.length) {
          renderSuggestedChips(d.suggested_questions);
        }
      } else {
        appendMessage("I apologize, but I could not process your query right now. Please try again.", "bot");
      }
    } catch (err) {
      if (typingIndicator) typingIndicator.style.display = "none";
      appendMessage("Unable to reach AyuCare servers. Please check your connection.", "bot");
    }
    scrollChatToBottom();
  }

  function appendMessage(text, sender, isEmergency = false, actionLink = null) {
    if (!chatBody) return;
    const bubble = document.createElement("div");
    bubble.className = `chat-bubble ${sender}${isEmergency ? ' emergency' : ''}`;

    // Format simple markdown bold and line breaks
    let formatted = text
      .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
      .replace(/\n/g, '<br>');

    let actionHtml = "";
    if (actionLink && actionLink.url) {
      actionHtml = `
        <div>
          <a href="${actionLink.url}" class="chat-action-link">
            <i class="fa-solid fa-arrow-right"></i> ${actionLink.label}
          </a>
        </div>
      `;
    }

    bubble.innerHTML = `${formatted}${actionHtml}`;
    chatBody.appendChild(bubble);
  }

  function scrollChatToBottom() {
    if (chatBody) {
      setTimeout(() => {
        chatBody.scrollTop = chatBody.scrollHeight;
      }, 50);
    }
  }
});
