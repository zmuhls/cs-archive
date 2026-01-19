---
layout: single
title: Archive Map
description: Interactive map of NYSTA meetings and county consolidation records
permalink: /map/
---

<link rel="stylesheet" href="https://unpkg.com/leaflet@1.8.0/dist/leaflet.css" integrity="sha512-hoalWLoI8r4UszCkZ5kL8vayOGVae1oxXe/2A4AO6J9+580uKHDO3JdHb7NzwwzK5xr/Fs0W40kiNHxM9vyTtQ==" crossorigin=""/>
<script src="https://unpkg.com/leaflet@1.8.0/dist/leaflet.js" integrity="sha512-BB3hKbKWOc9Ez/TAwyWxNXeoV9c1v6FIeYiBieIWkpLjauysF18NzgR1MBNBXf8/KABdlkX68nAhlwcDFLGPCQ==" crossorigin=""></script>
<script src="https://code.jquery.com/jquery-3.2.1.min.js"></script>

Interactive map showing locations from two collections: **NYSTA annual meeting sites** (1881-1927) and **county consolidation records** from NYS Archives Series B0494.

<div id="map"></div>

---

## Locations

<div class="location-tabs">
  <button class="tab active" data-tab="nysta">NYSTA Meetings (1881-1927)</button>
  <button class="tab" data-tab="counties">Consolidation Counties</button>
</div>

<div id="nysta" class="tab-content active">

<p class="location-note"><strong>16 meeting locations</strong> from the <a href="{{ '/collections/nys-teachers-association/' | relative_url }}">NYS Teachers' Association collection</a>.</p>

<ul class="location-list" id="nysta-list"></ul>

</div>

<div id="counties" class="tab-content">

<p class="location-note"><strong>29 counties</strong> with school district consolidation records from <a href="{{ '/collections/administrative-data/' | relative_url }}">District Administrative Data</a>.</p>

<ul class="location-list" id="county-list"></ul>

</div>

<script src="{{ '/assets/maps/archive-map.js' | relative_url }}"></script>

<style>
#map {
  width: 100%;
  height: 70vh;
  min-height: 420px;
  max-height: 800px;
  display: block;
  position: relative;
  border-radius: 8px;
  border: 1px solid #e1e1e1;
  margin-bottom: 1.5rem;
}

.leaflet-container img { max-width: none !important; }

.location-tabs {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin-bottom: 1rem;
}

.tab {
  padding: 0.5rem 1rem;
  cursor: pointer;
  border: 1px solid #e1e1e1;
  background: #f8f8f8;
  color: #333;
  font-family: inherit;
  font-size: 0.875rem;
  border-radius: 8px;
  transition: all 0.2s;
}

.tab:hover {
  background: #333;
  color: white;
  border-color: #333;
}

.tab.active {
  background: #333;
  color: white;
  border-color: #333;
}

.tab-content {
  display: none;
}

.tab-content.active {
  display: block;
}

.location-list {
  list-style: none;
  padding: 0;
  margin: 1rem 0 0 0;
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 0.5rem;
}

.location-list li {
  padding: 0.5rem 0.75rem;
  cursor: pointer;
  border-radius: 8px;
  transition: all 0.2s;
  color: #333;
  background: #f8f8f8;
  border: 1px solid #e1e1e1;
  font-size: 0.9rem;
}

.location-list li:hover {
  background: #333;
  color: white;
  border-color: #333;
}

.legend {
  background: white;
  padding: 10px;
  border-radius: 8px;
  box-shadow: 0 2px 6px rgba(0,0,0,0.15);
  line-height: 1.6;
  color: #333;
  border: 1px solid #e1e1e1;
  font-size: 0.875rem;
}

.legend i {
  width: 14px;
  height: 14px;
  float: left;
  margin-right: 8px;
  border-radius: 50%;
}

.legend-title {
  font-weight: 600;
  margin-bottom: 6px;
}

/* Subtle note under tabs to avoid visual bleed */
.location-note {
  color: #555;
  margin: 0.25rem 0 0.5rem 0;
  font-size: 0.95rem;
}

@media (max-width: 767px) {
  #map {
    height: 55vh;
    min-height: 300px;
  }
  .location-list {
    grid-template-columns: 1fr;
  }
}
</style>
