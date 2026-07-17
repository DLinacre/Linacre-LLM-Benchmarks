import re

with open('/home/user/super_app_builder.py', 'r') as f:
    content = f.read()

new_repos = """
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
"""

content = content.replace("            </div>\n        </section>", new_repos + "        </section>")

with open('/home/user/super_app_builder.py', 'w') as f:
    f.write(content)
