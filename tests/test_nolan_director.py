#!/usr/bin/env python3
"""Unit tests for DarkFactory Nolan History Director."""
import json
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

# ADR-01: Windows UTF-8 stdout/stderr
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

SRC_DIR = Path(__file__).resolve().parent.parent / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from nolan_director import NolanEpisodeManifest, NolanHistoryDirector
from research_engine import ResearchReport, WikipediaResearcher


def test_nolan_director_initialization():
    director = NolanHistoryDirector()
    assert director.researcher is not None


def test_generate_packaging():
    director = NolanHistoryDirector()
    mock_report = ResearchReport(
        topic="Stanislav Petrov Incident",
        query="Stanislav Petrov Incident",
        summary="Soviet false alarm incident of 1983",
        page_title="1983 Soviet nuclear false alarm incident",
        page_url="https://en.wikipedia.org/wiki/test",
    )
    packaging = director.generate_packaging("Stanislav Petrov Incident", mock_report)
    assert "logline" in packaging
    assert len(packaging["titles"]) == 3
    assert "thumbnail_concept" in packaging
    assert "title_overlay_text" in packaging["thumbnail_concept"]
    assert "IMAX" in packaging["thumbnail_concept"]["visual_composition"]


def test_generate_timeline_architecture():
    director = NolanHistoryDirector()
    mock_report = ResearchReport(
        topic="Chernobyl",
        query="Chernobyl",
        summary="Nuclear disaster",
        page_title="Chernobyl disaster",
        page_url="https://en.wikipedia.org/wiki/test",
    )
    timelines = director.generate_timeline_architecture(mock_report)
    assert "thread_a" in timelines
    assert "thread_b" in timelines
    assert "convergence_point" in timelines
    assert "Slow Clock" in timelines["thread_a"]
    assert "Rapid Clock" in timelines["thread_b"]


@patch.object(WikipediaResearcher, "research_topic")
def test_direct_episode_mocked(mock_research):
    mock_report = ResearchReport(
        topic="1983 Soviet nuclear false alarm",
        query="1983 Soviet nuclear false alarm",
        summary="On 26 September 1983, the Soviet Oko system reported missile launches.",
        page_title="1983 Soviet nuclear false alarm incident",
        page_url="https://en.wikipedia.org/wiki/test",
        key_figures=["Stanislav Petrov"],
        key_locations=["Serpukhov-15"],
        numerical_facts=["September 26, 1983", "five missiles", "20 minutes"],
    )
    mock_research.return_value = mock_report

    director = NolanHistoryDirector()
    manifest = director.direct_episode("1983 Soviet nuclear false alarm")

    assert isinstance(manifest, NolanEpisodeManifest)
    assert len(manifest.scenes) >= 3

    for sc in manifest.scenes:
        assert "scene_id" in sc
        assert "dual_shot" in sc
        assert "shot_a" in sc["dual_shot"]
        assert "shot_b" in sc["dual_shot"]
        assert "sound_design" in sc
        assert len(sc["sound_design"]["sfx_triggers"]) > 0
        assert "cosyvoice_instruct" in sc
        # Check Nolan photographic prompt tags
        prompt_a = sc["dual_shot"]["shot_a"]["prompt"]
        assert "--ar 16:9" in prompt_a or "IMAX" in prompt_a or "Hoyte van Hoytema" in prompt_a


def test_export_manifest_atomic(tmp_path):
    director = NolanHistoryDirector()
    manifest = NolanEpisodeManifest(
        project_id="test_episode",
        title="Test Episode Title",
        logline="A test logline.",
        niche="History",
        target_market="US",
        packaging={"titles": ["Title 1"]},
        timeline_architecture={"thread_a": "A", "thread_b": "B"},
        voice_engine={"provider": "Kokoro-82M"},
        scenes=[{"scene_id": 1, "audio_text": "Narration"}],
    )

    out_file = tmp_path / "nolan_manifest_test.json"
    saved_path = director.export_manifest(manifest, out_file)

    assert saved_path.exists()
    with open(saved_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert data["project_id"] == "test_episode"
    assert data["title"] == "Test Episode Title"
