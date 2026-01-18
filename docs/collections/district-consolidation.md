---
layout: browse
title: District Consolidation Records
description: School district consolidation data from 29 New York counties
permalink: /collections/district-consolidation/
filter_by: county
---

This collection contains school district consolidation tables from NYS Archives Series A4456. The records document the reorganization of rural school districts across New York State, organized by county.

## Overview

- **Source:** NYS Archives Series A4456
- **Coverage:** 29 New York counties
- **Document Type:** Tabular records and administrative data
- **Pages:** 116 total

## Table Types

The consolidation records include several types of data tables:

- **Union Free Schools** - Schools formed by union of common school districts
- **Town School Units** - School districts organized at the town level
- **Consolidated Districts** - Merged school districts
- **Central Rural Schools** - Centralized schools serving rural areas

## Browse by County

Select a county below to view its consolidation records, or use the [county browse page](/browse/by-county/) for the full listing.

{% assign county_artifacts = site.artifacts | where_exp: "item", "item.county != nil" | group_by: "county" | sort: "name" %}

<div class="county-grid">
{% for group in county_artifacts %}
<div class="county-item">
  <strong>{{ group.name }}</strong>
  <span class="count">{{ group.items.size }} items</span>
</div>
{% endfor %}
</div>

<style>
.county-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 0.75rem;
  margin: 1.5rem 0;
}

.county-item {
  padding: 0.75rem;
  background: #f8f8f8;
  border: 1px solid #e1e1e1;
  border-radius: 4px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.county-item .count {
  font-size: 0.8rem;
  color: #666;
}
</style>
