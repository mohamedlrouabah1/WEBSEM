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
    .then(response => {
        if (response.redirected) {
            window.location.href = response.url;
        } else {
            console.error('Expected a redirection response');
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
        console.log(userPreferences); // Display the user preferences in the console
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
        alert("Unable to retrieve your location");
    });
}

function loadUserPreferences(){
    var username = document.getElementById('usernameInput').value;
    document.getElementById('loadPreferencesModalMessage').innerText = ""

    username = username.replace(/\s+/g, '_');
    fetch('/user/preferences', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ username })
    })
    .then(response => {
        if (response.redirected) {
            window.location.href = response.url;
        } else {
            console.error('Expected a redirection response');
            return response.json();
        }
    })
    .then(data => {
        document.getElementById('loadPreferencesModalMessage').innerText = data.message
    })
    .catch(error => console.error('Error:', error));
}

function selectOption(option) {
    document.getElementById('dropdownMenuButton1').textContent = option;
}
function selectOption2(option) {
    document.getElementById('dropdownMenuButton2').textContent = option;
}
function stopPropagation(event) {
    event.stopPropagation(); // Prevent the event from propagating to close the dropdown
}


function performSearch() {
    var searchParams = {
        maxDistance: document.getElementById('maxDistanceInput').value,
        deliveryPrice: document.getElementById('deliveryPriceInput').value,
        openingHours: document.getElementById('openingHoursInput').value,
        openingDays: document.getElementById('openingDaysInput').value,
        rankby: document.getElementById('dropdownMenuButton2').textContent,
        // closingHours: document.getElementById('closingHoursInput').value
    };
    // var selectedDay = document.getElementById("openingDaysInput").value;

    var selectedOption = document.getElementById('dropdownMenuButton1').textContent;
    if (selectedOption === 'autour_de_moi') {
        // Handle geolocation here if "Autour de moi" is selected
        navigator.geolocation.getCurrentPosition(function(position) {
            searchParams.lat = position.coords.latitude;
            searchParams.lon = position.coords.longitude;
            console.log(searchParams); // Display the search parameters in the console
            sendSearchQuery(searchParams);
        });
    } else {
        // Handle search without geolocation
        sendSearchQuery(searchParams);
    }
}

function sendSearchQuery(params) {
    fetch('/query', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(params)
    })
    .then(response => {
        if (response.redirected) {
            window.location.href = response.url;
        } else {
            console.error('Expected a redirection response');
        }
    })
    .catch(error => console.error('Error:', error));
}


