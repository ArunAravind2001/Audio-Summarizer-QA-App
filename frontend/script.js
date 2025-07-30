const uploadForm = document.getElementById("upload-form");
const audioInput = document.getElementById("audio-file");
const transcriptDiv = document.getElementById("transcript");
const questionContainer = document.querySelector(".question-container");

const questionForm = document.getElementById("question-form");
const questionInput = document.getElementById("question");
const answerDiv = document.getElementById("answer");

// Update file button when file is selected
audioInput.addEventListener('change', function(e) {
  const chooseBtn = document.querySelector('.choose-file-btn');
  const uploadBtn = document.querySelector('.upload-btn');
  
  if (e.target.files.length > 0) {
    chooseBtn.innerHTML = `✓ ${e.target.files[0].name}`;
    chooseBtn.style.background = 'linear-gradient(135deg, #28a745, #20963d)';
    uploadBtn.style.display = 'inline-block';
  }
});

uploadForm.addEventListener("submit", async (e) => {
  e.preventDefault();

  const file = audioInput.files[0];
  const formData = new FormData();
  formData.append("file", file);

  // Show loading state
  transcriptDiv.innerHTML = '<div class="content-title">Transcript</div><div class="loading"><div class="spinner"></div>Uploading and transcribing...</div>';
  transcriptDiv.style.display = 'block';
  answerDiv.innerHTML = '';

  try {
    const res = await fetch("http://127.0.0.1:8000/uploadfile/", {
      method: "POST",
      body: formData,
    });

    const data = await res.json();
    transcriptDiv.innerHTML = '<div class="content-title">Transcript</div>' + data.transcript;
    questionContainer.style.display = "block";
  } catch (error) {
    transcriptDiv.innerHTML = '<div class="content-title">Error</div>Failed to transcribe audio. Please try again.';
  }
});

questionForm.addEventListener("submit", async (e) => {
  e.preventDefault();

  const question = questionInput.value;

  // Show loading state
  answerDiv.innerHTML = '<div class="content-title">Answer</div><div class="loading"><div class="spinner"></div>Processing your question...</div>';
  answerDiv.style.display = 'block';

  try {
    const res = await fetch("http://127.0.0.1:8000/ask/", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ question }),
    });

    const data = await res.json();
    answerDiv.innerHTML = '<div class="content-title">Answer</div>' + data.answer;
    questionInput.value = ''; // Clear the input
  } catch (error) {
    answerDiv.innerHTML = '<div class="content-title">Error</div>Failed to get answer. Please try again.';
  }
});