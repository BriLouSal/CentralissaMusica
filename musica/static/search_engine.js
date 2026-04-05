console.log("Search JS loaded");


const input = document.getElementById('music-search');
const autocomplete = document.querySelector('.autocomplete');

// autocomplete feature
input.addEventListener('input', async () => {

    const query = input.value;

    if (query.length < 1) {
        autocomplete.classList.add('hidden');
        autocomplete.innerHTML = '';
        return;
    }
    // Get the URL for my music api endpoint from Django's URL,
    // which will call deezer API and return the results as JSON

    const response = await fetch(`/music-search/autocomplete/${query}/`);
    const data = await response.json();
    console.log(data);  

    try{
        if (data.results && data.results.length > 0) {
            autocomplete.classList.remove('hidden');

        autocomplete.innerHTML = data.results.map(item => `
            <div class="flex items-center gap-3 px-4 py-2 hover:bg-gray-800 cursor-pointer"
                onclick="window.location.href='/music-player/${item.name}/'">

                <img src="${item.image || 'https://via.placeholder.com/40'}" 
                    class="w-10 h-10 rounded object-cover"/>

                <div>
                    <div class="text-white text-sm font-bold">
                        ${item.name ?? ''}
                    </div>
                    <div class="text-white text-xs font-semibold">
                        ${item.artist ?? ''}
                    </div>
                </div>

            </div>
        `).join('');

    } else {
        autocomplete.classList.add('hidden');
        autocomplete.innerHTML = '';
    }
        }catch (err) {
        console.error('Error fetching search results:', err);
        autocomplete.classList.add('hidden');
        autocomplete.innerHTML = '';
    }
});

