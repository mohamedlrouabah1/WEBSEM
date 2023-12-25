document.getElementById('address-input').addEventListener('input', function() {
    const query = this.value;
    if (query.length < 3) {
        document.getElementById('autocomplete-results').innerHTML = '';
        return;
    }

    fetch(`https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(query)}`)
        .then(response => response.json())
        .then(data => {
            document.getElementById('autocomplete-results').innerHTML = data.map(place => {
                const address = place.address || {};
                const city = address.city || address.town || address.village || '';
                const country = address.country || '';
                const postcode = address.postcode || '';
                return `<div class="autocomplete-item" data-lat="${place.lat}" data-lon="${place.lon}" 
                        onclick="selectAddress('${place.display_name}', ${place.lat}, ${place.lon}, '${city}', '${country}', '${postcode}')">
                            ${place.display_name}
                        </div>`;
            }).join('');
        })
        .catch(error => console.error('Error:', error));
});

function selectAddress(name, lat, lon, city, country, postcode) {
    fetch('/query', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ lat, lon, name, city, country, postcode })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            window.location.href = '/restaurants';
        }
    })
    .catch(error => console.error('Error:', error));
}
