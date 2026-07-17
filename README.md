<div align="center">
  <img src="assets/banner.svg" alt="Linacre.site LLM Hub Banner" width="100%" />

  <br><br>

  **The ultimate Cross-Platform Desktop & Mobile Super-App for tracking, calculating, and installing Local AI.**<br>
  *Built by [David Linacre](https://linacre.site) • Part of the Linacre.site Ecosystem*

  [![Deploy Status](https://img.shields.io/github/actions/workflow/status/LIN4CRE/Linacre-LLM-Benchmarks/deploy-pages.yml?branch=main&label=Pages%20Deploy&style=for-the-badge&color=2563EB)](https://github.com/LIN4CRE/Linacre-LLM-Benchmarks/actions)
  [![Windows Build](https://img.shields.io/github/actions/workflow/status/LIN4CRE/Linacre-LLM-Benchmarks/build-exe.yml?branch=main&label=Windows%20.EXE&style=for-the-badge&color=00e5ff)](https://github.com/LIN4CRE/Linacre-LLM-Benchmarks/actions)
  [![Android Build](https://img.shields.io/github/actions/workflow/status/LIN4CRE/Linacre-LLM-Benchmarks/build-apk.yml?branch=main&label=Android%20.APK&style=for-the-badge&color=3ddc84)](https://github.com/LIN4CRE/Linacre-LLM-Benchmarks/actions)
  [![License: MIT](https://img.shields.io/badge/License-MIT-9333EA.svg?style=for-the-badge)](https://opensource.org/licenses/MIT)

</div>

---

## ⚡ The 2026 AI Super-App

**Linacre LLM Hub** has evolved far beyond a simple leaderboard. It is now a **Single Page Super-App** natively packaged for the Web, Windows (via Electron), and Android (via Capacitor). 

With powerhouse open-weights like **DeepSeek V4 Pro** and **GLM-5.2** trading blows with the proprietary giants, finding the best model—and knowing if your hardware can run it—has never been more confusing. This hub solves that.

### 🌟 Core Features

- 📊 **Arena.ai Integration:** Live 24-hour rolling averages tracking the frontier of Language, Vision, and WebDev models.
- 🧮 **Hardware Matcher:** An interactive VRAM & Context window calculator. Enter your System RAM and GPU VRAM to dynamically test if models like Llama 3 70B or DeepSeek will fit in your memory (calculates exact GPU offload % for PC, Mac, and Android architectures).
- 🖱️ **1-Click Installers:** Curated, auto-detecting OS downloads for the absolute best offline-inference frontends (LM Studio, Layla, AnythingLLM, etc).
- 📈 **GitHub Trending:** A live dashboard scraping the fastest-growing local AI agent repos and tools in the open-source community.
- ✨ **Volumetric UI:** Built with raw HTML/CSS/JS featuring `color-mix()` CSS4 palettes, interactive mouse-glow glassmorphism, and hardware-accelerated animations.

---

## 🚀 Downloads

Because this app utilizes GitHub Actions for continuous integration, you can download the latest compiled binaries right from the [Actions tab](https://github.com/LIN4CRE/Linacre-LLM-Benchmarks/actions).

*   🌐 **Web Version:** [lin4cre.github.io/Linacre-LLM-Benchmarks](https://LIN4CRE.github.io/Linacre-LLM-Benchmarks/)
*   💻 **Windows:** Download the latest `Linacre-LLM-Hub-Windows.exe` artifact.
*   📱 **Android:** Download the latest `Linacre-LLM-Hub-Android.apk` artifact.

---

## 🛠️ Local Development

Want to compile the desktop or mobile versions yourself?

```bash
# 1. Clone the repository
git clone https://github.com/LIN4CRE/Linacre-LLM-Benchmarks.git
cd Linacre-LLM-Benchmarks

# 2. Install Dependencies
npm install

# 3. Build Windows Executable (.exe)
npm run build-win

# 4. Sync & Build Android App (Requires Android Studio)
npx cap sync android
cd android && ./gradlew assembleDebug
```

---

<div align="center">
  <i>Developed with ❤️ for <a href="https://linacre.site">Linacre.site</a></i>
</div>
