const API_URL = "";

function switchTab(tab) {
  document.getElementById("askPanel").classList.toggle("hidden", tab !== "ask");
  document.getElementById("quizPanel").classList.toggle("hidden", tab !== "quiz");
  document.getElementById("tabAskBtn").classList.toggle("active", tab === "ask");
  document.getElementById("tabQuizBtn").classList.toggle("active", tab === "quiz");
}

async function uploadFile() {
  const fileInput = document.getElementById("fileInput");
  const status = document.getElementById("uploadStatus");

  if (!fileInput.files.length) {
    status.textContent = "Please select a PDF file first.";
    return;
  }

  const formData = new FormData();
  formData.append("file", fileInput.files[0]);

  status.textContent = "Uploading and processing…";

  try {
    const response = await fetch(`${API_URL}/upload`, {
      method: "POST",
      body: formData
    });
    const data = await response.json();
    status.textContent = `Done — ${data.chunks_created} chunks created.`;
  } catch (error) {
    status.textContent = "Upload failed. Check backend server.";
  }
}

async function askQuestion() {
  const questionInput = document.getElementById("questionInput");
  const answerArea = document.getElementById("answerArea");
  const question = questionInput.value.trim();

  if (!question) return;

  answerArea.innerHTML = `<p class="loading-text">Thinking…</p>`;

  const formData = new FormData();
  formData.append("question", question);

  try {
    const response = await fetch(`${API_URL}/ask`, {
      method: "POST",
      body: formData
    });
    const data = await response.json();

    const confidence = data.confidence ?? 0;
    const stampClass = confidence >= 50 ? "stamp" : "stamp low";

    const sourcesHtml = (data.sources || [])
      .map((s, i) => `<div class="source-item">${i + 1}. ${s.slice(0, 160)}${s.length > 160 ? "…" : ""}</div>`)
      .join("");

    answerArea.innerHTML = `
      <div class="answer-card">
        <div class="answer-header">
          <div class="${stampClass}">
            <span class="stamp-num">${confidence}%</span>
            <span class="stamp-label">MATCH</span>
          </div>
          <div class="answer-text">${data.answer}</div>
        </div>
        <span class="sources-toggle" onclick="this.nextElementSibling.classList.toggle('open')">
          Show source notes (${(data.sources || []).length})
        </span>
        <div class="sources-list">${sourcesHtml}</div>
      </div>
    `;
  } catch (error) {
    answerArea.innerHTML = `<p class="loading-text">Something went wrong. Check backend server.</p>`;
  }
}

async function generateQuiz() {
  const quizArea = document.getElementById("quizArea");
  quizArea.innerHTML = `<p class="loading-text">Building your quiz…</p>`;

  try {
    const response = await fetch(`${API_URL}/quiz`, { method: "POST" });
    const data = await response.json();

    if (!data.questions || !data.questions.length) {
      quizArea.innerHTML = `<p class="loading-text">Couldn't generate questions. Upload notes first.</p>`;
      return;
    }

    quizArea.innerHTML = data.questions.map((q, qi) => `
      <div class="quiz-card">
        <div class="quiz-question">${qi + 1}. ${q.question}</div>
        ${q.options.map(opt => `
          <button class="quiz-option" onclick="revealAnswer(this, ${JSON.stringify(opt === q.answer)})">
            ${opt}
          </button>
        `).join("")}
      </div>
    `).join("");
  } catch (error) {
    quizArea.innerHTML = `<p class="loading-text">Something went wrong generating the quiz.</p>`;
  }
}

function revealAnswer(button, isCorrect) {
  const siblings = button.parentElement.querySelectorAll(".quiz-option");
  siblings.forEach(btn => btn.onclick = null);
  button.classList.add(isCorrect ? "correct" : "incorrect");
}

async function resetStore() {
  const status = document.getElementById("uploadStatus");

  try {
    await fetch(`${API_URL}/reset`, { method: "POST" });
    status.textContent = "All notes cleared.";
    document.getElementById("answerArea").innerHTML = "";
    document.getElementById("quizArea").innerHTML = "";
  } catch (error) {
    status.textContent = "Reset failed.";
  }
}