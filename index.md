---
layout: home
title: Common School Archive
description: Digital Humanities Archive of New York State Education (1800s-1900s)
---

Primary sources from New York State's common school system (1810s–1940s): from the proceedings of everyday school committees and their meeting minutes to district administrative data and notecard records of local schools by county across New York State.

## Explore the Collections

<div class="collection-cards">
  <a href="{{ '/collections/nys-teachers-association/' | relative_url }}" class="collection-card">
    <div class="collection-card-thumb">
      <img src="{{ '/derived/thumbs/IMG_0635.jpeg' | relative_url }}" alt="NYS Teachers' Association" loading="lazy">
    </div>
    <h3>NYS Teachers' Association</h3>
    <p>Annual meeting proceedings, membership rolls, and advocacy materials (1845–1940s) documenting the professionalization of teaching across 16 meeting locations statewide.</p>
  </a>

  <a href="{{ '/collections/local-district-governance/' | relative_url }}" class="collection-card">
    <div class="collection-card-thumb">
      <img src="{{ '/derived/thumbs/IMG_3863.jpeg' | relative_url }}" alt="Local District Governance" loading="lazy">
    </div>
    <h3>Local District Governance</h3>
    <p>Handwritten meeting minutes from rural one-room schools (1810s) through suburban consolidated districts (1930s). Board debates, committee reports, and votes.</p>
  </a>

  <a href="{{ '/collections/administrative-data/' | relative_url }}" class="collection-card">
    <div class="collection-card-thumb">
      <img src="{{ '/derived/thumbs/IMG_3419.jpeg' | relative_url }}" alt="District Administrative Data" loading="lazy">
    </div>
    <h3>Administrative Data</h3>
    <p>Notecard indexes, typed registries, and county consolidation tables from 29 counties. Reference materials for spatial and quantitative analysis.</p>
  </a>
</div>

## Browse the Archive

- [By Decade]({{ '/browse/by-decade/' | relative_url }}) - Documents from 1810s through 1940s
- [By Document Type]({{ '/browse/by-type/' | relative_url }}) - Letters, reports, meeting minutes, maps, and more
- [By County]({{ '/browse/by-county/' | relative_url }}) - Records organized by New York State county
- [By Location]({{ '/browse/by-location/' | relative_url }}) - Documents by geographic location

## Search

Use the [search page]({{ '/search/' | relative_url }}) to find specific documents by keyword across 168,845 words of transcribed text.

---

## About This Archive

**1,000+ pages** from **376 source images** yielding **168,845 words** of transcribed text. Documents have been digitized from NYS Archives series (A4645, B0594, B0494) and other repositories, then processed using multimodal AI (Qwen VL Plus) for transcription, classification, and metadata extraction.

[Learn more about the project]({{ '/about/' | relative_url }})

<style>
.collection-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 1.5rem;
  margin: 1.5rem 0;
}

.collection-card {
  display: block;
  padding: 1.5rem;
  background: white;
  border: 2px solid #333;
  border-radius: 8px;
  text-decoration: none;
  color: inherit;
  transition: all 0.2s;
}

.collection-card:hover {
  background: #333;
  color: white;
}

.collection-card-thumb {
  aspect-ratio: 4/3;
  overflow: hidden;
  border-radius: 6px;
  margin-bottom: 0.75rem;
  background: #f0f0f0;
}
.collection-card-thumb img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}

.collection-card h3 {
  margin: 0 0 0.5rem 0;
}

.collection-card p {
  margin: 0;
  font-size: 0.9rem;
  opacity: 0.8;
}
</style>
