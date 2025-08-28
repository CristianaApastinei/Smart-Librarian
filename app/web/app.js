// ---------- Theme ----------
const root = document.documentElement;
const themeToggle = document.getElementById('themeToggle');
const themeLabel = document.getElementById('themeLabel');
const savedTheme = localStorage.getItem('theme');

function setTheme(mode) {
  if (mode === 'dark') {
    root.setAttribute('data-theme', 'dark');
    themeLabel.textContent = 'Dark';
  } else {
    root.setAttribute('data-theme', 'light');
    themeLabel.textContent = 'Light';
  }
  localStorage.setItem('theme', mode);
}

if (savedTheme) {
  setTheme(savedTheme);
} else if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
  setTheme('dark');
} else {
  setTheme('light');
}
themeToggle.addEventListener('click', () => {
  const next = root.getAttribute('data-theme') === 'dark' ? 'light' : 'dark';
  setTheme(next);
});

// ---------- UI helpers ----------
const q = document.getElementById('q');
const log = document.getElementById('log');
const askBtn = document.getElementById('askBtn');
const clearBtn = document.getElementById('clearBtn');
const topK = document.getElementById('topK');
const sttBtn = document.getElementById('sttBtn');
const ttsBtn = document.getElementById('ttsBtn');

function addMsg(role, text) {
  const div = document.createElement('div');
  div.className = `msg ${role}`;
  div.textContent = text;
  log.appendChild(div);
  log.scrollTop = log.scrollHeight;
}

function setBusy(isBusy) {
  askBtn.disabled = isBusy;
  askBtn.textContent = isBusy ? 'Thinking…' : 'Ask';
}

// ---------- Chips (now selected by data attribute) ----------
document.querySelectorAll('[data-fill]').forEach(btn => {
  btn.addEventListener('click', () => {
    q.value = btn.dataset.fill;
    q.focus();
    // Want auto-send? Uncomment the next line:
    // send();
  });
});

// ---------- Send ----------
async function send() {
  const text = q.value.trim();
  if (!text) return;
  addMsg('user', text);
  setBusy(true);
  try {
    const resp = await fetch('/chat', {
      method: 'POST',
      headers: {'Content-Type':'application/json'},
      body: JSON.stringify({ message: text, top_k: Number(topK.value) })
    });
    const data = await resp.json();
    const answer = data.assistant || 'No response';
    addMsg('assistant', answer);

    // Auto-speak? uncomment:
    // startSpeaking(answer);
  } catch (e) {
    addMsg('assistant', '⚠️ Error talking to the server. Is FastAPI running?');
  } finally {
    setBusy(false);
  }
}

askBtn.addEventListener('click', send);
q.addEventListener('keydown', (e) => {
  if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') send();
});
clearBtn.addEventListener('click', () => { q.value = ''; q.focus(); });

// ---------- TTS (play/stop toggle) ----------
let speaking = false;
let currentUtterance = null;

function startSpeaking(text) {
  if (!('speechSynthesis' in window)) {
    addMsg('assistant', '🔇 Text-to-speech not supported in this browser.');
    return;
  }
  if (!text || !text.trim()) {
    addMsg('assistant', 'Nothing to read yet.');
    return;
  }

  window.speechSynthesis.cancel(); // stop any ongoing

  currentUtterance = new SpeechSynthesisUtterance(text);
  // currentUtterance.lang = 'en-US';
  currentUtterance.onstart = () => {
    speaking = true;
    ttsBtn.classList.add('speaking');
    ttsBtn.title = 'Stop speaking';
  };
  const clearSpeaking = () => {
    speaking = false;
    ttsBtn.classList.remove('speaking');
    ttsBtn.title = 'Speak last answer';
  };
  currentUtterance.onend = clearSpeaking;
  currentUtterance.onerror = clearSpeaking;

  window.speechSynthesis.speak(currentUtterance);
}

function stopSpeaking() {
  if (!('speechSynthesis' in window)) return;
  window.speechSynthesis.cancel();
  speaking = false;
  ttsBtn.classList.remove('speaking');
  ttsBtn.title = 'Speak last answer';
}

ttsBtn.addEventListener('click', () => {
  if (speaking) {
    stopSpeaking();
  } else {
    const msgs = Array.from(log.querySelectorAll('.msg.assistant'));
    const last = msgs[msgs.length - 1];
    startSpeaking(last ? last.textContent : '');
  }
});

// ESC to stop TTS quickly
window.addEventListener('keydown', (e) => {
  if (e.key === 'Escape' && speaking) stopSpeaking();
});

// ---------- STT (start/stop toggle) ----------
let recognition = null;
let listening = false;

function setupRecognition() {
  const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
  if (!SR) return null;
  const rec = new SR();
  rec.lang = 'en-US';
  rec.interimResults = true;
  rec.continuous = false;
  rec.maxAlternatives = 1;
  return rec;
}

function startListening() {
  if (listening) return;
  recognition = setupRecognition();
  if (!recognition) {
    addMsg('assistant', '🎙️ Speech-to-text not supported in this browser.');
    return;
  }

  listening = true;
  sttBtn.classList.add('recording');
  sttBtn.title = 'Stop recording';

  let finalTranscript = '';

  recognition.onresult = (event) => {
    let interim = '';
    for (let i = event.resultIndex; i < event.results.length; i++) {
      const transcript = event.results[i][0].transcript;
      if (event.results[i].isFinal) finalTranscript += transcript + ' ';
      else interim += transcript;
    }
    q.value = (finalTranscript + interim).trim();
  };

  recognition.onerror = (e) => {
    addMsg('assistant', '🎙️ Mic error: ' + (e.error || 'unknown'));
  };

  recognition.onend = () => {
    sttBtn.classList.remove('recording');
    sttBtn.title = 'Start voice input';
    listening = false;
  };

  try { recognition.start(); } catch (e) { console.warn('recognition.start error', e); }
}

function stopListening() {
  if (recognition && listening) {
    recognition.stop();
  }
}

sttBtn.addEventListener('click', () => {
  if (listening) stopListening(); else startListening();
});
