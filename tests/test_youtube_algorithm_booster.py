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


def test_video_chapters_generation():
    booster = YouTubeAlgorithmBooster()

    # Test short video (< 60s)
    short_chapters = booster.generate_video_chapters(video_duration_sec=40.0)
    assert len(short_chapters) >= 3
    assert short_chapters[0]["timestamp"] == "00:00"
    assert short_chapters[0]["time_sec"] == 0.0
    for i in range(1, len(short_chapters)):
        assert short_chapters[i]["time_sec"] - short_chapters[i - 1]["time_sec"] >= 10.0

    # Test long video (> 60s)
    long_chapters = booster.generate_video_chapters(video_duration_sec=600.0)
    assert len(long_chapters) >= 3
    assert long_chapters[0]["timestamp"] == "00:00"
    for ch in long_chapters:
        assert "title_en" in ch
        assert "title_es" in ch
        assert "title_pt" in ch
        assert "title_ja" in ch
        assert "title_ko" in ch
        assert "title_zh" in ch


def test_video_chapters_formatting():
    booster = YouTubeAlgorithmBooster()
    chapters = booster.generate_video_chapters(video_duration_sec=40.0)

    desc_en = booster.format_chapters_for_description(chapters, lang="en")
    assert "⏱️ CHAPTERS" in desc_en
    assert "00:00 Prologue" in desc_en

    desc_ja = booster.format_chapters_for_description(chapters, lang="ja")
    assert "⏱️ チャプター" in desc_ja
    assert "00:00 プロローグ" in desc_ja

    desc_pt = booster.format_chapters_for_description(chapters, lang="pt-BR")
    assert "⏱️ CAPÍTULOS" in desc_pt
    assert "00:00 Prólogo" in desc_pt


def test_multilingual_dubbing_manifest(tmp_path):
    dub_dir = tmp_path / "dubbing"
    booster = YouTubeAlgorithmBooster(dubbing_dir=dub_dir)

    dummy_audio = tmp_path / "master.mp3"
    dummy_audio.write_bytes(b"dummy_mp3_audio_bytes")

    manifest = booster.generate_multilingual_dubbing_manifest(
        project_id="pilot_audio_test",
        base_audio_file=dummy_audio,
        output_dir=dub_dir,
    )

    assert "en" in manifest
    assert "es" in manifest
    assert "pt-BR" in manifest
    assert "de" in manifest
    assert "ja" in manifest
    assert "ko" in manifest
    assert "zh-Hans" in manifest

    for lang, track in manifest.items():
        assert track["target_lufs"] == -14.0
        assert track["true_peak_max_dbtp"] == -1.0
        assert track["sample_rate_hz"] == 48000
        assert track["channels"] == 2
        assert Path(track["file_path"]).exists()


def test_pinned_engagement_comment():
    booster = YouTubeAlgorithmBooster()
    comment_en = booster.generate_pinned_engagement_comment("test_proj", "The 1983 Soviet Glitch", "en")
    assert "HISTORICAL DILEMMA" in comment_en
    assert "Subscribe to DarkFactory" in comment_en

    comment_pt = booster.generate_pinned_engagement_comment("test_proj", "The 1983 Soviet Glitch", "pt-BR")
    assert "DILEMA HISTÓRICO" in comment_pt
    assert "Tenente-Coronel Petrov" in comment_pt

    comment_ja = booster.generate_pinned_engagement_comment("test_proj", "The 1983 Soviet Glitch", "ja")
    assert "ペトロフ中佐" in comment_ja


def test_community_post_blueprint():
    booster = YouTubeAlgorithmBooster()
    poll = booster.generate_community_post_blueprint("test_proj", "The 1983 Soviet Glitch")
    assert poll["poll_type"] == "INTERACTIVE_DEBATE_POLL"
    assert len(poll["options"]) == 4
    assert any("Petrov" in opt for opt in poll["options"])


def test_top_hashtags():
    booster = YouTubeAlgorithmBooster()
    tags_en = booster.generate_top_hashtags("en")
    assert len(tags_en) == 3
    assert "#ColdWar" in tags_en

    tags_ja = booster.generate_top_hashtags("ja")
    assert len(tags_ja) == 3
    assert "#冷戦" in tags_ja


def test_google_search_key_moments_json_ld():
    booster = YouTubeAlgorithmBooster()
    chapters = booster.generate_video_chapters(video_duration_sec=100.0)
    json_ld = booster.generate_key_moments_json_ld(
        project_id="test_key_moments",
        title="1983 Soviet Crisis",
        description="Historic documentary",
        duration_sec=100.0,
        chapters=chapters,
        video_url="https://youtu.be/test_key_moments",
    )
    assert json_ld["@type"] == "VideoObject"
    assert len(json_ld["hasPart"]) == len(chapters)
    assert json_ld["hasPart"][0]["@type"] == "Clip"
    assert json_ld["hasPart"][0]["startOffset"] == 0
