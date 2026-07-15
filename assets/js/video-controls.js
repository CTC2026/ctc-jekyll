(function () {
  function getVideo(btn) {
    var section = btn.closest('.clip-section');
    return section ? section.querySelector('video') : null;
  }

  function switchSub(video, lang) {
    var tracks = video.textTracks;
    for (var i = 0; i < tracks.length; i++) {
      if (tracks[i].kind === 'descriptions') continue;
      tracks[i].mode = (lang !== 'off' && tracks[i].language === lang) ? 'showing' : 'hidden';
    }
  }

  function toggleAD(video, btn) {
    var tracks = video.textTracks;
    for (var i = 0; i < tracks.length; i++) {
      if (tracks[i].kind === 'descriptions') {
        var turnOn = tracks[i].mode !== 'showing';
        tracks[i].mode = turnOn ? 'showing' : 'hidden';
        btn.classList.toggle('active', turnOn);
        return;
      }
    }
  }

  function syncSubBtns(section, activeLang) {
    section.querySelectorAll('.sub-btn:not([data-lang="ad"])').forEach(function (btn) {
      btn.classList.toggle('active', btn.dataset.lang === activeLang);
    });
  }

  // Single delegated listener for all subtitle/AD buttons
  document.addEventListener('click', function (e) {
    var btn = e.target.closest('.sub-btn');
    if (!btn) return;
    var video = getVideo(btn);
    if (!video) return;
    var lang = btn.dataset.lang;
    if (lang === 'ad') {
      toggleAD(video, btn);
    } else {
      switchSub(video, lang);
      syncSubBtns(btn.closest('.clip-section'), lang);
    }
  });

  // Wire up timed MP3 playback for videos with data-ad-mp3-base
  function setupADPlayback(video) {
    var base = video.dataset.adMp3Base;
    if (!base) return;

    var currentAudio = null;
    var lastCueIdx = -1;

    var DUCK_VOLUME = 0.3; // video volume while a description plays
    var AD_VOLUME = 0.55;  // description volume: the AD voice is normalised ~5.5 dB
                           // hotter than the quiet 1964 film track, so play it below
                           // full scale to sit level with the film's normal volume

    function stopAudio() {
      if (currentAudio) { currentAudio.pause(); currentAudio = null; video.volume = 1; }
    }

    function getDescTrack() {
      var tracks = video.textTracks;
      for (var i = 0; i < tracks.length; i++) {
        if (tracks[i].kind === 'descriptions') return tracks[i];
      }
      return null;
    }

    video.addEventListener('timeupdate', function () {
      var descTrack = getDescTrack();
      if (!descTrack || descTrack.mode !== 'showing') return;
      var cues = descTrack.cues;
      if (!cues || cues.length === 0) return;

      var t = video.currentTime;
      var activeCueIdx = -1;
      for (var i = 0; i < cues.length; i++) {
        if (t >= cues[i].startTime && t < cues[i].endTime) {
          activeCueIdx = i;
          break;
        }
      }

      if (activeCueIdx === lastCueIdx) return;
      lastCueIdx = activeCueIdx;

      // Entering the gap after a cue: let the current description play out to its
      // natural end. (Previously we stopped it here, but `timeupdate` fires at
      // irregular ~250ms intervals, so the cut landed at a different point every
      // run — which is why the same clip sounded different each play and the last
      // word sometimes got clipped.)
      if (activeCueIdx < 0) return;

      // Entering a new cue: replace any still-playing description with this one.
      stopAudio();
      var n = String(activeCueIdx + 1).padStart(2, '0');
      currentAudio = new Audio(base + 'cue_' + n + '.mp3?v=5');
      currentAudio.volume = AD_VOLUME; // description level (see AD_VOLUME above)
      video.volume = DUCK_VOLUME;     // duck the film audio underneath it
      currentAudio.addEventListener('ended', function () { video.volume = 1; });
      currentAudio.play().catch(function (e) { console.warn('AD audio play blocked:', e); });
    });

    // Pausing or seeking stops the current description and clears the tracked cue
    // so it re-triggers cleanly on resume.
    video.addEventListener('pause', function () { stopAudio(); lastCueIdx = -1; });
    video.addEventListener('seeked', function () { stopAudio(); lastCueIdx = -1; });
  }

  // On load: lazy-load content images and set video preload
  document.addEventListener('DOMContentLoaded', function () {
    // Preload only metadata (duration/dimensions) for all videos — not the full stream
    document.querySelectorAll('video').forEach(function (v) {
      if (!v.hasAttribute('preload')) v.setAttribute('preload', 'metadata');
    });

    // Native lazy-load for all content images below the fold.
    // Skip header and page-banner images — those are above the fold and must load eagerly.
    var main = document.getElementById('main-content');
    if (main) {
      main.querySelectorAll('img').forEach(function (img) {
        if (img.closest('.page-banner')) return;
        if (!img.hasAttribute('loading')) img.setAttribute('loading', 'lazy');
      });
    }
  });

  // On load: disable controls that have no matching track, then default each
  // video to Chinese subtitles (else English) if any subtitle track exists.
  // The markup carries the full button row on every clip for visual
  // consistency; buttons whose track isn't present yet are disabled rather
  // than left as dead controls (they light up automatically once the track
  // is added).
  document.addEventListener('DOMContentLoaded', function () {
    document.querySelectorAll('.clip-section').forEach(function (section) {
      var video = section.querySelector('video');
      if (!video) return;
      setupADPlayback(video);
      var tracks = video.textTracks;
      var hasZh = false, hasEn = false, hasAD = false;
      for (var i = 0; i < tracks.length; i++) {
        if (tracks[i].kind === 'descriptions') hasAD = true;
        else if (tracks[i].language === 'zh') hasZh = true;
        else if (tracks[i].language === 'en') hasEn = true;
      }
      section.querySelectorAll('.sub-btn').forEach(function (btn) {
        var lang = btn.dataset.lang;
        var ok = (lang === 'zh' && hasZh) || (lang === 'en' && hasEn) ||
                 (lang === 'off' && (hasZh || hasEn)) || (lang === 'ad' && hasAD);
        if (!ok) {
          btn.disabled = true;
          btn.setAttribute('aria-disabled', 'true');
        }
      });
      if (hasZh || hasEn) {
        var defaultLang = hasZh ? 'zh' : 'en';
        switchSub(video, defaultLang);
        syncSubBtns(section, defaultLang);
      }
    });
  });
})();
