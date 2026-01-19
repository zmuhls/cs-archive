---
layout: single
title: Archive Map
description: Interactive map of NYSTA meetings and county consolidation records
permalink: /map/
---

<link rel="stylesheet" href="https://unpkg.com/leaflet@1.8.0/dist/leaflet.css" integrity="sha512-hoalWLoI8r4UszCkZ5kL8vayOGVae1oxXe/2A4AO6J9+580uKHDO3JdHb7NzwwzK5xr/Fs0W40kiNHxM9vyTtQ==" crossorigin=""/>
<script src="https://unpkg.com/leaflet@1.8.0/dist/leaflet.js" integrity="sha512-BB3hKbKWOc9Ez/TAwyWxNXeoV9c1v6FIeYiBieIWkpLjauysF18NzgR1MBNBXf8/KABdlkX68nAhlwcDFLGPCQ==" crossorigin=""></script>
<script src="https://code.jquery.com/jquery-3.2.1.min.js"></script>

<div id="map"></div>

## Locations

<div class="tab-container">
  <button class="tab active" data-tab="nysta">NYSTA Meetings (1881-1927)</button>
  <button class="tab" data-tab="counties">District Consolidation Counties</button>
</div>

<div id="nysta" class="tab-content active">
  <p><strong>16 meeting locations</strong> from the NYS Teachers' Association collection (1845-1940s)</p>
  <ul class="location-list" id="nysta-list"></ul>
</div>

<div id="counties" class="tab-content">
  <p><strong>29 counties</strong> with school district consolidation records from NYS Archives Series A4456</p>
  <ul class="location-list" id="county-list"></ul>
</div>

<script src="{{ '/assets/maps/archive-map.js' | relative_url }}"></script>

<style>
/* Map Container */
#map {
  width: 100%;
  height: 500px;
  min-height: 400px;
  margin-bottom: 2rem;
  border-radius: 4px;
  border: 1px solid #e1e1e1;
}

/* Legend Styles */
.legend {
  background: white;
  padding: 12px;
  border-radius: 5px;
  box-shadow: 0 0 15px rgba(0,0,0,0.2);
  line-height: 1.8;
  color: #333;
}
.legend i {
  width: 18px;
  height: 18px;
  float: left;
  margin-right: 8px;
  opacity: 0.8;
  border-radius: 50%;
}
.legend-title {
  font-weight: bold;
  margin-bottom: 8px;
}

/* Tab Styles */
.tab-container {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin-bottom: 1rem;
}
.tab {
  padding: 0.5rem 1rem;
  cursor: pointer;
  border: 2px solid #333;
  background: white;
  color: #333;
  font-family: inherit;
  font-size: 0.9rem;
  border-radius: 4px;
  transition: all 0.2s;
}
.tab:hover {
  background: #f5f5f5;
}
.tab.active {
  background: #333;
  color: white;
}
.tab-content {
  display: none;
}
.tab-content.active {
  display: block;
}
.tab-content p {
  margin-bottom: 1rem;
  color: #666;
}

/* Location List Styles */
.location-list {
  list-style: none;
  padding: 0;
  margin: 0;
  columns: 2;
  column-gap: 2rem;
}
.location-list li {
  padding: 0.5rem 0.75rem;
  cursor: pointer;
  border-radius: 4px;
  transition: background-color 0.2s;
  break-inside: avoid;
}
.location-list li:hover {
  background: #f5f5f5;
}

/* Marker Legend Colors */
.nysta-marker {
  background: #e74c3c;
}
.county-marker {
  background: #3498db;
}

/* Responsive Layout */
@media (max-width: 767px) {
  #map {
    height: 350px;
  }
  .location-list {
    columns: 1;
  }
}
</style>
