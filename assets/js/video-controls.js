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
    var tracks = video.textTracks;
    var descTrack = null;
    for (var i = 0; i < tracks.length; i++) {
      if (tracks[i].kind === 'descriptions') { descTrack = tracks[i]; break; }
    }
    if (!descTrack) return;

    var currentAudio = null;

    function stopAudio() {
      if (currentAudio) { currentAudio.pause(); currentAudio = null; }
    }

    descTrack.addEventListener('cuechange', function () {
      stopAudio();
      if (descTrack.mode !== 'showing') return;
      var activeCues = descTrack.activeCues;
      if (!activeCues || activeCues.length === 0) return;
      var allCues = Array.from(descTrack.cues);
      var idx = allCues.indexOf(activeCues[0]);
      if (idx < 0) return;
      var n = String(idx + 1).padStart(2, '0');
      currentAudio = new Audio(base + 'cue_' + n + '.mp3');
      currentAudio.play();
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
