/**
 * DarkFactory Cinema Studio — 4K Theatrical Video Player & Subtitles Engine
 */

class CinemaVideoEngine {
  constructor() {
    this.videoEl = null;
    this.letterboxBars = null;
    this.subtitleBanner = null;
    this.isAnamorphic239 = true;
    this.currentSubtitles = [];
    this.selectedThumbnailVariant = "A";
  }

  init(videoElId, barsElId, bannerElId) {
    this.videoEl = document.getElementById(videoElId);
    this.letterboxBars = document.getElementById(barsElId);
    this.subtitleBanner = document.getElementById(bannerElId);

    if (this.videoEl) {
      this.videoEl.addEventListener("timeupdate", () => this._onTimeUpdate());
    }
  }

  toggleLetterbox() {
    this.isAnamorphic239 = !this.isAnamorphic239;
    if (this.letterboxBars) {
      if (this.isAnamorphic239) {
        this.letterboxBars.classList.remove("hidden");
      } else {
        this.letterboxBars.classList.add("hidden");
      }
    }
    return this.isAnamorphic239;
  }

  async loadSubtitles(url) {
    try {
      const res = await fetch(url);
      const text = await res.text();
      this.currentSubtitles = this._parseSRT(text);
      console.log(`📜 Loaded ${this.currentSubtitles.length} subtitle cues from ${url}`);
    } catch (e) {
      console.warn("Failed to load subtitles:", e);
    }
  }

  _parseSRT(srtText) {
    const cues = [];
    const blocks = srtText.trim().replace(/\r/g, '').split('\n\n');
    blocks.forEach(block => {
      const lines = block.split('\n');
      if (lines.length >= 2) {
        const timeMatch = lines[1].match(/(\d{2}):(\d{2}):(\d{2}),(\d{3}) --> (\d{2}):(\d{2}):(\d{2}),(\d{3})/);
        if (timeMatch) {
          const start = parseInt(timeMatch[1]) * 3600 + parseInt(timeMatch[2]) * 60 + parseInt(timeMatch[3]) + parseInt(timeMatch[4]) / 1000;
          const end = parseInt(timeMatch[5]) * 3600 + parseInt(timeMatch[6]) * 60 + parseInt(timeMatch[7]) + parseInt(timeMatch[8]) / 1000;
          const text = lines.slice(2).join(' ');
          cues.push({ start, end, text });
        }
      }
    });
    return cues;
  }

  _onTimeUpdate() {
    if (!this.videoEl || !this.subtitleBanner || this.currentSubtitles.length === 0) return;
    const t = this.videoEl.currentTime;
    const activeCue = this.currentSubtitles.find(c => t >= c.start && t <= c.end);
    if (activeCue) {
      this.subtitleBanner.innerText = activeCue.text;
      this.subtitleBanner.style.display = "block";
    } else {
      this.subtitleBanner.innerText = "";
      this.subtitleBanner.style.display = "none";
    }
  }

  selectThumbnail(variant) {
    this.selectedThumbnailVariant = variant;
    document.querySelectorAll(".thumbnail-candidate").forEach(el => {
      if (el.dataset.variant === variant) {
        el.classList.add("selected");
      } else {
        el.classList.remove("selected");
      }
    });
    console.log(`🖼️ Selected Thumbnail Variant: ${variant}`);
  }
}

window.cinemaVideo = new CinemaVideoEngine();
