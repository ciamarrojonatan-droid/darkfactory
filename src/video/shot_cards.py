"""DarkFactory Video-ShotCraft Modular Shot Card Recipes."""

from __future__ import annotations

from typing import Any, Dict

SHOT_CARD_RECIPES: Dict[str, Dict[str, Any]] = {
    "dolly_in_tension": {
        "name": "Dolly-In Archival Tension",
        "camera_rig": "35mm Anamorphic on motorized silent dolly",
        "lens": "35mm T2.0",
        "duration_band_sec": (3.2, 4.5),
        "copy_space_zone": "left_third",
        "recommended_overlay": "tactical_hud",
        "prompt_directive": "Slow measured dolly push at 0.8 m/s toward focal artifact; maintain clean left-third shadow negative space.",
    },
    "macro_archival_reveal": {
        "name": "Macro Declassified Reveal",
        "camera_rig": "100mm Macro Probe Lens on slider",
        "lens": "100mm f/2.8",
        "duration_band_sec": (2.4, 3.8),
        "copy_space_zone": "upper_half",
        "recommended_overlay": "risograph_declassified",
        "prompt_directive": "Lateral macro rack focus gliding across paper grain, ink stamps, and brushed dial markings under tungsten spotlight.",
    },
    "hud_telemetry_cut": {
        "name": "Tactical Telemetry Cut",
        "camera_rig": "Locked gimbal oblique 45-degree war-room console shot",
        "lens": "50mm f/2.0",
        "duration_band_sec": (2.5, 4.0),
        "copy_space_zone": "right_third",
        "recommended_overlay": "tactical_hud",
        "prompt_directive": "Crisp radar command workstation motion with generous clean glass partition on right third for data HUD overlays.",
    },
    "blueprint_wipe_transition": {
        "name": "Blueprint Technical Wipe",
        "camera_rig": "Overhead orthometric gantry camera",
        "lens": "40mm rectilinear",
        "duration_band_sec": (3.0, 5.0),
        "copy_space_zone": "center_clean",
        "recommended_overlay": "blueprint_notebook",
        "prompt_directive": "Overhead orthographic glide across technical schematics with even cool 5600K studio illumination and uncluttered central space.",
    },
}


def get_shot_card_recipe(card_key: str) -> Dict[str, Any]:
    """Return canonical DarkFactory Video-ShotCraft modular shot card recipe."""
    if card_key not in SHOT_CARD_RECIPES:
        raise ValueError(f"Unknown shot card recipe '{card_key}'. Valid: {sorted(SHOT_CARD_RECIPES)}")
    return dict(SHOT_CARD_RECIPES[card_key])


def build_shot_card_directive(card_key: str) -> str:
    """Format a shot card recipe into an injection directive for video prompt generation."""
    card = get_shot_card_recipe(card_key)
    d_min, d_max = card["duration_band_sec"]
    return (
        f"[SHOT CARD: {card['name']}] Rig: {card['camera_rig']} ({card['lens']}) | "
        f"Duration Band: {d_min:.1f}-{d_max:.1f}s | Copy-Space: {card['copy_space_zone']} | "
        f"Overlay Pair: {card['recommended_overlay']} | Kinetic Rule: {card['prompt_directive']}"
    )
