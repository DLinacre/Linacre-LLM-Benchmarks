import re

with open('Linacre-LLM-Benchmarks/src/index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# 1. Add Navigation Link
nav_item = """
            <li data-target="view-calculator">
                <svg width="20" height="20" fill="none" stroke="currentColor" stroke-width="2"><path d="M9 3H5a2 2 0 00-2 2v4m6-6h10a2 2 0 012 2v4M9 3v18m0 0h10a2 2 0 002-2V9M9 21H5a2 2 0 01-2-2V9m0 0h20"/></svg>
                Hardware Matcher
            </li>"""
html = html.replace('<li data-target="view-trending">', nav_item + '\n            <li data-target="view-trending">')

# 2. Add Calculator Section HTML
calc_html = """
        <!-- VIEW 4: CALCULATOR -->
        <section id="view-calculator" class="view-section">
            <div class="trending-header">
                <h2><svg width="24" height="24" fill="none" stroke="#00e5ff" stroke-width="2"><path d="M12 2v20M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"/></svg> Hardware Matrix & VRAM Calculator</h2>
                <p>Find out exactly which local LLMs your device can run. Enter your specs below to calculate quantization fitment and estimated performance.</p>
            </div>
            
            <div class="calc-layout">
                <div class="calc-controls glass-panel">
                    <h3>Your Specifications</h3>
                    
                    <div class="input-group">
                        <label>Platform Architecture</label>
                        <div class="radio-group" id="archSelect">
                            <button class="radio-btn active" data-val="pc">PC (NVIDIA/AMD)</button>
                            <button class="radio-btn" data-val="mac">Apple Silicon (Mac)</button>
                            <button class="radio-btn" data-val="android">Android Phone</button>
                        </div>
                    </div>

                    <div class="input-group">
                        <label>System RAM: <span id="ramVal" class="highlight">16 GB</span></label>
                        <input type="range" id="ramSlider" min="4" max="128" step="2" value="16">
                    </div>

                    <div class="input-group" id="vramGroup">
                        <label>Dedicated GPU VRAM: <span id="vramVal" class="highlight">8 GB</span></label>
                        <input type="range" id="vramSlider" min="0" max="24" step="2" value="8">
                    </div>
                </div>

                <div class="calc-results">
                    <div class="models-grid" id="modelsGrid">
                        <!-- Injected via JS -->
                    </div>
                </div>
            </div>
        </section>
"""
html = html.replace('</main>', calc_html + '\n    </main>')

# 3. Add CSS
calc_css = """
    /* Calculator Tab */
    .calc-layout { display: grid; grid-template-columns: 1fr 2fr; gap: 30px; }
    .calc-controls { display: flex; flex-direction: column; gap: 25px; height: fit-content; }
    .calc-controls h3 { color: var(--neon-blue); margin-bottom: 10px; font-size: 1.2rem; }
    .input-group label { display: block; color: var(--text-muted); margin-bottom: 15px; font-weight: 600; font-size: 0.9rem; }
    .input-group .highlight { color: var(--neon-green); font-size: 1.1rem; margin-left: 5px; }
    .radio-group { display: flex; gap: 10px; flex-wrap: wrap; }
    .radio-btn { flex: 1; padding: 10px; background: rgba(255,255,255,0.05); border: 1px solid var(--glass-border); color: var(--text-main); border-radius: 8px; cursor: pointer; transition: 0.2s; font-family: var(--font-ui); font-size: 0.85rem; font-weight: 600;}
    .radio-btn:hover { background: rgba(255,255,255,0.1); }
    .radio-btn.active { background: rgba(0, 229, 255, 0.15); border-color: var(--neon-green); color: var(--neon-green); box-shadow: 0 0 15px rgba(0, 229, 255, 0.2); }
    
    input[type=range] { -webkit-appearance: none; width: 100%; background: transparent; }
    input[type=range]:focus { outline: none; }
    input[type=range]::-webkit-slider-thumb { -webkit-appearance: none; height: 20px; width: 20px; border-radius: 50%; background: var(--neon-green); cursor: pointer; margin-top: -8px; box-shadow: 0 0 15px var(--neon-green); transition: transform 0.1s;}
    input[type=range]::-webkit-slider-thumb:hover { transform: scale(1.2); }
    input[type=range]::-webkit-slider-runnable-track { width: 100%; height: 4px; cursor: pointer; background: rgba(255,255,255,0.2); border-radius: 2px; }
    
    .models-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 20px; }
    .model-card { display: flex; flex-direction: column; justify-content: space-between; gap: 15px; border-top-width: 4px; }
    .model-card.green { border-top-color: #27c93f; }
    .model-card.yellow { border-top-color: #ffbd2e; }
    .model-card.red { border-top-color: #ff5f56; opacity: 0.6; }
    .model-size { font-size: 1.8rem; font-weight: 800; }
    .model-name { color: var(--text-muted); font-size: 0.9rem; }
    .model-status { padding: 6px 12px; border-radius: 8px; font-size: 0.85rem; font-weight: 600; display: inline-block; width: fit-content; }
    .model-card.green .model-status { background: rgba(39, 201, 63, 0.1); color: #27c93f; }
    .model-card.yellow .model-status { background: rgba(255, 189, 46, 0.1); color: #ffbd2e; }
    .model-card.red .model-status { background: rgba(255, 95, 86, 0.1); color: #ff5f56; }

    /* Mouse Glow Effect */
    .glass-panel { position: relative; overflow: hidden; }
    .glass-panel::before { content: ''; position: absolute; top: var(--mouse-y, -100px); left: var(--mouse-x, -100px); width: 400px; height: 400px; background: radial-gradient(circle, rgba(255,255,255,0.05) 0%, transparent 60%); transform: translate(-50%, -50%); transition: opacity 0.3s; opacity: 0; pointer-events: none; z-index: 0; }
    .glass-panel:hover::before { opacity: 1; }
    .glass-panel > * { position: relative; z-index: 1; }

    @media (max-width: 900px) {
        .calc-layout { grid-template-columns: 1fr; }
    }
"""
html = html.replace('</style>', calc_css + '\n    </style>')

# 4. Add JS logic
calc_js = """
    // 5. Interactive Mouse Glow Effect
    const updateGlow = () => {
        document.querySelectorAll('.glass-panel').forEach(card => {
            card.addEventListener('mousemove', e => {
                const rect = card.getBoundingClientRect();
                card.style.setProperty('--mouse-x', `${e.clientX - rect.left}px`);
                card.style.setProperty('--mouse-y', `${e.clientY - rect.top}px`);
            });
        });
    };
    updateGlow(); // run once

    // 6. Hardware Calculator Logic
    const archBtns = document.querySelectorAll('#archSelect .radio-btn');
    const ramSlider = document.getElementById('ramSlider');
    const vramSlider = document.getElementById('vramSlider');
    const ramVal = document.getElementById('ramVal');
    const vramVal = document.getElementById('vramVal');
    const vramGroup = document.getElementById('vramGroup');
    const modelsGrid = document.getElementById('modelsGrid');

    let currentArch = 'pc';

    const localModels = [
        { size: '8B', name: 'Llama 3 / Qwen', memRequired: 5.5, ctxRequired: 1.5 },
        { size: '14B', name: 'Qwen 2.5 14B', memRequired: 9.5, ctxRequired: 2.0 },
        { size: '32B', name: 'Qwen / Mixtral', memRequired: 20.0, ctxRequired: 4.0 },
        { size: '70B', name: 'Llama 3 70B', memRequired: 42.0, ctxRequired: 8.0 },
        { size: '236B', name: 'DeepSeek V4 (MoE)', memRequired: 140.0, ctxRequired: 10.0 }
    ];

    function updateCalculator() {
        const ram = parseFloat(ramSlider.value);
        const vram = parseFloat(vramSlider.value);
        ramVal.innerText = `${ram} GB`;
        vramVal.innerText = `${vram} GB`;

        let availableVRAM = 0;
        let availableRAM = 0;

        if (currentArch === 'pc') {
            availableVRAM = vram;
            availableRAM = ram - 4; // OS reserve
        } else if (currentArch === 'mac') {
            availableVRAM = ram - 4; // Unified
            availableRAM = 0;
        } else if (currentArch === 'android') {
            availableVRAM = ram - 3; // Unified
            availableRAM = 0;
        }

        modelsGrid.innerHTML = '';

        localModels.forEach(model => {
            const totalRequired = model.memRequired + model.ctxRequired;
            
            let status = '';
            let message = '';
            let cssClass = '';

            if (currentArch === 'pc') {
                if (availableVRAM >= totalRequired) {
                    status = 'Green'; message = '🚀 Blazing Fast (Full GPU)'; cssClass = 'green';
                } else if (availableVRAM + availableRAM >= totalRequired) {
                    const offloadPct = Math.round((availableVRAM / totalRequired) * 100);
                    status = 'Yellow'; message = `🐢 Usable (${offloadPct}% GPU Offload)`; cssClass = 'yellow';
                } else {
                    status = 'Red'; message = '❌ Out of Memory (Crash)'; cssClass = 'red';
                }
            } else {
                // Unified memory architectures
                if (availableVRAM >= totalRequired) {
                    status = 'Green'; message = '🚀 Native Speed (Unified GPU)'; cssClass = 'green';
                } else {
                    status = 'Red'; message = '❌ Insufficient Memory'; cssClass = 'red';
                }
            }

            const card = document.createElement('div');
            card.className = `model-card glass-panel ${cssClass}`;
            card.innerHTML = `
                <div>
                    <div class="model-size">${model.size}</div>
                    <div class="model-name">${model.name} (Q4 Quantized)</div>
                </div>
                <div>
                    <div style="font-size: 0.8rem; color: var(--text-muted); margin-bottom: 8px;">Requires ~${totalRequired.toFixed(1)}GB total (Model + Context)</div>
                    <div class="model-status">${message}</div>
                </div>
            `;
            modelsGrid.appendChild(card);
        });

        // Re-attach mouse tracker for newly created cards
        updateGlow();
    }

    archBtns.forEach(btn => {
        btn.addEventListener('click', (e) => {
            archBtns.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            currentArch = btn.dataset.val;
            
            if (currentArch === 'pc') {
                vramGroup.style.display = 'block';
            } else {
                vramGroup.style.display = 'none';
            }
            updateCalculator();
        });
    });

    ramSlider.addEventListener('input', updateCalculator);
    vramSlider.addEventListener('input', updateCalculator);

    // Initial calc render
    updateCalculator();
"""

old_nav_logic = """} else if(targetId === 'view-trending') {
                pageTitle.innerHTML = 'GitHub <span>Trending</span> AI';
                pageSubtitle.innerText = 'Discovering the most active open-source AI projects this month.';
                syncBtn.style.display = 'none';
            }"""

new_nav_logic = old_nav_logic + """ else if(targetId === 'view-calculator') {
                pageTitle.innerHTML = 'Hardware <span>Matcher</span>';
                pageSubtitle.innerText = 'Calculate exactly which local LLMs your device can handle in real-time.';
                syncBtn.style.display = 'none';
            }"""

html = html.replace(old_nav_logic, new_nav_logic)
html = html.replace('});\n</script>', calc_js + '\n});\n</script>')

with open('Linacre-LLM-Benchmarks/src/index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("Added VRAM Calculator Tab and Mouse Tracking effects.")
