"""Stealth Browser Profile & Fingerprint Randomizer for DarkFactory RunningHub RPA.

Provides distinct, realistic, high-entropy browser fingerprints for autonomous
operation on RunningHub Accounts 4 (CosyVoice), 5 (MiniMax Music 3), and 7 (MiniMax H3).
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List


@dataclass
class StealthFingerprint:
    account: int
    user_agent: str
    sec_ch_ua: str
    sec_ch_ua_platform: str
    platform: str
    hardware_concurrency: int
    device_memory: int
    screen_width: int
    screen_height: int
    device_pixel_ratio: float
    webgl_vendor: str
    webgl_renderer: str
    languages: List[str]
    timezone: str
    canvas_noise_offset: float
    session_dir: str


# Profile 4: Windows 11 Pro | Studio Audio Workstation (CosyVoice Account 4)
CONTA_4_FINGERPRINT = StealthFingerprint(
    account=4,
    user_agent=(
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/130.0.6723.92 Safari/537.36"
    ),
    sec_ch_ua='"Chromium";v="130", "Not?A_Brand";v="99", "Google Chrome";v="130"',
    sec_ch_ua_platform='"Windows"',
    platform="Win32",
    hardware_concurrency=24,
    device_memory=64,
    screen_width=1920,
    screen_height=1080,
    device_pixel_ratio=1.0,
    webgl_vendor="Google Inc. (NVIDIA)",
    webgl_renderer="ANGLE (NVIDIA, NVIDIA GeForce RTX 4090 Direct3D11 vs_5_0 ps_5_0, D3D11)",
    languages=["pt-BR", "en-US", "pt", "en"],
    timezone="America/Sao_Paulo",
    canvas_noise_offset=0.00033,
    session_dir="playwright_session_cosyvoice",
)

# Profile 5: Windows 11 Pro | Orchestral Audio Mastering (MiniMax Music 3 Account 5)
CONTA_5_FINGERPRINT = StealthFingerprint(
    account=5,
    user_agent=(
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/129.0.6668.71 Safari/537.36"
    ),
    sec_ch_ua='"Chromium";v="129", "Not;A=Brand";v="8", "Google Chrome";v="129"',
    sec_ch_ua_platform='"Windows"',
    platform="Win32",
    hardware_concurrency=16,
    device_memory=32,
    screen_width=2560,
    screen_height=1440,
    device_pixel_ratio=1.25,
    webgl_vendor="Google Inc. (NVIDIA)",
    webgl_renderer="ANGLE (NVIDIA, NVIDIA GeForce RTX 4070 Direct3D11 vs_5_0 ps_5_0, D3D11)",
    languages=["pt-BR", "en-US", "pt", "es"],
    timezone="America/Sao_Paulo",
    canvas_noise_offset=0.00027,
    session_dir="playwright_session_minimax_music",
)

# Profile 7: Windows 11 Enterprise | Cinema T2V Workstation (MiniMax H3 Account 7)
CONTA_7_FINGERPRINT = StealthFingerprint(
    account=7,
    user_agent=(
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/128.0.6613.138 Safari/537.36"
    ),
    sec_ch_ua='"Chromium";v="128", "Not;A=Brand";v="24", "Google Chrome";v="128"',
    sec_ch_ua_platform='"Windows"',
    platform="Win32",
    hardware_concurrency=16,
    device_memory=16,
    screen_width=1920,
    screen_height=1080,
    device_pixel_ratio=1.0,
    webgl_vendor="Google Inc. (NVIDIA)",
    webgl_renderer="ANGLE (NVIDIA, NVIDIA GeForce RTX 3080 Direct3D11 vs_5_0 ps_5_0, D3D11)",
    languages=["pt-BR", "pt", "en-US", "en"],
    timezone="America/Sao_Paulo",
    canvas_noise_offset=0.00019,
    session_dir="playwright_session_minimax_h3",
)


def get_stealth_fingerprint(account: int = 4) -> StealthFingerprint:
    """Return the designated stealth profile for DarkFactory accounts (4, 5, 7)."""
    if account == 5:
        return CONTA_5_FINGERPRINT
    if account == 7:
        return CONTA_7_FINGERPRINT
    return CONTA_4_FINGERPRINT


def build_stealth_init_script(fp: StealthFingerprint) -> str:
    """Build client-side JavaScript injected before page scripts load to spoof hardware/fingerprints."""
    return f"""
(() => {{
    'use strict';

    try {{
        delete Object.getPrototypeOf(navigator).webdriver;
    }} catch (e) {{}}
    Object.defineProperty(navigator, 'webdriver', {{
        get: () => undefined,
        configurable: true
    }});

    Object.defineProperty(navigator, 'hardwareConcurrency', {{
        get: () => {fp.hardware_concurrency},
        configurable: true
    }});
    Object.defineProperty(navigator, 'deviceMemory', {{
        get: () => {fp.device_memory},
        configurable: true
    }});
    Object.defineProperty(navigator, 'platform', {{
        get: () => '{fp.platform}',
        configurable: true
    }});

    Object.defineProperty(navigator, 'languages', {{
        get: () => {fp.languages},
        configurable: true
    }});

    const screenProps = {{
        width: {fp.screen_width},
        height: {fp.screen_height},
        availWidth: {fp.screen_width},
        availHeight: {fp.screen_height - 40},
        colorDepth: 24,
        pixelDepth: 24
    }};
    for (const [prop, val] of Object.entries(screenProps)) {{
        try {{
            Object.defineProperty(screen, prop, {{ get: () => val, configurable: true }});
        }} catch(e) {{}}
    }}
    try {{
        Object.defineProperty(window, 'devicePixelRatio', {{
            get: () => {fp.device_pixel_ratio},
            configurable: true
        }});
    }} catch(e) {{}}

    const fakeVendor = '{fp.webgl_vendor}';
    const fakeRenderer = '{fp.webgl_renderer}';

    const patchWebGL = (proto) => {{
        if (!proto) return;
        const origGetParameter = proto.getParameter;
        proto.getParameter = function(param) {{
            if (param === 0x9245) return fakeVendor;
            if (param === 0x9246) return fakeRenderer;
            return origGetParameter.apply(this, arguments);
        }};
    }};

    try {{
        if (typeof WebGLRenderingContext !== 'undefined') {{
            patchWebGL(WebGLRenderingContext.prototype);
        }}
        if (typeof WebGL2RenderingContext !== 'undefined') {{
            patchWebGL(WebGL2RenderingContext.prototype);
        }}
    }} catch (e) {{}}

    const noise = {fp.canvas_noise_offset};
    const origToDataURL = HTMLCanvasElement.prototype.toDataURL;
    HTMLCanvasElement.prototype.toDataURL = function(type) {{
        try {{
            const ctx = this.getContext('2d');
            if (ctx && this.width > 16 && this.height > 16) {{
                const imgData = ctx.getImageData(0, 0, Math.min(10, this.width), Math.min(10, this.height));
                for (let i = 0; i < imgData.data.length; i += 4) {{
                    imgData.data[i] = Math.min(255, Math.max(0, imgData.data[i] + Math.round((i % 3 === 0 ? 1 : -1) * noise * 255)));
                }}
                ctx.putImageData(imgData, 0, 0);
            }}
        }} catch (e) {{}}
        return origToDataURL.apply(this, arguments);
    }};

    if (!window.chrome) {{
        window.chrome = {{}};
    }}
    if (!window.chrome.app) {{
        window.chrome.app = {{
            isInstalled: false,
            InstallState: {{ DISABLED: 'disabled', INSTALLED: 'installed', NOT_INSTALLED: 'not_installed' }},
            RunningState: {{ CANNOT_RUN: 'cannot_run', READY_TO_RUN: 'ready_to_run', RUNNING: 'running' }}
        }};
    }}
    if (!window.chrome.runtime) {{
        window.chrome.runtime = {{
            OnInstalledReason: {{ CHROME_UPDATE: 'chrome_update', INSTALL: 'install', SHARED_MODULE_UPDATE: 'shared_module_update', UPDATE: 'update' }},
            PlatformArch: {{ ARM: 'arm', ARM64: 'arm64', MIPS: 'mips', MIPS64: 'mips64', X86_32: 'x86-32', X86_64: 'x86-64' }},
            PlatformNaclArch: {{ ARM: 'arm', MIPS: 'mips', MIPS64: 'mips64', X86_32: 'x86-32', X86_64: 'x86-64' }},
            PlatformOs: {{ ANDROID: 'android', CROS: 'cros', LINUX: 'linux', MAC: 'mac', OPENBSD: 'openbsd', WIN: 'win' }}
        }};
    }}

    try {{
        const fakePlugins = [
            {{ name: 'PDF Viewer', filename: 'internal-pdf-viewer', description: 'Portable Document Format' }},
            {{ name: 'Chrome PDF Viewer', filename: 'internal-pdf-viewer', description: 'Portable Document Format' }},
            {{ name: 'Chromium PDF Viewer', filename: 'internal-pdf-viewer', description: 'Portable Document Format' }}
        ];
        Object.defineProperty(navigator, 'plugins', {{
            get: () => fakePlugins,
            configurable: true
        }});
    }} catch (e) {{}}

    if (navigator.permissions && navigator.permissions.query) {{
        const origQuery = navigator.permissions.query;
        navigator.permissions.query = (params) => {{
            if (params && params.name === 'notifications') {{
                return Promise.resolve({{ state: Notification.permission }});
            }}
            return origQuery(params);
        }};
    }}
}})();
"""


def get_playwright_launch_options(account: int, base_dir: Path) -> Dict[str, Any]:
    """Return Playwright context configuration tailored for DarkFactory account."""
    fp = get_stealth_fingerprint(account)
    session_dir = base_dir / fp.session_dir

    chrome_installed = (
        Path("C:/Program Files/Google/Chrome/Application/chrome.exe").exists()
        or Path("C:/Program Files (x86)/Google/Chrome/Application/chrome.exe").exists()
    )

    opts: Dict[str, Any] = {
        "user_data_dir": session_dir,
        "headless": False,
        "viewport": {"width": fp.screen_width, "height": fp.screen_height},
        "user_agent": fp.user_agent,
        "locale": fp.languages[0],
        "timezone_id": fp.timezone,
        "device_scale_factor": fp.device_pixel_ratio,
        "accept_downloads": True,
        "extra_http_headers": {
            "Sec-Ch-Ua": fp.sec_ch_ua,
            "Sec-Ch-Ua-Mobile": "?0",
            "Sec-Ch-Ua-Platform": fp.sec_ch_ua_platform,
            "Accept-Language": f"{fp.languages[0]},{fp.languages[1]};q=0.9,en-US;q=0.8,en;q=0.7",
        },
        "args": [
            "--disable-blink-features=AutomationControlled",
            "--no-sandbox",
            "--disable-setuid-sandbox",
            "--disable-infobars",
            "--new-window",
            f"--window-size={fp.screen_width},{fp.screen_height}",
            "--start-maximized",
        ],
    }
    if chrome_installed:
        opts["channel"] = "chrome"
    return opts
