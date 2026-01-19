---
layout: single
title: Browse the Archive
description: Explore artifacts from the Common School Archive
permalink: /browse/
---

Explore primary sources by decade, document type, county, or location. Materials include handwritten meeting minutes, typed proceedings, notecard indexes, and county consolidation tables from the 1810s through 1940s.

## Browse By

<div class="browse-options">
  <div class="browse-option">
    <h3><a href="{{ '/browse/by-decade/' | relative_url }}">By Decade</a></h3>
    <p>Explore documents organized by time period, from the 1840s through the 1940s.</p>
  </div>
  
  <div class="browse-option">
    <h3><a href="{{ '/browse/by-type/' | relative_url }}">By Document Type</a></h3>
    <p>Filter by document type: letters, reports, meeting minutes, maps, and more.</p>
  </div>
  
  <div class="browse-option">
    <h3><a href="{{ '/browse/by-county/' | relative_url }}">By County</a></h3>
    <p>View records organized by New York State county.</p>
  </div>
  
  <div class="browse-option">
    <h3><a href="{{ '/browse/by-location/' | relative_url }}">By Location</a></h3>
    <p>Browse documents by the locations mentioned within them.</p>
  </div>
</div>

## Collections

<div class="collection-links">
  <div class="collection-link">
    <h3><a href="{{ '/collections/local-district-governance/' | relative_url }}">Local District Governance Records</a></h3>
    <p>Board meeting minutes from rural and suburban districts (1810s–1930s). Compare South-Kortright (1810s) and Amityville (1930s) governance.</p>
  </div>
  
  <div class="collection-link">
    <h3><a href="{{ '/collections/administrative-data/' | relative_url }}">District Administrative Data & Statistics</a></h3>
    <p>Index cards and county consolidation tables for quantitative research on district evolution (Series B0594 and B0494).</p>
  </div>
  
  <div class="collection-link">
    <h3><a href="{{ '/collections/nys-teachers-association/' | relative_url }}">NYS Teachers' Association</a></h3>
    <p>Proceedings and related materials tracing NYSTA's history from origin into the early 20th century.</p>
  </div>
</div>

<style>
.browse-options, .collection-links {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1rem;
  margin: 1.5rem 0;
}

.browse-option, .collection-link {
  background: #f8f8f8;
  border: 1px solid #e1e1e1;
  border-radius: 8px;
  padding: 1rem;
  transition: all 0.2s;
}

.browse-option:hover, .collection-link:hover {
  background: #333;
  border-color: #333;
}

.browse-option:hover h3 a, .collection-link:hover h3 a {
  color: white;
}

.browse-option:hover p, .collection-link:hover p {
  color: #ccc;
}

.browse-option h3, .collection-link h3 {
  margin: 0 0 0.5rem 0;
}

.browse-option h3 a, .collection-link h3 a {
  text-decoration: none;
  color: #333;
  font-weight: 600;
}

.browse-option p, .collection-link p {
  font-size: 0.9rem;
  color: #666;
  margin: 0;
  line-height: 1.4;
}
</style>
