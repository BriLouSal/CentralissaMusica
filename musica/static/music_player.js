const playBtn = document.getElementById('playBtn')
const deck = document.getElementById('deckA')
const sliderVolume = document.getElementById('volumeSlider')
const volumeDisplay = document.querySelector('.volumeDisplay')
let angle = 0
let spinning = false

let sound = null
let queue = []
let currentIndex = 0
async function playMusic () {
  // Fetch the url to grab the music and make the song play via the URL, which our python function handles to download the music and then play it for the user
  if (!sound) {
    const res = await fetch(
      `/play_music/${encodeURIComponent(artist)}/${encodeURIComponent(music)}/`
    )

    const data = await res.json()

    sound = new Howl({
      src: [data.audio_url],
      html5: true,
      volume: sliderVolume ? Number(sliderVolume.value) : 1,

      onplay: () => {
        spinning = true
        playBtn.textContent = '❚❚'
      },

      onpause: () => {
        spinning = false
        playBtn.textContent = '▶'
      }
    })

    sound.play()
  } else {
    if (sound.playing()) {
      sound.pause()
    } else {
      sound.play()
    }
  }
}

// Create a listener that allows me to create  a vinyl like disk animation, which
// I loved about, and I feel like it's very snazzy and I like it that way
// so it's possible that we can do this

async function queueRandomizedVersion () {
  const res = await fetch('/musica/randomized_playlist/')
  const data = await res.json()

  queue = data.playlist
  currentIndex = 0

  playCurrentSong()
}

async function playCurrentSong () {
  const song = queue[currentIndex]

  if (!song) return

  const res = await fetch(
    `/play_music/${encodeURIComponent(song.artist)}/${encodeURIComponent(
      song.title
    )}/`
  )
  const data = await res.json()

  if (sound) {
    sound.stop()
    sound.unload()
  }
  sound = new Howl({
    src: [data.audio_url],
  
    html5: true,
    onplay: () => {
      spinning = true;  
      playBtn.textContent = '❚❚';
    },

    onpause: () => {
      spinning = false;
      playBtn.textContent = '▶';
    },

    onend: () => {
      playNextSong();
    }
  });

  sound.play();
}
playBtn.addEventListener('click', playMusic);

function playNextSong(){
  currentIndex++;

  // What we want to do is check the query, and for the Opposite Song previous
  if(currentIndex > queue.length){
    // Then we start at CurrentIndex 0 since we shifted it 
    currentIndex = 0;
  }
  playCurrentSong();
}

let vinylAngle = 0;
function spin(){
  if(spinning && deck ){
    vinylAngle += 0.4;
    deck.style.transform = `rotate(${vinylAngle}deg)`;

  }
  requestAnimationFrame(spin);
}

spin();
function setVolume(value){
  const vol = Math.max(0, Math.min(1, Number(value)));
    if (sound) {
    sound.volume(newVolume);
  }

  if (volumeDisplay) {
    volumeDisplay.textContent = `${Math.round(newVolume * 100)}%`;
  }
}

function initVolumeSlider() {
  if (!sliderVolume) return;

  sliderVolume.value = 1;

  sliderVolume.addEventListener('input', () => {
    setVolume(sliderVolume.value);
  });
}