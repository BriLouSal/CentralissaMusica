document.addEventListener('DOMContentLoaded', function () {
  VANTA.NET({
    el: '#home-bg',
    mouseControls: true,
    touchControls: true,
    gyroControls: false,
    color: 0xffffff,
    backgroundAlpha: 0,
    points: 10,
    maxDistance: 20
  })

  anime({
    targets: 'music-logo span',
    scale: [1, 1.4],
    direction: 'alternate',
    loop: true,
    easing: 'easeInOutSine',
    duration: 600
  })
})
