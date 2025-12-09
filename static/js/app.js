let map;
let markers = [];
let pharmacies = [];
let currentTab = 'pharmacies';
let currentCity = '';

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
    if (map) return;
    map = L.map('map').setView([0.4162, 9.4673], 7);
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
    }).addTo(map);
}

function getMarkerColor(pharmacy) {
    if (pharmacy.is_garde) return '#ef4444';
    if (pharmacy.is_gare) return '#3b82f6';
    if (pharmacy.type_etablissement && pharmacy.type_etablissement.toLowerCase().includes('dépôt')) return '#f97316';
    return '#10b981';
}

function createMarkerIcon(color) {
    return L.divIcon({
        className: 'custom-marker',
        html: `<div style="
            background-color: ${color};
            width: 32px;
            height: 32px;
            border-radius: 50%;
            border: 3px solid white;
            box-shadow: 0 2px 8px rgba(0,0,0,0.3);
            display: flex;
            align-items: center;
            justify-content: center;
        ">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="white">
                <path d="M19 3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm-7 14h-2v-4H6v-2h4V7h2v4h4v2h-4v4z"/>
            </svg>
        </div>`,
        iconSize: [32, 32],
        iconAnchor: [16, 16],
        popupAnchor: [0, -16]
    });
}

function clearMarkers() {
    markers.forEach(marker => map.removeLayer(marker));
    markers = [];
}

function displayOnMap(data) {
    if (!map) initMap();
    clearMarkers();
    
    data.forEach(pharmacy => {
        if (!pharmacy.lat || !pharmacy.lng) return;
        
        const color = getMarkerColor(pharmacy);
        const icon = createMarkerIcon(color);
        
        const popupContent = `
            <div class="p-2">
                <h4 class="font-semibold text-gray-800">${pharmacy.nom}</h4>
                <p class="text-sm text-gray-600">${pharmacy.quartier}, ${pharmacy.ville}</p>
                ${pharmacy.telephone ? `<p class="text-sm text-emerald-600 mt-1">${pharmacy.telephone}</p>` : ''}
                ${pharmacy.is_garde ? '<span class="inline-block mt-2 px-2 py-0.5 bg-red-100 text-red-700 text-xs rounded-full">24h/24</span>' : ''}
            </div>
        `;
        
        const marker = L.marker([pharmacy.lat, pharmacy.lng], { icon })
            .bindPopup(popupContent)
            .addTo(map);
        
        markers.push(marker);
    });
    
    if (data.length > 0) {
        const validData = data.filter(p => p.lat && p.lng);
        if (validData.length > 0) {
            const bounds = L.latLngBounds(validData.map(p => [p.lat, p.lng]));
            map.fitBounds(bounds, { padding: [30, 30] });
        }
    }
}

function createPharmacyCard(pharmacy) {
    const borderColor = pharmacy.is_garde ? 'border-l-red-500' : 
                       pharmacy.is_gare ? 'border-l-blue-500' : 'border-l-emerald-500';
    
    return `
        <div class="pharmacy-card bg-white rounded-xl p-4 shadow-sm border-l-4 ${borderColor} active:scale-[0.98] transition cursor-pointer"
             onclick="showPharmacyDetail(${JSON.stringify(pharmacy).replace(/"/g, '&quot;')})">
            <div class="flex items-start justify-between">
                <div class="flex-1 min-w-0">
                    <h3 class="font-semibold text-gray-800 truncate">${pharmacy.nom}</h3>
                    <p class="text-sm text-gray-500 mt-0.5">${pharmacy.quartier || ''}</p>
                    <p class="text-xs text-gray-400">${pharmacy.ville}</p>
                </div>
                ${pharmacy.is_garde ? `
                    <span class="flex-shrink-0 ml-2 px-2 py-1 bg-red-100 text-red-700 text-xs font-medium rounded-full">
                        24h/24
                    </span>
                ` : ''}
            </div>
            ${pharmacy.telephone ? `
                <a href="tel:${pharmacy.telephone.split('/')[0].trim()}" 
                   onclick="event.stopPropagation()"
                   class="mt-3 flex items-center gap-2 text-sm text-emerald-600 font-medium">
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z"/>
                    </svg>
                    ${pharmacy.telephone.split('/')[0].trim()}
                </a>
            ` : ''}
        </div>
    `;
}

function showPharmacyDetail(pharmacy) {
    const modal = document.getElementById('pharmacyModal');
    const title = document.getElementById('modalTitle');
    const content = document.getElementById('modalContent');
    
    title.textContent = pharmacy.nom;
    
    content.innerHTML = `
        <div class="space-y-4">
            ${pharmacy.is_garde ? `
                <div class="flex items-center gap-2 p-3 bg-red-50 rounded-xl">
                    <div class="w-3 h-3 bg-red-500 rounded-full animate-pulse"></div>
                    <span class="text-sm font-medium text-red-700">Pharmacie de garde - Ouvert 24h/24</span>
                </div>
            ` : ''}
            
            <div class="space-y-3">
                <div class="flex items-start gap-3">
                    <div class="w-10 h-10 bg-gray-100 rounded-lg flex items-center justify-center flex-shrink-0">
                        <svg class="w-5 h-5 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z"/>
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z"/>
                        </svg>
                    </div>
                    <div>
                        <p class="text-sm text-gray-500">Adresse</p>
                        <p class="font-medium text-gray-800">${pharmacy.quartier || 'Non spécifié'}</p>
                        <p class="text-sm text-gray-600">${pharmacy.ville}</p>
                    </div>
                </div>
                
                ${pharmacy.telephone ? `
                    <div class="flex items-start gap-3">
                        <div class="w-10 h-10 bg-emerald-100 rounded-lg flex items-center justify-center flex-shrink-0">
                            <svg class="w-5 h-5 text-emerald-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z"/>
                            </svg>
                        </div>
                        <div>
                            <p class="text-sm text-gray-500">Téléphone</p>
                            <a href="tel:${pharmacy.telephone.split('/')[0].trim()}" class="font-medium text-emerald-600">${pharmacy.telephone}</a>
                        </div>
                    </div>
                ` : ''}
                
                ${pharmacy.horaires ? `
                    <div class="flex items-start gap-3">
                        <div class="w-10 h-10 bg-gray-100 rounded-lg flex items-center justify-center flex-shrink-0">
                            <svg class="w-5 h-5 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"/>
                            </svg>
                        </div>
                        <div>
                            <p class="text-sm text-gray-500">Horaires</p>
                            <p class="font-medium text-gray-800">${pharmacy.horaires}</p>
                        </div>
                    </div>
                ` : ''}
                
                ${pharmacy.services ? `
                    <div class="flex items-start gap-3">
                        <div class="w-10 h-10 bg-gray-100 rounded-lg flex items-center justify-center flex-shrink-0">
                            <svg class="w-5 h-5 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"/>
                            </svg>
                        </div>
                        <div>
                            <p class="text-sm text-gray-500">Services</p>
                            <p class="text-sm text-gray-800">${pharmacy.services}</p>
                        </div>
                    </div>
                ` : ''}
            </div>
            
            ${pharmacy.telephone ? `
                <a href="tel:${pharmacy.telephone.split('/')[0].trim()}" 
                   class="mt-4 w-full py-3 bg-emerald-600 text-white font-semibold rounded-xl flex items-center justify-center gap-2 hover:bg-emerald-700 transition">
                    <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z"/>
                    </svg>
                    Appeler
                </a>
            ` : ''}
        </div>
    `;
    
    modal.classList.remove('hidden');
    modal.classList.add('flex');
}

function closeModal() {
    const modal = document.getElementById('pharmacyModal');
    modal.classList.add('hidden');
    modal.classList.remove('flex');
}

function switchTab(tab) {
    currentTab = tab;
    
    document.querySelectorAll('.tab-content').forEach(el => el.classList.add('hidden'));
    document.getElementById(`tab-${tab}`).classList.remove('hidden');
    
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.remove('border-primary-600', 'text-primary-600');
        btn.classList.add('border-transparent', 'text-gray-500');
    });
    document.querySelectorAll(`.tab-btn[data-tab="${tab}"]`).forEach(btn => {
        btn.classList.add('border-primary-600', 'text-primary-600');
        btn.classList.remove('border-transparent', 'text-gray-500');
    });
    
    document.querySelectorAll('.mobile-tab-btn').forEach(btn => {
        btn.classList.remove('active', 'text-emerald-600');
        btn.classList.add('text-gray-400');
    });
    document.querySelectorAll(`.mobile-tab-btn[data-tab="${tab}"]`).forEach(btn => {
        btn.classList.add('active', 'text-emerald-600');
        btn.classList.remove('text-gray-400');
    });
    
    if (tab === 'map') {
        setTimeout(() => {
            initMap();
            map.invalidateSize();
            displayOnMap(pharmacies);
        }, 100);
    }
    
    if (tab === 'garde') {
        fetchPharmacies(true);
    } else if (tab === 'pharmacies') {
        fetchPharmacies(false);
    }
}

function filterByCity(city) {
    currentCity = city;
    
    document.querySelectorAll('.city-filter').forEach(btn => {
        if (btn.dataset.city === city) {
            btn.classList.add('bg-white', 'text-primary-700');
            btn.classList.remove('bg-white/10', 'text-white');
        } else {
            btn.classList.remove('bg-white', 'text-primary-700');
            btn.classList.add('bg-white/10', 'text-white');
        }
    });
    
    fetchPharmacies(currentTab === 'garde');
    
    if (city && CITY_CENTERS[city] && map) {
        map.setView(CITY_CENTERS[city], 13);
    }
}

async function fetchPharmacies(gardeOnly = false) {
    const search = document.getElementById('searchInput').value;
    
    const params = new URLSearchParams();
    if (search) params.append('search', search);
    if (currentCity) params.append('ville', currentCity);
    if (gardeOnly) params.append('garde', 'true');
    
    try {
        const response = await fetch(`/api/pharmacies?${params}`);
        const data = await response.json();
        pharmacies = data;
        
        if (gardeOnly) {
            document.getElementById('countGarde').textContent = `(${data.length})`;
            document.getElementById('gardeList').innerHTML = data.length > 0 
                ? data.map(p => createPharmacyCard(p)).join('')
                : '<p class="text-center text-gray-500 py-8">Aucune pharmacie de garde trouvée</p>';
        } else {
            document.getElementById('countAll').textContent = `(${data.length})`;
            document.getElementById('pharmacyList').innerHTML = data.length > 0 
                ? data.map(p => createPharmacyCard(p)).join('')
                : '<p class="text-center text-gray-500 py-8">Aucune pharmacie trouvée</p>';
        }
        
        if (currentTab === 'map') {
            displayOnMap(data);
        }
    } catch (error) {
        console.error('Error fetching pharmacies:', error);
    }
}

let debounceTimer;
function debounce(func, delay) {
    clearTimeout(debounceTimer);
    debounceTimer = setTimeout(func, delay);
}

document.addEventListener('DOMContentLoaded', () => {
    fetchPharmacies();
    
    document.getElementById('searchInput').addEventListener('input', () => {
        debounce(() => fetchPharmacies(currentTab === 'garde'), 300);
    });
    
    document.getElementById('pharmacyModal').addEventListener('click', (e) => {
        if (e.target === e.currentTarget) {
            closeModal();
        }
    });
});
