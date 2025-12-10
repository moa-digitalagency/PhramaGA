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

const CITY_COLORS = {
    "Libreville": "bg-blue-100 text-blue-700",
    "Port-Gentil": "bg-purple-100 text-purple-700",
    "Franceville": "bg-orange-100 text-orange-700",
    "Moanda": "bg-pink-100 text-pink-700",
    "Makokou": "bg-cyan-100 text-cyan-700",
    "Oyem": "bg-amber-100 text-amber-700",
    "Mouila": "bg-lime-100 text-lime-700",
    "Koulamoutou": "bg-rose-100 text-rose-700",
    "Ntom": "bg-teal-100 text-teal-700"
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
                <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 18c-4.41 0-8-3.59-8-8s3.59-8 8-8 8 3.59 8 8-3.59 8-8 8zm-1-13h2v4h4v2h-4v4h-2v-4H7v-2h4V7z"/>
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
        if (pharmacy.lat === null || pharmacy.lat === undefined || pharmacy.lng === null || pharmacy.lng === undefined) return;
        
        const color = getMarkerColor(pharmacy);
        const icon = createMarkerIcon(color);
        
        const marker = L.marker([pharmacy.lat, pharmacy.lng], { icon })
            .addTo(map);
        
        marker.on('click', function() {
            showPharmacyDetail(pharmacy);
        });
        
        markers.push(marker);
    });
    
    if (data.length > 0) {
        const validData = data.filter(p => p.lat !== null && p.lat !== undefined && p.lng !== null && p.lng !== undefined);
        if (validData.length > 0) {
            const bounds = L.latLngBounds(validData.map(p => [p.lat, p.lng]));
            map.fitBounds(bounds, { padding: [30, 30] });
        }
    }
}

function getCityBadgeClass(ville) {
    return CITY_COLORS[ville] || "bg-gray-100 text-gray-700";
}

function createMapPopup(pharmacy) {
    const pharmacyData = JSON.stringify(pharmacy).replace(/"/g, '&quot;').replace(/'/g, '&#39;');
    return `
        <div style="min-width: 200px; max-width: 260px; cursor: pointer;" onclick="showPharmacyDetail(${pharmacyData})">
            <div style="padding: 10px;">
                <h4 style="font-weight: 600; color: #1f2937; font-size: 13px; margin: 0 0 6px 0;">${pharmacy.nom}</h4>
                <p style="font-size: 11px; color: #6b7280; margin: 0 0 6px 0;">${pharmacy.quartier || ''}, ${pharmacy.ville}</p>
                ${pharmacy.telephone ? `<p style="font-size: 12px; color: #059669; margin: 0 0 6px 0; font-weight: 500;">${pharmacy.telephone}</p>` : ''}
                <div style="display: flex; gap: 4px; flex-wrap: wrap;">
                    ${pharmacy.is_garde ? '<span style="display: inline-flex; align-items: center; gap: 3px; padding: 2px 6px; background: #fef2f2; color: #b91c1c; font-size: 10px; border-radius: 12px; font-weight: 500;"><span style="width: 5px; height: 5px; background: #ef4444; border-radius: 50%;"></span>Garde</span>' : ''}
                    <span style="padding: 2px 6px; background: #ecfdf5; color: #047857; font-size: 10px; border-radius: 12px; font-weight: 500;">${pharmacy.ville}</span>
                </div>
                <p style="font-size: 10px; color: #9ca3af; margin: 8px 0 0 0; text-align: center;">Toucher pour voir les détails</p>
            </div>
        </div>
    `;
}

function locateNearestGardePharmacy() {
    const btn = document.getElementById('gpsLocateBtn');
    const originalIcon = '<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z"/><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z"/></svg>';
    btn.innerHTML = '<svg class="w-5 h-5 animate-spin" fill="none" stroke="currentColor" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg>';
    
    if (!navigator.geolocation) {
        alert('La géolocalisation n\'est pas supportée par votre navigateur');
        btn.innerHTML = originalIcon;
        return;
    }
    
    navigator.geolocation.getCurrentPosition(
        (position) => {
            const userLat = position.coords.latitude;
            const userLng = position.coords.longitude;
            
            let nearestCity = '';
            let minDistance = Infinity;
            
            for (const [city, coords] of Object.entries(CITY_CENTERS)) {
                const distance = Math.sqrt(Math.pow(coords[0] - userLat, 2) + Math.pow(coords[1] - userLng, 2));
                if (distance < minDistance) {
                    minDistance = distance;
                    nearestCity = city;
                }
            }
            
            if (currentTab === 'garde') {
                currentCity = nearestCity;
                document.querySelectorAll('.city-filter').forEach(btn => {
                    if (btn.dataset.city === nearestCity) {
                        btn.classList.add('bg-white', 'text-primary-700');
                        btn.classList.remove('bg-white/10', 'text-white');
                    } else {
                        btn.classList.remove('bg-white', 'text-primary-700');
                        btn.classList.add('bg-white/10', 'text-white');
                    }
                });
                fetchPharmacies(true);
                btn.innerHTML = originalIcon;
            } else {
                const gardeInCity = pharmacies.filter(p => p.is_garde && p.ville === nearestCity && p.lat !== null && p.lng !== null);
                
                if (gardeInCity.length === 0) {
                    const allGarde = pharmacies.filter(p => p.is_garde && p.lat !== null && p.lng !== null);
                    if (allGarde.length === 0) {
                        alert('Aucune pharmacie de garde trouvée');
                        btn.innerHTML = originalIcon;
                        return;
                    }
                    showNearestPharmaciesOnMap(userLat, userLng, allGarde, 'Garde les plus proches');
                } else {
                    showNearestPharmaciesOnMap(userLat, userLng, gardeInCity, `Garde à ${nearestCity}`);
                }
                btn.innerHTML = originalIcon;
            }
        },
        (error) => {
            let message = 'Impossible d\'obtenir votre position';
            switch(error.code) {
                case error.PERMISSION_DENIED:
                    message = 'Vous avez refusé l\'accès à votre position';
                    break;
                case error.POSITION_UNAVAILABLE:
                    message = 'Position indisponible';
                    break;
                case error.TIMEOUT:
                    message = 'Délai d\'attente dépassé';
                    break;
            }
            alert(message);
            btn.innerHTML = originalIcon;
        },
        { enableHighAccuracy: true, timeout: 10000 }
    );
}

function showNearestPharmaciesOnMap(userLat, userLng, pharmacyList, title) {
    // Switch to map tab
    switchTab('map');
    
    setTimeout(() => {
        if (!map) initMap();
        clearMarkers();
        
        // Add user marker
        const userMarker = L.marker([userLat, userLng], {
            icon: L.divIcon({
                className: 'user-marker',
                html: `<div style="
                    background-color: #3b82f6;
                    width: 24px;
                    height: 24px;
                    border-radius: 50%;
                    border: 4px solid white;
                    box-shadow: 0 2px 10px rgba(59, 130, 246, 0.5);
                "></div>`,
                iconSize: [24, 24],
                iconAnchor: [12, 12]
            })
        }).addTo(map).bindPopup('<b>Votre position</b>');
        markers.push(userMarker);
        
        // Sort by distance and show pharmacies
        const sortedPharmacies = pharmacyList.map(p => ({
            ...p,
            distance: Math.sqrt(Math.pow(p.lat - userLat, 2) + Math.pow(p.lng - userLng, 2))
        })).sort((a, b) => a.distance - b.distance);
        
        sortedPharmacies.forEach((pharmacy, index) => {
            const color = '#ef4444'; // Red for garde
            const icon = createMarkerIcon(color);
            
            const marker = L.marker([pharmacy.lat, pharmacy.lng], { icon })
                .addTo(map);
            
            marker.on('click', function() {
                showPharmacyDetail(pharmacy);
            });
            
            markers.push(marker);
            
            if (index === 0) {
                showPharmacyDetail(pharmacy);
            }
        });
        
        // Fit bounds to show user and pharmacies
        const allPoints = [[userLat, userLng], ...sortedPharmacies.map(p => [p.lat, p.lng])];
        const bounds = L.latLngBounds(allPoints);
        map.fitBounds(bounds, { padding: [50, 50] });
        
    }, 200);
}

const TYPE_COLORS = {
    'pharmacie_generale': { border: 'border-l-emerald-500', bg: 'bg-emerald-100', text: 'text-emerald-700', label: 'Pharmacie générale' },
    'depot_pharmaceutique': { border: 'border-l-orange-500', bg: 'bg-orange-100', text: 'text-orange-700', label: 'Dépôt pharmaceutique' },
    'pharmacie_hospitaliere': { border: 'border-l-purple-500', bg: 'bg-purple-100', text: 'text-purple-700', label: 'Pharmacie hospitalière' }
};

const CATEGORY_LABELS = {
    'standard': 'Standard',
    'gare': 'Gare',
    'hopital': 'Hôpital',
    'aeroport': 'Aéroport',
    'centre_commercial': 'Centre commercial',
    'marche': 'Marché',
    'centre_ville': 'Centre-ville',
    'zone_residentielle': 'Zone résidentielle'
};

function normalizeTypeEtablissement(typeStr) {
    if (!typeStr) return 'pharmacie_generale';
    const lower = typeStr.toLowerCase();
    if (lower.includes('dépôt') || lower.includes('depot')) return 'depot_pharmaceutique';
    if (lower.includes('hospitalière') || lower.includes('hospitaliere')) return 'pharmacie_hospitaliere';
    return 'pharmacie_generale';
}

function getTypeStyle(pharmacy) {
    const normalizedType = normalizeTypeEtablissement(pharmacy.type_etablissement);
    return TYPE_COLORS[normalizedType] || TYPE_COLORS['pharmacie_generale'];
}

function getTypeBadge(pharmacy) {
    const typeStyle = getTypeStyle(pharmacy);
    return `<span class="flex-shrink-0 px-2 py-1 ${typeStyle.bg} ${typeStyle.text} text-xs font-medium rounded-full">
        ${typeStyle.label}
    </span>`;
}

function getGardeBadge(pharmacy) {
    if (pharmacy.is_garde) {
        return `<span class="flex-shrink-0 px-2 py-1 bg-red-100 text-red-700 text-xs font-medium rounded-full flex items-center gap-1">
            <span class="w-2 h-2 bg-red-500 rounded-full animate-pulse"></span>
            Garde
        </span>`;
    }
    return '';
}

function getCategoryBadge(pharmacy) {
    const category = pharmacy.categorie_emplacement || 'standard';
    const label = CATEGORY_LABELS[category] || 'Standard';
    return `<span class="flex-shrink-0 px-2 py-1 bg-indigo-100 text-indigo-700 text-xs font-medium rounded-full">
        ${label}
    </span>`;
}

function createPharmacyCard(pharmacy) {
    const cityBadgeClass = getCityBadgeClass(pharmacy.ville);
    const typeStyle = getTypeStyle(pharmacy);
    const borderColor = pharmacy.is_garde ? 'border-l-red-500' : typeStyle.border;
    
    return `
        <div class="pharmacy-card bg-white rounded-xl p-4 shadow-sm border-l-4 ${borderColor} border border-gray-100 active:scale-[0.98] transition cursor-pointer hover:shadow-md"
             onclick="showPharmacyDetail(${JSON.stringify(pharmacy).replace(/"/g, '&quot;')})">
            <div class="flex items-start justify-between">
                <div class="flex-1 min-w-0">
                    <h3 class="font-semibold text-gray-800 truncate">${pharmacy.nom}</h3>
                    <p class="text-sm text-gray-500 mt-0.5">${pharmacy.quartier || ''}</p>
                    ${pharmacy.telephone ? `
                        <div class="flex items-center gap-1.5 mt-1">
                            <span class="inline-flex items-center gap-1.5 px-2.5 py-1 bg-emerald-50 text-emerald-700 text-sm font-medium rounded-full">
                                <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z"/>
                                </svg>
                                ${pharmacy.telephone}
                            </span>
                        </div>
                    ` : ''}
                </div>
            </div>
            <div class="flex flex-wrap gap-1.5 mt-3">
                ${getGardeBadge(pharmacy)}
                ${getTypeBadge(pharmacy)}
                ${getCategoryBadge(pharmacy)}
                <span class="flex-shrink-0 px-2 py-1 ${cityBadgeClass} text-xs font-medium rounded-full">
                    ${pharmacy.ville}
                </span>
                ${pharmacy.is_verified ? `
                    <span class="flex-shrink-0 px-2 py-1 bg-blue-100 text-blue-700 text-xs font-medium rounded-full flex items-center gap-1">
                        <svg class="w-3 h-3" fill="currentColor" viewBox="0 0 24 24">
                            <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/>
                        </svg>
                        Vérifié
                    </span>
                ` : `
                    <span class="flex-shrink-0 px-2 py-1 bg-gray-100 text-gray-500 text-xs font-medium rounded-full flex items-center gap-1">
                        <svg class="w-3 h-3" fill="currentColor" viewBox="0 0 24 24">
                            <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-2h2v2zm0-4h-2V7h2v6z"/>
                        </svg>
                        Non vérifié
                    </span>
                `}
            </div>
        </div>
    `;
}

function locatePharmacy(pharmacyId, lat, lng) {
    if (!navigator.geolocation) {
        alert('La géolocalisation n\'est pas supportée par votre navigateur');
        return;
    }
    
    navigator.geolocation.getCurrentPosition(
        (position) => {
            const userLat = position.coords.latitude;
            const userLng = position.coords.longitude;
            
            if (lat !== null && lat !== undefined && lng !== null && lng !== undefined) {
                switchTab('map');
                setTimeout(() => {
                    if (map) {
                        const bounds = L.latLngBounds([[userLat, userLng], [lat, lng]]);
                        map.fitBounds(bounds, { padding: [50, 50] });
                        
                        L.marker([userLat, userLng], {
                            icon: L.divIcon({
                                className: 'user-marker',
                                html: `<div style="
                                    background-color: #3b82f6;
                                    width: 20px;
                                    height: 20px;
                                    border-radius: 50%;
                                    border: 3px solid white;
                                    box-shadow: 0 2px 8px rgba(0,0,0,0.3);
                                "></div>`,
                                iconSize: [20, 20],
                                iconAnchor: [10, 10]
                            })
                        }).addTo(map).bindPopup('Votre position').openPopup();
                    }
                }, 200);
            } else {
                alert('Les coordonnées de cette pharmacie ne sont pas disponibles');
            }
        },
        (error) => {
            let message = 'Impossible d\'obtenir votre position';
            switch(error.code) {
                case error.PERMISSION_DENIED:
                    message = 'Vous avez refusé l\'accès à votre position';
                    break;
                case error.POSITION_UNAVAILABLE:
                    message = 'Position indisponible';
                    break;
                case error.TIMEOUT:
                    message = 'Délai d\'attente dépassé';
                    break;
            }
            alert(message);
        }
    );
}

function showPharmacyDetail(pharmacy) {
    const modal = document.getElementById('pharmacyModal');
    const title = document.getElementById('modalTitle');
    const content = document.getElementById('modalContent');
    
    title.textContent = pharmacy.nom;
    const cityBadgeClass = getCityBadgeClass(pharmacy.ville);
    
    content.innerHTML = `
        <div class="space-y-4">
            <div class="flex flex-wrap gap-2">
                <span class="px-3 py-1 ${cityBadgeClass} text-sm font-medium rounded-full">
                    ${pharmacy.ville}
                </span>
                ${pharmacy.is_garde ? `
                    <span class="px-3 py-1 bg-red-100 text-red-700 text-sm font-medium rounded-full">
                        Garde
                    </span>
                ` : ''}
                ${pharmacy.is_verified ? `
                    <span class="px-3 py-1 bg-blue-100 text-blue-700 text-sm font-medium rounded-full flex items-center gap-1">
                        <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 24 24">
                            <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/>
                        </svg>
                        Établissement vérifié
                    </span>
                ` : `
                    <span class="px-3 py-1 bg-gray-100 text-gray-500 text-sm font-medium rounded-full flex items-center gap-1">
                        <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 24 24">
                            <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-2h2v2zm0-4h-2V7h2v6z"/>
                        </svg>
                        Non vérifié
                    </span>
                `}
            </div>
            
            ${pharmacy.is_garde ? `
                <div class="flex items-center gap-2 p-3 bg-red-50 rounded-xl">
                    <div class="w-3 h-3 bg-red-500 rounded-full animate-pulse"></div>
                    <span class="text-sm font-medium text-red-700">Pharmacie de garde</span>
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
            
            <div class="flex flex-col gap-2 mt-4">
                ${pharmacy.telephone ? `
                    <a href="tel:${pharmacy.telephone.split('/')[0].trim()}" 
                       class="w-full py-3 bg-emerald-600 text-white font-semibold rounded-xl flex items-center justify-center gap-2 hover:bg-emerald-700 transition">
                        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z"/>
                        </svg>
                        Appeler
                    </a>
                ` : ''}
                
                <button onclick="closeModal(); locatePharmacy(${pharmacy.id}, ${pharmacy.lat}, ${pharmacy.lng})"
                   class="w-full py-3 bg-blue-600 text-white font-semibold rounded-xl flex items-center justify-center gap-2 hover:bg-blue-700 transition">
                    <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z"/>
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z"/>
                    </svg>
                    Localiser
                </button>
                
                ${pharmacy.location_validated && pharmacy.lat !== null && pharmacy.lat !== undefined && pharmacy.lng !== null && pharmacy.lng !== undefined ? `
                    <a href="https://www.google.com/maps/dir/?api=1&destination=${pharmacy.lat},${pharmacy.lng}" 
                       target="_blank"
                       class="w-full py-3 bg-purple-600 text-white font-semibold rounded-xl flex items-center justify-center gap-2 hover:bg-purple-700 transition">
                        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 20l-5.447-2.724A1 1 0 013 16.382V5.618a1 1 0 011.447-.894L9 7m0 13l6-3m-6 3V7m6 10l4.553 2.276A1 1 0 0021 18.382V7.618a1 1 0 00-.553-.894L15 4m0 13V4m0 0L9 7"/>
                        </svg>
                        Se rendre
                    </a>
                ` : `
                    <button disabled
                       class="w-full py-3 bg-gray-300 text-gray-500 font-semibold rounded-xl flex items-center justify-center gap-2 cursor-not-allowed">
                        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 20l-5.447-2.724A1 1 0 013 16.382V5.618a1 1 0 011.447-.894L9 7m0 13l6-3m-6 3V7m6 10l4.553 2.276A1 1 0 0021 18.382V7.618a1 1 0 00-.553-.894L15 4m0 13V4m0 0L9 7"/>
                        </svg>
                        Se rendre (non validée)
                    </button>
                `}
                
                <button onclick="showComplementInfo(${pharmacy.id})"
                   class="w-full py-3 bg-amber-500 text-white font-semibold rounded-xl flex items-center justify-center gap-2 hover:bg-amber-600 transition">
                    <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"/>
                    </svg>
                    Compléter Info
                </button>
            </div>
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

function showComplementInfo(pharmacyId) {
    const modal = document.getElementById('pharmacyModal');
    const title = document.getElementById('modalTitle');
    const content = document.getElementById('modalContent');
    
    title.textContent = 'Compléter les informations';
    
    content.innerHTML = `
        <div class="space-y-4">
            <p class="text-sm text-gray-600">Choisissez le type d'information à soumettre :</p>
            
            <button onclick="showLocationForm(${pharmacyId})"
               class="w-full py-4 bg-blue-50 hover:bg-blue-100 border border-blue-200 rounded-xl flex items-center gap-3 transition">
                <div class="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center ml-3">
                    <svg class="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z"/>
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z"/>
                    </svg>
                </div>
                <div class="text-left">
                    <p class="font-semibold text-gray-800">Proposer une localisation GPS</p>
                    <p class="text-sm text-gray-500">Envoyer les coordonnées de la pharmacie</p>
                </div>
            </button>
            
            <button onclick="showInfoForm(${pharmacyId})"
               class="w-full py-4 bg-amber-50 hover:bg-amber-100 border border-amber-200 rounded-xl flex items-center gap-3 transition">
                <div class="w-12 h-12 bg-amber-100 rounded-lg flex items-center justify-center ml-3">
                    <svg class="w-6 h-6 text-amber-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"/>
                    </svg>
                </div>
                <div class="text-left">
                    <p class="font-semibold text-gray-800">Corriger une information</p>
                    <p class="text-sm text-gray-500">Téléphone, horaires, services, etc.</p>
                </div>
            </button>
            
            <button onclick="closeModal()"
               class="w-full py-3 bg-gray-200 text-gray-700 font-semibold rounded-xl flex items-center justify-center gap-2 hover:bg-gray-300 transition mt-4">
                Annuler
            </button>
        </div>
    `;
    
    modal.classList.remove('hidden');
    modal.classList.add('flex');
}

function showLocationForm(pharmacyId) {
    const content = document.getElementById('modalContent');
    const title = document.getElementById('modalTitle');
    
    title.textContent = 'Proposer une localisation';
    
    content.innerHTML = `
        <div class="space-y-4">
            <div class="p-4 bg-blue-50 rounded-xl border border-blue-200">
                <p class="text-sm text-blue-700">
                    Rendez-vous devant la pharmacie et cliquez sur "Utiliser ma position actuelle" pour envoyer les coordonnées GPS.
                </p>
            </div>
            
            <form id="locationForm" class="space-y-4">
                <div class="grid grid-cols-2 gap-3">
                    <div>
                        <label class="block text-sm font-medium text-gray-700 mb-1">Latitude</label>
                        <input type="text" id="submitLat" readonly class="w-full px-3 py-2 border border-gray-300 rounded-lg bg-gray-50 text-gray-600" placeholder="--">
                    </div>
                    <div>
                        <label class="block text-sm font-medium text-gray-700 mb-1">Longitude</label>
                        <input type="text" id="submitLng" readonly class="w-full px-3 py-2 border border-gray-300 rounded-lg bg-gray-50 text-gray-600" placeholder="--">
                    </div>
                </div>
                
                <button type="button" onclick="getCurrentLocation()"
                   class="w-full py-3 bg-blue-600 text-white font-semibold rounded-xl flex items-center justify-center gap-2 hover:bg-blue-700 transition">
                    <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z"/>
                    </svg>
                    Utiliser ma position actuelle
                </button>
                
                <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1">Votre nom (optionnel)</label>
                    <input type="text" id="submitName" class="w-full px-3 py-2 border border-gray-300 rounded-lg" placeholder="Votre nom">
                </div>
                
                <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1">Votre téléphone (optionnel)</label>
                    <input type="tel" id="submitPhone" class="w-full px-3 py-2 border border-gray-300 rounded-lg" placeholder="Ex: 077 00 00 00">
                </div>
                
                <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1">Commentaire (optionnel)</label>
                    <textarea id="submitComment" rows="2" class="w-full px-3 py-2 border border-gray-300 rounded-lg" placeholder="Informations supplémentaires..."></textarea>
                </div>
                
                <div class="flex gap-3">
                    <button type="button" onclick="showComplementInfo(${pharmacyId})"
                       class="flex-1 py-3 bg-gray-200 text-gray-700 font-semibold rounded-xl hover:bg-gray-300 transition">
                        Retour
                    </button>
                    <button type="button" onclick="submitLocation(${pharmacyId})"
                       class="flex-1 py-3 bg-emerald-600 text-white font-semibold rounded-xl hover:bg-emerald-700 transition">
                        Envoyer
                    </button>
                </div>
            </form>
        </div>
    `;
}

function showInfoForm(pharmacyId) {
    const content = document.getElementById('modalContent');
    const title = document.getElementById('modalTitle');
    
    title.textContent = 'Corriger une information';
    
    content.innerHTML = `
        <div class="space-y-4">
            <form id="infoForm" class="space-y-4">
                <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1">Type d'information à corriger</label>
                    <select id="fieldName" class="w-full px-3 py-2 border border-gray-300 rounded-lg">
                        <option value="">Sélectionnez...</option>
                        <option value="telephone">Téléphone</option>
                        <option value="horaires">Horaires d'ouverture</option>
                        <option value="quartier">Quartier / Adresse</option>
                        <option value="services">Services proposés</option>
                        <option value="proprietaire">Propriétaire</option>
                    </select>
                </div>
                
                <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1">Nouvelle valeur</label>
                    <textarea id="proposedValue" rows="3" class="w-full px-3 py-2 border border-gray-300 rounded-lg" placeholder="Entrez la valeur correcte..."></textarea>
                </div>
                
                <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1">Votre nom (optionnel)</label>
                    <input type="text" id="infoSubmitName" class="w-full px-3 py-2 border border-gray-300 rounded-lg" placeholder="Votre nom">
                </div>
                
                <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1">Votre téléphone (optionnel)</label>
                    <input type="tel" id="infoSubmitPhone" class="w-full px-3 py-2 border border-gray-300 rounded-lg" placeholder="Ex: 077 00 00 00">
                </div>
                
                <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1">Commentaire (optionnel)</label>
                    <textarea id="infoSubmitComment" rows="2" class="w-full px-3 py-2 border border-gray-300 rounded-lg" placeholder="Précisions supplémentaires..."></textarea>
                </div>
                
                <div class="flex gap-3">
                    <button type="button" onclick="showComplementInfo(${pharmacyId})"
                       class="flex-1 py-3 bg-gray-200 text-gray-700 font-semibold rounded-xl hover:bg-gray-300 transition">
                        Retour
                    </button>
                    <button type="button" onclick="submitInfo(${pharmacyId})"
                       class="flex-1 py-3 bg-emerald-600 text-white font-semibold rounded-xl hover:bg-emerald-700 transition">
                        Envoyer
                    </button>
                </div>
            </form>
        </div>
    `;
}

function getCurrentLocation() {
    if (!navigator.geolocation) {
        alert('La géolocalisation n\'est pas supportée par votre navigateur');
        return;
    }
    
    const latInput = document.getElementById('submitLat');
    const lngInput = document.getElementById('submitLng');
    
    latInput.value = 'Chargement...';
    lngInput.value = 'Chargement...';
    
    navigator.geolocation.getCurrentPosition(
        (position) => {
            latInput.value = position.coords.latitude.toFixed(6);
            lngInput.value = position.coords.longitude.toFixed(6);
        },
        (error) => {
            latInput.value = '--';
            lngInput.value = '--';
            let message = 'Impossible d\'obtenir votre position';
            switch(error.code) {
                case error.PERMISSION_DENIED:
                    message = 'Vous avez refusé l\'accès à votre position';
                    break;
                case error.POSITION_UNAVAILABLE:
                    message = 'Position indisponible';
                    break;
                case error.TIMEOUT:
                    message = 'Délai d\'attente dépassé';
                    break;
            }
            alert(message);
        }
    );
}

async function submitLocation(pharmacyId) {
    const lat = document.getElementById('submitLat').value;
    const lng = document.getElementById('submitLng').value;
    
    if (!lat || !lng || lat === '--' || lng === '--' || lat === 'Chargement...') {
        alert('Veuillez d\'abord obtenir votre position GPS');
        return;
    }
    
    const data = {
        latitude: parseFloat(lat),
        longitude: parseFloat(lng),
        name: document.getElementById('submitName').value,
        phone: document.getElementById('submitPhone').value,
        comment: document.getElementById('submitComment').value
    };
    
    try {
        const response = await fetch(`/api/pharmacy/${pharmacyId}/submit-location`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        
        const result = await response.json();
        
        if (result.success) {
            showSuccessMessage('Localisation envoyée ! Elle sera vérifiée par notre équipe.');
        } else {
            alert(result.error || 'Erreur lors de l\'envoi');
        }
    } catch (error) {
        console.error('Error:', error);
        alert('Erreur lors de l\'envoi. Veuillez réessayer.');
    }
}

async function submitInfo(pharmacyId) {
    const fieldName = document.getElementById('fieldName').value;
    const proposedValue = document.getElementById('proposedValue').value;
    
    if (!fieldName) {
        alert('Veuillez sélectionner le type d\'information');
        return;
    }
    
    if (!proposedValue.trim()) {
        alert('Veuillez entrer la nouvelle valeur');
        return;
    }
    
    const data = {
        field_name: fieldName,
        proposed_value: proposedValue,
        name: document.getElementById('infoSubmitName').value,
        phone: document.getElementById('infoSubmitPhone').value,
        comment: document.getElementById('infoSubmitComment').value
    };
    
    try {
        const response = await fetch(`/api/pharmacy/${pharmacyId}/submit-info`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        
        const result = await response.json();
        
        if (result.success) {
            showSuccessMessage('Information envoyée ! Elle sera vérifiée par notre équipe.');
        } else {
            alert(result.error || 'Erreur lors de l\'envoi');
        }
    } catch (error) {
        console.error('Error:', error);
        alert('Erreur lors de l\'envoi. Veuillez réessayer.');
    }
}

function showSuccessMessage(message) {
    const content = document.getElementById('modalContent');
    const title = document.getElementById('modalTitle');
    
    title.textContent = 'Merci !';
    
    content.innerHTML = `
        <div class="space-y-4 text-center">
            <div class="w-20 h-20 bg-emerald-100 rounded-full flex items-center justify-center mx-auto">
                <svg class="w-10 h-10 text-emerald-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/>
                </svg>
            </div>
            <p class="text-gray-700">${message}</p>
            <button onclick="closeModal()"
               class="w-full py-3 bg-emerald-600 text-white font-semibold rounded-xl hover:bg-emerald-700 transition">
                Fermer
            </button>
        </div>
    `;
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
    
    const searchSection = document.getElementById('searchSection');
    if (searchSection) {
        if (tab === 'pharmacies') {
            searchSection.style.display = 'block';
        } else {
            searchSection.style.display = 'none';
        }
    }
    
    const gpsBtn = document.getElementById('gpsLocateBtn');
    if (gpsBtn) {
        if (tab === 'garde' || tab === 'map') {
            gpsBtn.classList.remove('hidden');
            gpsBtn.classList.add('flex');
        } else {
            gpsBtn.classList.add('hidden');
            gpsBtn.classList.remove('flex');
        }
    }
    
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

function resetSuggestionForm() {
    document.getElementById('suggestionForm').reset();
    document.getElementById('suggestionForm').classList.remove('hidden');
    document.getElementById('suggestionSuccess').classList.add('hidden');
    updateSuggestionForm();
}

function updateSuggestionForm() {
    const category = document.getElementById('suggestionCategory').value;
    const standardFields = document.getElementById('standardFields');
    const pharmacyFields = document.getElementById('pharmacyFields');
    const submitBtnText = document.getElementById('submitBtnText');
    
    if (category === 'pharmacie') {
        standardFields.classList.add('hidden');
        pharmacyFields.classList.remove('hidden');
        if (submitBtnText) submitBtnText.textContent = 'Proposer cette pharmacie';
    } else {
        standardFields.classList.remove('hidden');
        pharmacyFields.classList.add('hidden');
        if (submitBtnText) submitBtnText.textContent = 'Envoyer ma suggestion';
    }
}

async function submitSuggestion(e) {
    e.preventDefault();
    
    const category = document.getElementById('suggestionCategory').value;
    const name = document.getElementById('suggestionName').value;
    const phone = document.getElementById('suggestionPhone').value;
    const email = document.getElementById('suggestionEmail').value;
    
    if (!category) {
        alert('Veuillez sélectionner une catégorie');
        return;
    }
    
    try {
        let response;
        
        if (category === 'pharmacie') {
            const nom = document.getElementById('pharmacyNom').value;
            const ville = document.getElementById('pharmacyVille').value;
            
            if (!nom || !ville) {
                alert('Le nom et la ville sont obligatoires');
                return;
            }
            
            const latValue = document.getElementById('pharmacyLat').value;
            const lngValue = document.getElementById('pharmacyLng').value;
            
            const data = {
                nom,
                ville,
                quartier: document.getElementById('pharmacyQuartier').value,
                telephone: document.getElementById('pharmacyTelephone').value,
                bp: document.getElementById('pharmacyBP').value,
                horaires: document.getElementById('pharmacyHoraires').value,
                services: document.getElementById('pharmacyServices').value,
                proprietaire: document.getElementById('pharmacyProprietaire').value,
                type_etablissement: document.getElementById('pharmacyType').value,
                categorie: document.getElementById('pharmacyCategorie').value,
                is_garde: document.getElementById('pharmacyIsGarde').checked,
                comment: document.getElementById('pharmacyComment').value,
                latitude: latValue ? parseFloat(latValue) : null,
                longitude: lngValue ? parseFloat(lngValue) : null,
                name,
                phone,
                email
            };
            
            response = await fetch('/api/pharmacy-proposal', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            });
        } else {
            const subject = document.getElementById('suggestionSubject').value;
            const message = document.getElementById('suggestionMessage').value;
            
            if (!subject || !message) {
                alert('Veuillez remplir tous les champs obligatoires');
                return;
            }
            
            response = await fetch('/api/suggestions', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ category, subject, message, name, phone, email })
            });
        }
        
        const result = await response.json();
        
        if (result.success) {
            document.getElementById('suggestionForm').classList.add('hidden');
            document.getElementById('suggestionSuccess').classList.remove('hidden');
        } else {
            alert(result.error || 'Une erreur est survenue');
        }
    } catch (error) {
        console.error('Error submitting suggestion:', error);
        alert('Erreur de connexion. Veuillez réessayer.');
    }
}

function getPharmacyLocation() {
    const btn = document.getElementById('getLocationBtn');
    const btnText = document.getElementById('getLocationBtnText');
    const latInput = document.getElementById('pharmacyLat');
    const lngInput = document.getElementById('pharmacyLng');
    const statusEl = document.getElementById('locationStatus');
    
    if (!navigator.geolocation) {
        alert('La géolocalisation n\'est pas supportée par votre navigateur');
        return;
    }
    
    btn.disabled = true;
    btnText.textContent = 'Récupération en cours...';
    btn.classList.add('opacity-75');
    
    navigator.geolocation.getCurrentPosition(
        (position) => {
            const lat = position.coords.latitude;
            const lng = position.coords.longitude;
            
            latInput.value = lat.toFixed(6);
            lngInput.value = lng.toFixed(6);
            
            statusEl.textContent = 'Position récupérée avec succès !';
            statusEl.classList.remove('hidden', 'text-red-600');
            statusEl.classList.add('text-green-600');
            
            btn.disabled = false;
            btnText.textContent = 'Récupérer ma position actuelle';
            btn.classList.remove('opacity-75');
        },
        (error) => {
            let message = 'Impossible d\'obtenir votre position';
            switch(error.code) {
                case error.PERMISSION_DENIED:
                    message = 'Vous avez refusé l\'accès à votre position. Saisissez les coordonnées manuellement.';
                    break;
                case error.POSITION_UNAVAILABLE:
                    message = 'Position indisponible. Saisissez les coordonnées manuellement.';
                    break;
                case error.TIMEOUT:
                    message = 'Délai d\'attente dépassé. Réessayez ou saisissez manuellement.';
                    break;
            }
            
            statusEl.textContent = message;
            statusEl.classList.remove('hidden', 'text-green-600');
            statusEl.classList.add('text-red-600');
            
            btn.disabled = false;
            btnText.textContent = 'Réessayer';
            btn.classList.remove('opacity-75');
        },
        { enableHighAccuracy: true, timeout: 15000 }
    );
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
    
    const suggestionForm = document.getElementById('suggestionForm');
    if (suggestionForm) {
        suggestionForm.addEventListener('submit', submitSuggestion);
    }
});
