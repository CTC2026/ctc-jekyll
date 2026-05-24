---
layout: default
title: Home
---

<div class="home-hero">
  <video class="home-hero-bg" autoplay muted loop playsinline aria-hidden="true">
    <source src="{{ '/assets/videos/CTC_HomeBG_v5.mp4' | relative_url }}" type="video/mp4">
  </video>
  <button class="video-pause-btn" aria-label="Pause background video" onclick="
    var v = this.closest('.home-hero').querySelector('video');
    if (v.paused) { v.play(); this.setAttribute('aria-label','Pause background video'); this.textContent='⏸'; }
    else { v.pause(); this.setAttribute('aria-label','Play background video'); this.textContent='▶'; }
  ">⏸</button>
</div>

<h1>Welcome</h1>

<div class="card-grid">
  <a href="{{ '/about/' | relative_url }}" class="card">
    <div class="card-body">
      <h2 class="card-heading">About CTC</h2>
      <p>Learn about the project and its goals.</p>
    </div>
  </a>
  <a href="{{ '/resources/' | relative_url }}" class="card">
    <img src="{{ '/assets/images/guan_resourcebanner.png' | relative_url }}" alt="Scene from a Chinese theater play">
    <div class="card-body">
      <h2 class="card-heading">Resources for Plays</h2>
      <p>Scripts, commentary, and teaching materials.</p>
    </div>
  </a>
  <a href="{{ '/media/' | relative_url }}" class="card">
    <div class="card-body">
      <h2 class="card-heading">Media Types and Opera Styles</h2>
      <p>Explore different forms of Chinese theater.</p>
    </div>
  </a>
  <a href="{{ '/how-to-teach/' | relative_url }}" class="card">
    <div class="card-body">
      <h2 class="card-heading">How to Teach</h2>
      <p>Guides and strategies for educators.</p>
    </div>
  </a>
</div>
