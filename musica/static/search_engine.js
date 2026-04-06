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

            if (data.results && data.results.length > 0) {
                autocomplete.classList.remove('hidden');

                autocomplete.innerHTML = data.results.map(item => {
                    
                    const isArtist = item.type === 'artist';
                    const redirectUrl = isArtist
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

                                <div class="text-[10px] text-gray-500 uppercase">
                                    ${item.type ?? ''}
                                </div>
                            </div>
                        </div>
                    `;
                }).join('');

            } else {
                autocomplete.classList.add('hidden');
                autocomplete.innerHTML = '';
            }

        } catch (err) {
            console.error('Error fetching search results:', err);
            autocomplete.classList.add('hidden');
            autocomplete.innerHTML = '';
        }

    }, 300); // 🔥 debounce delay (300ms)
});