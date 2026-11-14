#!/usr/bin/env python3
"""DarkFactory Pre-Flight Authentication & Session Gate.

Enforces persistent authenticated sessions for:
1. Google Flow (flow.google.com) — Gemini Omni Flash 1.2 & DeepMind Veo 3.1
2. RunningHub (runninghub.ai) — Accounts 4 (CosyVoice), 5 (MiniMax Music), 7 (MiniMax H3)

Operational Rules:
- Before any asset (video, audio, foley, motion) is generated in the pipeline,
  the orchestrator verifies that persistent sessions are authenticated.
- If a session is missing or expired, the gate automatically launches a headful
  Chromium browser window for 1-time manual login by the operator, polls for success,
  and saves storage_state.json and browser profiles.
- Subsequent pipeline runs operate completely headless with persistent cookies.
"""
import argparse
import json
import logging
import os
import sys
import time
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

# ADR-01: Windows UTF-8 stdout/stderr reconfiguration
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("AuthGate")

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
CHROME_SESSIONS_DIR = PROJECT_ROOT / "chrome_session"
GOOGLE_FLOW_SESSION_DIR = CHROME_SESSIONS_DIR / "google_flow"
RUNNINGHUB_SESSION_DIR = CHROME_SESSIONS_DIR / "runninghub"

GOOGLE_FLOW_URL = os.getenv("GOOGLE_FLOW_URL", "https://flow.google.com")
RUNNINGHUB_URL = os.getenv("RUNNINGHUB_URL", "https://www.runninghub.ai")


def ensure_session_dirs() -> None:
    """Ensure persistent session storage directories exist."""
    GOOGLE_FLOW_SESSION_DIR.mkdir(parents=True, exist_ok=True)
    RUNNINGHUB_SESSION_DIR.mkdir(parents=True, exist_ok=True)


def is_google_flow_authenticated(page) -> bool:
    """Check if the current Google Flow page state indicates an authenticated user."""
    url = page.url.lower()
    # If redirected to Google Accounts login or signin prompt
    if "accounts.google.com" in url or "signin" in url:
        return False

    # Check for authenticated indicators (e.g., flow project workspace, user profile, create prompt bar)
    try:
        content = page.content().lower()
        if "sign in" in content and "create" not in content:
            # Might be unauthenticated landing page
            btn_signin = page.query_selector('a[href*="accounts.google.com"], button:has-text("Sign in")')
            if btn_signin and btn_signin.is_visible():
                return False

        # If on flow domain and no sign-in prompt is blocking
        if "flow.google.com" in url or "labs.google" in url:
            return True
    except Exception:
        pass
    return False


def is_runninghub_authenticated(page) -> bool:
    """Check if the current RunningHub page state indicates an active session."""
    url = page.url.lower()
    if "/login" in url or "auth" in url:
        return False

    try:
        # Check for profile avatar, points balance, or workspace elements
        user_menu = page.query_selector('.user-avatar, .avatar, [class*="avatar"], [class*="user-profile"], [class*="points"]')
        if user_menu:
            return True
        content = page.content().lower()
        if "workspace" in url or "workbench" in content or "pontos" in content or "credits" in content:
            return True
    except Exception:
        pass
    return False


def check_google_flow_session(session_dir: Optional[Path] = None, headless: bool = True, timeout_sec: int = 15) -> bool:
    """Verify whether Google Flow session is authenticated."""
    from playwright.sync_api import sync_playwright

    s_dir = session_dir or GOOGLE_FLOW_SESSION_DIR
    ensure_session_dirs()
    state_file = s_dir / "storage_state.json"
    if not (s_dir / "Default").exists() and not state_file.exists():
        logger.warning("Google Flow session directory has no saved profile or storage state.")
        return False

    logger.info("Checking Google Flow session validity...")
    try:
        with sync_playwright() as p:
            context = p.chromium.launch_persistent_context(
                user_data_dir=str(s_dir),
                headless=headless,
                args=["--disable-blink-features=AutomationControlled"],
            )
            page = context.new_page()
            page.goto(GOOGLE_FLOW_URL, timeout=timeout_sec * 1000)
            page.wait_for_load_state("domcontentloaded", timeout=timeout_sec * 1000)
            time.sleep(2)
            auth = is_google_flow_authenticated(page)
            context.close()
            return auth
    except Exception as exc:
        logger.warning(f"Error checking Google Flow session: {exc}")
        return False


def check_runninghub_session(session_dir: Optional[Path] = None, headless: bool = True, timeout_sec: int = 15) -> bool:
    """Verify whether RunningHub session is authenticated."""
    from playwright.sync_api import sync_playwright

    s_dir = session_dir or RUNNINGHUB_SESSION_DIR
    ensure_session_dirs()
    state_file = s_dir / "storage_state.json"
    if not (s_dir / "Default").exists() and not state_file.exists():
        logger.warning("RunningHub session directory has no saved profile or storage state.")
        return False

    # Fast verification if valid storage_state.json with RunningHub cookies exists
    if state_file.exists():
        try:
            state_data = json.loads(state_file.read_text(encoding="utf-8"))
            cookies = state_data.get("cookies", [])
            for c in cookies:
                if "runninghub" in c.get("domain", "").lower() or "token" in c.get("name", "").lower():
                    return True
        except Exception:
            pass

    logger.info("Checking RunningHub session validity...")
    try:
        with sync_playwright() as p:
            context = p.chromium.launch_persistent_context(
                user_data_dir=str(s_dir),
                headless=headless,
                args=["--disable-blink-features=AutomationControlled"],
            )
            page = context.new_page()
            page.goto(RUNNINGHUB_URL, timeout=timeout_sec * 1000)
            page.wait_for_load_state("domcontentloaded", timeout=timeout_sec * 1000)
            time.sleep(2)
            auth = is_runninghub_authenticated(page)
            context.close()
            return auth
    except Exception as exc:
        logger.warning(f"Error checking RunningHub session: {exc}")
        return False


def interactive_login_google_flow(timeout_sec: int = 300) -> bool:
    """Launch headful browser for the operator to log into Google Flow manually."""
    from playwright.sync_api import sync_playwright

    ensure_session_dirs()
    logger.info("===================================================================")
    logger.info("🔑 INICIANDO LOGIN INTERATIVO NO GOOGLE FLOW")
    logger.info("Uma janela visível do navegador Chrome será aberta agora.")
    logger.info("Por favor, faça o login na sua conta Google na janela do navegador.")
    logger.info("O sistema detectará o login automaticamente e salvará a sessão.")
    logger.info("===================================================================")

    try:
        with sync_playwright() as p:
            context = p.chromium.launch_persistent_context(
                user_data_dir=str(GOOGLE_FLOW_SESSION_DIR),
                headless=False,
                args=["--disable-blink-features=AutomationControlled", "--start-maximized"],
            )
            page = context.new_page()
            page.goto(GOOGLE_FLOW_URL)

            start_t = time.time()
            authenticated = False
            while time.time() - start_t < timeout_sec:
                if is_google_flow_authenticated(page):
                    authenticated = True
                    break
                time.sleep(2)

            if authenticated:
                logger.info("✅ Login no Google Flow detectado com sucesso!")
                state_file = GOOGLE_FLOW_SESSION_DIR / "storage_state.json"
                context.storage_state(path=str(state_file))
                logger.info(f"Sessão persistente salva em: {state_file}")
                context.close()
                return True
            else:
                logger.error(f"❌ Tempo limite ({timeout_sec}s) esgotado aguardando login no Google Flow.")
                context.close()
                return False
    except Exception as exc:
        logger.error(f"Falha ao executar login interativo no Google Flow: {exc}")
        return False


def interactive_login_runninghub(timeout_sec: int = 300) -> bool:
    """Launch headful browser for the operator to log into RunningHub manually."""
    from playwright.sync_api import sync_playwright

    ensure_session_dirs()
    logger.info("===================================================================")
    logger.info("🔑 INICIANDO LOGIN INTERATIVO NO RUNNINGHUB")
    logger.info("Uma janela visível do navegador Chrome será aberta agora.")
    logger.info("Por favor, faça o login na sua conta RunningHub.")
    logger.info("O sistema detectará o login automaticamente e salvará a sessão.")
    logger.info("===================================================================")

    try:
        with sync_playwright() as p:
            context = p.chromium.launch_persistent_context(
                user_data_dir=str(RUNNINGHUB_SESSION_DIR),
                headless=False,
                args=["--disable-blink-features=AutomationControlled", "--start-maximized"],
            )
            page = context.new_page()
            page.goto(RUNNINGHUB_URL)

            start_t = time.time()
            authenticated = False
            while time.time() - start_t < timeout_sec:
                if is_runninghub_authenticated(page):
                    authenticated = True
                    break
                time.sleep(2)

            if authenticated:
                logger.info("✅ Login no RunningHub detectado com sucesso!")
                state_file = RUNNINGHUB_SESSION_DIR / "storage_state.json"
                context.storage_state(path=str(state_file))
                logger.info(f"Sessão persistente salva em: {state_file}")
                context.close()
                return True
            else:
                logger.error(f"❌ Tempo limite ({timeout_sec}s) esgotado aguardando login no RunningHub.")
                context.close()
                return False
    except Exception as exc:
        logger.error(f"Falha ao executar login interativo no RunningHub: {exc}")
        return False


def enforce_production_auth_gate(interactive: bool = True, dry_run: bool = False) -> bool:
    """Mandatory Pre-flight gate: enforces active sessions for Google Flow and RunningHub.

    - Called by orchestrator before any asset generation begins.
    - If dry_run is True (CI/test suite), bypasses network checks.
    - If sessions are missing and interactive=True, opens headful windows automatically.
    """
    if dry_run or os.getenv("DARKFACTORY_DRY_RUN", "0") == "1":
        logger.info("🛡️ Pre-Flight Auth Gate: DRY-RUN mode active (skipping live browser sessions).")
        return True

    logger.info("🛡️ Pre-Flight Auth Gate: Verificando autenticação das plataformas industriais...")
    ensure_session_dirs()

    # 1. Google Flow Check
    flow_ok = check_google_flow_session(headless=True)
    if not flow_ok:
        logger.warning("⚠️ Sessão do Google Flow não autenticada!")
        if interactive:
            logger.info("Abrindo janela de login para Google Flow...")
            flow_ok = interactive_login_google_flow()
            if not flow_ok:
                raise PermissionError("Falha na autenticação do Google Flow. Pipeline abortado.")
        else:
            raise PermissionError("Production Auth Gate Check Failed: Google Flow não autenticado e modo interativo desativado.")

    # 2. RunningHub Check
    rh_ok = check_runninghub_session(headless=True)
    if not rh_ok:
        logger.warning("⚠️ Sessão do RunningHub não autenticada!")
        if interactive:
            logger.info("Abrindo janela de login para RunningHub...")
            rh_ok = interactive_login_runninghub()
            if not rh_ok:
                raise PermissionError("Falha na autenticação do RunningHub. Pipeline abortado.")
        else:
            raise PermissionError("Production Auth Gate Check Failed: RunningHub não autenticado e modo interativo desativado.")

    logger.info("✅ Pre-Flight Auth Gate: 100% Autenticado (Google Flow + RunningHub prontos).")
    return True


def main() -> None:
    parser = argparse.ArgumentParser(description="DarkFactory Pre-Flight Authentication Gate")
    parser.add_argument("--check", action="store_true", help="Check active session status without opening windows")
    parser.add_argument("--login-google", action="store_true", help="Trigger interactive login for Google Flow")
    parser.add_argument("--login-runninghub", action="store_true", help="Trigger interactive login for RunningHub")
    parser.add_argument("--login-all", action="store_true", help="Check and trigger interactive login for all platforms")
    parser.add_argument("--dry-run", action="store_true", help="Simulate authentication gate check")
    args = parser.parse_args()

    if args.dry_run:
        ok = enforce_production_auth_gate(interactive=False, dry_run=True)
        print(f"Auth Gate Dry-Run Status: {ok}")
        sys.exit(0)

    if args.login_google:
        ok = interactive_login_google_flow()
        sys.exit(0 if ok else 1)

    if args.login_runninghub:
        ok = interactive_login_runninghub()
        sys.exit(0 if ok else 1)

    if args.login_all:
        ok = enforce_production_auth_gate(interactive=True, dry_run=False)
        sys.exit(0 if ok else 1)

    if args.check:
        ensure_session_dirs()
        gf = check_google_flow_session(headless=True)
        rh = check_runninghub_session(headless=True)
        print(f"Google Flow Authenticated: {gf}")
        print(f"RunningHub Authenticated:  {rh}")
        sys.exit(0 if (gf and rh) else 1)

    # Default action: enforce gate
    ok = enforce_production_auth_gate(interactive=True)
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
