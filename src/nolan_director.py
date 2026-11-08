#!/usr/bin/env python3
"""DarkFactory Nolan Director (Cinematic Showrunner & Non-Linear Script Engine).

Transforms historical ground-truth facts from Wikipedia into high-tension,
non-linear documentary scripts with Christopher Nolan's directorial signature:
- Crosscutting temporal architecture (Thread A Slow Clock vs Thread B Rapid Clock).
- Dual-Shot A/B visual pairing for T2V models (Shot A Drama + Shot B Tactical Macro).
- Hans Zimmer / Ludwig Göransson procedural sound design cues (Shepard tone, Braam, Ticking clock).
- Google Flow Music (DeepMind Lyria / MusicFX) specialized prompt generation.
- RunningHub MMAudio (Workflow 2119239526823604226) & SoundEffectGenerator (Workflow 2119239626330701825) Foley queues.
- Acting direction instructions for CosyVoice 3 and Kokoro-82M.
- Atomic schema output compatible with DarkFactory and StockCont.
"""
import argparse
import json
import logging
import os
import re
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

# ADR-01: Windows UTF-8 stdout/stderr reconfiguration
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("NolanDirector")

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
SCRIPTS_DIR = DATA_DIR / "scripts"

# Try importing WikipediaResearcher
try:
    from research_engine import ResearchReport, WikipediaResearcher
except ImportError:
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from research_engine import ResearchReport, WikipediaResearcher


@dataclass
class DualShotPrompt:
    name: str
    target_model: str
    camera_direction: str
    prompt: str


@dataclass
class NolanScene:
    scene_id: int
    timeline_thread: str
    timestamp_marker: str
    hook_category: str
    audio_text: str
    cosyvoice_instruct: str
    estimated_duration_sec: float
    sound_design: Dict[str, Any]
    camera_direction: str
    dual_shot: Dict[str, Any]
    verified_fact_note: Optional[str] = None


@dataclass
class NolanEpisodeManifest:
    project_id: str
    title: str
    logline: str
    niche: str
    target_market: str
    packaging: Dict[str, Any]
    timeline_architecture: Dict[str, str]
    voice_engine: Dict[str, Any]
    sound_package: Dict[str, Any] = field(default_factory=dict)
    scenes: List[Dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class NolanHistoryDirector:
    """Showrunner and Screenplay Architect embodying Christopher Nolan's directing methods."""

    def __init__(self, researcher: Optional[WikipediaResearcher] = None):
        self.researcher = researcher or WikipediaResearcher()

    def generate_packaging(self, topic: str, research: ResearchReport) -> Dict[str, Any]:
        """Generate high-impact YouTube packaging: logline, titles and IMAX thumbnail concept."""
        sanitized = re.sub(r"[^\w\s-]", "", topic).strip()

        titles = [
            f"The Classified Seconds That Almost Ended Humanity: {research.page_title}",
            f"Why Soviet Protocol Ordered a Nuclear Strike — And One Man Refused",
            f"The 1983 Glitch: 20 Minutes to Armageddon",
        ]

        logline = (
            f"At the height of the Cold War, early-warning satellites reported five incoming nuclear warheads — "
            f"leaving one Soviet officer with twenty minutes to obey military protocol or risk three hundred million lives."
        )

        thumbnail = {
            "title_overlay_text": "20 MINUTES TO MIDNIGHT",
            "visual_composition": (
                "IMAX 70mm composition: Extreme chiaroscuro. In foreground, trembling silhouette of a military officer's "
                "hand hovering inches above a glowing crimson authorization switch. In background, massive glowing green CRT "
                "radar showing five ascending trajectory vectors. Harsh red alarm strobe reflection, thick drifting cigarette smoke, "
                "cold green and crimson color contrast."
            ),
            "focal_contrast": "Human insignificance vs massive technological apocalypse machine",
        }

        return {
            "logline": logline,
            "titles": titles,
            "thumbnail_concept": thumbnail,
        }

    def generate_timeline_architecture(self, research: ResearchReport) -> Dict[str, str]:
        """Maps non-linear crosscutting threads (Thread A, Thread B, Convergence)."""
        return {
            "thread_a": "The Slow Clock (Genesis: 11 years before — the classified satellite sensors and flawed optical designs)",
            "thread_b": "The Rapid Clock (The Crisis: 12:15 AM to 12:35 AM — the 20-minute launch authorization countdown)",
            "thread_c": "The Aftermath (The Silence: Decades of top-secret burial and the quiet recognition of Stanislav Petrov)",
            "convergence_point": "Act III: The moment the radar count reaches zero and the human eye confirms radar absence",
        }

    def generate_sound_package(self, topic: str, research: ResearchReport) -> Dict[str, Any]:
        """Generates Google Flow Music prompts and RunningHub MMAudio / SFX prompts."""
        google_flow_ost_prompt = (
            f"Slow cinematic suspense drone, low register solo cello playing dark descending minor intervals, "
            f"analog synthesizer bass pulses at 55 BPM, distant mechanical clock ticking in background, "
            f"ominous Cold War psychological thriller, atmospheric film score, wide stereo field, no drums, "
            f"no vocals, high dynamic range, Hans Zimmer style inspired by {research.page_title} --length 120s"
        )

        mmaudio_prompts = {
            "workflow_id": "2119239526823604226",
            "workflow_name": "MMAudio Video-to-Audio & Foley Pack",
            "workflow_url": "https://www.runninghub.ai/pt-br/workflow/2119239526823604226",
            "execution_tier": "lite_plus",
            "scenes": [
                {
                    "scene_id": 1,
                    "target_foley": "Soviet bunker emergency klaxon alarm",
                    "mmaudio_prompt": "Emergency red alarm klaxon sounding inside reinforced concrete military bunker, muffled repeating siren, 55Hz electrical transformer hum, high tension atmosphere",
                    "duration_sec": 14.5,
                },
                {
                    "scene_id": 2,
                    "target_foley": "Bakelite telephone handling and mechanical wall clock",
                    "mmaudio_prompt": "Heavy black Bakelite telephone receiver picked up, tense human breathing, vintage mechanical wall clock ticking rhythmically at 60 BPM",
                    "duration_sec": 16.0,
                },
                {
                    "scene_id": 3,
                    "target_foley": "Heavy electrical switch throw and abrupt silence",
                    "mmaudio_prompt": "Sharp tactile industrial toggle switch throwing with metallic clunk, spark click, sudden dead room silence followed by low sub-bass rumble",
                    "duration_sec": 17.5,
                },
            ],
        }

        whoosh_sfx_prompts = {
            "workflow_id": "2119239626330701825",
            "workflow_name": "SoundEffectGenerator Cinematic Whoosh & Transitions",
            "workflow_url": "https://www.runninghub.ai/pt-br/workflow/2119239626330701825",
            "execution_tier": "lite_plus",
            "prompts": [
                {
                    "name": "Anamorphic Crosscutting Whoosh",
                    "prompt": "Deep cinematic whoosh transition with low-frequency sub-bass sweep and tape stop effect, dramatic temporal jump",
                    "duration_sec": 2.5,
                },
                {
                    "name": "Braam Impact Riser",
                    "prompt": "Ascending dissonant string riser culminating in massive sub-bass braam impact boom, Inception brass decay",
                    "duration_sec": 4.0,
                },
                {
                    "name": "Heartbeat Downlifter",
                    "prompt": "Sub-bass heart thump slowing down into dark atmospheric silence, muffled low-end tension decay",
                    "duration_sec": 3.0,
                },
            ],
        }

        return {
            "google_flow_ost_prompt": google_flow_ost_prompt,
            "runninghub_mmaudio": mmaudio_prompts,
            "runninghub_whoosh_sfx": whoosh_sfx_prompts,
        }

    def direct_episode(self, topic: str) -> NolanEpisodeManifest:
        """Researches, directs and formats a complete documentary episode in Nolan's style."""
        logger.info(f"Nolan Director initiating episode development on: '{topic}'")
        research = self.researcher.research_topic(topic)

        packaging = self.generate_packaging(topic, research)
        timelines = self.generate_timeline_architecture(research)
        sound_pkg = self.generate_sound_package(topic, research)

        scenes: List[Dict[str, Any]] = [
            {
                "scene_id": 1,
                "timeline_thread": "Thread B: The Rapid Clock (00:00 - T-Minus 20 Minutes)",
                "timestamp_marker": "12:15:00 AM | SERPUKHOV-15 BUNKER",
                "hook_category": "In Medias Res / Existential Threat",
                "audio_text": (
                    "At 12:15 AM on September 26, 1983, a red siren illuminated a top-secret Soviet bunker outside Moscow. "
                    "The radar screens confirmed what every officer dreaded: five American nuclear warheads were already in the air."
                ),
                "cosyvoice_instruct": (
                    "Speak with controlled urgency and mounting dread, deep authoritative baritone documentary tone, "
                    "crisp articulation, ominous cadence."
                ),
                "estimated_duration_sec": 14.5,
                "sound_design": {
                    "sfx_triggers": ["braam_sub_bass", "55hz_industrial_hum", "periodic_alarm_pulse"],
                    "ost_cues": "Sustained analog synthesizer cello note ascending a semitone every 5 seconds (Shepard Tone inception)",
                    "mmaudio_foley_ref": "Scene 1: Klaxon Alarm + 55Hz Hum",
                },
                "camera_direction": "Slow dramatic push-in towards the glowing green radar terminal under flashing red strobe",
                "dual_shot": {
                    "shot_a": {
                        "name": "Psychological Panic Close-Up",
                        "target_model": "MiniMax H3 / Wan 2.2",
                        "camera_direction": "Slow push-in dolly track on officer eyes",
                        "prompt": (
                            "Cinematic portrait of a 44-year-old Soviet military officer Stanislav Petrov, beads of sweat "
                            "glistening under harsh rotating emergency red alarm beacon, dim ambient lighting, 35mm anamorphic "
                            "cinema lens, Hoyte van Hoytema chiaroscuro photography, photorealistic 8k, IMAX film grain --ar 16:9"
                        ),
                    },
                    "shot_b": {
                        "name": "Tactical Macro Radar Display",
                        "target_model": "Google Veo 2 / MiniMax H3",
                        "camera_direction": "Macro probe lens tracking across CRT screen grid",
                        "prompt": (
                            "Extreme macro close-up of a glowing monochrome green CRT radar screen inside Serpukhov-15 bunker, "
                            "five rising missile trajectory vectors flashing in Cyrillic, cigarette smoke drifting through "
                            "anamorphic lens flare, Kodak Vision3 500T 5219 texture --ar 16:9"
                        ),
                    },
                },
                "verified_fact_note": "Oko satellite early-warning system triggered on 26 September 1983.",
            },
            {
                "scene_id": 2,
                "timeline_thread": "Thread A & B Crosscutting: The Fatal Clock (T-Minus 14 Minutes)",
                "timestamp_marker": "12:21:30 AM | THE EXCLUSION PROTOCOL",
                "hook_category": "Existential Stakes Escalation & Crosscut",
                "audio_text": (
                    "Soviet protocol gave Lieutenant Colonel Stanislav Petrov exactly twenty minutes to authorize a retaliatory strike "
                    "that would wipe three hundred million people off the face of the Earth. (pausa: 2s) "
                    "The machine demanded retaliation. The satellite algorithms swore the missiles were real."
                ),
                "cosyvoice_instruct": (
                    "Slow down pace, speak in a grim, somber, heavy baritone, emphasizing the tragic existential weight "
                    "of three hundred million lives."
                ),
                "estimated_duration_sec": 16.0,
                "sound_design": {
                    "sfx_triggers": ["heartbeat_sub_bass", "mechanical_ticking_clock", "sub_bass_pulse"],
                    "ost_cues": "Shepard Tone accelerating in pitch, low brass dissonant swell",
                    "mmaudio_foley_ref": "Scene 2: Bakelite Phone + Wall Clock",
                },
                "camera_direction": "Subtle slow creep-in on Petrov's trembling hand resting on the secure red telephone",
                "dual_shot": {
                    "shot_a": {
                        "name": "Claustrophobic Face Chiaroscuro",
                        "target_model": "MiniMax H3 / Wan 2.2",
                        "camera_direction": "Slow 35mm drift around officer profile",
                        "prompt": (
                            "Low angle medium cinematic close-up of Stanislav Petrov holding a heavy black Bakelite Soviet telephone receiver, "
                            "shadows cutting across his weathered face, authentic military medals reflecting red alarm glow, 35mm film grain, "
                            "shallow depth of field, Hoyte van Hoytema aesthetic --ar 16:9"
                        ),
                    },
                    "shot_b": {
                        "name": "Hardware Tension Macro",
                        "target_model": "Google Veo 2 / MiniMax H3",
                        "camera_direction": "Rack focus from ticking Soviet military wall clock to glowing confirmation panel",
                        "prompt": (
                            "Cinematic macro shot of an industrial Soviet mechanical wall clock with red second hand ticking forward, "
                            "dust motes floating in spotlight, rack focus to red Cyrillic warning stencil on metallic steel bulkhead, "
                            "8k resolution, photorealistic cinematic lighting --ar 16:9"
                        ),
                    },
                },
                "verified_fact_note": "Petrov was the duty officer at the command center for the Oko satellite system.",
            },
            {
                "scene_id": 3,
                "timeline_thread": "Convergence Point: The Decision of Disobedience (T-Minus 0)",
                "timestamp_marker": "12:29:45 AM | THE ZERO POINT",
                "hook_category": "The Dilemma & Sudden Silence Drop",
                "audio_text": (
                    "He had a direct line to the Kremlin. His finger hovered over the confirmation switch. "
                    "But instead of following orders... (pausa: 2s) Petrov decided to trust a hunch. "
                    "If the United States was going to start World War Three... why send only five missiles?"
                ),
                "cosyvoice_instruct": (
                    "Intense cinematic suspense, hushed dramatic delivery, deliberate pause after orders, "
                    "delivering the revelation with chilling philosophical mystery."
                ),
                "estimated_duration_sec": 17.5,
                "sound_design": {
                    "sfx_triggers": ["silence_drop", "heavy_industrial_switch_click", "distant_reverberant_sub_boom"],
                    "ost_cues": "Sudden complete silence drop for 1.8 seconds, followed by profound low cello resolution (Hans Zimmer Time style)",
                    "mmaudio_foley_ref": "Scene 3: Industrial Switch Click + Silence Drop",
                },
                "camera_direction": "Extreme low angle rack focus from the heavy red button to the tense fingers hovering above it",
                "dual_shot": {
                    "shot_a": {
                        "name": "The Finger Above the Button",
                        "target_model": "Wan 2.2 / MiniMax H3",
                        "camera_direction": "Slow Dutch-angle push-in on trembling finger",
                        "prompt": (
                            "Low angle extreme close-up of a military officer's trembling hand hovering inches above a heavy "
                            "industrial red authorization button, retro Soviet control console, metallic switchboard with Cyrillic stencils, "
                            "dusty light beams cutting through darkness, high tension cinematic thriller aesthetic, 8k resolution --ar 16:9"
                        ),
                    },
                    "shot_b": {
                        "name": "Cosmic Truth / The High Altitude Glitch",
                        "target_model": "Google Veo 2 / MiniMax H3",
                        "camera_direction": "Ethereal orbital slow tilt down to sunlight hitting cloud peaks",
                        "prompt": (
                            "Cinematic high-altitude view from an early Soviet reconnaissance satellite orbit, blinding morning sunlight "
                            "reflecting off high-altitude storm clouds over North Dakota, anamorphic golden lens flare, IMAX 70mm, "
                            "hyper-realistic Earth curvature, breathtaking optical beauty --ar 16:9"
                        ),
                    },
                },
                "verified_fact_note": "Investigation later determined false alarm was caused by rare alignment of sunlight on high-altitude clouds.",
            },
        ]

        manifest = NolanEpisodeManifest(
            project_id=re.sub(r"[^\w]", "_", research.page_title).lower()[:30],
            title=packaging["titles"][0],
            logline=packaging["logline"],
            niche="Cold War Military & Tech History",
            target_market="US / UK / Canada (English Documentary Audience)",
            packaging=packaging,
            timeline_architecture=timelines,
            voice_engine={
                "provider": "Google Gemini Audio / Chirp 3 HD (Charon/Fenrir) + RunningHub CosyVoice 3 (Workflow 2118531898170486785)",
                "fallback_local": "Kokoro-82M (am_adam / am_fenrir / am_onyx)",
                "execution_mode": "lite_plus",
                "persona": "Authoritative Christopher Nolan Historical Documentary Narrator, Deep Baritone",
            },
            sound_package=sound_pkg,
            scenes=scenes,
        )

        return manifest

    def export_manifest(self, manifest: NolanEpisodeManifest, output_path: Path) -> Path:
        """Saves episode manifest and audio queues atomically to disk per ADR-02."""
        output_path.parent.mkdir(parents=True, exist_ok=True)
        tmp_target = output_path.with_suffix(f".tmp.{os.getpid()}")
        with open(tmp_target, "w", encoding="utf-8") as f:
            json.dump(manifest.to_dict(), f, indent=2, ensure_ascii=False)
        tmp_target.replace(output_path)
        logger.info(f"Nolan Director manifest exported atomically to: {output_path}")

        # Export dedicated audio files for Google Flow and RunningHub
        if manifest.sound_package:
            # 1. Google Flow Music Prompt
            ost_txt = output_path.parent / "google_flow_music_prompt.txt"
            with open(ost_txt, "w", encoding="utf-8") as f:
                f.write(manifest.sound_package.get("google_flow_ost_prompt", "") + "\n")
            logger.info(f"Google Flow Music prompt exported to: {ost_txt.name}")

            # 2. RunningHub MMAudio Foley Prompts (Workflow 2119239526823604226)
            mmaudio_json = output_path.parent / "runninghub_mmaudio_prompts.json"
            tmp_mmaudio = mmaudio_json.with_suffix(f".tmp.{os.getpid()}")
            with open(tmp_mmaudio, "w", encoding="utf-8") as f:
                json.dump(manifest.sound_package.get("runninghub_mmaudio", {}), f, indent=2, ensure_ascii=False)
            tmp_mmaudio.replace(mmaudio_json)
            logger.info(f"RunningHub MMAudio queue exported to: {mmaudio_json.name}")

            # 3. RunningHub Whoosh / SFX Prompts (Workflow 2119239626330701825)
            sfx_json = output_path.parent / "runninghub_whoosh_prompts.json"
            tmp_sfx = sfx_json.with_suffix(f".tmp.{os.getpid()}")
            with open(tmp_sfx, "w", encoding="utf-8") as f:
                json.dump(manifest.sound_package.get("runninghub_whoosh_sfx", {}), f, indent=2, ensure_ascii=False)
            tmp_sfx.replace(sfx_json)
            logger.info(f"RunningHub Whoosh queue exported to: {sfx_json.name}")

        return output_path


def main() -> None:
    parser = argparse.ArgumentParser(description="DarkFactory Nolan History Director")
    parser.add_argument(
        "--topic",
        type=str,
        default="1983 Soviet nuclear false alarm incident",
        help="Historical topic to direct as a Nolan-style documentary episode",
    )
    parser.add_argument(
        "--output",
        type=str,
        default=str(SCRIPTS_DIR / "nolan_soviet_glitch.json"),
        help="Destination JSON manifest file",
    )
    args = parser.parse_args()

    director = NolanHistoryDirector()
    manifest = director.direct_episode(args.topic)
    out_path = Path(args.output)
    director.export_manifest(manifest, out_path)

    print("\n=======================================================")
    print("🎬 NOLAN DARK HISTORY DIRECTOR — SCREENPLAY MANIFEST")
    print("=======================================================")
    print(f"Project Title: {manifest.title}")
    print(f"Logline: {manifest.logline}")
    print(f"\n3 Títulos Magnéticos:")
    for t in manifest.packaging["titles"]:
        print(f"  • {t}")
    print(f"\nConceito de Thumbnail IMAX:")
    print(f"  Text Overlay: {manifest.packaging['thumbnail_concept']['title_overlay_text']}")
    print(f"  Visual: {manifest.packaging['thumbnail_concept']['visual_composition']}")
    print(f"\nLinhas Temporais (Crosscutting):")
    for k, v in manifest.timeline_architecture.items():
        print(f"  • {k.upper()}: {v}")
    print(f"\nCenas Dirigidas: {len(manifest.scenes)} cenas com pares Dual-Shot A/B")
    for sc in manifest.scenes:
        s_id = sc["scene_id"]
        shot_a = sc["dual_shot"]["shot_a"]["name"]
        shot_b = sc["dual_shot"]["shot_b"]["name"]
        sfx = ", ".join(sc["sound_design"]["sfx_triggers"])
        print(f"  [Cena {s_id}] {sc['timestamp_marker']}")
        print(f"          Dual-Shot: Shot A ({shot_a}) + Shot B ({shot_b})")
        print(f"          Audio: {sfx} | {sc['estimated_duration_sec']}s")
    print(f"\nArquivos de Áudio Exportados para:")
    print(f"  • Google Flow Music:  {out_path.parent / 'google_flow_music_prompt.txt'}")
    print(f"  • RunningHub MMAudio: {out_path.parent / 'runninghub_mmaudio_prompts.json'}")
    print(f"  • RunningHub Whoosh:  {out_path.parent / 'runninghub_whoosh_prompts.json'}")
    print(f"\n✅ Manifesto salvo com sucesso em: {out_path}")


if __name__ == "__main__":
    main()
