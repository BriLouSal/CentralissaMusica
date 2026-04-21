// We want to import the spotify music player



document.addEventListener("DOMContentLoaded", function() {
    const spotifyPlayer = document.getElementById("spotify-player");
    if (spotifyPlayer) {
        // Get the Spotify URI from the data attribute
        const spotifyUri = spotifyPlayer.getAttribute("data-spotify-uri");
        // Create the iframe element
        const iframe = document.createElement("iframe");
        iframe.src = `https://open.spotify.com/embed/track/${spotifyUri}`;
        iframe.width = "300";
        iframe.height = "380";
        iframe.frameBorder = "0";
        iframe.allow = "encrypted-media";
        // Append the iframe to the spotify player container
        spotifyPlayer.appendChild(iframe);
    }
});





