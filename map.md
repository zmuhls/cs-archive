---
layout: single
title: Archive Map
description: Interactive map of NYSTA meetings and county consolidation records
permalink: /map/
---

<link rel="stylesheet" href="https://unpkg.com/leaflet@1.8.0/dist/leaflet.css" integrity="sha512-hoalWLoI8r4UszCkZ5kL8vayOGVae1oxXe/2A4AO6J9+580uKHDO3JdHb7NzwwzK5xr/Fs0W40kiNHxM9vyTtQ==" crossorigin=""/>
<script src="https://unpkg.com/leaflet@1.8.0/dist/leaflet.js" integrity="sha512-BB3hKbKWOc9Ez/TAwyWxNXeoV9c1v6FIeYiBieIWkpLjauysF18NzgR1MBNBXf8/KABdlkX68nAhlwcDFLGPCQ==" crossorigin=""></script>
<script src="https://code.jquery.com/jquery-3.2.1.min.js"></script>

<div class="map-container">
  <div id="map"></div>
</div>

## Locations

<div class="locations-panel">
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
</div>

<script src="{{ '/assets/maps/archive-map.js' | relative_url }}"></script>

<style>
/* Map Container - matches site card styling */
.map-container {
  background: #f8f8f8;
  padding: 1rem;
  border-radius: 8px;
  margin-bottom: 2rem;
}

#map {
  width: 100%;
  height: 500px;
  min-height: 400px;
  border-radius: 8px;
  border: 1px solid #e1e1e1;
  background: white;
}

/* Locations Panel */
.locations-panel {
  background: white;
  border: 1px solid #e1e1e1;
  border-radius: 8px;
  padding: 1.5rem;
}

/* Legend Styles */
.legend {
  background: white;
  padding: 12px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.15);
  line-height: 1.8;
  color: #333;
  border: 1px solid #e1e1e1;
}
.legend i {
  width: 18px;
  height: 18px;
  float: left;
  margin-right: 8px;
  opacity: 0.9;
  border-radius: 50%;
}
.legend-title {
  font-weight: bold;
  margin-bottom: 8px;
  color: #333;
}

/* Tab Styles - matches site button patterns */
.tab-container {
  display: flex;
  flex-wrap: wrap;
  gap: 0.75rem;
  margin-bottom: 1.5rem;
}
.tab {
  padding: 0.75rem 1.25rem;
  cursor: pointer;
  border: 2px solid #333;
  background: white;
  color: #333;
  font-family: inherit;
  font-size: 0.9rem;
  font-weight: 500;
  border-radius: 8px;
  transition: all 0.2s;
}
.tab:hover {
  background: #333;
  color: white;
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
  font-size: 0.95rem;
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
  padding: 0.6rem 0.75rem;
  cursor: pointer;
  border-radius: 8px;
  transition: all 0.2s;
  break-inside: avoid;
  color: #333;
  border: 1px solid transparent;
}
.location-list li:hover {
  background: #333;
  color: white;
  border-color: #333;
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
  .map-container {
    padding: 0.75rem;
  }
  #map {
    height: 350px;
  }
  .locations-panel {
    padding: 1rem;
  }
  .location-list {
    columns: 1;
  }
  .tab {
    padding: 0.6rem 1rem;
    font-size: 0.85rem;
  }
}
</style>
