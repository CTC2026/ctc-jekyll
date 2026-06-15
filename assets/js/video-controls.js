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

    function stopAudio() {
      if (currentAudio) { currentAudio.pause(); currentAudio = null; video.volume = 1; }
      lastCueIdx = -1;
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
      stopAudio();
      lastCueIdx = activeCueIdx;
      if (activeCueIdx < 0) return;

      var n = String(activeCueIdx + 1).padStart(2, '0');
      currentAudio = new Audio(base + 'cue_' + n + '.mp3?v=2');
      video.volume = 0;
      currentAudio.addEventListener('ended', function () { video.volume = 1; });
      currentAudio.play().catch(function (e) { console.warn('AD audio play blocked:', e); });
    });

    video.addEventListener('pause', stopAudio);
    video.addEventListener('seeked', stopAudio);
  }

  // On load: default each video to Chinese subtitles if available, else English
  document.addEventListener('DOMContentLoaded', function () {
    document.querySelectorAll('.clip-section').forEach(function (section) {
      var video = section.querySelector('video');
      if (!video) return;
      setupADPlayback(video);
      var tracks = video.textTracks;
      var hasZh = false;
      for (var i = 0; i < tracks.length; i++) {
        if (tracks[i].kind !== 'descriptions' && tracks[i].language === 'zh') {
          hasZh = true;
          break;
        }
      }
      var defaultLang = hasZh ? 'zh' : 'en';
      switchSub(video, defaultLang);
      syncSubBtns(section, defaultLang);
    });
  });
})();
