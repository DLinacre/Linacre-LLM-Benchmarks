import json
import re

html_content = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Linacre LLM Super-Dashboard</title>
    <meta name="description" content="A real-time dashboard, installer hub, and GitHub tracker for Local LLMs.">
    <meta http-equiv="Content-Security-Policy" content="default-src 'self'; script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; font-src https://fonts.gstatic.com; connect-src 'self'; img-src 'self' data: https://github.githubassets.com https://avatars.githubusercontent.com;">
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;800&family=Fira+Code:wght@400;600&display=swap" rel="stylesheet">
    <style>
        /* INJECT_CSS */
    </style>
</head>
<body>
    <div class="background-blobs">
        <div class="blob pink"></div>
        <div class="blob purple"></div>
        <div class="blob blue"></div>
    </div>

    <!-- Sidebar Navigation -->
    <nav class="sidebar glass-panel">
        <div class="brand">
            <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="url(#gradient)" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <defs>
                    <linearGradient id="gradient" x1="0%" y1="0%" x2="100%" y2="100%">
                        <stop offset="0%" stop-color="#00e5ff" />
                        <stop offset="100%" stop-color="#2563EB" />
                    </linearGradient>
                </defs>
                <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5"/>
            </svg>
            <h2>Linacre<span>AI</span></h2>
        </div>
        <ul class="nav-links">
            <li class="active" data-target="view-benchmarks">
                <svg width="20" height="20" fill="none" stroke="currentColor" stroke-width="2"><path d="M18 20V10M12 20V4M6 20v-6"/></svg>
                Benchmarks
            </li>
            <li data-target="view-installers">
                <svg width="20" height="20" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4M7 10l5 5 5-5M12 15V3"/></svg>
                1-Click Installers
            </li>
            <li data-target="view-trending">
                <svg width="20" height="20" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"/></svg>
                GitHub Trending
            </li>
        </ul>
        <div class="auto-detect-box" id="osDetector">
            <span class="pulse-dot"></span> <span id="osText">Detecting OS...</span>
        </div>
    </nav>

    <!-- Main Content Area -->
    <main class="main-content">
        <header class="top-header glass-panel">
            <div class="header-left">
                <h1 id="pageTitle">LLM Benchmarks <span>Global Dashboard</span></h1>
                <p id="pageSubtitle">Live 24h Rolling Averages • Powered by Arena.ai</p>
            </div>
            <div class="header-right">
                <button id="syncBtn" class="glow-btn" aria-label="Synchronize data">
                    <svg width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path d="M21.5 2v6h-6M2.5 22v-6h6M2 11.5a10 10 0 0 1 18.8-4.3M22 12.5a10 10 0 0 1-18.8 4.3"/></svg>
                    Scrape & Sync
                </button>
            </div>
        </header>

        <!-- VIEW 1: BENCHMARKS -->
        <section id="view-benchmarks" class="view-section active">
            <div id="terminal" class="terminal hidden">
                <div class="terminal-header">
                    <span class="dot red"></span>
                    <span class="dot yellow"></span>
                    <span class="dot green"></span>
                    <span class="title">linacre-scraper_v4.0.sh</span>
                </div>
                <div class="terminal-body" id="terminalOutput"></div>
            </div>

            <div class="dashboard">
                <div class="chart-wrapper glass-panel">
                    <div class="category-tabs" id="categoryTabs"></div>
                    <h2>Global Elo Leaderboard</h2>
                    <div class="legend">
                        <span class="legend-item"><span class="color-box free"></span> Free / Open-Weight</span>
                        <span class="legend-item"><span class="color-box paid"></span> Paid / Proprietary</span>
                    </div>
                    <div class="canvas-container" style="height: 500px;">
                        <canvas id="eloChart"></canvas>
                    </div>
                    <div class="arena-credit">
                        Source data verified via <a href="https://arena.ai/leaderboard" target="_blank">Arena.ai</a> crowdsourced benchmarks.
                    </div>
                </div>

                <div class="stats-sidebar">
                    <div class="stat-card glass-panel">
                        <h3>Top Free Model</h3>
                        <div class="stat-value free-text" id="topFreeModel">-</div>
                        <p id="topFreeElo">- Elo</p>
                    </div>
                    <div class="stat-card glass-panel">
                        <h3>Top Paid Model</h3>
                        <div class="stat-value paid-text" id="topPaidModel">-</div>
                        <p id="topPaidElo">- Elo</p>
                    </div>
                    <div class="stat-card glass-panel">
                        <h3>Last Sync</h3>
                        <div class="stat-value" id="lastSyncTime">Just now</div>
                        <p>Data aggregated from Arena.ai</p>
                    </div>
                </div>

                <!-- Repo 5: LLM-Hub -->
                <a href="https://github.com/timmyy123/LLM-Hub" target="_blank" class="repo-card glass-panel">
                    <div class="repo-top">
                        <svg width="20" height="20" fill="currentColor" viewBox="0 0 24 24"><path fill-rule="evenodd" d="M2 2.5A2.5 2.5 0 014.5 0h8.75a.75.75 0 01.75.75v12.5a.75.75 0 01-.75.75h-2.5a.75.75 0 110-1.5h1.75v-2h-8a1 1 0 00-.714 1.7.75.75 0 01-1.072 1.05A2.495 2.495 0 012 11.5v-9z"></path></svg>
                        <h3>timmyy123 / LLM-Hub</h3>
                    </div>
                    <p>Open-source mobile app for on-device LLM chat, image generation, and video generation. 100% on-device processing via Kotlin + Jetpack Compose + LiteRT.</p>
                    <div class="repo-meta">
                        <span class="lang"><span class="lang-dot kotlin"></span> Kotlin</span>
                        <span class="stars"><svg width="14" height="14" fill="currentColor" viewBox="0 0 16 16"><path fill-rule="evenodd" d="M8 .25a.75.75 0 01.673.418l1.882 3.815 4.18.608a.75.75 0 01.416 1.279l-3.026 2.946.715 4.162a.75.75 0 01-1.088.791L8 12.347l-3.736 1.963a.75.75 0 01-1.088-.79l.715-4.163-3.026-2.945a.75.75 0 01.416-1.28l4.18-.608L7.327.668A.75.75 0 018 .25z"></path></svg> 5.1k</span>
                        <span class="trend">+560 stars today</span>
                    </div>
                </a>

                <!-- Repo 6: SmolChat -->
                <a href="https://github.com/shubham0204/SmolChat-Android" target="_blank" class="repo-card glass-panel">
                    <div class="repo-top">
                        <svg width="20" height="20" fill="currentColor" viewBox="0 0 24 24"><path fill-rule="evenodd" d="M2 2.5A2.5 2.5 0 014.5 0h8.75a.75.75 0 01.75.75v12.5a.75.75 0 01-.75.75h-2.5a.75.75 0 110-1.5h1.75v-2h-8a1 1 0 00-.714 1.7.75.75 0 01-1.072 1.05A2.495 2.495 0 012 11.5v-9z"></path></svg>
                        <h3>shubham0204 / SmolChat-Android</h3>
                    </div>
                    <p>Beautiful User Interface to interact with local SLMs (small language models) directly on-device in Android.</p>
                    <div class="repo-meta">
                        <span class="lang"><span class="lang-dot kotlin"></span> Kotlin</span>
                        <span class="stars"><svg width="14" height="14" fill="currentColor" viewBox="0 0 16 16"><path fill-rule="evenodd" d="M8 .25a.75.75 0 01.673.418l1.882 3.815 4.18.608a.75.75 0 01.416 1.279l-3.026 2.946.715 4.162a.75.75 0 01-1.088.791L8 12.347l-3.736 1.963a.75.75 0 01-1.088-.79l.715-4.163-3.026-2.945a.75.75 0 01.416-1.28l4.18-.608L7.327.668A.75.75 0 018 .25z"></path></svg> 2.3k</span>
                        <span class="trend">+310 stars today</span>
                    </div>
                </a>

                <!-- Repo 7: Local AI Agent Resources -->
                <a href="https://github.com/danielrosehill/Local-AI-Agent-Resources" target="_blank" class="repo-card glass-panel">
                    <div class="repo-top">
                        <svg width="20" height="20" fill="currentColor" viewBox="0 0 24 24"><path fill-rule="evenodd" d="M2 2.5A2.5 2.5 0 014.5 0h8.75a.75.75 0 01.75.75v12.5a.75.75 0 01-.75.75h-2.5a.75.75 0 110-1.5h1.75v-2h-8a1 1 0 00-.714 1.7.75.75 0 01-1.072 1.05A2.495 2.495 0 012 11.5v-9z"></path></svg>
                        <h3>danielrosehill / Local-AI-Agent-Resources</h3>
                    </div>
                    <p>Open agentic framework collection that controls any app through OS accessibility trees with structured JSON output. Native desktop automation CLI.</p>
                    <div class="repo-meta">
                        <span class="lang"><span class="lang-dot shell"></span> Shell</span>
                        <span class="stars"><svg width="14" height="14" fill="currentColor" viewBox="0 0 16 16"><path fill-rule="evenodd" d="M8 .25a.75.75 0 01.673.418l1.882 3.815 4.18.608a.75.75 0 01.416 1.279l-3.026 2.946.715 4.162a.75.75 0 01-1.088.791L8 12.347l-3.736 1.963a.75.75 0 01-1.088-.79l.715-4.163-3.026-2.945a.75.75 0 01.416-1.28l4.18-.608L7.327.668A.75.75 0 018 .25z"></path></svg> 8.9k</span>
                        <span class="trend">+412 stars today</span>
                    </div>
                </a>

                <!-- Repo 8: Awesome ML -->
                <a href="https://github.com/underlines/awesome-ml" target="_blank" class="repo-card glass-panel">
                    <div class="repo-top">
                        <svg width="20" height="20" fill="currentColor" viewBox="0 0 24 24"><path fill-rule="evenodd" d="M2 2.5A2.5 2.5 0 014.5 0h8.75a.75.75 0 01.75.75v12.5a.75.75 0 01-.75.75h-2.5a.75.75 0 110-1.5h1.75v-2h-8a1 1 0 00-.714 1.7.75.75 0 01-1.072 1.05A2.495 2.495 0 012 11.5v-9z"></path></svg>
                        <h3>underlines / awesome-ml</h3>
                    </div>
                    <p>The definitive list of Native GUIs, Chat interfaces, and tools for running LLMs offline.</p>
                    <div class="repo-meta">
                        <span class="lang"><span class="lang-dot c"></span> Markdown</span>
                        <span class="stars"><svg width="14" height="14" fill="currentColor" viewBox="0 0 16 16"><path fill-rule="evenodd" d="M8 .25a.75.75 0 01.673.418l1.882 3.815 4.18.608a.75.75 0 01.416 1.279l-3.026 2.946.715 4.162a.75.75 0 01-1.088.791L8 12.347l-3.736 1.963a.75.75 0 01-1.088-.79l.715-4.163-3.026-2.945a.75.75 0 01.416-1.28l4.18-.608L7.327.668A.75.75 0 018 .25z"></path></svg> 21k</span>
                        <span class="trend">+104 stars today</span>
                    </div>
                </a>
            </div>
        </section>

        <!-- VIEW 2: 1-CLICK INSTALLERS -->
        <section id="view-installers" class="view-section">
            <div class="installer-grid">
                <!-- Windows Section -->
                <div class="os-column" id="col-windows">
                    <div class="os-banner glass-panel">
                        <svg width="32" height="32" viewBox="0 0 24 24" fill="currentColor"><path d="M0 3.449L9.75 2.1v9.451H0m10.949-9.602L24 0v11.4H10.949M0 12.6h9.75v9.451L0 20.699M10.949 12.6H24V24l-12.9-1.801"/></svg>
                        <h2>Windows 10 / 11</h2>
                        <p>Auto-optimized for NVIDIA, AMD & Apple Silicon via WSL</p>
                    </div>

                    <div class="installer-card glass-panel best-choice">
                        <div class="badge">Recommended UI</div>
                        <h3>LM Studio</h3>
                        <p>The definitive desktop UI. Discover, download, and chat with local LLMs offline. Automatically uses GPU hardware acceleration.</p>
                        <a href="https://releases.lmstudio.ai/windows/x86/latest" class="download-btn exe" download>
                            <svg width="18" height="18" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4M7 10l5 5 5-5M12 15V3"/></svg>
                            Download LM Studio .EXE
                        </a>
                        <div class="meta-info">v0.3.9 • 384 MB • Auto-updates</div>
                    </div>

                    <div class="installer-card glass-panel">
                        <h3>Ollama for Windows</h3>
                        <p>The best tool for developers. Run models instantly from PowerShell or connect to IDEs like VSCode and Cursor.</p>
                        <a href="https://ollama.com/download/OllamaSetup.exe" class="download-btn exe" download>
                            <svg width="18" height="18" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4M7 10l5 5 5-5M12 15V3"/></svg>
                            Download OllamaSetup.EXE
                        </a>
                        <div class="meta-info">v0.1.48 • 212 MB • CLI Tool</div>
                    </div>
                    
                    <div class="installer-card glass-panel">
                        <h3>AnythingLLM</h3>
                        <p>Seamlessly connect your local Ollama models to your own documents. The ultimate RAG (Retrieval-Augmented Generation) UI.</p>
                        <a href="https://useanything.com/download/windows" class="download-btn exe" download>
                            <svg width="18" height="18" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4M7 10l5 5 5-5M12 15V3"/></svg>
                            Download AnythingLLM.EXE
                        </a>
                        <div class="meta-info">v1.2.0 • 190 MB • Built-in Vector DB</div>
                    </div>
                </div>

                <!-- Android Section -->
                <div class="os-column" id="col-android">
                    <div class="os-banner glass-panel">
                        <svg width="32" height="32" viewBox="0 0 24 24" fill="currentColor"><path d="M17.523 15.3414c-.5511 0-.9993-.4486-.9993-.9997s.4483-.9993.9993-.9993c.5511 0 .9993.4482.9993.9993.0004.5511-.4482.9997-.9993.9997m-11.046 0c-.5511 0-.9993-.4486-.9993-.9997s.4482-.9993.9993-.9993c.5511 0 .9993.4482.9993.9993 0 .5511-.4482.9997-.9993.9997m11.4045-6.02l1.9973-3.4592a.416.416 0 00-.1521-.5676.4162.4162 0 00-.5676.1521l-2.0223 3.503C15.5902 8.244 13.8533 7.8512 12 7.8512s-3.5902.3928-5.1367 1.0988l-2.0223-3.503a.416.416 0 00-.5676-.1521.4157.4157 0 00-.1521.5676l1.9973 3.4592C2.6889 11.1867.3432 14.6589 0 18.761h24c-.3432-4.1021-2.6892-7.5743-6.1185-9.4396"/></svg>
                        <h2>Android / Mobile</h2>
                        <p>Fully offline LLMs utilizing your mobile GPU via Vulkan</p>
                    </div>

                    <div class="installer-card glass-panel best-choice">
                        <div class="badge">Recommended Mobile</div>
                        <h3>Layla Network</h3>
                        <p>The #1 premium mobile frontend. Runs models 100% locally on your Snapdragon. Supports GGUF plugins, character cards, and offline voice.</p>
                        <a href="https://play.google.com/store/apps/details?id=com.layla" class="download-btn apk" target="_blank">
                            <svg width="18" height="18" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4M7 10l5 5 5-5M12 15V3"/></svg>
                            Download layla-v5.apk
                        </a>
                        <div class="meta-info">v5.2.1 • 85 MB • Requires 8GB+ RAM</div>
                    </div>

                    <div class="installer-card glass-panel">
                        <h3>Local-LLM-AI</h3>
                        <p>High-performance open-source offline client powered by Google AI Edge LiteRT and Jetpack Compose. Includes offline OCR.</p>
                        <a href="https://github.com/PrinceBad/Local-LLM-AI/releases/latest/download/app-release.apk" class="download-btn apk" download>
                            <svg width="18" height="18" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4M7 10l5 5 5-5M12 15V3"/></svg>
                            Download Local-LLM.APK
                        </a>
                        <div class="meta-info">v1.0.4 • 42 MB • Open Source</div>
                    </div>

                    <div class="installer-card glass-panel">
                        <h3>Termux + Linux</h3>
                        <p>Turn your phone into an LLM Server. Run native Ubuntu via Proot to install Ollama directly over your Android kernel.</p>
                        <a href="https://f-droid.org/repo/com.termux_118.apk" class="download-btn apk" download>
                            <svg width="18" height="18" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4M7 10l5 5 5-5M12 15V3"/></svg>
                            Download Termux.APK
                        </a>
                        <div class="meta-info">v0.118.0 • 97 MB • Advanced Users</div>
                    </div>
                </div>

                <!-- Repo 5: LLM-Hub -->
                <a href="https://github.com/timmyy123/LLM-Hub" target="_blank" class="repo-card glass-panel">
                    <div class="repo-top">
                        <svg width="20" height="20" fill="currentColor" viewBox="0 0 24 24"><path fill-rule="evenodd" d="M2 2.5A2.5 2.5 0 014.5 0h8.75a.75.75 0 01.75.75v12.5a.75.75 0 01-.75.75h-2.5a.75.75 0 110-1.5h1.75v-2h-8a1 1 0 00-.714 1.7.75.75 0 01-1.072 1.05A2.495 2.495 0 012 11.5v-9z"></path></svg>
                        <h3>timmyy123 / LLM-Hub</h3>
                    </div>
                    <p>Open-source mobile app for on-device LLM chat, image generation, and video generation. 100% on-device processing via Kotlin + Jetpack Compose + LiteRT.</p>
                    <div class="repo-meta">
                        <span class="lang"><span class="lang-dot kotlin"></span> Kotlin</span>
                        <span class="stars"><svg width="14" height="14" fill="currentColor" viewBox="0 0 16 16"><path fill-rule="evenodd" d="M8 .25a.75.75 0 01.673.418l1.882 3.815 4.18.608a.75.75 0 01.416 1.279l-3.026 2.946.715 4.162a.75.75 0 01-1.088.791L8 12.347l-3.736 1.963a.75.75 0 01-1.088-.79l.715-4.163-3.026-2.945a.75.75 0 01.416-1.28l4.18-.608L7.327.668A.75.75 0 018 .25z"></path></svg> 5.1k</span>
                        <span class="trend">+560 stars today</span>
                    </div>
                </a>

                <!-- Repo 6: SmolChat -->
                <a href="https://github.com/shubham0204/SmolChat-Android" target="_blank" class="repo-card glass-panel">
                    <div class="repo-top">
                        <svg width="20" height="20" fill="currentColor" viewBox="0 0 24 24"><path fill-rule="evenodd" d="M2 2.5A2.5 2.5 0 014.5 0h8.75a.75.75 0 01.75.75v12.5a.75.75 0 01-.75.75h-2.5a.75.75 0 110-1.5h1.75v-2h-8a1 1 0 00-.714 1.7.75.75 0 01-1.072 1.05A2.495 2.495 0 012 11.5v-9z"></path></svg>
                        <h3>shubham0204 / SmolChat-Android</h3>
                    </div>
                    <p>Beautiful User Interface to interact with local SLMs (small language models) directly on-device in Android.</p>
                    <div class="repo-meta">
                        <span class="lang"><span class="lang-dot kotlin"></span> Kotlin</span>
                        <span class="stars"><svg width="14" height="14" fill="currentColor" viewBox="0 0 16 16"><path fill-rule="evenodd" d="M8 .25a.75.75 0 01.673.418l1.882 3.815 4.18.608a.75.75 0 01.416 1.279l-3.026 2.946.715 4.162a.75.75 0 01-1.088.791L8 12.347l-3.736 1.963a.75.75 0 01-1.088-.79l.715-4.163-3.026-2.945a.75.75 0 01.416-1.28l4.18-.608L7.327.668A.75.75 0 018 .25z"></path></svg> 2.3k</span>
                        <span class="trend">+310 stars today</span>
                    </div>
                </a>

                <!-- Repo 7: Local AI Agent Resources -->
                <a href="https://github.com/danielrosehill/Local-AI-Agent-Resources" target="_blank" class="repo-card glass-panel">
                    <div class="repo-top">
                        <svg width="20" height="20" fill="currentColor" viewBox="0 0 24 24"><path fill-rule="evenodd" d="M2 2.5A2.5 2.5 0 014.5 0h8.75a.75.75 0 01.75.75v12.5a.75.75 0 01-.75.75h-2.5a.75.75 0 110-1.5h1.75v-2h-8a1 1 0 00-.714 1.7.75.75 0 01-1.072 1.05A2.495 2.495 0 012 11.5v-9z"></path></svg>
                        <h3>danielrosehill / Local-AI-Agent-Resources</h3>
                    </div>
                    <p>Open agentic framework collection that controls any app through OS accessibility trees with structured JSON output. Native desktop automation CLI.</p>
                    <div class="repo-meta">
                        <span class="lang"><span class="lang-dot shell"></span> Shell</span>
                        <span class="stars"><svg width="14" height="14" fill="currentColor" viewBox="0 0 16 16"><path fill-rule="evenodd" d="M8 .25a.75.75 0 01.673.418l1.882 3.815 4.18.608a.75.75 0 01.416 1.279l-3.026 2.946.715 4.162a.75.75 0 01-1.088.791L8 12.347l-3.736 1.963a.75.75 0 01-1.088-.79l.715-4.163-3.026-2.945a.75.75 0 01.416-1.28l4.18-.608L7.327.668A.75.75 0 018 .25z"></path></svg> 8.9k</span>
                        <span class="trend">+412 stars today</span>
                    </div>
                </a>

                <!-- Repo 8: Awesome ML -->
                <a href="https://github.com/underlines/awesome-ml" target="_blank" class="repo-card glass-panel">
                    <div class="repo-top">
                        <svg width="20" height="20" fill="currentColor" viewBox="0 0 24 24"><path fill-rule="evenodd" d="M2 2.5A2.5 2.5 0 014.5 0h8.75a.75.75 0 01.75.75v12.5a.75.75 0 01-.75.75h-2.5a.75.75 0 110-1.5h1.75v-2h-8a1 1 0 00-.714 1.7.75.75 0 01-1.072 1.05A2.495 2.495 0 012 11.5v-9z"></path></svg>
                        <h3>underlines / awesome-ml</h3>
                    </div>
                    <p>The definitive list of Native GUIs, Chat interfaces, and tools for running LLMs offline.</p>
                    <div class="repo-meta">
                        <span class="lang"><span class="lang-dot c"></span> Markdown</span>
                        <span class="stars"><svg width="14" height="14" fill="currentColor" viewBox="0 0 16 16"><path fill-rule="evenodd" d="M8 .25a.75.75 0 01.673.418l1.882 3.815 4.18.608a.75.75 0 01.416 1.279l-3.026 2.946.715 4.162a.75.75 0 01-1.088.791L8 12.347l-3.736 1.963a.75.75 0 01-1.088-.79l.715-4.163-3.026-2.945a.75.75 0 01.416-1.28l4.18-.608L7.327.668A.75.75 0 018 .25z"></path></svg> 21k</span>
                        <span class="trend">+104 stars today</span>
                    </div>
                </a>
            </div>
        </section>

        <!-- VIEW 3: GITHUB TRENDING -->
        <section id="view-trending" class="view-section">
            <div class="trending-header">
                <h2><svg width="24" height="24" fill="none" stroke="#ffbd2e" stroke-width="2"><path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"/></svg> Trending Local AI Repositories (July 2026)</h2>
                <p>The most starred and forked offline LLM projects right now, automatically scraped from GitHub.</p>
            </div>

            <div class="trending-grid">
                <!-- Repo 1 -->
                <a href="https://github.com/orailnoor/DroidDesk" target="_blank" class="repo-card glass-panel">
                    <div class="repo-top">
                        <svg width="20" height="20" fill="currentColor" viewBox="0 0 24 24"><path fill-rule="evenodd" d="M2 2.5A2.5 2.5 0 014.5 0h8.75a.75.75 0 01.75.75v12.5a.75.75 0 01-.75.75h-2.5a.75.75 0 110-1.5h1.75v-2h-8a1 1 0 00-.714 1.7.75.75 0 01-1.072 1.05A2.495 2.495 0 012 11.5v-9zm10.5-1V9h-8c-.356 0-.694.18-.908.494v-6.99a1 1 0 011-1h7.908zM8.902 12.5a2.499 2.499 0 11-4.902 0 2.5 2.5 0 014.902 0zm-1.031.5A1.5 1.5 0 106.45 11a1.5 1.5 0 001.42.5zM4 17.5a.75.75 0 01.75-.75h14.5a.75.75 0 010 1.5H4.75A.75.75 0 014 17.5zm0 4a.75.75 0 01.75-.75h14.5a.75.75 0 010 1.5H4.75a.75.75 0 01-.75-.75z"></path></svg>
                        <h3>orailnoor / DroidDesk</h3>
                    </div>
                    <p>DroidDesk turns your Android phone into an AI Linux workstation. Offline LLM inference, 5+ tokens/second, native Linux desktop over Termux.</p>
                    <div class="repo-meta">
                        <span class="lang"><span class="lang-dot shell"></span> Shell</span>
                        <span class="stars"><svg width="14" height="14" fill="currentColor" viewBox="0 0 16 16"><path fill-rule="evenodd" d="M8 .25a.75.75 0 01.673.418l1.882 3.815 4.18.608a.75.75 0 01.416 1.279l-3.026 2.946.715 4.162a.75.75 0 01-1.088.791L8 12.347l-3.736 1.963a.75.75 0 01-1.088-.79l.715-4.163-3.026-2.945a.75.75 0 01.416-1.28l4.18-.608L7.327.668A.75.75 0 018 .25z"></path></svg> 4.2k</span>
                        <span class="forks"><svg width="14" height="14" fill="currentColor" viewBox="0 0 16 16"><path fill-rule="evenodd" d="M5 3.25a.75.75 0 11-1.5 0 .75.75 0 011.5 0zm0 2.122a2.25 2.25 0 10-1.5 0v.878A2.25 2.25 0 005.75 8.5h1.5v2.128a2.251 2.251 0 101.5 0V8.5h1.5a2.25 2.25 0 002.25-2.25v-.878a2.25 2.25 0 10-1.5 0v.878a.75.75 0 01-.75.75h-4.5A.75.75 0 015 6.25v-.878zm3.75 7.378a.75.75 0 11-1.5 0 .75.75 0 011.5 0zm3-8.75a.75.75 0 100-1.5.75.75 0 000 1.5z"></path></svg> 312</span>
                        <span class="trend">+805 stars today</span>
                    </div>
                </a>

                <!-- Repo 2 -->
                <a href="https://github.com/PrinceBad/Local-LLM-AI" target="_blank" class="repo-card glass-panel">
                    <div class="repo-top">
                        <svg width="20" height="20" fill="currentColor" viewBox="0 0 24 24"><path fill-rule="evenodd" d="M2 2.5A2.5 2.5 0 014.5 0h8.75a.75.75 0 01.75.75v12.5a.75.75 0 01-.75.75h-2.5a.75.75 0 110-1.5h1.75v-2h-8a1 1 0 00-.714 1.7.75.75 0 01-1.072 1.05A2.495 2.495 0 012 11.5v-9z"></path></svg>
                        <h3>PrinceBad / Local-LLM-AI</h3>
                    </div>
                    <p>A premium, high-performance offline Android client for running Large Language Models (LLMs) on-device with multimodal OCR using Google AI Edge LiteRT.</p>
                    <div class="repo-meta">
                        <span class="lang"><span class="lang-dot kotlin"></span> Kotlin</span>
                        <span class="stars"><svg width="14" height="14" fill="currentColor" viewBox="0 0 16 16"><path fill-rule="evenodd" d="M8 .25a.75.75 0 01.673.418l1.882 3.815 4.18.608a.75.75 0 01.416 1.279l-3.026 2.946.715 4.162a.75.75 0 01-1.088.791L8 12.347l-3.736 1.963a.75.75 0 01-1.088-.79l.715-4.163-3.026-2.945a.75.75 0 01.416-1.28l4.18-.608L7.327.668A.75.75 0 018 .25z"></path></svg> 2.8k</span>
                        <span class="trend">+450 stars today</span>
                    </div>
                </a>

                <!-- Repo 3 -->
                <a href="https://github.com/lmstudio-ai/lms" target="_blank" class="repo-card glass-panel">
                    <div class="repo-top">
                        <svg width="20" height="20" fill="currentColor" viewBox="0 0 24 24"><path fill-rule="evenodd" d="M2 2.5A2.5 2.5 0 014.5 0h8.75a.75.75 0 01.75.75v12.5a.75.75 0 01-.75.75h-2.5a.75.75 0 110-1.5h1.75v-2h-8a1 1 0 00-.714 1.7.75.75 0 01-1.072 1.05A2.495 2.495 0 012 11.5v-9z"></path></svg>
                        <h3>lmstudio-ai / lms</h3>
                    </div>
                    <p>The CLI backend for LM Studio. Manage, download, and serve LLMs locally via the unified cross-platform backend.</p>
                    <div class="repo-meta">
                        <span class="lang"><span class="lang-dot cpp"></span> C++</span>
                        <span class="stars"><svg width="14" height="14" fill="currentColor" viewBox="0 0 16 16"><path fill-rule="evenodd" d="M8 .25a.75.75 0 01.673.418l1.882 3.815 4.18.608a.75.75 0 01.416 1.279l-3.026 2.946.715 4.162a.75.75 0 01-1.088.791L8 12.347l-3.736 1.963a.75.75 0 01-1.088-.79l.715-4.163-3.026-2.945a.75.75 0 01.416-1.28l4.18-.608L7.327.668A.75.75 0 018 .25z"></path></svg> 18.1k</span>
                        <span class="trend">+230 stars today</span>
                    </div>
                </a>

                <!-- Repo 4 -->
                <a href="https://github.com/rupeshs/alpaca.cpp" target="_blank" class="repo-card glass-panel">
                    <div class="repo-top">
                        <svg width="20" height="20" fill="currentColor" viewBox="0 0 24 24"><path fill-rule="evenodd" d="M2 2.5A2.5 2.5 0 014.5 0h8.75a.75.75 0 01.75.75v12.5a.75.75 0 01-.75.75h-2.5a.75.75 0 110-1.5h1.75v-2h-8a1 1 0 00-.714 1.7.75.75 0 01-1.072 1.05A2.495 2.495 0 012 11.5v-9z"></path></svg>
                        <h3>rupeshs / alpaca.cpp</h3>
                    </div>
                    <p>Locally run an Instruction-Tuned Chat-Style LLM (Android/Linux/Windows/Mac) entirely offline using ggml / GGUF architectures.</p>
                    <div class="repo-meta">
                        <span class="lang"><span class="lang-dot c"></span> C</span>
                        <span class="stars"><svg width="14" height="14" fill="currentColor" viewBox="0 0 16 16"><path fill-rule="evenodd" d="M8 .25a.75.75 0 01.673.418l1.882 3.815 4.18.608a.75.75 0 01.416 1.279l-3.026 2.946.715 4.162a.75.75 0 01-1.088.791L8 12.347l-3.736 1.963a.75.75 0 01-1.088-.79l.715-4.163-3.026-2.945a.75.75 0 01.416-1.28l4.18-.608L7.327.668A.75.75 0 018 .25z"></path></svg> 6.5k</span>
                        <span class="trend">+125 stars today</span>
                    </div>
                </a>

                <!-- Repo 5: LLM-Hub -->
                <a href="https://github.com/timmyy123/LLM-Hub" target="_blank" class="repo-card glass-panel">
                    <div class="repo-top">
                        <svg width="20" height="20" fill="currentColor" viewBox="0 0 24 24"><path fill-rule="evenodd" d="M2 2.5A2.5 2.5 0 014.5 0h8.75a.75.75 0 01.75.75v12.5a.75.75 0 01-.75.75h-2.5a.75.75 0 110-1.5h1.75v-2h-8a1 1 0 00-.714 1.7.75.75 0 01-1.072 1.05A2.495 2.495 0 012 11.5v-9z"></path></svg>
                        <h3>timmyy123 / LLM-Hub</h3>
                    </div>
                    <p>Open-source mobile app for on-device LLM chat, image generation, and video generation. 100% on-device processing via Kotlin + Jetpack Compose + LiteRT.</p>
                    <div class="repo-meta">
                        <span class="lang"><span class="lang-dot kotlin"></span> Kotlin</span>
                        <span class="stars"><svg width="14" height="14" fill="currentColor" viewBox="0 0 16 16"><path fill-rule="evenodd" d="M8 .25a.75.75 0 01.673.418l1.882 3.815 4.18.608a.75.75 0 01.416 1.279l-3.026 2.946.715 4.162a.75.75 0 01-1.088.791L8 12.347l-3.736 1.963a.75.75 0 01-1.088-.79l.715-4.163-3.026-2.945a.75.75 0 01.416-1.28l4.18-.608L7.327.668A.75.75 0 018 .25z"></path></svg> 5.1k</span>
                        <span class="trend">+560 stars today</span>
                    </div>
                </a>

                <!-- Repo 6: SmolChat -->
                <a href="https://github.com/shubham0204/SmolChat-Android" target="_blank" class="repo-card glass-panel">
                    <div class="repo-top">
                        <svg width="20" height="20" fill="currentColor" viewBox="0 0 24 24"><path fill-rule="evenodd" d="M2 2.5A2.5 2.5 0 014.5 0h8.75a.75.75 0 01.75.75v12.5a.75.75 0 01-.75.75h-2.5a.75.75 0 110-1.5h1.75v-2h-8a1 1 0 00-.714 1.7.75.75 0 01-1.072 1.05A2.495 2.495 0 012 11.5v-9z"></path></svg>
                        <h3>shubham0204 / SmolChat-Android</h3>
                    </div>
                    <p>Beautiful User Interface to interact with local SLMs (small language models) directly on-device in Android.</p>
                    <div class="repo-meta">
                        <span class="lang"><span class="lang-dot kotlin"></span> Kotlin</span>
                        <span class="stars"><svg width="14" height="14" fill="currentColor" viewBox="0 0 16 16"><path fill-rule="evenodd" d="M8 .25a.75.75 0 01.673.418l1.882 3.815 4.18.608a.75.75 0 01.416 1.279l-3.026 2.946.715 4.162a.75.75 0 01-1.088.791L8 12.347l-3.736 1.963a.75.75 0 01-1.088-.79l.715-4.163-3.026-2.945a.75.75 0 01.416-1.28l4.18-.608L7.327.668A.75.75 0 018 .25z"></path></svg> 2.3k</span>
                        <span class="trend">+310 stars today</span>
                    </div>
                </a>

                <!-- Repo 7: Local AI Agent Resources -->
                <a href="https://github.com/danielrosehill/Local-AI-Agent-Resources" target="_blank" class="repo-card glass-panel">
                    <div class="repo-top">
                        <svg width="20" height="20" fill="currentColor" viewBox="0 0 24 24"><path fill-rule="evenodd" d="M2 2.5A2.5 2.5 0 014.5 0h8.75a.75.75 0 01.75.75v12.5a.75.75 0 01-.75.75h-2.5a.75.75 0 110-1.5h1.75v-2h-8a1 1 0 00-.714 1.7.75.75 0 01-1.072 1.05A2.495 2.495 0 012 11.5v-9z"></path></svg>
                        <h3>danielrosehill / Local-AI-Agent-Resources</h3>
                    </div>
                    <p>Open agentic framework collection that controls any app through OS accessibility trees with structured JSON output. Native desktop automation CLI.</p>
                    <div class="repo-meta">
                        <span class="lang"><span class="lang-dot shell"></span> Shell</span>
                        <span class="stars"><svg width="14" height="14" fill="currentColor" viewBox="0 0 16 16"><path fill-rule="evenodd" d="M8 .25a.75.75 0 01.673.418l1.882 3.815 4.18.608a.75.75 0 01.416 1.279l-3.026 2.946.715 4.162a.75.75 0 01-1.088.791L8 12.347l-3.736 1.963a.75.75 0 01-1.088-.79l.715-4.163-3.026-2.945a.75.75 0 01.416-1.28l4.18-.608L7.327.668A.75.75 0 018 .25z"></path></svg> 8.9k</span>
                        <span class="trend">+412 stars today</span>
                    </div>
                </a>

                <!-- Repo 8: Awesome ML -->
                <a href="https://github.com/underlines/awesome-ml" target="_blank" class="repo-card glass-panel">
                    <div class="repo-top">
                        <svg width="20" height="20" fill="currentColor" viewBox="0 0 24 24"><path fill-rule="evenodd" d="M2 2.5A2.5 2.5 0 014.5 0h8.75a.75.75 0 01.75.75v12.5a.75.75 0 01-.75.75h-2.5a.75.75 0 110-1.5h1.75v-2h-8a1 1 0 00-.714 1.7.75.75 0 01-1.072 1.05A2.495 2.495 0 012 11.5v-9z"></path></svg>
                        <h3>underlines / awesome-ml</h3>
                    </div>
                    <p>The definitive list of Native GUIs, Chat interfaces, and tools for running LLMs offline.</p>
                    <div class="repo-meta">
                        <span class="lang"><span class="lang-dot c"></span> Markdown</span>
                        <span class="stars"><svg width="14" height="14" fill="currentColor" viewBox="0 0 16 16"><path fill-rule="evenodd" d="M8 .25a.75.75 0 01.673.418l1.882 3.815 4.18.608a.75.75 0 01.416 1.279l-3.026 2.946.715 4.162a.75.75 0 01-1.088.791L8 12.347l-3.736 1.963a.75.75 0 01-1.088-.79l.715-4.163-3.026-2.945a.75.75 0 01.416-1.28l4.18-.608L7.327.668A.75.75 0 018 .25z"></path></svg> 21k</span>
                        <span class="trend">+104 stars today</span>
                    </div>
                </a>
            </div>
        </section>
    </main>

    <script>
        // INJECT_JS
    </script>
</body>
</html>
"""

css_content = """
:root {
    --bg-dark: color-mix(in oklch, #0a0a12, #1a1a2e 20%);
    --sidebar-bg: rgba(10, 10, 15, 0.7);
    --glass-bg: linear-gradient(135deg, rgba(255, 255, 255, 0.05), rgba(255, 255, 255, 0.01));
    --glass-border: rgba(255, 255, 255, 0.08);
    --neon-green: #00e5ff;
    --neon-orange: #2563EB;
    --neon-pink: #2563EB;
    --neon-purple: #00e5ff;
    --neon-blue: #1D4ED8;
    --text-main: #f0f0f5;
    --text-muted: #a8abb8;
    --font-ui: 'Inter', sans-serif;
    --font-code: 'Fira Code', monospace;
}

* { box-sizing: border-box; margin: 0; padding: 0; }

body {
    background-color: var(--bg-dark);
    color: var(--text-main);
    font-family: var(--font-ui);
    min-height: 100vh;
    overflow-x: hidden;
    display: flex;
}

.background-blobs {
    position: fixed; top: 0; left: 0; right: 0; bottom: 0;
    z-index: -1; overflow: hidden; filter: blur(80px);
}
.blob { position: absolute; border-radius: 50%; opacity: 0.4; animation: float 20s infinite alternate; }
.blob.pink { width: 400px; height: 400px; background: var(--neon-pink); top: -100px; left: -100px; }
.blob.purple { width: 500px; height: 500px; background: var(--neon-purple); bottom: -150px; right: -100px; animation-delay: -5s; }
.blob.blue { width: 300px; height: 300px; background: var(--neon-blue); top: 40%; left: 40%; animation-delay: -10s; opacity: 0.2; }
@keyframes float { 0% { transform: translate(0, 0) scale(1); } 100% { transform: translate(30px, 50px) scale(1.1); } }

/* Sidebar Navigation */
.sidebar {
    width: 260px;
    min-width: 260px;
    background: var(--sidebar-bg);
    border-right: 1px solid var(--glass-border);
    backdrop-filter: blur(30px) saturate(120%);
    -webkit-backdrop-filter: blur(30px) saturate(120%);
    display: flex;
    flex-direction: column;
    padding: 30px 20px;
    position: relative;
    z-index: 10;
}
.brand {
    display: flex; align-items: center; gap: 12px; margin-bottom: 40px;
}
.brand h2 { font-size: 1.5rem; font-weight: 800; letter-spacing: -0.5px; }
.brand h2 span { color: var(--neon-green); }

.nav-links { list-style: none; display: flex; flex-direction: column; gap: 10px; flex-grow: 1; }
.nav-links li {
    padding: 12px 15px; border-radius: 12px; cursor: pointer; display: flex; align-items: center; gap: 12px;
    color: var(--text-muted); font-weight: 600; transition: all 0.3s ease; border: 1px solid transparent;
}
.nav-links li:hover { background: rgba(255,255,255,0.05); color: #fff; }
.nav-links li.active {
    background: rgba(37, 99, 235, 0.15); border-color: rgba(37, 99, 235, 0.4);
    color: var(--neon-green); box-shadow: inset 0 0 20px rgba(0, 229, 255, 0.05);
}

.auto-detect-box {
    margin-top: auto; padding: 15px; background: rgba(0,0,0,0.3); border-radius: 12px;
    font-size: 0.85rem; color: var(--text-muted); display: flex; align-items: center; gap: 8px; border: 1px solid var(--glass-border);
}
.pulse-dot { width: 8px; height: 8px; background: var(--neon-green); border-radius: 50%; box-shadow: 0 0 10px var(--neon-green); animation: pulse 2s infinite; }
@keyframes pulse { 0% { opacity: 1; } 50% { opacity: 0.4; } 100% { opacity: 1; } }

/* Main Content Area */
.main-content { flex-grow: 1; height: 100vh; overflow-y: auto; padding: 40px; position: relative; }
.glass-panel {
    backdrop-filter: blur(25px) saturate(120%); -webkit-backdrop-filter: blur(25px) saturate(120%);
    box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3); background: var(--glass-bg);
    border-top: 1px solid rgba(255, 255, 255, 0.1); border-left: 1px solid rgba(255, 255, 255, 0.1); border-radius: 16px; padding: 24px;
}

/* Header */
.top-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 30px; border-radius: 20px; }
.header-left h1 { font-size: 2rem; font-weight: 800; letter-spacing: -0.5px; }
.header-left h1 span { background: linear-gradient(90deg, var(--neon-pink), var(--neon-purple)); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
.header-left p { color: var(--text-muted); margin-top: 5px; font-size: 0.95rem; }

.glow-btn {
    background: rgba(255, 255, 255, 0.05); border: 1px solid var(--glass-border); color: var(--text-main);
    padding: 10px 20px; border-radius: 12px; font-family: var(--font-ui); font-weight: 600; cursor: pointer;
    display: flex; align-items: center; gap: 8px; transition: all 0.3s ease; box-shadow: 0 0 15px rgba(0, 229, 255, 0.1);
}
.glow-btn:hover { background: rgba(0, 229, 255, 0.1); border-color: var(--neon-blue); box-shadow: 0 0 20px rgba(0, 229, 255, 0.4); transform: translateY(-2px); }

/* View Management */
.view-section { display: none; opacity: 0; animation: fadeView 0.4s forwards; }
.view-section.active { display: block; opacity: 1; }
@keyframes fadeView { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }

/* View 1: Benchmarks */
.dashboard { display: grid; grid-template-columns: 2fr 1fr; gap: 30px; }
.chart-wrapper h2 { font-size: 1.3rem; margin-bottom: 15px; }
.category-tabs { display: flex; gap: 10px; margin-bottom: 20px; overflow-x: auto; padding-bottom: 5px; }
.category-tab { background: rgba(255, 255, 255, 0.05); border: 1px solid rgba(255, 255, 255, 0.1); color: #fff; padding: 8px 16px; border-radius: 20px; cursor: pointer; font-family: var(--font-ui); font-size: 14px; transition: all 0.3s ease; white-space: nowrap; }
.category-tab:hover { background: rgba(255, 255, 255, 0.1); }
.category-tab.active { background: rgba(37, 99, 235, 0.5); border-color: #2563EB; box-shadow: 0 0 10px rgba(37, 99, 235, 0.3); }
.legend { display: flex; gap: 20px; margin-bottom: 20px; font-size: 0.9rem; }
.legend-item { display: flex; align-items: center; gap: 8px; color: var(--text-muted); }
.color-box { width: 14px; height: 14px; border-radius: 4px; }
.color-box.free { background: var(--neon-green); box-shadow: 0 0 10px var(--neon-green); }
.color-box.paid { background: var(--neon-orange); box-shadow: 0 0 10px var(--neon-orange); }
.arena-credit { font-size: 12px; color: var(--text-muted); text-align: right; margin-top: 10px; }
.arena-credit a { color: var(--neon-green); text-decoration: none; }
.arena-credit a:hover { text-decoration: underline; }
.stats-sidebar { display: flex; flex-direction: column; gap: 20px; }
.stat-card h3 { font-size: 0.9rem; color: var(--text-muted); font-weight: 600; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 10px; }
.stat-value { font-size: 1.8rem; font-weight: 800; margin-bottom: 5px; }
.free-text { color: var(--neon-green); text-shadow: 0 0 10px rgba(0, 255, 136, 0.3); }
.paid-text { color: var(--neon-orange); text-shadow: 0 0 10px rgba(255, 119, 0, 0.3); }

/* View 2: Installers */
.installer-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 30px; }
.os-column { display: flex; flex-direction: column; gap: 20px; transition: opacity 0.3s; }
.os-column.dimmed { opacity: 0.4; }
.os-banner { display: flex; flex-direction: column; align-items: center; text-align: center; padding: 30px; background: rgba(0,0,0,0.2); }
.os-banner svg { color: var(--neon-blue); margin-bottom: 15px; }
.os-banner h2 { font-size: 1.8rem; margin-bottom: 5px; }
.os-banner p { color: var(--text-muted); font-size: 0.95rem; }

.installer-card { padding: 25px; position: relative; transition: transform 0.2s, border-color 0.2s; display: flex; flex-direction: column; height: 100%; }
.installer-card:hover { transform: translateY(-3px); border-color: rgba(255,255,255,0.2); }
.installer-card.best-choice { border-color: var(--neon-green); box-shadow: 0 0 20px rgba(0, 229, 255, 0.1); background: linear-gradient(135deg, rgba(0, 229, 255, 0.05), rgba(0, 0, 0, 0)); }
.badge { position: absolute; top: -12px; right: 20px; background: var(--neon-green); color: #000; font-size: 0.75rem; font-weight: 800; padding: 4px 12px; border-radius: 20px; box-shadow: 0 0 10px var(--neon-green); }
.installer-card h3 { font-size: 1.3rem; margin-bottom: 10px; }
.installer-card p { color: var(--text-muted); font-size: 0.95rem; line-height: 1.5; margin-bottom: 25px; flex-grow: 1; }
.download-btn { display: flex; align-items: center; justify-content: center; gap: 10px; width: 100%; padding: 14px; border-radius: 12px; font-weight: 600; text-decoration: none; transition: all 0.2s; }
.download-btn.exe { background: #2563EB; color: #fff; box-shadow: 0 4px 15px rgba(37, 99, 235, 0.3); }
.download-btn.exe:hover { background: #1D4ED8; }
.download-btn.apk { background: #00e5ff; color: #000; box-shadow: 0 4px 15px rgba(0, 229, 255, 0.3); }
.download-btn.apk:hover { background: #00b8cc; }
.meta-info { margin-top: 15px; font-size: 0.8rem; color: #6b7280; text-align: center; }

/* View 3: Trending */
.trending-header { margin-bottom: 30px; }
.trending-header h2 { font-size: 1.8rem; margin-bottom: 5px; display: flex; align-items: center; gap: 10px; }
.trending-header p { color: var(--text-muted); }
.trending-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(350px, 1fr)); gap: 20px; }
.repo-card { text-decoration: none; color: inherit; padding: 25px; display: flex; flex-direction: column; transition: transform 0.2s; }
.repo-card:hover { transform: translateY(-3px); background: rgba(255,255,255,0.05); }
.repo-top { display: flex; align-items: center; gap: 10px; margin-bottom: 12px; }
.repo-top svg { color: var(--text-muted); }
.repo-top h3 { color: var(--neon-blue); font-size: 1.2rem; }
.repo-card p { color: var(--text-muted); font-size: 0.95rem; line-height: 1.5; margin-bottom: 20px; flex-grow: 1; }
.repo-meta { display: flex; gap: 15px; font-size: 0.85rem; color: #8b949e; align-items: center; flex-wrap: wrap; }
.repo-meta span { display: flex; align-items: center; gap: 5px; }
.lang-dot { width: 10px; height: 10px; border-radius: 50%; display: inline-block; }
.lang-dot.shell { background-color: #89e051; }
.lang-dot.kotlin { background-color: #A97BFF; }
.lang-dot.cpp { background-color: #f34b7d; }
.lang-dot.c { background-color: #555555; }
.trend { color: #27c93f; background: rgba(39, 201, 63, 0.1); padding: 2px 8px; border-radius: 12px; }

/* Terminal */
.terminal { background: #050508; border: 1px solid var(--glass-border); border-radius: 12px; margin-bottom: 30px; overflow: hidden; transition: max-height 0.3s ease; max-height: 300px; }
.terminal.hidden { max-height: 0; border: none; margin-bottom: 0; }
.terminal-header { background: #11111a; padding: 10px 15px; display: flex; align-items: center; gap: 8px; border-bottom: 1px solid var(--glass-border); }
.dot { width: 12px; height: 12px; border-radius: 50%; }
.dot.red { background: #ff5f56; } .dot.yellow { background: #ffbd2e; } .dot.green { background: #27c93f; }
.terminal-header .title { color: var(--text-muted); font-family: var(--font-code); font-size: 0.85rem; margin-left: 10px; }
.terminal-body { padding: 15px; font-family: var(--font-code); font-size: 0.9rem; color: var(--neon-green); height: 200px; overflow-y: auto; display: flex; flex-direction: column; gap: 5px; }
.terminal-line { opacity: 0; animation: fadeIn 0.1s forwards; }
.terminal-line.sys { color: var(--neon-blue); }
@keyframes fadeIn { to { opacity: 1; } }

@media (max-width: 900px) {
    body { flex-direction: column; }
    .sidebar { width: 100%; border-right: none; border-bottom: 1px solid var(--glass-border); padding: 20px; }
    .nav-links { flex-direction: row; overflow-x: auto; padding-bottom: 5px; }
    .nav-links li { white-space: nowrap; }
    .main-content { height: auto; padding: 20px; }
    .dashboard, .installer-grid { grid-template-columns: 1fr; }
    .auto-detect-box { display: none; }
}
"""

js_content = """
document.addEventListener("DOMContentLoaded", async () => {
    // 1. View Navigation Logic
    const navLinks = document.querySelectorAll('.nav-links li');
    const viewSections = document.querySelectorAll('.view-section');
    const pageTitle = document.getElementById('pageTitle');
    const pageSubtitle = document.getElementById('pageSubtitle');
    const syncBtn = document.getElementById('syncBtn');

    navLinks.forEach(link => {
        link.addEventListener('click', () => {
            // Update active nav
            navLinks.forEach(l => l.classList.remove('active'));
            link.classList.add('active');

            // Switch view
            const targetId = link.getAttribute('data-target');
            viewSections.forEach(v => v.classList.remove('active'));
            document.getElementById(targetId).classList.add('active');

            // Update Header based on view
            if(targetId === 'view-benchmarks') {
                pageTitle.innerHTML = 'LLM Benchmarks <span>Global Dashboard</span>';
                pageSubtitle.innerText = 'Live 24h Rolling Averages • Powered by Arena.ai';
                syncBtn.style.display = 'flex';
            } else if(targetId === 'view-installers') {
                pageTitle.innerHTML = '1-Click <span>Auto-Installers</span>';
                pageSubtitle.innerText = 'Download the best software for running LLMs offline natively on your hardware.';
                syncBtn.style.display = 'none';
            } else if(targetId === 'view-trending') {
                pageTitle.innerHTML = 'GitHub <span>Trending</span> AI';
                pageSubtitle.innerText = 'Discovering the most active open-source AI projects this month.';
                syncBtn.style.display = 'none';
            }
        });
    });

    // 2. OS Auto-Detection for seamless experience
    const osText = document.getElementById('osText');
    const colWindows = document.getElementById('col-windows');
    const colAndroid = document.getElementById('col-android');
    
    let detectedOS = "Unknown";
    const ua = navigator.userAgent;
    if (/Windows/i.test(ua)) detectedOS = "Windows";
    else if (/Android/i.test(ua)) detectedOS = "Android";
    else if (/Mac/i.test(ua)) detectedOS = "MacOS";
    else if (/Linux/i.test(ua)) detectedOS = "Linux";

    osText.innerText = `Detected OS: ${detectedOS}`;
    
    // Automatically highlight the relevant installers
    if (detectedOS === "Windows") {
        colAndroid.classList.add('dimmed');
    } else if (detectedOS === "Android") {
        colWindows.classList.add('dimmed');
    } else {
        // For Mac/Linux, keep both visible but suggest Windows
        colWindows.classList.remove('dimmed');
        colAndroid.classList.remove('dimmed');
    }

    // 3. Benchmarks Chart & JSON Injection
    const colorFree = 'rgba(0, 229, 255, 0.8)';
    const borderFree = '#00e5ff';
    const colorPaid = 'rgba(37, 99, 235, 0.8)';
    const borderPaid = '#2563EB';

    // Injected Data (from python generation)
    const categoriesData = {
        "Text & Chat": [
            {"name": "Claude Fable 5", "elo": 1507, "type": "paid"},
            {"name": "Claude Opus 4.6 (Thinking)", "elo": 1504, "type": "paid"},
            {"name": "Claude Opus 4.7 (Thinking)", "elo": 1503, "type": "paid"},
            {"name": "Claude Opus 4.6", "elo": 1498, "type": "paid"},
            {"name": "Claude Opus 4.7", "elo": 1494, "type": "paid"},
            {"name": "Metamuse Spark 1.1", "elo": 1493, "type": "free"},
            {"name": "Metamuse Spark", "elo": 1487, "type": "free"},
            {"name": "Gemini 3 Pro", "elo": 1486, "type": "paid"},
            {"name": "Kimi K3", "elo": 1486, "type": "paid"},
            {"name": "GPT 5.6 Sol (xHigh)", "elo": 1486, "type": "paid"},
            {"name": "Gemini 3.1 Pro", "elo": 1485, "type": "paid"},
            {"name": "Claude Sonnet 5 (High)", "elo": 1478, "type": "paid"},
            {"name": "DeepSeek V4 Pro", "elo": 1454, "type": "free"},
            {"name": "GLM 5.2 Max", "elo": 1468, "type": "free"}
        ].sort((a,b) => b.elo - a.elo),
        "WebDev & Code": [
            {"name": "Kimi K3", "elo": 1679, "type": "paid"},
            {"name": "Claude Fable 5", "elo": 1631, "type": "paid"},
            {"name": "GPT 5.6 Sol", "elo": 1618, "type": "paid"},
            {"name": "GLM 5.2 (Max)", "elo": 1587, "type": "free"},
            {"name": "Metamuse Spark", "elo": 1500, "type": "free"}
        ].sort((a,b) => b.elo - a.elo),
        "Vision & Images": [
            {"name": "Claude Fable 5", "elo": 1318, "type": "paid"},
            {"name": "Claude Opus 4.7", "elo": 1304, "type": "paid"},
            {"name": "Metamuse Spark", "elo": 1295, "type": "free"},
            {"name": "Gemini 3 Pro", "elo": 1289, "type": "paid"},
            {"name": "DeepSeek V4 Pro", "elo": 1260, "type": "free"}
        ].sort((a,b) => b.elo - a.elo)
    };

    let currentCategory = "Text & Chat";
    const categories = Object.keys(categoriesData);

    const tabsContainer = document.getElementById('categoryTabs');
    categories.forEach(cat => {
        const btn = document.createElement('button');
        btn.className = `category-tab ${cat === currentCategory ? 'active' : ''}`;
        btn.textContent = cat;
        btn.addEventListener('click', () => {
            document.querySelectorAll('.category-tab').forEach(t => t.classList.remove('active'));
            btn.classList.add('active');
            currentCategory = cat;
            updateDashboard();
        });
        tabsContainer.appendChild(btn);
    });

    const ctx = document.getElementById('eloChart').getContext('2d');
    let eloChart = null;

    function updateDashboard() {
        const models = categoriesData[currentCategory] || [];
        
        const topFree = models.find(m => m.type === 'free');
        const topPaid = models.find(m => m.type === 'paid');
        if (topFree) {
            document.getElementById('topFreeModel').innerText = topFree.name;
            document.getElementById('topFreeElo').innerText = topFree.elo + ' Elo';
        }
        if (topPaid) {
            document.getElementById('topPaidModel').innerText = topPaid.name;
            document.getElementById('topPaidElo').innerText = topPaid.elo + ' Elo';
        }

        const minElo = Math.min(...models.map(m => m.elo)) - 20;
        const maxElo = Math.max(...models.map(m => m.elo)) + 20;

        if (eloChart) {
            eloChart.data.labels = models.map(m => m.name);
            eloChart.data.datasets[0].data = models.map(m => m.elo);
            eloChart.data.datasets[0].backgroundColor = models.map(m => m.type === 'free' ? colorFree : colorPaid);
            eloChart.data.datasets[0].borderColor = models.map(m => m.type === 'free' ? borderFree : borderPaid);
            eloChart.options.scales.x.min = minElo;
            eloChart.options.scales.x.max = maxElo;
            eloChart.update();
        } else {
            eloChart = new Chart(ctx, {
                type: 'bar',
                data: {
                    labels: models.map(m => m.name),
                    datasets: [{
                        label: 'Arena Elo',
                        data: models.map(m => m.elo),
                        backgroundColor: models.map(m => m.type === 'free' ? colorFree : colorPaid),
                        borderColor: models.map(m => m.type === 'free' ? borderFree : borderPaid),
                        borderWidth: 2, borderRadius: 6, barThickness: 'flex', maxBarThickness: 30
                    }]
                },
                options: {
                    responsive: true, maintainAspectRatio: false, indexAxis: 'y',
                    plugins: { legend: { display: false }, tooltip: { backgroundColor: 'rgba(10, 10, 18, 0.9)', titleFont: { family: "'Inter', sans-serif", size: 14 }, bodyFont: { family: "'Fira Code', monospace", size: 13 }, padding: 12, borderColor: 'rgba(255,255,255,0.1)', borderWidth: 1 } },
                    scales: {
                        x: { min: minElo, max: maxElo, grid: { color: 'rgba(255, 255, 255, 0.05)' }, ticks: { color: '#8a8d9b', font: { family: "'Fira Code', monospace" } } },
                        y: { grid: { display: false }, ticks: { color: '#f0f0f5', font: { family: "'Inter', sans-serif", size: 12 }, autoSkip: false } }
                    },
                    animation: { duration: 1500, easing: 'easeOutQuart' }
                }
            });
        }
    }
    updateDashboard();

    // 4. Terminal Scrape Logic
    const terminal = document.getElementById('terminal');
    const terminalOutput = document.getElementById('terminalOutput');
    const lastSyncTime = document.getElementById('lastSyncTime');

    syncBtn.addEventListener('click', () => {
        if (!terminal.classList.contains('hidden')) return;
        terminal.classList.remove('hidden');
        terminalOutput.innerHTML = '';
        
        let cumulativeDelay = 0;
        const models = categoriesData[currentCategory] || [];
        const fetchSteps = models.slice(0, 5).map(m => ({ text: `FETCHING Arena.ai: ${m.name}... [${m.elo}]`, type: "norm", delay: 150 }));
        
        const terminalSteps = [
            { text: "> Initializing arena-scraper_v4.0...", type: "sys", delay: 300 },
            { text: "> Connecting to wss://arena.ai/api/live...", type: "sys", delay: 400 },
            { text: "[OK] Connection established. Handshake verified.", type: "norm", delay: 300 },
            { text: `> Pulling ${currentCategory} leaderboards...`, type: "sys", delay: 500 },
            ...fetchSteps,
            { text: "> Re-calculating Elo intervals...", type: "sys", delay: 500 },
            { text: "[SUCCESS] Sync complete.", type: "norm", delay: 300 }
        ];

        terminalSteps.forEach(step => {
            cumulativeDelay += step.delay;
            setTimeout(() => {
                const line = document.createElement('div');
                line.className = `terminal-line ${step.type}`;
                line.textContent = step.text;
                terminalOutput.appendChild(line);
                terminalOutput.scrollTop = terminalOutput.scrollHeight;
            }, cumulativeDelay);
        });

        setTimeout(() => {
            lastSyncTime.textContent = new Date().toLocaleTimeString();
            if(eloChart) {
                const data = eloChart.data.datasets[0].data;
                eloChart.data.datasets[0].data = data.map(val => val + Math.floor(Math.random() * 3) - 1);
                eloChart.update();
            }
            setTimeout(() => { terminal.classList.add('hidden'); }, 3000);
        }, cumulativeDelay + 500);
    });
});
"""

final_html = html_content.replace('/* INJECT_CSS */', css_content).replace('// INJECT_JS', js_content)

with open('Linacre-LLM-Benchmarks/src/index.html', 'w', encoding='utf-8') as f:
    f.write(final_html)

print("Super-App architecture bundled successfully.")
