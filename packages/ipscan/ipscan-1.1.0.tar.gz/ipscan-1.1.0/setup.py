import os
import setuptools

# Long description loader with language support (default to English)
def detect_lang():
    # Allow override via environment variable like: SET IPSCAN_LANG=zh-TW
    env = os.getenv("IPSCAN_LANG", "").strip()
    if env:
        return env
    # Default to English to keep PyPI page consistent
    return "en"

def load_readme(lang):
    """Return (description, long_description_markdown) for the selected language.
    Fallback order: exact lang -> zh-TW if Chinese -> English README.md
    """
    # Map language to README filename
    lang_lower = (lang or "").lower()
    readme_file = "README.md"  # default English
    desc = "Fast IP scanner — multithreaded Ping and ARP scanning"

    if lang_lower.startswith("zh"):
        candidate = "README.zh-TW.md"
        if os.path.exists(candidate):
            readme_file = candidate
            desc = "快速IP掃描工具 - 多線程 Ping 和 ARP 掃描"

    try:
        with open(readme_file, "r", encoding="utf-8") as f:
            return desc, f.read()
    except Exception:
        # Safe fallback to a short English text
        return (
            "Fast IP scanner — multithreaded Ping and ARP scanning",
            "# ipscan\n\nFast IP scanner for Windows. See README.md for details.",
        )

_desc, _long_description = load_readme(detect_lang())

# 從 __init__.py 獲取版本信息
def get_version():
    with open("ipscan/__init__.py", "r", encoding="utf-8") as f:
        for line in f:
            if line.startswith("__version__"):
                return line.split("=")[1].strip().strip('"').strip("'")
    return "1.0.2"

setuptools.setup(
    name="ipscan",
    version=get_version(),
    author="Wing",
    author_email="tomt99688@gmail.com",
    description=_desc,
    long_description=_long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Wing9897/ipscan.git",
    project_urls={
        "Source": "https://github.com/Wing9897/ipscan",
        "English README": "https://github.com/Wing9897/ipscan/blob/main/README.md",
        "繁體中文 README": "https://github.com/Wing9897/ipscan/blob/main/README.zh-TW.md",
    },
    packages=setuptools.find_packages(),
    install_requires=[
        'ping3>=4.0.0',
        'tqdm>=4.60.0',
    ],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
    # License classifier removed (deprecated). Use SPDX expression via `license` instead.
        "Operating System :: Microsoft :: Windows",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: System :: Networking",
    "Natural Language :: English",
    "Natural Language :: Chinese (Traditional)",
    ],
    # Use an SPDX license expression and include the LICENSE file in built distributions
    license="MIT",
    license_files=("LICENSE",),
    python_requires='>=3.7',
    entry_points={
        'console_scripts': [
            'fping=ipscan.fping:main',
            'sarp=ipscan.sarp:main',
            'sping=ipscan.sping:main',
        ]
    },
    keywords="ip scan ping arp network scanner",
)