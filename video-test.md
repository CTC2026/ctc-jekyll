---
layout: page
title: Video Test Page
permalink: /video-test/
---

<p>This page tests R2-hosted video playback with bilingual subtitle switching.</p>

<div class="clip-section">
  <h3>Test Clip</h3>
  <p class="clip-desc">AI-generated scene — dark fantasy cinematic sequence.</p>

  <div class="video-wrap">
    <video id="test-video" controls crossorigin="anonymous">
      <source src="REPLACE_WITH_R2_URL/jimeng-test.mp4" type="video/mp4">
      <track id="track-zh" kind="subtitles" srclang="zh" label="中文" src="https://pub-41c640610b8146e0a2c6dc8915ac1f9d.r2.dev/assets/subtitles/test-zh.vtt">
      <track id="track-en" kind="subtitles" srclang="en" label="English" src="https://pub-41c640610b8146e0a2c6dc8915ac1f9d.r2.dev/assets/subtitles/test-en.vtt">
      Your browser does not support HTML5 video.
    </video>
  </div>

  <div class="subtitle-controls" role="group" aria-label="Subtitle language">
    <button class="sub-btn active" data-lang="zh" onclick="switchSubtitle('zh')"><span lang="zh">中文字幕</span></button>
    <button class="sub-btn" data-lang="en" onclick="switchSubtitle('en')">English</button>
    <button class="sub-btn" data-lang="off" onclick="switchSubtitle('off')">Off</button>
  </div>
</div>

<script>
function switchSubtitle(lang) {
  var video = document.getElementById('test-video');
  var tracks = video.textTracks;
  for (var i = 0; i < tracks.length; i++) {
    tracks[i].mode = (tracks[i].language === lang) ? 'showing' : 'hidden';
  }
  document.querySelectorAll('.sub-btn').forEach(function(btn) {
    btn.classList.toggle('active', btn.dataset.lang === lang);
  });
}
// Default: show Chinese subtitles
document.addEventListener('DOMContentLoaded', function() { switchSubtitle('zh'); });
</script>

<style>
.subtitle-controls {
  margin-top: 0.75rem;
  display: flex;
  gap: 0.5rem;
}
.sub-btn {
  padding: 0.3rem 0.9rem;
  font-size: 0.78rem;
  font-weight: 700;
  border: 2px solid var(--burgundy);
  border-radius: 2rem;
  background: transparent;
  color: var(--burgundy);
  cursor: pointer;
  font-family: inherit;
}
.sub-btn:hover { background: var(--burgundy); color: white; }
.sub-btn.active { background: var(--burgundy); color: white; }
</style>
