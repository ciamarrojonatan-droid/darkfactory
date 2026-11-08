#!/usr/bin/env python3
"""Unit tests for DarkFactory YouTube Algorithm & Distribution Optimizer."""
import json
import sys
from pathlib import Path

# ADR-01: Windows UTF-8 stdout/stderr
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

SRC_DIR = Path(__file__).resolve().parent.parent / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from youtube_algorithm_booster import YouTubeAlgorithmBooster


def test_multilingual_localizations_generation():
    booster = YouTubeAlgorithmBooster()
    en_title = "The 1983 Soviet Glitch: 20 Minutes to Armageddon"
    en_desc = "Official documentary on Stanislav Petrov."

    localizations = booster.generate_multilingual_localizations(en_title, en_desc)

    assert "es" in localizations
    assert "pt-BR" in localizations
    assert "de" in localizations
    assert "ja" in localizations
    assert "ko" in localizations
    assert "zh-Hans" in localizations

    assert "El Error Soviético" in localizations["es"]["title"]
    assert "O Erro Soviético" in localizations["pt-BR"]["title"]
    assert "Der Sowjet-Fehler" in localizations["de"]["title"]
    assert "1983年ソ連核警報誤報事件" in localizations["ja"]["title"]
    assert "1983년 소련 핵 오보 사건" in localizations["ko"]["title"]
    assert "1983年苏联核警报假警事件" in localizations["zh-Hans"]["title"]

    for lang, meta in localizations.items():
        assert len(meta["title"]) <= 100
        assert len(meta["description"]) <= 5000
        assert any(keyword in meta["description"] for keyword in ["RECREACIÓN", "RECONSTITUIÇÃO", "REKONSTRUKTION", "歴史アーカイブ再現", "역사적 아카이브 재구성", "历史档案还原"])


def test_multilingual_subtitles_generation(tmp_path):
    booster = YouTubeAlgorithmBooster()

    dummy_srt = tmp_path / "test_en.srt"
    dummy_srt.write_text(
        "1\n00:00:00,000 --> 00:00:05,000\nAt 12:15 AM on September 26, 1983 a red siren illuminated a top-secret Soviet bunker outside Moscow.\n",
        encoding="utf-8",
    )

    out_subs = tmp_path / "subs_out"
    tracks = booster.generate_multilingual_subtitles(base_srt_file=dummy_srt, output_dir=out_subs)

    assert "en" in tracks
    assert "es" in tracks
    assert "pt-BR" in tracks
    assert "ja" in tracks
    assert "ko" in tracks
    assert "zh-Hans" in tracks

    es_file = tracks["es"]
    assert es_file.exists()
    es_content = es_file.read_text(encoding="utf-8")
    assert "A las 12:15 AM del 26 de septiembre de 1983" in es_content

    pt_file = tracks["pt-BR"]
    assert pt_file.exists()
    pt_content = pt_file.read_text(encoding="utf-8")
    assert "Às 00h15 de 26 de setembro de 1983" in pt_content

    ja_file = tracks["ja"]
    assert ja_file.exists()
    assert "1983年9月26日午前0時15分" in ja_file.read_text(encoding="utf-8")

    ko_file = tracks["ko"]
    assert ko_file.exists()
    assert "1983년 9월 26일 오전 0시 15분" in ko_file.read_text(encoding="utf-8")

    zh_file = tracks["zh-Hans"]
    assert zh_file.exists()
    assert "1983年9月26日凌晨0点15分" in zh_file.read_text(encoding="utf-8")


def test_cards_and_end_screens_blueprint():
    booster = YouTubeAlgorithmBooster()
    duration = 100.0  # 100 seconds
    blueprint = booster.generate_cards_and_end_screens_blueprint(duration)

    assert blueprint["info_card"]["trigger_sec"] == 50.0
    assert blueprint["info_card"]["trigger_timestamp"] == "00:50"

    assert blueprint["end_screen"]["start_sec"] == 80.0
    assert blueprint["end_screen"]["start_timestamp"] == "01:20"
    assert len(blueprint["end_screen"]["elements"]) == 3


def test_triple_thumbnail_package():
    booster = YouTubeAlgorithmBooster()
    variants = booster.generate_triple_thumbnail_package(Path("data/test_thumb.jpg"))

    assert len(variants) == 3
    assert "Thumbnail A" in variants[0]["variant"]
    assert "Thumbnail B" in variants[1]["variant"]
    assert "Thumbnail C" in variants[2]["variant"]
    assert all("text_overlay" in v for v in variants)


def test_build_complete_algorithm_package(tmp_path):
    pkg_dir = tmp_path / "packages"
    booster = YouTubeAlgorithmBooster(booster_dir=pkg_dir)

    dummy_srt = tmp_path / "sample.srt"
    dummy_srt.write_text("1\n00:00:00,000 --> 00:00:02,000\nHello world\n", encoding="utf-8")

    package = booster.build_complete_algorithm_package(
        project_id="pilot_test",
        english_title="The 1983 Soviet Glitch: 20 Minutes to Armageddon",
        english_description="Full description.",
        video_duration_sec=60.0,
        base_srt_file=dummy_srt,
        master_video_id="yt_test_id_999",
    )

    assert package["algorithm_score"] >= 95
    assert "localizations" in package
    assert "subtitles_tracks" in package
    assert package["shorts_related_video_link"]["target_master_video_id"] == "yt_test_id_999"

    saved_pkg_file = pkg_dir / "pilot_test_algorithm_package.json"
    assert saved_pkg_file.exists()
