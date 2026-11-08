/**
 * DarkFactory Cinema Studio — Web Audio API 4-Stem Mixer Engine
 * Controls: Voice (CosyVoice/Kokoro), OST Drone (Lyria), Foley (MMAudio), Master Mix
 */

class AudioMixerEngine {
  constructor() {
    this.audioCtx = null;
    this.channels = {
      voice: { el: null, source: null, gain: null, analyser: null, isMuted: false, isSolo: false, prevVolume: 0.8 },
      ost: { el: null, source: null, gain: null, analyser: null, isMuted: false, isSolo: false, prevVolume: 0.65 },
      foley: { el: null, source: null, gain: null, analyser: null, isMuted: false, isSolo: false, prevVolume: 0.7 },
      master: { el: null, source: null, gain: null, analyser: null, isMuted: false, isSolo: false, prevVolume: 0.9 },
    };
    this.isPlaying = false;
    this.initialized = false;
    this.animFrameId = null;
  }

  initContext() {
    if (this.initialized) return;
    const AudioContextClass = window.AudioContext || window.webkitAudioContext;
    this.audioCtx = new AudioContextClass();

    Object.keys(this.channels).forEach(key => {
      const el = new Audio();
      el.crossOrigin = "anonymous";
      el.preload = "auto";
      
      const source = this.audioCtx.createMediaElementSource(el);
      const gain = this.audioCtx.createGain();
      const analyser = this.audioCtx.createAnalyser();
      analyser.fftSize = 64;

      source.connect(gain);
      gain.connect(analyser);
      analyser.connect(this.audioCtx.destination);

      gain.gain.value = this.channels[key].prevVolume;

      this.channels[key].el = el;
      this.channels[key].source = source;
      this.channels[key].gain = gain;
      this.channels[key].analyser = analyser;
    });

    this.initialized = true;
    console.log("🎚️ Web Audio 4-Stem Mixer Initialized");
  }

  loadStems(stemsData) {
    this.initContext();

    if (stemsData.voice && stemsData.voice.length > 0) {
      this.channels.voice.el.src = stemsData.voice[0].url;
    }
    if (stemsData.ost && stemsData.ost.length > 0) {
      this.channels.ost.el.src = stemsData.ost[0].url;
    }
    if (stemsData.foley && stemsData.foley.length > 0) {
      this.channels.foley.el.src = stemsData.foley[0].url;
    }
    if (stemsData.master && stemsData.master.length > 0) {
      this.channels.master.el.src = stemsData.master[0].url;
    }
  }

  togglePlayAll() {
    this.initContext();
    if (this.audioCtx.state === "suspended") {
      this.audioCtx.resume();
    }

    if (this.isPlaying) {
      Object.values(this.channels).forEach(ch => ch.el && ch.el.pause());
      this.isPlaying = false;
      if (this.animFrameId) cancelAnimationFrame(this.animFrameId);
      return false;
    } else {
      // Synchronize playhead
      Object.values(this.channels).forEach(ch => {
        if (ch.el && ch.el.src) {
          ch.el.currentTime = 0;
          ch.el.play().catch(e => console.warn("Playback error:", e));
        }
      });
      this.isPlaying = true;
      this._startVUMeterLoop();
      return true;
    }
  }

  setVolume(channelKey, volumeNorm) {
    if (!this.channels[channelKey]) return;
    const ch = this.channels[channelKey];
    ch.prevVolume = volumeNorm;
    if (!ch.isMuted) {
      ch.gain.gain.setTargetAtTime(volumeNorm, this.audioCtx.currentTime, 0.05);
    }
  }

  toggleMute(channelKey) {
    if (!this.channels[channelKey]) return;
    const ch = this.channels[channelKey];
    ch.isMuted = !ch.isMuted;
    const targetGain = ch.isMuted ? 0 : ch.prevVolume;
    ch.gain.gain.setTargetAtTime(targetGain, this.audioCtx.currentTime, 0.05);
    return ch.isMuted;
  }

  toggleSolo(channelKey) {
    if (!this.channels[channelKey]) return;
    const targetCh = this.channels[channelKey];
    targetCh.isSolo = !targetCh.isSolo;

    const anySolo = Object.values(this.channels).some(c => c.isSolo);

    Object.keys(this.channels).forEach(k => {
      const c = this.channels[k];
      if (anySolo) {
        const targetGain = c.isSolo ? c.prevVolume : 0;
        c.gain.gain.setTargetAtTime(targetGain, this.audioCtx.currentTime, 0.05);
      } else {
        const targetGain = c.isMuted ? 0 : c.prevVolume;
        c.gain.gain.setTargetAtTime(targetGain, this.audioCtx.currentTime, 0.05);
      }
    });

    return targetCh.isSolo;
  }

  _startVUMeterLoop() {
    const updateVUs = () => {
      if (!this.isPlaying) return;

      Object.keys(this.channels).forEach(key => {
        const ch = this.channels[key];
        const meterEl = document.getElementById(`vu-${key}`);
        if (!meterEl || !ch.analyser) return;

        const dataArray = new Uint8Array(ch.analyser.frequencyBinCount);
        ch.analyser.getByteFrequencyData(dataArray);

        let sum = 0;
        for (let i = 0; i < dataArray.length; i++) sum += dataArray[i];
        const avg = sum / dataArray.length;
        const percent = Math.min(100, Math.round((avg / 255) * 140));

        meterEl.style.height = `${percent}%`;
      });

      this.animFrameId = requestAnimationFrame(updateVUs);
    };
    updateVUs();
  }
}

window.soundLab = new AudioMixerEngine();
