---
layout: page
title: Search
permalink: /search/
---

<search class="search-wrap">
  <input type="search" id="search-input" class="search-input"
         placeholder="Type keywords to search…"
         aria-label="Search site content"
         autocomplete="off">
  <ul id="search-results" class="search-results" aria-label="Search results" aria-live="polite"></ul>
</search>

<script src="https://unpkg.com/simple-jekyll-search@1.10.0/dest/simple-jekyll-search.min.js"></script>
<script>
SimpleJekyllSearch({
  searchInput: document.getElementById('search-input'),
  resultsContainer: document.getElementById('search-results'),
  json: '{{ "/search.json" | relative_url }}',
  searchResultTemplate: '<li><a href="{url}">{title}</a><p>{content}</p></li>',
  noResultsText: '<li class="no-results">No results found.</li>',
  limit: 10,
  fuzzy: false
});
</script>
