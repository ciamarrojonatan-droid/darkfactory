#!/usr/bin/env python3
"""Unit tests for DarkFactory YouTube Compliance & Safety QC Engine."""
import json
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch
import pytest

# ADR-01: Windows UTF-8 stdout/stderr
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

SRC_DIR = Path(__file__).resolve().parent.parent / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from youtube_compliance_qc import BBC_PBS_DISCLAIMER, ComplianceStatus, YouTubeComplianceQC
from youtube_publisher import YouTubePublisher


def test_clean_metadata_audit():
    qc = YouTubeComplianceQC()
    title = "The 1983 Soviet Glitch: 20 Minutes to Armageddon"
    desc = "A detailed historical documentary about Stanislav Petrov and the Oko satellite network."
    tags = ["history", "soviet", "cold war", "documentary"]

    rem_title, rem_desc, issues, has_crit = qc.audit_metadata(title, desc, tags)

    assert not has_crit
    assert BBC_PBS_DISCLAIMER in rem_desc
    assert "Stanislav Petrov" in rem_desc


def test_yellow_dollar_edsa_remediation():
    qc = YouTubeComplianceQC()
    title = "The Terrifying Slaughter of the Frontline"
    desc = "Soldiers on a suicide mission suffered a bloodbath in the final battle."
    tags = ["war"]

    rem_title, rem_desc, issues, has_crit = qc.audit_metadata(title, desc, tags)

    assert not has_crit
    assert "casualties" in rem_title.lower()
    assert "high-risk operation" in rem_desc.lower()
    assert "severe confrontation" in rem_desc.lower()
    assert any("Auto-remediated" in (i.remediation_applied or "") for i in issues)


def test_strict_blocker_detection():
    qc = YouTubeComplianceQC()
    title = "Classified Secrets: How to build a bomb with nuclear physics"
    desc = "Technical assembly."

    rem_title, rem_desc, issues, has_crit = qc.audit_metadata(title, desc, [])
    assert has_crit is True
    assert any(i.severity == "CRITICAL" for i in issues)


def test_tag_stuffing_removal():
    qc = YouTubeComplianceQC()
    title = "Valid Title"
    desc = (
        "Legitimate opening paragraph.\n"
        "cold war, nuclear, russia, america, moscow, submarine, missiles, radar, alarm, attack, war\n"
        "Closing historical note."
    )

    rem_title, rem_desc, issues, has_crit = qc.audit_metadata(title, desc, [])
    assert "cold war, nuclear, russia" not in rem_desc
    assert any("Tag-stuffing" in i.message for i in issues)


def test_thumbnail_oversize_rejection(tmp_path):
    qc = YouTubeComplianceQC()
    oversized_thumb = tmp_path / "huge_thumb.jpg"
    # Write > 2.1 MB
    oversized_thumb.write_bytes(b"0" * (int(2.2 * 1024 * 1024)))

    ok, issues = qc.audit_thumbnail(oversized_thumb)
    assert ok is False
    assert any("exceeds YouTube 2.0 MB ceiling" in i.message for i in issues)


def test_dispute_kit_generation(tmp_path):
    dispute_dir = tmp_path / "disputes"
    qc = YouTubeComplianceQC(dispute_dir=dispute_dir)

    kit_path = qc.generate_dispute_kit(
        project_id="soviet_glitch_01",
        title="The 1983 Soviet Glitch",
        sound_package={"google_flow_ost_prompt": "Low solo cello suspense drone"},
    )

    assert kit_path.exists()
    content = kit_path.read_text(encoding="utf-8")
    assert "LEGAL COUNTER-NOTIFICATION & CONTENT ID DISPUTE DOSSIER" in content
    assert "Google Flow Music" in content
    assert "MMAudio" in content
    assert "17 U.S. Code § 107" in content


def test_evaluate_full_episode_quarantine(tmp_path):
    q_dir = tmp_path / "quarantine"
    qc = YouTubeComplianceQC(quarantine_dir=q_dir)

    dummy_video = tmp_path / "video.mp4"
    dummy_video.write_bytes(b"video_bytes")

    report = qc.evaluate_full_episode(
        project_id="forbidden_project",
        title="Classified: How to make a warhead weapon",
        description="Dangerous content",
        tags=["danger"],
        video_path=dummy_video,
    )

    assert report.status == ComplianceStatus.BLOCKED_QUARANTINE
    assert report.compliance_score < 60
    assert report.quarantine_path is not None
    assert Path(report.quarantine_path).exists()


def test_youtube_publisher_blocks_on_compliance_failure(tmp_path):
    dummy_video = tmp_path / "vid.mp4"
    dummy_video.write_bytes(b"video_content")

    pub = YouTubePublisher(history_file=tmp_path / "hist.json")

    # Should raise RuntimeError because title contains strict blocker
    with pytest.raises(RuntimeError) as exc_info:
        pub.upload_video(
            video_path=dummy_video,
            title="Classified: How to assemble a weapon device",
            description="Bad content",
            dry_run=True,
            skip_qc=False,
        )
    assert "UPLOAD BLOCKED by YouTube Compliance QC" in str(exc_info.value)


def test_self_certification_manifest_generation():
    qc = YouTubeComplianceQC()
    manifest = qc.generate_self_certification_manifest(
        project_id="test_cert",
        title="The 1983 Soviet Nuclear Alert",
        description="Historical documentary analyzing Serpukhov-15 declassified telemetry.",
    )
    assert manifest["project_id"] == "test_cert"
    assert "Green Dollar Sign" in manifest["projected_monetization_status"]
    assert "inappropriate_language" in manifest["self_certification_questionnaire"]
    assert manifest["self_certification_questionnaire"]["altered_or_synthetic_content"]["disclosure_checkbox"] is True


def test_edsa_framing_evaluation():
    qc = YouTubeComplianceQC()
    res = qc.evaluate_edsa_framing(
        title="The Classified Cold War Incident",
        description="Historical archival documentary and analysis of the 1983 Soviet radar telemetry.",
    )
    assert res["has_edsa_protection"] is True
    assert res["status"] == "EDSA_PROTECTED"
    assert "documentary" in res["anchors_detected"]

