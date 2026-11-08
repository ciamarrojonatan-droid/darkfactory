#!/usr/bin/env python3
"""Unit tests for DarkFactory Wikipedia Research Engine."""
import json
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

# ADR-01: Windows UTF-8 stdout/stderr
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

# Add src to sys.path
SRC_DIR = Path(__file__).resolve().parent.parent / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from research_engine import ResearchReport, WikipediaResearcher


def test_researcher_initialization():
    r = WikipediaResearcher(user_agent="TestAgent/1.0", max_retries=2, timeout=5)
    assert r.user_agent == "TestAgent/1.0"
    assert r.max_retries == 2
    assert r.timeout == 5


def test_extract_numerical_facts():
    r = WikipediaResearcher()
    sample_text = (
        "On September 26, 1983, at 12:15 AM, the Oko early warning system detected "
        "5 intercontinental ballistic missiles approaching. Lieutenant Colonel Stanislav Petrov "
        "had exactly 20 minutes to authorize retaliatory action that would endanger 300 million people."
    )
    facts = r.extract_numerical_facts(sample_text)
    assert len(facts) > 0
    # Check that key temporal or quantitative markers are detected
    has_date_or_number = any("1983" in f or "September" in f or "million" in f or "minutes" in f for f in facts)
    assert has_date_or_number


def test_extract_key_figures_and_places():
    r = WikipediaResearcher()
    sample_text = (
        "Stanislav Petrov sat in the Serpukhov-15 bunker outside Moscow. "
        "General Yury Votintsev later commended him."
    )
    figures, locations = r.extract_key_figures_and_places(sample_text)
    assert "Stanislav Petrov" in figures
    assert any("Serpukhov-15" in loc or "Moscow" in loc for loc in locations)


def test_synthesize_dramatic_hooks():
    r = WikipediaResearcher()
    summary = "A false alarm occurred when sun reflections on high-altitude clouds simulated missiles."
    facts = ["five nuclear warheads were indicated", "20 minutes to respond"]
    hooks = r.synthesize_dramatic_hooks(summary, facts)
    assert len(hooks) >= 2
    assert any("Thermonuclear" in h or "Existential" in h for h in hooks)
    assert any("Machine Error" in h or "reflections" in h for h in hooks)


@patch.object(WikipediaResearcher, "_http_get_json")
def test_research_topic_mocked(mock_http, tmp_path):
    r = WikipediaResearcher()

    def side_effect(url):
        if "action=query" in url:
            return {
                "query": {
                    "search": [
                        {
                            "title": "1983 Soviet nuclear false alarm incident",
                            "pageid": 12345,
                            "snippet": "Incident involving Stanislav Petrov",
                            "wordcount": 3000,
                        }
                    ]
                }
            }
        elif "page/summary" in url:
            return {
                "title": "1983 Soviet nuclear false alarm incident",
                "extract": "On 26 September 1983, Stanislav Petrov prevented nuclear war at Serpukhov-15.",
                "description": "Historical Cold War incident",
                "content_urls": {
                    "desktop": {"page": "https://en.wikipedia.org/wiki/1983_incident"}
                },
            }
        elif "page/related" in url:
            return {"pages": []}
        return None

    mock_http.side_effect = side_effect
    report = r.research_topic("1983 Soviet nuclear false alarm")

    assert isinstance(report, ResearchReport)
    assert report.page_title == "1983 Soviet nuclear false alarm incident"
    assert "Stanislav Petrov" in report.key_figures or "Stanislav Petrov" in report.summary
    assert len(report.dramatic_hooks) > 0
    assert len(report.visual_opportunities) > 0


def test_enrich_script_atomic(tmp_path):
    r = WikipediaResearcher()
    script_file = tmp_path / "test_script.json"
    dummy_data = {
        "title": "Test Documentary",
        "scenes": [
            {
                "scene_id": 1,
                "audio_text": "Stanislav Petrov was in the bunker when alarms sounded.",
            }
        ],
    }
    with open(script_file, "w", encoding="utf-8") as f:
        json.dump(dummy_data, f)

    report = ResearchReport(
        topic="Stanislav Petrov",
        query="Stanislav Petrov",
        summary="Summary of Stanislav Petrov incident",
        page_title="Stanislav Petrov",
        page_url="https://en.wikipedia.org/wiki/Stanislav_Petrov",
        key_figures=["Stanislav Petrov"],
        key_locations=["Serpukhov-15"],
        numerical_facts=["September 26, 1983"],
        timeline=[{"context": "September 26, 1983"}],
        dramatic_hooks=["Tension at the bunker"],
        visual_opportunities=["Bunker shot"],
        verified_facts=[
            {
                "statement": "Stanislav Petrov was the duty officer at the command center.",
                "source": "Wikipedia",
                "url": "http://example.com",
            }
        ],
    )

    enriched = r.enrich_script(script_file, report)
    assert "factual_ground_truth" in enriched
    assert enriched["factual_ground_truth"]["source_topic"] == "Stanislav Petrov"
    assert script_file.exists()
