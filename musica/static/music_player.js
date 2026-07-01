const playBtn = document.getElementById('playBtn')
const deck = document.getElementById('albumCover')
const albumCoverEl = document.getElementById('albumCover')

const sliderVolume = document.getElementById('volumeSlider')
const volumeDisplay = document.querySelector('.volumeDisplay')


const songTitleEl = document.getElementById('songTitle')
const artistNameEl = document.getElementById('artistName')
const currentTimeEl = document.getElementById('currentTime')
const durationEl = document.getElementById('duration')

let spinning = false

let sound = null
let queue = []
let currentIndex = 0


let wavesurfer = null

// Prevents WaveSurfer auto-sync from fighting the user when they drag/seek.
let isUserSeeking = false

// Used so we can cancel the animation frame loop.
let syncFrame = null

let vinylAngle = 0

async function playMusic () {
  if (!sound) {
    const res = await fetch(
      `/play_music/${encodeURIComponent(artist)}/${encodeURIComponent(music)}/`
    )

    if (!res.ok) {


      const text = await res.text()
      console.error('Music request failed:', text)
      return
    }

    const data = await res.json()

    await loadSong({
      title: music,
      artist: artist,
      audio_url: data.audio_url,
      cover_url: data.cover_url
    })
  } else {
    if (sound.playing()) {
      sound.pause()
    } else {
      sound.play()
      startSyncLoop()
    }
  }
}

async function queueRandomizedVersion () {
  console.log('Creating playlist queue...')

  const url = `/musica/generate_random_query/${encodeURIComponent(
    artist
  )}/${encodeURIComponent(music)}/`

  console.log('Playlist URL:', url)

  const res = await fetch(url)

  console.log('Playlist fetch status:', res.status)

  if (!res.ok) {
    const text = await res.text()
    console.error('Playlist request failed:', text)
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

  if (!res.ok) {
    const text = await res.text()
    console.error('Failed to fetch queued song:', text)
    return
  }

  const data = await res.json()

  await loadSong({
    title: song.title,
    artist: song.artist,
    audio_url: data.audio_url,
    cover_url: data.cover_url || song.cover_url
  })
}

async function loadSong ({ title, artist, audio_url, cover_url }) {
  stopCurrentSound()

  initWaveSurfer(audio_url)

  updateSongUI(title, artist, cover_url)

  sound = new Howl({
    src: [audio_url],
    html5: true,
    volume: sliderVolume ? Number(sliderVolume.value) : 1,

    onplay: () => {
      spinning = true
      playBtn.textContent = '❚❚'
      startSyncLoop()
    },

    onpause: () => {
      spinning = false
      playBtn.textContent = '▶'
      stopSyncLoop()
    },

    onstop: () => {
      spinning = false
      playBtn.textContent = '▶'
      stopSyncLoop()
    },

    onend: () => {
      stopSyncLoop()
      playNextSong()
    },

    onload: () => {
      if (durationEl) {
        durationEl.textContent = formatTime(sound.duration())
      }
    },

    onloaderror: (id, error) => {
      console.error('Howler load error:', error)
    },

    onplayerror: (id, error) => {
      console.error('Howler play error:', error)
    }
  })

  const id = sound.play()

  sound.pannerAttr(
    {
      panningModel: 'HRTF',
      distanceModel: 'inverse',
      refDistance: 1,
      maxDistance: 10000,
      rolloffFactor: 1
    },
    id
  )

  Howler.pos(0, 0, 0)
  sound.pos(1, 0, 0, id)
}

function stopCurrentSound () {
  stopSyncLoop()

  if (sound) {
    sound.stop()
    sound.unload()
    sound = null
  }
}

async function playNextSong () {
  if (queue.length === 0) {
    await queueRandomizedVersion()
    return
  }

  currentIndex++

  if (currentIndex >= queue.length) {
    currentIndex = 0
  }

  await playCurrentSong()
}

function initWaveSurfer (url) {
  if (wavesurfer) {
    wavesurfer.destroy()
    wavesurfer = null
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
    if (durationEl) {
      durationEl.textContent = formatTime(wavesurfer.getDuration())
    }
  })

  wavesurfer.on('interaction', () => {
    if (!sound || !wavesurfer) return

    isUserSeeking = true

    const newTime = wavesurfer.getCurrentTime()
    sound.seek(newTime)

    if (currentTimeEl) {
      currentTimeEl.textContent = formatTime(newTime)
    }

    if (!sound.playing()) {
      sound.play()
    }


    setTimeout(() => {
      isUserSeeking = false
    }, 150)
  })

  wavesurfer.on('seek', progress => {
    if (!sound) return

    isUserSeeking = true

    const duration = sound.duration()
    const newTime = progress * duration

    sound.seek(newTime)

    if (currentTimeEl) {
      currentTimeEl.textContent = formatTime(newTime)
    }

    if (!sound.playing()) {
      sound.play()
    }


    setTimeout(() => {
      isUserSeeking = false
    }, 150)
  })
}

function startSyncLoop () {
  stopSyncLoop()

  const sync = () => {
    if (!sound || !wavesurfer || !sound.playing()) {
      syncFrame = null
      return
    }


    if (!isUserSeeking) {
      const current = Number(sound.seek()) || 0
      const duration = sound.duration()

      if (duration > 0) {
        const progress = current / duration

        wavesurfer.seekTo(progress)

        if (currentTimeEl) {
          currentTimeEl.textContent = formatTime(current)
        }
      }
    }

    syncFrame = requestAnimationFrame(sync)
  }

  syncFrame = requestAnimationFrame(sync)
}

function stopSyncLoop () {
  if (syncFrame) {
    cancelAnimationFrame(syncFrame)
    syncFrame = null
  }
}

function updateSongUI (title, artist, coverUrl) {
  if (songTitleEl) {
    songTitleEl.textContent = title
  }

  if (artistNameEl) {
    artistNameEl.textContent = artist
  }

  if (albumCoverEl && coverUrl) {
    albumCoverEl.src = coverUrl
    albumCoverEl.alt = `${title} cover`
  }

  // Spotify-like browser tab title.
  document.title = `${title} • ${artist} | CentralissaMusica`

  if (currentTimeEl) {
    currentTimeEl.textContent = '0:00'
  }

  if (durationEl) {
    durationEl.textContent = '0:00'
  }
}

function spin () {
  if (spinning && deck) {
    vinylAngle += 0.5
    deck.style.transform = `rotate(${vinylAngle}deg)`
  }

  requestAnimationFrame(spin)
}

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

function formatTime (seconds) {
  seconds = Number(seconds) || 0

  const min = Math.floor(seconds / 60)
  const sec = Math.floor(seconds % 60)

  return `${min}:${sec < 10 ? '0' : ''}${sec}`
}

playBtn.addEventListener('click', playMusic)

initVolumeSlider()
spin()