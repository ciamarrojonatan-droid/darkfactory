#!/usr/bin/env python3
"""DarkFactory Google Flow Playwright Stealth RPA Bot.

Automates clip generation on Google Flow (flow.google.com):
1. Loads specialized generation queues:
   - Gemini Omni Flash 1.2: Long-form continuity takes (up to 15s) with 6 reference image slots.
   - Google DeepMind Veo 3 / 3.1: 4K native hero shots (8s) with Panavision anamorphic optics.
2. Injects prompts and settings into Google Flow using a persistent Chrome session.
3. Automatically downloads generated video clips into data/broll/ for final assembly.
4. Provides automatic fallback to RunningHub T2V / procedural footage if Flow session is unauthenticated.
5. Operates in dry-run mode for CI/test suites without live browser launches.
"""
import argparse
import json
import logging
import os
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

# ADR-01: Windows UTF-8 stdout/stderr
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("GoogleFlowBot")

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
SCRIPTS_DIR = DATA_DIR / "scripts"
BROLL_DIR = DATA_DIR / "broll"
SESSIONS_DIR = PROJECT_ROOT / "chrome_session" / "google_flow"


class GoogleFlowBot:
    """Automates Google Flow video generation with stealth and failover."""

    def __init__(self, broll_dir: Optional[Path] = None, session_dir: Optional[Path] = None):
        self.broll_dir = broll_dir or BROLL_DIR
        self.session_dir = session_dir or SESSIONS_DIR
        self.broll_dir.mkdir(parents=True, exist_ok=True)
        self.session_dir.mkdir(parents=True, exist_ok=True)

    def dispatch_flow_queues(
        self,
        omni_queue_file: Path,
        veo3_queue_file: Path,
        dry_run: bool = False,
        allow_procedural: bool = False,
    ) -> Dict[str, Any]:
        """Dispatches both Omni Flash 1.2 and Veo 3.1 generation queues."""
        if not omni_queue_file.exists() or not veo3_queue_file.exists():
            raise FileNotFoundError("Google Flow queue files missing. Please run nolan_director.py first.")

        with open(omni_queue_file, "r", encoding="utf-8") as f:
            omni_data = json.load(f)
        with open(veo3_queue_file, "r", encoding="utf-8") as f:
            veo3_data = json.load(f)

        logger.info(f"Loaded Omni Flash Queue ({len(omni_data.get('scenes', []))} scenes)")
        logger.info(f"Loaded Veo 3.1 4K Queue ({len(veo3_data.get('scenes', []))} scenes)")

        results = {
            "studio": "Google Flow (flow.google.com)",
            "omni_flash_renders": [],
            "veo3_renders": [],
            "status": "completed",
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        }

        # Process Omni Flash 1.2 continuity scenes (Shot A)
        for sc in omni_data.get("scenes", []):
            s_id = sc["scene_id"]
            target_name = f"cena {s_id}.mp4" if s_id == 1 else f"scene_{s_id}.mp4"
            target_path = self.broll_dir / target_name

            if dry_run:
                logger.info(f"[DRY-RUN] Simulating Omni Flash 1.2 render for Scene {s_id} ({sc['shot_name']}) -> {target_name}")
                if not target_path.exists():
                    target_path.write_bytes(b"dummy_omni_render_bytes")
                results["omni_flash_renders"].append({"scene_id": s_id, "file": str(target_path), "is_dry_run": True})
            else:
                success = self._execute_playwright_flow_prompt(
                    model="gemini-omni-flash-1.2",
                    prompt=sc["prompt"],
                    duration=sc.get("target_duration_sec", 14.5),
                    output_file=target_path,
                )
                if not success:
                    logger.warning(f"Google Flow render for Scene {s_id} failed or unauthenticated. Applying RunningHub MiniMax H3 fallback...")
                    self.fallback_to_runninghub_or_procedural(
                        s_id,
                        shot_type="shot_a",
                        target_file=target_path,
                        prompt=sc["prompt"],
                        duration=sc.get("target_duration_sec", 14.5),
                        allow_procedural=allow_procedural,
                    )
                results["omni_flash_renders"].append({"scene_id": s_id, "file": str(target_path), "is_fallback": not success})

        # Process Veo 3 / 3.1 4K Tactical Climax scenes (Shot B)
        for sc in veo3_data.get("scenes", []):
            s_id = sc["scene_id"]
            target_name = f"cena {s_id}b.mp4" if s_id == 1 else f"scene_{s_id}_b.mp4"
            target_path = self.broll_dir / target_name

            if dry_run:
                logger.info(f"[DRY-RUN] Simulating Veo 3.1 4K render for Scene {s_id} ({sc['shot_name']}) -> {target_name}")
                if not target_path.exists():
                    target_path.write_bytes(b"dummy_veo3_render_bytes")
                results["veo3_renders"].append({"scene_id": s_id, "file": str(target_path), "is_dry_run": True})
            else:
                success = self._execute_playwright_flow_prompt(
                    model="veo-3.1-generate-4k",
                    prompt=sc["prompt"],
                    duration=sc.get("target_duration_sec", 8.0),
                    output_file=target_path,
                )
                if not success:
                    logger.warning(f"Google Flow Veo 3.1 render for Scene {s_id} failed. Applying RunningHub MiniMax H3 fallback...")
                    self.fallback_to_runninghub_or_procedural(
                        s_id,
                        shot_type="shot_b",
                        target_file=target_path,
                        prompt=sc["prompt"],
                        duration=sc.get("target_duration_sec", 8.0),
                        allow_procedural=allow_procedural,
                    )
                results["veo3_renders"].append({"scene_id": s_id, "file": str(target_path), "is_fallback": not success})

        return results

    def _execute_playwright_flow_prompt(
        self,
        model: str,
        prompt: str,
        duration: float,
        output_file: Path,
    ) -> bool:
        """Launches stealth Playwright session to inject prompt and download clip from Google Flow."""
        state_file = self.session_dir / "storage_state.json"
        has_profile = (self.session_dir / "Default").exists() or state_file.exists()
        if not has_profile:
            logger.info("Google Flow persistent session profile not found. Triggering fallback engine.")
            return False

        try:
            from playwright.sync_api import sync_playwright

            with sync_playwright() as p:
                launch_kwargs: Dict[str, Any] = {
                    "user_data_dir": str(self.session_dir),
                    "headless": True,
                    "args": ["--disable-blink-features=AutomationControlled"],
                }
                context = p.chromium.launch_persistent_context(**launch_kwargs)
                page = context.new_page()

                flow_url = os.getenv("GOOGLE_FLOW_URL", "https://flow.google.com")
                page.goto(flow_url, timeout=30000)
                page.wait_for_load_state("domcontentloaded", timeout=30000)

                # Check if prompt textarea exists
                prompt_input = page.query_selector('textarea, [contenteditable="true"], input[placeholder*="prompt"]')
                if not prompt_input:
                    logger.warning("Prompt input field not located on Google Flow page.")
                    context.close()
                    return False

                prompt_input.fill(prompt)
                time.sleep(1)

                # Submit generation
                submit_btn = page.query_selector('button:has-text("Generate"), button:has-text("Create"), button[aria-label*="Generate"]')
                if submit_btn and submit_btn.is_enabled():
                    submit_btn.click()
                else:
                    page.keyboard.press("Enter")

                # Await video element with timeout 90s
                logger.info(f"Awaiting Google Flow generation for model {model} (timeout=90s)...")
                video_el = page.wait_for_selector("video[src], a[download*='.mp4']", timeout=90000)
                if video_el:
                    src = video_el.get_attribute("src") or video_el.get_attribute("href")
                    if src and src.startswith("http"):
                        import urllib.request
                        urllib.request.urlretrieve(src, str(output_file))
                        if output_file.exists() and output_file.stat().st_size > 50000:
                            logger.info(f"✅ Downloaded Google Flow video clip: {output_file.name}")
                            context.close()
                            return True

                context.close()
        except Exception as e:
            logger.warning(f"Playwright Google Flow execution failed ({e}). Comuting to RunningHub MiniMax H3 fallback.")

        return False

    def fallback_to_runninghub_or_procedural(
        self,
        scene_id: int,
        shot_type: str,
        target_file: Path,
        prompt: str = "",
        duration: float = 10.0,
        allow_procedural: bool = False,
    ) -> Path:
        """Fallback engine: attempts RunningHub MiniMax H3 fallback; quarantine if both fail."""
        if target_file.exists() and target_file.stat().st_size > 50000:
            logger.info(f"Using existing cached B-roll for Scene {scene_id} ({shot_type}): {target_file.name}")
            return target_file

        # If procedural is explicitly allowed or no prompt provided (test mode)
        if allow_procedural or not prompt:
            logger.warning(f"Generating procedural fallback plate for Scene {scene_id} (test mode)...")
            from render_pilot_video import create_procedural_broll_image
            image_fallback = target_file.with_suffix(".jpg")
            create_procedural_broll_image(image_fallback, scene_id=scene_id, scene_title=f"SCENE {scene_id} {shot_type.upper()}")
            return image_fallback

        # 1. Primary Fallback: RunningHub MiniMax H3 Cinematic V2 Turbo
        logger.info(f"Triggering RunningHub MiniMax H3 Cinematic fallback for Scene {scene_id} ({shot_type})...")
        try:
            from src.video.minimax_h3_engine import MiniMaxH3VideoEngine
            engine = MiniMaxH3VideoEngine(output_dir=self.broll_dir)
            h3_res = engine.generate_video(
                prompt=prompt,
                duration_sec=duration,
                destination_path=target_file,
                force_procedural=False,
                allow_procedural_fallback=False,
            )
            if h3_res.video_path.exists() and h3_res.video_path.stat().st_size > 50000:
                logger.info(f"✅ Scene {scene_id} successfully generated via RunningHub MiniMax H3: {h3_res.filename}")
                if h3_res.video_path != target_file:
                    import shutil
                    shutil.copy(str(h3_res.video_path), str(target_file))
                return target_file
        except Exception as rh_exc:
            logger.warning(f"RunningHub MiniMax H3 fallback failed for Scene {scene_id}: {rh_exc}")

        # 2. Hard Quarantine Gate (No fake procedural videos allowed in production!)
        quarantine_dir = DATA_DIR / "quarantine" / f"scene_{scene_id}_{shot_type}_failure"
        quarantine_dir.mkdir(parents=True, exist_ok=True)
        failure_report = {
            "scene_id": scene_id,
            "shot_type": shot_type,
            "prompt": prompt,
            "duration": duration,
            "error": "Failed on both Google Flow and RunningHub MiniMax H3. Procedural fallback is permanently disabled.",
            "timestamp": time.time(),
        }
        (quarantine_dir / "quarantine_report.json").write_text(json.dumps(failure_report, indent=2), encoding="utf-8")
        raise RuntimeError(
            f"CRITICAL: Scene {scene_id} ({shot_type}) failed to generate on Google Flow and RunningHub MiniMax H3. "
            f"Procedural fallback is disabled. See quarantine diagnostics at: {quarantine_dir}"
        )


def main() -> None:
    parser = argparse.ArgumentParser(description="DarkFactory Google Flow RPA Bot")
    parser.add_argument(
        "--omni-queue",
        type=str,
        default=str(SCRIPTS_DIR / "google_flow_omni_queue.json"),
        help="Path to Omni Flash queue JSON",
    )
    parser.add_argument(
        "--veo3-queue",
        type=str,
        default=str(SCRIPTS_DIR / "google_flow_veo3_queue.json"),
        help="Path to Veo 3.1 queue JSON",
    )
    parser.add_argument("--dry-run", action="store_true", help="Simulate video generation without browser session")
    args = parser.parse_args()

    bot = GoogleFlowBot()
    res = bot.dispatch_flow_queues(
        omni_queue_file=Path(args.omni_queue),
        veo3_queue_file=Path(args.veo3_queue),
        dry_run=args.dry_run,
    )
    print(f"\nGoogle Flow Bot Execution Summary: {json.dumps(res, indent=2)}")


if __name__ == "__main__":
    main()
