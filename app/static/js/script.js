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

function collectAndSendPreferences() {
    // First, check if geolocation is supported
    if (!navigator.geolocation) {
        alert("Geolocation is not supported by your browser");
        return;
    }

    // Get the current position
    navigator.geolocation.getCurrentPosition(function(position) {
        // On success, add the lat and lon to userPreferences
        var userPreferences = {
            name: document.getElementById('name').value,
            address: document.getElementById('address').value,
            city: document.getElementById('city').value,
            country: document.getElementById('country').value,
            postal_code: document.getElementById('postal_code').value,
            max_distance: document.getElementById('max_distance').value,
            latitude: position.coords.latitude, // add latitude
            longitude: position.coords.longitude, // add longitude
            max_price: document.getElementById('max_price').value,
            seller_url: document.getElementById('seller_url').value,
            item_offered: document.getElementById('item_offered').value, 
        };

        // Now send the data with the fetch call
        fetch('/preferences', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(userPreferences)
        })
        .then(response => response.json())
        .then(data => {
            alert(data.message);
        })
        .catch(error => {
            console.error('Erreur:', error);
            alert('Erreur lors de l\'enregistrement des préférences.');
        });

    }, function() {
        // Handle error
        alert("Unable to retrieve your location");
    });
}

function loadUserPreferences(){
    var username = document.getElementById('usernameInput').value;
    
    username = username.replace(/\s+/g, '_');
    fetch('/user-preferences', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ username })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            window.location.href = '/restaurants';
            redirect('/restaurants');
        }
    })
    .catch(error => console.error('Error:', error));
}  
function getCurrentLocation() {
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(function(position) {
            const lat = position.coords.latitude;
            const lon = position.coords.longitude;
            // Une fois que vous avez obtenu les coordonnées, vous pouvez les utiliser pour lancer la recherche
            searchNearbyRestaurants(lat, lon);
        }, function(error) {
            console.error('Erreur de géolocalisation:', error);
            alert("Impossible de récupérer votre emplacement actuel.");
        });
    } else {
        alert("La géolocalisation n'est pas prise en charge par votre navigateur.");
    }
}
function searchNearbyRestaurants(lat, lon) {
    fetch('/query', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ lat, lon})
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            window.location.href = '/restaurants';
        }
    })
    .catch(error => console.error('Error:', error));}
