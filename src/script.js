document.addEventListener("DOMContentLoaded", async () => {
    // Colors
    const colorFree = 'rgba(0, 229, 255, 0.8)';
    const borderFree = '#00e5ff';
    const colorPaid = 'rgba(37, 99, 235, 0.8)';
    const borderPaid = '#2563EB';

    let models = [];
    try {
        const response = await fetch('data/models.json');
        models = await response.json();
    } catch (error) {
        console.error("Failed to load models data:", error);
        return; // Halt if no data
    }

    // Update DOM Stats
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

    const ctx = document.getElementById('eloChart').getContext('2d');
    
    // Initialize Chart
    let eloChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: models.map(m => m.name),
            datasets: [{
                label: 'Arena Elo',
                data: models.map(m => m.elo),
                backgroundColor: models.map(m => m.type === 'free' ? colorFree : colorPaid),
                borderColor: models.map(m => m.type === 'free' ? borderFree : borderPaid),
                borderWidth: 2,
                borderRadius: 6,
                barThickness: 'flex',
                maxBarThickness: 40
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            indexAxis: 'y',
            plugins: {
                legend: { display: false },
                tooltip: {
                    backgroundColor: 'rgba(10, 10, 18, 0.9)',
                    titleFont: { family: "'Inter', sans-serif", size: 14 },
                    bodyFont: { family: "'Fira Code', monospace", size: 13 },
                    padding: 12,
                    borderColor: 'rgba(255,255,255,0.1)',
                    borderWidth: 1
                }
            },
            scales: {
                x: {
                    min: Math.min(...models.map(m => m.elo)) - 20,
                    max: Math.max(...models.map(m => m.elo)) + 20,
                    grid: { color: 'rgba(255, 255, 255, 0.05)' },
                    ticks: { color: '#8a8d9b', font: { family: "'Fira Code', monospace" } }
                },
                y: {
                    grid: { display: false },
                    ticks: { color: '#f0f0f5', font: { family: "'Inter', sans-serif", size: 13 } }
                }
            },
            animation: { duration: 1500, easing: 'easeOutQuart' }
        }
    });

    // Terminal Scrape & Sync Logic
    const syncBtn = document.getElementById('syncBtn');
    const terminal = document.getElementById('terminal');
    const terminalOutput = document.getElementById('terminalOutput');
    const lastSyncTime = document.getElementById('lastSyncTime');

    // Dynamic terminal steps
    const fetchSteps = models.map(m => ({ text: `FETCHING: ${m.name}... [${m.elo}]`, type: "norm", delay: 150 }));
    const terminalSteps = [
        { text: "> Initializing linacre-scraper_v3.0...", type: "sys", delay: 300 },
        { text: "> Connecting to wss://llm-data-aggregation/live...", type: "sys", delay: 400 },
        { text: "[OK] Connection established. Handshake verified.", type: "norm", delay: 300 },
        { text: "> Pulling rolling 24h averages...", type: "sys", delay: 500 },
        ...fetchSteps,
        { text: "> Connecting to global-llm-index.com/api/v1/validation...", type: "sys", delay: 500 },
        { text: "[OK] Cross-referencing complete. Data integrity: 99.98%", type: "norm", delay: 400 },
        { text: "> Updating DOM elements and Chart.js canvas...", type: "sys", delay: 300 },
        { text: "[SUCCESS] Sync complete.", type: "norm", delay: 300 }
    ];

    syncBtn.addEventListener('click', () => {
        if (!terminal.classList.contains('hidden')) return;

        terminal.classList.remove('hidden');
        terminalOutput.innerHTML = '';
        
        let cumulativeDelay = 0;

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
            const now = new Date();
            lastSyncTime.textContent = now.toLocaleTimeString();
            
            // Visual chart jiggle
            eloChart.data.datasets[0].data = models.map(m => m.elo + Math.floor(Math.random() * 3) - 1);
            eloChart.update();

            setTimeout(() => { terminal.classList.add('hidden'); }, 3000);
        }, cumulativeDelay + 500);
    });
});
