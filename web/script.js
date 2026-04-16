// === Starfield Mejorado con Luna Realista === 
// (Mantén todo el código del starfield que ya tienes)

/* === Música de fondo === */
const music = document.getElementById('bg-music');
const musicBtn = document.getElementById('music-btn');
let musicOn = false;

music.volume = 0.6; // volumen inicial

function toggleMusic() {
  if (musicOn) {
    music.pause();
    musicBtn.classList.remove('on');
    musicBtn.querySelector('i').className = 'fas fa-music';
  } else {
    music.play()
      .then(() => {
        musicBtn.classList.add('on');
        musicBtn.querySelector('i').className = 'fas fa-volume-up';
      })
      .catch(err => console.error('Error al reproducir:', err));
  }
  musicOn = !musicOn;
}

musicBtn.addEventListener('click', toggleMusic);

// === Toggle de Tema ===
const themeSwitch = document.getElementById("theme-switch");

function applyTheme(theme) {
  document.body.classList.toggle("dark", theme === "dark");
  document.body.classList.toggle("light", theme === "light");
  localStorage.setItem("theme", theme);
  
  // Cambiar icono según el tema
  const icon = themeSwitch.querySelector('i');
  icon.className = theme === "dark" ? "fas fa-sun" : "fas fa-moon";
}

function initTheme() {
  const savedTheme = localStorage.getItem("theme");
  const systemDark = window.matchMedia("(prefers-color-scheme: dark)").matches;
  
  if (savedTheme) {
    applyTheme(savedTheme);
  } else {
    applyTheme(systemDark ? "dark" : "light");
  }
}

themeSwitch.addEventListener("click", () => {
  const newTheme = document.body.classList.contains("dark") ? "light" : "dark";
  applyTheme(newTheme);
});

// === Funciones de descarga ===
function downloadVideo() {
  const url = document.getElementById("video-url").value;
  if (!url) {
    alert("Por favor, ingrese una URL de YouTube.");
    return;
  }
  window.open(`/download_video?url=${encodeURIComponent(url)}`, "_blank");
}

function downloadAudioV1() {
  const url = document.getElementById("audio-url").value;
  if (!url) {
    alert("Por favor, ingrese una URL de YouTube.");
    return;
  }
  window.open(`/download_audioV1?url=${encodeURIComponent(url)}`, "_blank");
}

// Inicialización cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', () => {
  initTheme();
  
  // Primer clic/tap en cualquier parte desbloquea el audio en móviles
  const unlock = () => { if (!musicOn) toggleMusic(); };
  document.addEventListener('click', unlock, { once: true });
  document.addEventListener('touchstart', unlock, { once: true });
  
  // Resto de tu inicialización...
});