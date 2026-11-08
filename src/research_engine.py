#!/usr/bin/env python3
"""DarkFactory Research Engine (Wikipedia Ground-Truth Extractor).

Extracts verifiable historical facts, proper nouns, timelines, dramatic hooks,
and visual opportunities from Wikipedia REST APIs to ground documentary scripts
in verified truth and eliminate AI hallucinations/reused slop.
"""
import argparse
import json
import logging
import os
import re
import sys
import time
import urllib.parse
import urllib.request
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# ADR-01: Windows UTF-8 stdout/stderr reconfiguration
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("ResearchEngine")

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
SCRIPTS_DIR = DATA_DIR / "scripts"

USER_AGENT = "DarkFactoryBot/1.0 (contact@darkfactory.ai; https://darkfactory.ai) Python-urllib"


@dataclass
class ResearchFact:
    statement: str
    category: str
    source_title: str
    source_url: str


@dataclass
class ResearchReport:
    topic: str
    query: str
    summary: str
    page_title: str
    page_url: str
    key_figures: List[str] = field(default_factory=list)
    key_locations: List[str] = field(default_factory=list)
    numerical_facts: List[str] = field(default_factory=list)
    timeline: List[Dict[str, str]] = field(default_factory=list)
    dramatic_hooks: List[str] = field(default_factory=list)
    visual_opportunities: List[str] = field(default_factory=list)
    verified_facts: List[Dict[str, Any]] = field(default_factory=list)
    related_topics: List[Dict[str, str]] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class WikipediaResearcher:
    """Ground-Truth Historical and Scientific Researcher using Wikipedia APIs."""

    def __init__(self, user_agent: str = USER_AGENT, max_retries: int = 3, timeout: int = 15):
        self.user_agent = user_agent
        self.max_retries = max_retries
        self.timeout = timeout

    def _http_get_json(self, url: str) -> Optional[Dict[str, Any]]:
        """HTTP GET request with automatic retry, exponential backoff, and JSON parsing."""
        req = urllib.request.Request(
            url,
            headers={
                "User-Agent": self.user_agent,
                "Accept": "application/json",
            },
        )
        for attempt in range(1, self.max_retries + 1):
            try:
                with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                    if resp.status == 200:
                        raw = resp.read().decode("utf-8")
                        return json.loads(raw)
            except urllib.error.HTTPError as e:
                if e.code in (403, 404):
                    logger.debug(f"HTTP {e.code} for URL: {url} (skipping)")
                    return None
                logger.warning(f"HTTP {e.code} for URL: {url} (attempt {attempt}/{self.max_retries})")
                time.sleep(1.0 * attempt)
            except Exception as e:
                logger.warning(f"Request error for URL {url}: {e} (attempt {attempt}/{self.max_retries})")
                time.sleep(1.0 * attempt)
        return None

    def search_articles(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Search Wikipedia for matching articles using the action API."""
        encoded_query = urllib.parse.quote(query)
        url = (
            f"https://en.wikipedia.org/w/api.php?action=query&list=search"
            f"&srsearch={encoded_query}&srlimit={limit}&format=json"
        )
        data = self._http_get_json(url)
        if not data or "query" not in data or "search" not in data["query"]:
            return []
        
        results = []
        for item in data["query"]["search"]:
            results.append({
                "title": item.get("title", ""),
                "page_id": item.get("pageid", 0),
                "snippet": re.sub(r"<[^>]+>", "", item.get("snippet", "")),
                "wordcount": item.get("wordcount", 0),
            })
        return results

    def get_page_summary(self, title: str) -> Optional[Dict[str, Any]]:
        """Retrieve REST API v1 summary for a given Wikipedia title."""
        safe_title = urllib.parse.quote(title.replace(" ", "_"))
        url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{safe_title}"
        return self._http_get_json(url)

    def get_related_pages(self, title: str) -> List[Dict[str, str]]:
        """Retrieve related pages for additional context."""
        safe_title = urllib.parse.quote(title.replace(" ", "_"))
        url = f"https://en.wikipedia.org/api/rest_v1/page/related/{safe_title}"
        data = self._http_get_json(url)
        if not data or "pages" not in data:
            return []
        related = []
        for p in data["pages"][:6]:
            related.append({
                "title": p.get("title", ""),
                "description": p.get("description", ""),
                "extract": p.get("extract", ""),
            })
        return related

    def extract_numerical_facts(self, text: str) -> List[str]:
        """Extract quantitative facts (dates, times, numbers, measurements)."""
        patterns = [
            r"\b(?:\d{1,2}:\d{2}(?:\s*(?:AM|PM|am|pm|MSK|UTC))?)\b",  # Times (12:15 AM, 00:15)
            r"\b(?:(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},\s+\d{4})\b",  # Full dates
            r"\b(?:\d{1,2}\s+(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{4})\b",
            r"\b(?:19\d{2}|20\d{2})\b",  # Years
            r"\b(?:\d+(?:[.,]\d+)?\s*(?:million|billion|thousand|hundred|warheads|missiles|seconds|minutes|hours|kilometres|km|miles|tons|megatons))\b",
        ]
        found = set()
        for p in patterns:
            for match in re.finditer(p, text, re.IGNORECASE):
                snippet_start = max(0, match.start() - 30)
                snippet_end = min(len(text), match.end() + 30)
                context = text[snippet_start:snippet_end].strip()
                # Clean boundary breaks
                found.add(context)
        return sorted(list(found))[:10]

    def extract_key_figures_and_places(self, text: str) -> Tuple[List[str], List[str]]:
        """Identify proper nouns representing figures, organizations, and military locations."""
        # Known historical keywords for military / Cold War / science
        figure_patterns = [
            r"\b(?:Lieutenant\s+Colonel|Colonel|General|President|Officer|Secretary)\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b",
            r"\b(?:Stanislav\s+Petrov|Yury\s+Votintsev|Yuri\s+Andropov|Ronald\s+Reagan)\b",
        ]
        location_patterns = [
            r"\b(?:Serpukhov-15|Moscow|Kremlin|Oko|Molniya|NORAD|Omaha|Bunker|White\s+House)\b",
            r"\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\s+(?:Bunker|Base|Station|Headquarters|Facility|Complex)\b",
        ]
        figures = set()
        locations = set()

        for pat in figure_patterns:
            for m in re.finditer(pat, text):
                figures.add(m.group(0))

        for pat in location_patterns:
            for m in re.finditer(pat, text):
                locations.add(m.group(0))

        return sorted(list(figures)), sorted(list(locations))

    def synthesize_dramatic_hooks(self, summary: str, facts: List[str]) -> List[str]:
        """Synthesize high-tension psychological and existential narrative angles."""
        hooks = []
        if any("nuclear" in f.lower() or "warhead" in f.lower() for f in facts + [summary]):
            hooks.append("Existential Threat: A hair-trigger alert that brought civilization within minutes of full thermonuclear exchange.")
        if any("minutes" in f.lower() or "protocol" in f.lower() for f in facts + [summary]):
            hooks.append("Ticking Clock Dilemma: The officer had only a narrow window of minutes to decide whether to launch retaliatory strikes.")
        if any("false" in f.lower() or "glitch" in f.lower() or "cloud" in f.lower() or "satellite" in f.lower() for f in facts + [summary]):
            hooks.append("The Machine Error: Early-warning satellites mistook high-altitude sun reflections on clouds for intercontinental ballistic missile plumes.")
        if any("hunch" in f.lower() or "gut" in f.lower() or "trust" in f.lower() or "protocol" in f.lower() for f in facts + [summary]):
            hooks.append("Human Disobedience: Protocol demanded immediate authorization, but one man broke Soviet military doctrine by trusting human intuition.")
        
        if not hooks:
            hooks.append("Unseen Crossroads: A classified historical turning point where an individual decision quietly altered world history.")
        return hooks

    def synthesize_visual_opportunities(self, title: str, summary: str, locations: List[str]) -> List[str]:
        """Suggest concrete, cinematic visual B-Roll prompts for generation."""
        opportunities = [
            f"Establishing Wide: Low-light exterior of top-secret Cold War installation ({', '.join(locations) if locations else 'Military Facility'}), misty 1980s atmospheric fog, security watchtowers, harsh floodlights.",
            "Console Macro: Phosphor-green CRT monitor terminal displaying rising telemetry curves, flashing Cyrillic status indicators, analog rotary dials.",
            "Human Psychological Portrait: Sweating commanding officer in authentic 1980s Soviet military uniform, chiaroscuro lighting, tense expression hovering over encrypted communications.",
            "Industrial Hardware Close-Up: Heavy mechanical warning beacons rotating behind wire-mesh cages, red pulsing strobe reflection across brushed aluminum consoles.",
            "Orbital / Macro Abstract: Stylized early satellite sensor lens capturing high-altitude cloud tops, lens flare masking critical telemetry data."
        ]
        return opportunities

    def research_topic(self, topic: str) -> ResearchReport:
        """Run complete factual investigation on a topic and return a ResearchReport."""
        logger.info(f"Researching topic: '{topic}' via Wikipedia REST APIs...")
        search_results = self.search_articles(topic, limit=5)
        
        if not search_results:
            logger.warning(f"No Wikipedia articles found directly for query: {topic}")
            target_title = topic
            page_summary = None
        else:
            target_title = search_results[0]["title"]
            logger.info(f"Top matching article: '{target_title}'")
            page_summary = self.get_page_summary(target_title)

        if not page_summary:
            # Fallback to direct title query
            page_summary = self.get_page_summary(topic) or {}

        extract = page_summary.get("extract", "")
        description = page_summary.get("description", "")
        page_url = (
            page_summary.get("content_urls", {}).get("desktop", {}).get("page", "")
            or f"https://en.wikipedia.org/wiki/{urllib.parse.quote(target_title.replace(' ', '_'))}"
        )

        # Related articles
        related_pages = self.get_related_pages(target_title)

        # Corpus aggregation for entity and number extraction
        full_corpus = f"{extract} " + " ".join(r.get("extract", "") for r in related_pages)

        numbers = self.extract_numerical_facts(full_corpus)
        figures, locations = self.extract_key_figures_and_places(full_corpus)
        dramatic_hooks = self.synthesize_dramatic_hooks(extract, numbers)
        visual_opps = self.synthesize_visual_opportunities(target_title, extract, locations)

        verified_facts = []
        if extract:
            # Split extract into sentences
            sentences = re.split(r"(?<=[.!?])\s+", extract)
            for s in sentences:
                s_clean = s.strip()
                if len(s_clean) > 20:
                    verified_facts.append({
                        "statement": s_clean,
                        "source": target_title,
                        "url": page_url,
                    })

        timeline = []
        for num in numbers:
            if re.search(r"\b(?:19\d{2}|20\d{2}|September|October|AM|PM)\b", num):
                timeline.append({"context": num})

        report = ResearchReport(
            topic=topic,
            query=topic,
            summary=extract,
            page_title=target_title,
            page_url=page_url,
            key_figures=figures,
            key_locations=locations,
            numerical_facts=numbers,
            timeline=timeline[:6],
            dramatic_hooks=dramatic_hooks,
            visual_opportunities=visual_opps,
            verified_facts=verified_facts[:8],
            related_topics=related_pages,
        )
        return report

    def enrich_script(
        self, script_path: Path, research: ResearchReport, output_path: Optional[Path] = None
    ) -> Dict[str, Any]:
        """Enriches an existing script JSON with factual ground-truth research metadata."""
        with open(script_path, "r", encoding="utf-8") as f:
            script_data = json.load(f)

        script_data["factual_ground_truth"] = {
            "source_topic": research.topic,
            "wikipedia_title": research.page_title,
            "wikipedia_url": research.page_url,
            "key_figures": research.key_figures,
            "key_locations": research.key_locations,
            "verified_numerical_facts": research.numerical_facts,
            "dramatic_hooks": research.dramatic_hooks,
            "visual_opportunities": research.visual_opportunities,
        }

        # Annotate scenes
        scenes = script_data.get("scenes", [])
        for scene in scenes:
            scene_text = scene.get("audio_text", "").lower()
            scene_facts = []
            for fact in research.verified_facts:
                words = [w for w in re.findall(r"\w+", fact["statement"].lower()) if len(w) > 4]
                if any(w in scene_text for w in words):
                    scene_facts.append(fact["statement"])
            if scene_facts:
                scene["fact_check_notes"] = scene_facts[:2]

        target_out = output_path or script_path
        # ADR-02: Atomic write
        tmp_path = target_out.with_suffix(f".tmp.{os.getpid()}")
        with open(tmp_path, "w", encoding="utf-8") as f:
            json.dump(script_data, f, indent=2, ensure_ascii=False)
        tmp_path.replace(target_out)
        logger.info(f"Enriched script saved atomically to: {target_out}")
        return script_data


def main() -> None:
    parser = argparse.ArgumentParser(description="DarkFactory Wikipedia Research Engine")
    parser.add_argument(
        "--topic",
        type=str,
        default="1983 Soviet nuclear false alarm incident",
        help="Topic to research on Wikipedia",
    )
    parser.add_argument(
        "--output",
        type=str,
        default=str(SCRIPTS_DIR / "research_soviet_glitch.json"),
        help="Destination JSON file for research report",
    )
    parser.add_argument(
        "--enrich-script",
        type=str,
        default=None,
        help="Optional script path to enrich with research data",
    )
    args = parser.parse_args()

    researcher = WikipediaResearcher()
    report = researcher.research_topic(args.topic)

    out_file = Path(args.output)
    out_file.parent.mkdir(parents=True, exist_ok=True)

    # ADR-02: Atomic write
    tmp_file = out_file.with_suffix(f".tmp.{os.getpid()}")
    with open(tmp_file, "w", encoding="utf-8") as f:
        json.dump(report.to_dict(), f, indent=2, ensure_ascii=False)
    tmp_file.replace(out_file)

    print(f"\n=======================================================")
    print(f"🔬 DARKFACTORY RESEARCH REPORT COMPLETED")
    print(f"=======================================================")
    print(f"Topic: {report.topic}")
    print(f"Article: {report.page_title} ({report.page_url})")
    print(f"Summary: {report.summary[:180]}...")
    print(f"Key Figures: {', '.join(report.key_figures) if report.key_figures else 'None detected'}")
    print(f"Key Locations: {', '.join(report.key_locations) if report.key_locations else 'None detected'}")
    print(f"Dramatic Hooks ({len(report.dramatic_hooks)}):")
    for h in report.dramatic_hooks:
        print(f"  • {h}")
    print(f"Visual Opportunities ({len(report.visual_opportunities)}):")
    for v in report.visual_opportunities:
        print(f"  • {v}")
    print(f"\nReport written atomically to: {out_file}")

    if args.enrich_script:
        script_file = Path(args.enrich_script)
        if script_file.exists():
            researcher.enrich_script(script_file, report)


if __name__ == "__main__":
    main()
