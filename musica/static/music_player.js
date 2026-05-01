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

// Create a listener that allows me to create  a vinyl like disk animation, which
// I loved about, and I feel like it's very snazzy and I like it that way
// so it's possible that we can do this

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


async function queueRandomizedVersion(){
  
}