// Common School Archive Map
// Displays NYSTA meeting locations and district consolidation counties

// Initialize map centered on New York State
let archiveMap = L.map("map");

L.tileLayer('https://{s}.tile.openstreetmap.fr/hot/{z}/{x}/{y}.png', {
    maxZoom: 18,
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
}).addTo(archiveMap);

// Center on NYS
archiveMap.setView([42.9, -75.5], 7);

// NYSTA Meeting Locations GeoJSON (inline for simplicity)
const nystaMeetings = {
    "type": "FeatureCollection",
    "features": [
        {"type": "Feature", "properties": {"name": "Albany", "type": "administrative", "years": ["1927"], "description": "Publisher location, statewide administration"}, "geometry": {"type": "Point", "coordinates": [-73.7562, 42.6526]}},
        {"type": "Feature", "properties": {"name": "Brooklyn", "type": "meeting", "years": ["1889"], "description": "Annual meeting"}, "geometry": {"type": "Point", "coordinates": [-73.9442, 40.6782]}},
        {"type": "Feature", "properties": {"name": "Buffalo", "type": "meeting", "years": ["1901"], "description": "Annual meeting"}, "geometry": {"type": "Point", "coordinates": [-78.8784, 42.8864]}},
        {"type": "Feature", "properties": {"name": "Cliff Haven", "type": "venue", "years": [], "description": "Summer school/retreat"}, "geometry": {"type": "Point", "coordinates": [-73.4279, 44.8789]}},
        {"type": "Feature", "properties": {"name": "Elizabethtown", "type": "meeting", "years": ["1887"], "description": "Essex County courthouse"}, "geometry": {"type": "Point", "coordinates": [-73.5907, 44.2156]}},
        {"type": "Feature", "properties": {"name": "Elmira", "type": "meeting", "years": ["1884"], "description": "Baldwin Street location"}, "geometry": {"type": "Point", "coordinates": [-76.8077, 42.0898]}},
        {"type": "Feature", "properties": {"name": "Fort Edward", "type": "venue", "years": [], "description": "Fort William Henry Hotel"}, "geometry": {"type": "Point", "coordinates": [-73.5882, 43.2670]}},
        {"type": "Feature", "properties": {"name": "New York City", "type": "meeting", "years": ["1896", "1897", "1911"], "description": "Annual meetings"}, "geometry": {"type": "Point", "coordinates": [-74.0060, 40.7128]}},
        {"type": "Feature", "properties": {"name": "Rochester", "type": "meeting", "years": ["1897", "1898"], "description": "Annual meetings"}, "geometry": {"type": "Point", "coordinates": [-77.6109, 43.1566]}},
        {"type": "Feature", "properties": {"name": "Saratoga Springs", "type": "meeting", "years": ["1881", "1890", "1891", "1894", "1902"], "description": "Annual meetings"}, "geometry": {"type": "Point", "coordinates": [-73.7854, 43.0831]}},
        {"type": "Feature", "properties": {"name": "Syracuse", "type": "meeting", "years": ["1895", "1905", "1906"], "description": "Annual meetings"}, "geometry": {"type": "Point", "coordinates": [-76.1474, 43.0481]}},
        {"type": "Feature", "properties": {"name": "Thousand Islands", "type": "meeting", "years": ["1900"], "description": "Summer meeting"}, "geometry": {"type": "Point", "coordinates": [-75.9180, 44.3500]}},
        {"type": "Feature", "properties": {"name": "Utica", "type": "meeting", "years": ["1927"], "description": "Event location"}, "geometry": {"type": "Point", "coordinates": [-75.2327, 43.1009]}},
        {"type": "Feature", "properties": {"name": "Watkins Glen", "type": "meeting", "years": ["1888"], "description": "Annual meeting"}, "geometry": {"type": "Point", "coordinates": [-76.8733, 42.3806]}},
        {"type": "Feature", "properties": {"name": "Yonkers", "type": "meeting", "years": ["1882"], "description": "Annual meeting"}, "geometry": {"type": "Point", "coordinates": [-73.8987, 40.9312]}}
    ]
};

// District Consolidation Counties GeoJSON
const consolidationCounties = {
    "type": "FeatureCollection",
    "features": [
        {"type": "Feature", "properties": {"name": "Broome County", "pages": 3, "region": "Southern Tier"}, "geometry": {"type": "Point", "coordinates": [-75.9180, 42.1605]}},
        {"type": "Feature", "properties": {"name": "Cattaraugus County", "pages": 5, "region": "Western NY"}, "geometry": {"type": "Point", "coordinates": [-78.6788, 42.2487]}},
        {"type": "Feature", "properties": {"name": "Cayuga County", "pages": 4, "region": "Finger Lakes"}, "geometry": {"type": "Point", "coordinates": [-76.5604, 42.9267]}},
        {"type": "Feature", "properties": {"name": "Chautauqua County", "pages": 5, "region": "Western NY"}, "geometry": {"type": "Point", "coordinates": [-79.4139, 42.2973]}},
        {"type": "Feature", "properties": {"name": "Chemung County", "pages": 3, "region": "Southern Tier"}, "geometry": {"type": "Point", "coordinates": [-76.7567, 42.1447]}},
        {"type": "Feature", "properties": {"name": "Chenango County", "pages": 6, "region": "Central NY"}, "geometry": {"type": "Point", "coordinates": [-75.6100, 42.4935]}},
        {"type": "Feature", "properties": {"name": "Clinton County", "pages": 5, "region": "North Country"}, "geometry": {"type": "Point", "coordinates": [-73.6778, 44.7489]}},
        {"type": "Feature", "properties": {"name": "Columbia County", "pages": 3, "region": "Hudson Valley"}, "geometry": {"type": "Point", "coordinates": [-73.6312, 42.2501]}},
        {"type": "Feature", "properties": {"name": "Cortland County", "pages": 3, "region": "Central NY"}, "geometry": {"type": "Point", "coordinates": [-76.0644, 42.5962]}},
        {"type": "Feature", "properties": {"name": "Delaware County", "pages": 6, "region": "Catskills"}, "geometry": {"type": "Point", "coordinates": [-74.9163, 42.1979]}},
        {"type": "Feature", "properties": {"name": "Dutchess County", "pages": 4, "region": "Hudson Valley"}, "geometry": {"type": "Point", "coordinates": [-73.7478, 41.7650]}},
        {"type": "Feature", "properties": {"name": "Erie County", "pages": 4, "region": "Western NY"}, "geometry": {"type": "Point", "coordinates": [-78.7998, 42.7523]}},
        {"type": "Feature", "properties": {"name": "Essex County", "pages": 4, "region": "Adirondacks"}, "geometry": {"type": "Point", "coordinates": [-73.7715, 44.1165]}},
        {"type": "Feature", "properties": {"name": "Franklin County", "pages": 3, "region": "North Country"}, "geometry": {"type": "Point", "coordinates": [-74.3046, 44.5929]}},
        {"type": "Feature", "properties": {"name": "Fulton County", "pages": 3, "region": "Mohawk Valley"}, "geometry": {"type": "Point", "coordinates": [-74.4235, 43.1142]}},
        {"type": "Feature", "properties": {"name": "Genesee County", "pages": 1, "region": "Western NY"}, "geometry": {"type": "Point", "coordinates": [-78.1939, 43.0009]}},
        {"type": "Feature", "properties": {"name": "Greene County", "pages": 4, "region": "Catskills"}, "geometry": {"type": "Point", "coordinates": [-74.1274, 42.2792]}},
        {"type": "Feature", "properties": {"name": "Hamilton County", "pages": 2, "region": "Adirondacks"}, "geometry": {"type": "Point", "coordinates": [-74.4971, 43.6573]}},
        {"type": "Feature", "properties": {"name": "Herkimer County", "pages": 5, "region": "Mohawk Valley"}, "geometry": {"type": "Point", "coordinates": [-74.9621, 43.4195]}},
        {"type": "Feature", "properties": {"name": "Jefferson County", "pages": 5, "region": "North Country"}, "geometry": {"type": "Point", "coordinates": [-75.9801, 44.0015]}},
        {"type": "Feature", "properties": {"name": "Lewis County", "pages": 4, "region": "North Country"}, "geometry": {"type": "Point", "coordinates": [-75.4486, 43.7846]}},
        {"type": "Feature", "properties": {"name": "Livingston County", "pages": 4, "region": "Finger Lakes"}, "geometry": {"type": "Point", "coordinates": [-77.7658, 42.7278]}},
        {"type": "Feature", "properties": {"name": "Madison County", "pages": 6, "region": "Central NY"}, "geometry": {"type": "Point", "coordinates": [-75.6697, 42.9126]}},
        {"type": "Feature", "properties": {"name": "Monroe County", "pages": 3, "region": "Western NY"}, "geometry": {"type": "Point", "coordinates": [-77.6109, 43.1566]}},
        {"type": "Feature", "properties": {"name": "Montgomery County", "pages": 3, "region": "Mohawk Valley"}, "geometry": {"type": "Point", "coordinates": [-74.4396, 42.9028]}},
        {"type": "Feature", "properties": {"name": "Nassau County", "pages": 4, "region": "Long Island"}, "geometry": {"type": "Point", "coordinates": [-73.5594, 40.7408]}},
        {"type": "Feature", "properties": {"name": "Niagara County", "pages": 2, "region": "Western NY"}, "geometry": {"type": "Point", "coordinates": [-78.8314, 43.2205]}},
        {"type": "Feature", "properties": {"name": "Oneida County", "pages": 5, "region": "Mohawk Valley"}, "geometry": {"type": "Point", "coordinates": [-75.4346, 43.2412]}},
        {"type": "Feature", "properties": {"name": "Onondaga County", "pages": 5, "region": "Central NY"}, "geometry": {"type": "Point", "coordinates": [-76.1949, 43.0063]}}
    ]
};

// Custom icons
const nystaIcon = L.divIcon({
    className: 'custom-marker',
    html: '<div style="background:#e74c3c; width:12px; height:12px; border-radius:50%; border:2px solid white; box-shadow:0 0 4px rgba(0,0,0,0.4);"></div>',
    iconSize: [16, 16],
    iconAnchor: [8, 8]
});

const countyIcon = L.divIcon({
    className: 'custom-marker',
    html: '<div style="background:#3498db; width:14px; height:14px; border-radius:3px; border:2px solid white; box-shadow:0 0 4px rgba(0,0,0,0.4);"></div>',
    iconSize: [18, 18],
    iconAnchor: [9, 9]
});

// Layer groups
let nystaLayer = L.layerGroup();
let countyLayer = L.layerGroup();

// Add NYSTA markers
L.geoJSON(nystaMeetings, {
    pointToLayer: (feature, latlng) => L.marker(latlng, {icon: nystaIcon}),
    onEachFeature: (feature, layer) => {
        const p = feature.properties;
        const years = p.years.length > 0 ? p.years.join(', ') : 'Undated';
        layer.bindPopup(`
            <h3 style="margin:0 0 8px 0;">${p.name}</h3>
            <hr style="margin:8px 0;">
            <b>Type:</b> ${p.type}<br>
            <b>Years:</b> ${years}<br>
            <b>Notes:</b> ${p.description}<br><br>
            <a href="https://zmuhls.github.io/cs-archive/collections/nys-teachers-association/" target="_blank" style="color:#e74c3c; text-decoration:none; font-weight:bold;">📚 View NYSTA Collection →</a>
        `);
    }
}).addTo(nystaLayer);

// Add County markers
L.geoJSON(consolidationCounties, {
    pointToLayer: (feature, latlng) => L.marker(latlng, {icon: countyIcon}),
    onEachFeature: (feature, layer) => {
        const p = feature.properties;
        const countySlug = p.name.toLowerCase().replace(/\s+/g, '-');
        layer.bindPopup(`
            <h3 style="margin:0 0 8px 0;">${p.name}</h3>
            <hr style="margin:8px 0;">
            <b>Region:</b> ${p.region}<br>
            <b>Pages:</b> ${p.pages} consolidation record pages<br>
            <a href="https://zmuhls.github.io/cs-archive/collections/district-consolidation-by-county/#${countySlug}" target="_blank" style="color:#3498db; text-decoration:none; font-weight:bold;">📄 View Records →</a>
        `);
    }
}).addTo(countyLayer);

// Add layers to map
nystaLayer.addTo(archiveMap);
countyLayer.addTo(archiveMap);

// Layer control
const overlays = {
    "NYSTA Meetings": nystaLayer,
    "Consolidation Counties": countyLayer
};

L.control.layers(null, overlays, {collapsed: false}).addTo(archiveMap);

// Legend
const legend = L.control({position: 'bottomright'});
legend.onAdd = function(map) {
    const div = L.DomUtil.create('div', 'legend');
    div.innerHTML = `
        <div class="legend-title">Legend</div>
        <div><i style="background:#e74c3c;"></i> NYSTA Meeting</div>
        <div><i style="background:#3498db; border-radius:3px;"></i> County (Consolidation)</div>
    `;
    return div;
};
legend.addTo(archiveMap);

// Populate sidebar lists
nystaMeetings.features
    .sort((a, b) => a.properties.name.localeCompare(b.properties.name))
    .forEach(feature => {
        const p = feature.properties;
        const years = p.years.length > 0 ? ` (${p.years.join(', ')})` : '';
        $("#nysta-list").append(`<li data-lat="${feature.geometry.coordinates[1]}" data-lng="${feature.geometry.coordinates[0]}">${p.name}${years}</li>`);
    });

consolidationCounties.features
    .sort((a, b) => a.properties.name.localeCompare(b.properties.name))
    .forEach(feature => {
        const p = feature.properties;
        $("#county-list").append(`<li data-lat="${feature.geometry.coordinates[1]}" data-lng="${feature.geometry.coordinates[0]}">${p.name} — ${p.region}</li>`);
    });

// Click handlers for sidebar
$(".location-list").on("click", "li", function() {
    const lat = $(this).data("lat");
    const lng = $(this).data("lng");
    archiveMap.setView([lat, lng], 10);
});

// Tab switching
$(".tab").on("click", function() {
    $(".tab").removeClass("active");
    $(this).addClass("active");
    $(".tab-content").removeClass("active");
    $("#" + $(this).data("tab")).addClass("active");
});
