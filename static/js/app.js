let map;
let markers = [];
let pharmacies = [];

const CITY_CENTERS = {
    "Libreville": [0.4162, 9.4673],
    "Port-Gentil": [-0.7193, 8.7815],
    "Franceville": [-1.6333, 13.5833],
    "Moanda": [-1.5333, 13.2000],
    "Makokou": [0.5667, 12.8500],
    "Oyem": [1.6000, 11.5833],
    "Mouila": [-1.8667, 11.0500],
    "Koulamoutou": [-1.1333, 12.4667],
    "Ntom": [0.3667, 9.7667]
};

function initMap() {
    map = L.map('map').setView([0.4162, 9.4673], 12);
    
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
    }).addTo(map);
}

function getMarkerColor(pharmacy) {
    if (pharmacy.is_garde) return '#dc2626';
    if (pharmacy.is_gare) return '#3b82f6';
    if (pharmacy.type_etablissement.toLowerCase().includes('dépôt')) return '#f97316';
    return '#16a34a';
}

function createMarkerIcon(color) {
    return L.divIcon({
        className: 'custom-marker',
        html: `<div style="
            background-color: ${color};
            width: 24px;
            height: 24px;
            border-radius: 50%;
            border: 3px solid white;
            box-shadow: 0 2px 6px rgba(0,0,0,0.3);
            display: flex;
            align-items: center;
            justify-content: center;
        ">
            <svg width="12" height="12" viewBox="0 0 24 24" fill="white">
                <path d="M19 3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm-7 14h-2v-4H6v-2h4V7h2v4h4v2h-4v4z"/>
            </svg>
        </div>`,
        iconSize: [24, 24],
        iconAnchor: [12, 12],
        popupAnchor: [0, -12]
    });
}

function createPopupContent(pharmacy) {
    const badgeClass = pharmacy.is_garde ? 'badge-garde' : 'badge-general';
    const badgeText = pharmacy.is_garde ? '24h/24 - Garde' : pharmacy.type_etablissement;
    
    return `
        <div class="pharmacy-popup">
            <h4>${pharmacy.nom}</h4>
            <p><strong>Quartier:</strong> ${pharmacy.quartier}</p>
            <p><strong>Ville:</strong> ${pharmacy.ville}</p>
            ${pharmacy.telephone ? `<p><strong>Tél:</strong> ${pharmacy.telephone}</p>` : ''}
            ${pharmacy.horaires ? `<p><strong>Horaires:</strong> ${pharmacy.horaires}</p>` : ''}
            ${pharmacy.services ? `<p><strong>Services:</strong> ${pharmacy.services}</p>` : ''}
            <span class="badge ${badgeClass}">${badgeText}</span>
        </div>
    `;
}

function clearMarkers() {
    markers.forEach(marker => map.removeLayer(marker));
    markers = [];
}

function displayPharmacies(data) {
    clearMarkers();
    
    data.forEach(pharmacy => {
        const color = getMarkerColor(pharmacy);
        const icon = createMarkerIcon(color);
        
        const marker = L.marker([pharmacy.lat, pharmacy.lng], { icon })
            .bindPopup(createPopupContent(pharmacy))
            .addTo(map);
        
        markers.push(marker);
    });
    
    document.getElementById('displayedCount').textContent = data.length;
    document.getElementById('listCount').textContent = `(${data.length} résultats)`;
    
    updatePharmacyList(data);
    
    if (data.length > 0) {
        const bounds = L.latLngBounds(data.map(p => [p.lat, p.lng]));
        map.fitBounds(bounds, { padding: [50, 50] });
    }
}

function updatePharmacyList(data) {
    const container = document.getElementById('pharmacyList');
    
    if (data.length === 0) {
        container.innerHTML = '<p class="col-span-2 text-center text-gray-500 py-8">Aucune pharmacie trouvée</p>';
        return;
    }
    
    container.innerHTML = data.map(pharmacy => {
        const bgColor = pharmacy.is_garde ? 'border-l-red-500' : 
                       pharmacy.is_gare ? 'border-l-blue-500' : 'border-l-green-500';
        
        return `
            <div class="pharmacy-card bg-gray-50 rounded-lg p-3 border-l-4 ${bgColor} cursor-pointer" 
                 onclick="focusPharmacy(${pharmacy.lat}, ${pharmacy.lng})">
                <h4 class="font-semibold text-gray-800 text-sm">${pharmacy.nom}</h4>
                <p class="text-xs text-gray-600 mt-1">${pharmacy.quartier}, ${pharmacy.ville}</p>
                ${pharmacy.telephone ? `<p class="text-xs text-green-600 mt-1">${pharmacy.telephone}</p>` : ''}
                ${pharmacy.is_garde ? '<span class="inline-block mt-2 px-2 py-0.5 bg-red-100 text-red-700 text-xs rounded-full">24h/24</span>' : ''}
            </div>
        `;
    }).join('');
}

function focusPharmacy(lat, lng) {
    map.setView([lat, lng], 16);
    
    markers.forEach(marker => {
        const pos = marker.getLatLng();
        if (Math.abs(pos.lat - lat) < 0.0001 && Math.abs(pos.lng - lng) < 0.0001) {
            marker.openPopup();
        }
    });
}

async function fetchPharmacies() {
    const search = document.getElementById('searchInput').value;
    const ville = document.getElementById('villeSelect').value;
    const type = document.getElementById('typeSelect').value;
    const garde = document.getElementById('gardeCheckbox').checked;
    const gare = document.getElementById('gareCheckbox').checked;
    
    const params = new URLSearchParams();
    if (search) params.append('search', search);
    if (ville) params.append('ville', ville);
    if (type) params.append('type', type);
    if (garde) params.append('garde', 'true');
    if (gare) params.append('gare', 'true');
    
    try {
        const response = await fetch(`/api/pharmacies?${params}`);
        const data = await response.json();
        pharmacies = data;
        displayPharmacies(data);
        
        if (ville && CITY_CENTERS[ville]) {
            map.setView(CITY_CENTERS[ville], 13);
        }
    } catch (error) {
        console.error('Erreur lors du chargement des pharmacies:', error);
    }
}

async function fetchStats() {
    try {
        const response = await fetch('/api/stats');
        const stats = await response.json();
        
        document.getElementById('totalCount').textContent = stats.total;
        document.getElementById('gardeCount').textContent = stats.pharmacies_garde;
    } catch (error) {
        console.error('Erreur lors du chargement des statistiques:', error);
    }
}

function resetFilters() {
    document.getElementById('searchInput').value = '';
    document.getElementById('villeSelect').value = '';
    document.getElementById('typeSelect').value = '';
    document.getElementById('gardeCheckbox').checked = false;
    document.getElementById('gareCheckbox').checked = false;
    
    map.setView([0.4162, 9.4673], 12);
    fetchPharmacies();
}

let debounceTimer;
function debounce(func, delay) {
    clearTimeout(debounceTimer);
    debounceTimer = setTimeout(func, delay);
}

document.addEventListener('DOMContentLoaded', () => {
    initMap();
    fetchStats();
    fetchPharmacies();
    
    document.getElementById('searchInput').addEventListener('input', () => debounce(fetchPharmacies, 300));
    document.getElementById('villeSelect').addEventListener('change', fetchPharmacies);
    document.getElementById('typeSelect').addEventListener('change', fetchPharmacies);
    document.getElementById('gardeCheckbox').addEventListener('change', fetchPharmacies);
    document.getElementById('gareCheckbox').addEventListener('change', fetchPharmacies);
    document.getElementById('resetFilters').addEventListener('click', resetFilters);
});
