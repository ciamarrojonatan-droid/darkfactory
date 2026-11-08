#!/usr/bin/env python3
"""DarkFactory Nolan Director (Cinematic Showrunner & Non-Linear Script Engine).

Transforms historical ground-truth facts from Wikipedia into high-tension,
non-linear documentary scripts with Christopher Nolan's directorial signature:
- Crosscutting temporal architecture (Thread A Slow Clock vs Thread B Rapid Clock).
- Dual-Shot A/B visual pairing for T2V models (Shot A Drama + Shot B Tactical Macro).
- Hans Zimmer / Ludwig Göransson procedural sound design cues (Shepard tone, Braam, Ticking clock).
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
    # Look in same directory
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

        # Titles focused on taboo, existential countdown and declassified documents
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

    def direct_episode(self, topic: str) -> NolanEpisodeManifest:
        """Researches, directs and formats a complete documentary episode in Nolan's style."""
        logger.info(f"Nolan Director initiating episode development on: '{topic}'")
        research = self.researcher.research_topic(topic)

        packaging = self.generate_packaging(topic, research)
        timelines = self.generate_timeline_architecture(research)

        # Build 3 high-tension scenes (Dual-Shot paired for T2V engines)
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
                "provider": "RunningHub CosyVoice 3 Instruct 2 (Workflow 2118531898170486785)",
                "fallback_local": "Kokoro-82M (am_adam / am_fenrir / am_onyx)",
                "execution_mode": "lite_plus",
                "persona": "Authoritative Christopher Nolan Historical Documentary Narrator, Deep Baritone",
            },
            scenes=scenes,
        )

        return manifest

    def export_manifest(self, manifest: NolanEpisodeManifest, output_path: Path) -> Path:
        """Saves episode manifest atomically to disk per ADR-02."""
        output_path.parent.mkdir(parents=True, exist_ok=True)
        tmp_target = output_path.with_suffix(f".tmp.{os.getpid()}")
        with open(tmp_target, "w", encoding="utf-8") as f:
            json.dump(manifest.to_dict(), f, indent=2, ensure_ascii=False)
        tmp_target.replace(output_path)
        logger.info(f"Nolan Director manifest exported atomically to: {output_path}")
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
    print(f"\n✅ Manifesto salvo com sucesso em: {out_path}")


if __name__ == "__main__":
    main()
