const audio = document.getElementById("audio");
const playBtn = document.getElementById("playBtn");
const deck = document.getElementById("deckA");

let angle = 0;
let spinning = false;

async function playMusic() {
    // Fetch the data required for the music palyer and ensure that we can 
    // like 
  if (!audio.src) {
    const dataRes = await fetch(
      `/play_music/${encodeURIComponent(artist)}/${encodeURIComponent(music)}/`
    );

    const data = await dataRes.json();
    audio.src = data.audio_url;
  }

  if (audio.paused) {
    await audio.play();
    grab_music_time();

  } else {
    audio.pause();
  }
}

playBtn.addEventListener("click", playMusic);

audio.addEventListener("play", () => {
  spinning = true;
  playBtn.textContent = "❚❚ Pause";
});

audio.addEventListener("pause", () => {
  spinning = false;
  playBtn.textContent = "▶ Play";
});


// Now we can grab the music_time of the audio
function grab_music_time(){
    audio.addEventListener('loadedmetadata', () => {
        console.log("Duration: ", audio.duration)

    });

}

function formatTime(seconds){
    const minute = Math.floor(seconds/60);
    const second = Math.floor(seconds    % 60).toString().padStart(2, "0");
    return `${minute}:${second}`
}
