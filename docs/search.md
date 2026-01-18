---
layout: single
title: Search the Archive
description: Search across 168,845 words of transcribed documents
permalink: /search/
---

<div id="search-container">
  <input type="text" id="search-input" placeholder="Search documents..." autofocus>
  <div id="search-results"></div>
</div>

<script src="https://unpkg.com/lunr/lunr.js"></script>
<script>
(function() {
  // Build search index from artifacts
  var documents = [
    {% for artifact in site.artifacts %}
    {
      "id": "{{ artifact.artifact_id }}",
      "title": {{ artifact.title | jsonify }},
      "url": "{{ artifact.url | relative_url }}",
      "type": "{{ artifact.item_type | replace: '_', ' ' }}",
      "location": {{ artifact.location | jsonify }},
      "decade": "{{ artifact.decade }}",
      "content": {{ artifact.content | strip_html | truncatewords: 200 | jsonify }}
    }{% unless forloop.last %},{% endunless %}
    {% endfor %}
  ];

  // Build Lunr index
  var idx = lunr(function () {
    this.ref('id');
    this.field('title', { boost: 10 });
    this.field('location', { boost: 5 });
    this.field('type');
    this.field('content');

    documents.forEach(function (doc) {
      this.add(doc);
    }, this);
  });

  // Create lookup map
  var docMap = {};
  documents.forEach(function(doc) {
    docMap[doc.id] = doc;
  });

  // Search functionality
  var searchInput = document.getElementById('search-input');
  var resultsContainer = document.getElementById('search-results');

  searchInput.addEventListener('input', function() {
    var query = this.value.trim();

    if (query.length < 2) {
      resultsContainer.innerHTML = '<p class="search-hint">Enter at least 2 characters to search...</p>';
      return;
    }

    try {
      var results = idx.search(query + '*');
      displayResults(results, query);
    } catch (e) {
      // Handle Lunr query syntax errors
      try {
        var results = idx.search(query);
        displayResults(results, query);
      } catch (e2) {
        resultsContainer.innerHTML = '<p class="search-error">Invalid search query. Try simpler terms.</p>';
      }
    }
  });

  function displayResults(results, query) {
    if (results.length === 0) {
      resultsContainer.innerHTML = '<p class="no-results">No documents found matching "' + escapeHtml(query) + '"</p>';
      return;
    }

    var html = '<p class="result-count">' + results.length + ' document' + (results.length === 1 ? '' : 's') + ' found</p>';
    html += '<div class="result-list">';

    results.slice(0, 50).forEach(function(result) {
      var doc = docMap[result.ref];
      if (doc) {
        html += '<a href="' + doc.url + '" class="result-item">';
        html += '<h3 class="result-title">' + escapeHtml(doc.title) + '</h3>';
        html += '<div class="result-meta">';
        html += '<span class="result-id">' + doc.id + '</span>';
        html += '<span class="result-type">' + doc.type + '</span>';
        if (doc.decade) html += '<span class="result-decade">' + doc.decade + '</span>';
        html += '</div>';
        if (doc.location) {
          html += '<p class="result-location">' + escapeHtml(doc.location) + '</p>';
        }
        html += '</a>';
      }
    });

    html += '</div>';

    if (results.length > 50) {
      html += '<p class="more-results">Showing first 50 of ' + results.length + ' results</p>';
    }

    resultsContainer.innerHTML = html;
  }

  function escapeHtml(text) {
    if (!text) return '';
    var div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
  }

  // Initialize
  resultsContainer.innerHTML = '<p class="search-hint">Enter a search term to find documents...</p>';
})();
</script>

<style>
#search-container {
  max-width: 800px;
  margin: 0 auto;
}

#search-input {
  width: 100%;
  padding: 1rem;
  font-size: 1.25rem;
  border: 2px solid #333;
  border-radius: 8px;
  margin-bottom: 1.5rem;
}

#search-input:focus {
  outline: none;
  border-color: #0066cc;
  box-shadow: 0 0 0 3px rgba(0, 102, 204, 0.1);
}

.search-hint, .no-results, .search-error {
  color: #666;
  font-style: italic;
  text-align: center;
  padding: 2rem;
}

.search-error {
  color: #cc0000;
}

.result-count {
  font-size: 0.9rem;
  color: #666;
  margin-bottom: 1rem;
}

.result-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.result-item {
  display: block;
  padding: 1rem;
  background: #f8f8f8;
  border: 1px solid #e1e1e1;
  border-radius: 8px;
  text-decoration: none;
  color: inherit;
  transition: all 0.2s;
}

.result-item:hover {
  background: #fff;
  border-color: #333;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.result-title {
  margin: 0 0 0.5rem 0;
  font-size: 1.1rem;
}

.result-meta {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 0.5rem;
}

.result-meta span {
  font-size: 0.75rem;
  background: #e8e8e8;
  padding: 0.2rem 0.5rem;
  border-radius: 3px;
}

.result-id {
  font-family: monospace;
}

.result-location {
  margin: 0;
  font-size: 0.9rem;
  color: #666;
}

.more-results {
  text-align: center;
  color: #666;
  font-style: italic;
  margin-top: 1rem;
}
</style>
