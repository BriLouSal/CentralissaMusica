console.log("Search JS loaded");

const input = document.getElementById('music-search');
const autocomplete = document.querySelector('.autocomplete');

let timeout;

input.addEventListener('input', () => {
    clearTimeout(timeout);

    timeout = setTimeout(async () => {
        const query = input.value.trim();

        if (query.length < 1) {
            autocomplete.classList.add('hidden');
            autocomplete.innerHTML = '';
            return;
        }

        try {
            const response = await fetch(`/music-search/autocomplete/${query}/`);
            const data = await response.json();

            console.log(data);


            const hasResults =
                (data.tracks && data.tracks.length > 0) ||
                (data.artists && data.artists.length > 0);

            if (hasResults) {
                autocomplete.classList.remove('hidden');

                autocomplete.innerHTML = `
                    ${renderSection("Artists", data.artists)}
                    ${renderSection("Songs", data.tracks)}
                `;

            } else {
                autocomplete.classList.add('hidden');
                autocomplete.innerHTML = '';
            }

        } catch (err) {
            console.error('Error fetching search results:', err);
            autocomplete.classList.add('hidden');
            autocomplete.innerHTML = '';
        }

    }, 300);
});



function renderSection(title, items) {
    if (!items || items.length === 0) return '';

    return `
        <div class="px-4 py-2 text-gray-400 text-xs uppercase">
            ${title}
        </div>
        ${items.map(item => renderItem(item)).join('')}
    `;
}


// Check if item is artist or track, then render accordingly
function renderItem(item) {
    const isArtist = item.type === 'artist';

    const redirectUrl = isArtist
    // We need to encode the name to make sure it works with special characters and spaces, we may have like a special character like $ in the name, or spaces, so we need to encode it to make sure it works correctly in the URL
        ? `/artist/${encodeURIComponent(item.name)}/`
        : `/music-player/${encodeURIComponent(item.name)}/`;

    return `
        <div class="flex items-center gap-3 px-4 py-2 hover:bg-gray-800 cursor-pointer"
             onclick="window.location.href='${redirectUrl}'">

            <img src="${item.image || 'https://via.placeholder.com/40'}" 
                 class="w-10 h-10 rounded object-cover"/>

            <div class="flex flex-col">
                <div class="text-white text-sm font-bold">
                    ${item.name ?? ''}
                </div>

                <div class="text-gray-400 text-xs">
                    ${isArtist ? 'Artist' : (item.artist ?? '')}
                </div>
            </div>
        </div>
    `;
}