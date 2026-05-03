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
    initWaveSurfer(data.audio_url)

    sound = new Howl({
      src: [data.audio_url],
      html5: true,
      volume: sliderVolume ? Number(sliderVolume.value) : 1,

      onplay: () => {
        spinning = true
        playBtn.textContent = '❚❚'
        syncWaveToHowler()
      },

      onpause: () => {
        spinning = false
        playBtn.textContent = '▶'
      },
      onend: () => {
        playNextSong()
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
  console.log('Creating playlist queue...')

  const url = `/musica/generate_random_query/${encodeURIComponent(
    music
  )}/${encodeURIComponent(artist)}/`
  console.log('Playlist URL:', url)

  const res = await fetch(url)

  console.log('Playlist fetch status:', res.status)

  if (!res.ok) {
    const text = await res.text()
    console.error('Playlist request failed HTML:', text)
    return
  }

  const data = await res.json()
  console.log('Playlist data:', data)

  if (!data.playlist || data.playlist.length === 0) {
    console.warn('No songs returned')
    return
  }

  queue = data.playlist

  currentIndex = 0

  await playCurrentSong()
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
    volume: sliderVolume ? Number(sliderVolume.value) : 1,

    html5: true,
    onplay: () => {
      spinning = true
      playBtn.textContent = '❚❚'
      syncWaveToHowler()
    },

    onpause: () => {
      spinning = false
      playBtn.textContent = '▶'
    },

    onend: () => {
      playNextSong()
    }
  })

  sound.play()
}
playBtn.addEventListener('click', playMusic)

async function playNextSong () {
  if (queue.length === 0) {
    await queueRandomizedVersion()
    return
  }

  currentIndex++
  // Then we start at CurrentIndex 0 since we shifted it

  if (currentIndex >= queue.length) {
    // Then we start at CurrentIndex 0 since we shifted it

    currentIndex = 0
  }

  playCurrentSong()
}

let vinylAngle = 0
function spin () {
  if (spinning && deck) {
    vinylAngle += 0.4
    deck.style.transform = `rotate(${vinylAngle}deg)`
  }
  requestAnimationFrame(spin)
}

spin()
function setVolume (value) {
  const vol = Math.max(0, Math.min(1, Number(value)))
  if (sound) {
    sound.volume(vol)
  }

  if (volumeDisplay) {
    volumeDisplay.textContent = `${Math.round(vol * 100)}%`
  }
}

function initVolumeSlider () {
  if (!sliderVolume) return

  sliderVolume.value = 1

  sliderVolume.addEventListener('input', () => {
    setVolume(sliderVolume.value)
  })
}
initVolumeSlider()

let wavesurfer = null

function initWaveSurfer (url) {
  if (wavesurfer) {
    wavesurfer.destroy()
  }

  wavesurfer = WaveSurfer.create({
    container: '#waveform',
    waveColor: '#9ca3af',
    progressColor: '#ec4899',
    cursorColor: '#ffffff',
    height: 70,
    barWidth: 3,
    barGap: 2,
    barRadius: 3,
    responsive: true
  })

  wavesurfer.load(url)

  wavesurfer.on('ready', () => {
    document.getElementById('duration').textContent = formatTime(
      wavesurfer.getDuration()
    )
  })

  wavesurfer.on('audioprocess', () => {
    document.getElementById('currentTime').textContent = formatTime(
      wavesurfer.getCurrentTime()
    )
  })
  wavesurfer.on('interaction', () => {
    if (!sound || !wavesurfer) return

    const newTime = wavesurfer.getCurrentTime()

    sound.seek(newTime)
    // Update the song! Make sure that we get it updated when the user seeks
    // a new music, I tried doing seek so I guessed that interaction will do
    document.getElementById('currentTime').textContent = formatTime(newTime)

    if (!sound.playing()) {
      sound.play()
    }

    syncWaveToHowler()
  })

  wavesurfer.on('seek', progress => {
    if (!sound) return

    const duration = sound.duration()
    const newTime = progress * duration

    sound.seek(newTime)

    document.getElementById('currentTime').textContent = formatTime(newTime)

    if (!sound.playing()) {
      sound.play()
    }

    syncWaveToHowler()
  })
}

function formatTime (seconds) {
  const min = Math.floor(seconds / 60)
  const sec = Math.floor(seconds % 60)
  return `${min}:${sec < 10 ? '0' : ''}${sec}`
}

function syncWaveToHowler () {
  if (!sound || !wavesurfer) return

  const current = sound.seek()
  const duration = sound.duration()

  if (duration > 0) {
    wavesurfer.seekTo(current / duration)
    document.getElementById('currentTime').textContent = formatTime(current)
  }

  if (sound.playing()) {
    requestAnimationFrame(syncWaveToHowler)
  }
}
