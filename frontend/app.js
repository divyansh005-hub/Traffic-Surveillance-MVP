// Smart Traffic Intelligence Platform - STCS Terminal Alpha-9 Controller
const API_BASE = 'http://localhost:8001';
let manualOverride = 'AUTO';
let intensityChart = null;
let chartData = {
    labels: [],
    counts: [],
    speeds: []
};

// 1. Initialize Charts (Neon Aesthetic)
function initCharts() {
    const ctx = document.getElementById('intensityChart').getContext('2d');
    
    // Gradient for counts
    const countGradient = ctx.createLinearGradient(0, 0, 0, 400);
    countGradient.addColorStop(0, 'rgba(14, 165, 233, 0.4)');
    countGradient.addColorStop(1, 'rgba(14, 165, 233, 0)');

    intensityChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: chartData.labels,
            datasets: [
                {
                    label: 'Vehicle Count',
                    data: chartData.counts,
                    borderColor: '#0ea5e9',
                    backgroundColor: countGradient,
                    fill: true,
                    tension: 0.4,
                    borderWidth: 4,
                    pointRadius: 0,
                    pointHoverRadius: 6,
                    pointHoverBackgroundColor: '#0ea5e9',
                    pointHoverBorderColor: '#fff',
                    pointHoverBorderWidth: 2
                },
                {
                    label: 'Avg Speed',
                    data: chartData.speeds,
                    borderColor: '#f59e0b',
                    fill: false,
                    tension: 0.4,
                    borderWidth: 3,
                    pointRadius: 0,
                    yAxisID: 'y1'
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            interaction: { intersect: false, mode: 'index' },
            scales: {
                x: { 
                    display: false 
                },
                y: { 
                    beginAtZero: true, 
                    grid: { color: 'rgba(0,0,0,0.05)', drawBorder: false },
                    ticks: { color: '#64748b', font: { family: "'Inter', sans-serif", size: 10 } }
                },
                y1: {
                    position: 'right',
                    beginAtZero: true,
                    grid: { display: false },
                    ticks: { color: '#f59e0b', font: { family: "'Inter', sans-serif", size: 10 } }
                }
            },
            plugins: {
                legend: { display: false },
                tooltip: {
                    backgroundColor: 'rgba(255, 255, 255, 0.95)',
                    titleColor: '#0f172a',
                    bodyColor: '#475569',
                    borderColor: 'rgba(14, 165, 233, 0.2)',
                    borderWidth: 1,
                    padding: 12,
                    displayColors: false,
                    cornerRadius: 8
                }
            }
        }
    });
}

// 2. Fetch & Update Logic
async function fetchLatest() {
    try {
        const response = await fetch(`${API_BASE}/results/latest`);
        const data = await response.json();
        
        if (data.message === 'No data available') return;

        // Clean values before insertion
        const vCount = parseInt(data.vehicle_count, 10);
        const aSpeed = parseFloat(data.avg_speed);
        
        // Update UI Elements (New IDs)
        document.getElementById('total-vehicle-count').textContent = isNaN(vCount) ? 0 : vCount.toLocaleString();
        document.getElementById('avg-speed-value').innerHTML = `${isNaN(aSpeed) ? 0 : aSpeed} <span class="text-xs text-slate-500">km/h</span>`;
        
        const congestionElem = document.getElementById('congestion-status');
        congestionElem.textContent = data.congestion_level;
        congestionElem.className = `text-xl font-headline font-bold uppercase status-${data.congestion_level.toLowerCase()}`;
        
        document.getElementById('density-value').textContent = `${data.density}%`;
        document.getElementById('lane-changes-value').textContent = data.total_lane_changes;
        
        // System Performance
        const fpsReal = parseFloat(data.fps);
        const latReal = parseFloat(data.latency);
        document.getElementById('system-fps').textContent = isNaN(fpsReal) ? 0 : fpsReal;
        document.getElementById('fps-bar').style.width = `${Math.min((isNaN(fpsReal) ? 0 : fpsReal / 30) * 100, 100)}%`;
        
        document.getElementById('system-latency').textContent = `${isNaN(latReal) ? 0 : latReal} ms`;
        document.getElementById('latency-bar').style.width = `${Math.min((isNaN(latReal) ? 0 : latReal / 500) * 100, 100)}%`;
        
        const confReal = parseFloat(data.avg_confidence);
        document.getElementById('system-confidence').textContent = `${isNaN(confReal) ? 0 : confReal.toFixed(1)}%`;
        document.getElementById('confidence-bar').style.width = `${isNaN(confReal) ? 0 : confReal}%`;
        
        // Prediction & Trends
        const predReal = parseInt(data.predicted_count, 10);
        let trendHtml = '';
        if (data.trend) {
            const trendClass = data.trend === '↑' ? 'text-error' : (data.trend === '↓' ? 'text-[#4ADE80]' : 'text-primary-container');
            trendHtml = `<span class="${trendClass}">${data.trend}</span>`;
        }
        document.getElementById('prediction-full-text').innerHTML = `Prediction: ${isNaN(predReal) ? 0 : predReal} vehicles &rarr; ${data.predicted_congestion} (${trendHtml})`;

        // Insights Panel
        const insightsContainer = document.getElementById('ai-insights-container');
        if (insightsContainer && data.insights && data.insights.length > 0) {
            insightsContainer.innerHTML = data.insights.map(msg => 
                `<div class="flex items-start gap-2 text-xs font-mono text-slate-300">
                    <span class="text-tertiary-fixed font-bold">></span>
                    <span>${msg}</span>
                </div>`
            ).join('');
        }
        
        // Security Tab
        const secAlertBadge = document.getElementById('sec-alert-badge');
        const secAlertMsg = document.getElementById('sec-alert-msg');
        if (secAlertBadge && secAlertMsg) {
            if (data.congestion_level === 'HIGH' || data.density > 80) {
                secAlertBadge.textContent = 'CRITICAL ALERTS';
                secAlertBadge.className = 'px-2 py-1 bg-error-container text-error text-xs font-bold rounded animate-pulse';
                secAlertMsg.textContent = 'High congestion detected. Recommend manual override or route diversion.';
                secAlertMsg.className = 'text-xs text-error mt-2 font-mono';
            } else if (data.congestion_level === 'MEDIUM') {
                secAlertBadge.textContent = 'WARNING';
                secAlertBadge.className = 'px-2 py-1 bg-tertiary-container text-on-tertiary-container text-xs font-bold rounded';
                secAlertMsg.textContent = 'Moderate traffic build-up. Monitoring closely.';
                secAlertMsg.className = 'text-xs text-tertiary-fixed-dim mt-2 font-mono';
            } else {
                secAlertBadge.textContent = 'NO ALERTS';
                secAlertBadge.className = 'px-2 py-1 bg-surface-container-high text-slate-400 text-xs font-bold rounded';
                secAlertMsg.textContent = 'System operating within normal parameters.';
                secAlertMsg.className = 'text-xs text-slate-500 mt-2 font-mono';
            }
        }
        
        // Signal Simulation
        const simTimer = document.getElementById('sim-timer');
        if (simTimer && data.remaining_time !== undefined) {
            simTimer.textContent = `${data.remaining_time.toFixed(1)} s`;
        }

        const simIcon = document.getElementById('sim-icon');
        if (simIcon) {
            let active = data.active_signal || 'AUTO';
            if (manualOverride !== 'AUTO') {
                active = manualOverride;
            }
            
            // Default Red
            document.querySelectorAll('.sim-light').forEach(l => {
                l.className = 'sim-light red';
            });
            
            if (active === 'LEFT_GREEN' || active === 'GREEN') {
                document.getElementById('light-left').className = 'sim-light green';
                document.getElementById('light-right').className = 'sim-light green';
            } else if (active === 'RIGHT_GREEN') {
                document.getElementById('light-top').className = 'sim-light green';
                document.getElementById('light-bottom').className = 'sim-light green';
            }
            
            updateSimulation(data.lane_stats, active);
        }

        // Live Feed
        if (data.frame) {
            document.getElementById('liveFeed').src = `data:image/jpeg;base64,${data.frame}`;
        }

        // HUD Timestamp
        const now = new Date();
        const ms = now.getMilliseconds().toString().padStart(3, '0');
        document.getElementById('hud-timestamp').textContent = `${now.toLocaleTimeString([], { hour12: false })}:${ms} MS`;

        // Update Zone Health (Using Real Lane Stats)
        if (data.lane_stats) {
            updateLaneDistribution(data.lane_stats);
        }

        // Update Chart Data
        const timeStr = now.toLocaleTimeString([], { hour12: false, hour: '2-digit', minute: '2-digit', second: '2-digit' });
        chartData.labels.push(timeStr);
        chartData.counts.push(data.vehicle_count);
        chartData.speeds.push(parseFloat(data.avg_speed));

        if (chartData.labels.length > 30) {
            chartData.labels.shift();
            chartData.counts.shift();
            chartData.speeds.shift();
        }
        
        if (intensityChart) intensityChart.update('none');
        
        // Update Deep Analytics Chart if tab is visible
        updateDeepAnalytics();

    } catch (error) {
        console.error('Fetch error:', error);
    }
}

function updateSimulation(laneStats, activeSignal) {
    if (!laneStats) return;
    
    const isLeftGreen = activeSignal === 'LEFT_GREEN' || activeSignal === 'GREEN';
    const isRightGreen = activeSignal === 'RIGHT_GREEN';
    
    // Map 4 detected lanes to 8 simulated lanes for bidirectional look
    const simMapping = {
        1: { count: laneStats["1"] ? Math.floor(laneStats["1"].count / 2) : 0, isH: true, dir: 'right', isGreen: isLeftGreen },
        2: { count: laneStats["1"] ? Math.ceil(laneStats["1"].count / 2) : 0, isH: true, dir: 'right', isGreen: isLeftGreen },
        5: { count: laneStats["2"] ? Math.floor(laneStats["2"].count / 2) : 0, isH: true, dir: 'left', isGreen: isLeftGreen },
        6: { count: laneStats["2"] ? Math.ceil(laneStats["2"].count / 2) : 0, isH: true, dir: 'left', isGreen: isLeftGreen },
        
        3: { count: laneStats["3"] ? Math.floor(laneStats["3"].count / 2) : 0, isH: false, dir: 'down', isGreen: isRightGreen },
        4: { count: laneStats["3"] ? Math.ceil(laneStats["3"].count / 2) : 0, isH: false, dir: 'down', isGreen: isRightGreen },
        7: { count: laneStats["4"] ? Math.floor(laneStats["4"].count / 2) : 0, isH: false, dir: 'up', isGreen: isRightGreen },
        8: { count: laneStats["4"] ? Math.ceil(laneStats["4"].count / 2) : 0, isH: false, dir: 'up', isGreen: isRightGreen }
    };
    
    for (let i = 1; i <= 8; i++) {
        const queue = document.getElementById(`lane-${i}-queue`);
        if (!queue || !simMapping[i]) continue;
        
        const mapData = simMapping[i];
        const count = mapData.count;
        const currentElements = queue.children.length;
        const targetCount = Math.min(count, 5); // Max 5 vehicles per simulated lane queue visually
        
        if (currentElements < targetCount) {
            for (let j = 0; j < targetCount - currentElements; j++) {
                const dot = document.createElement('div');
                dot.className = mapData.isH ? 'real-vehicle-h' : 'real-vehicle-v';
                queue.appendChild(dot);
            }
        } else if (currentElements > targetCount) {
            for (let j = 0; j < currentElements - targetCount; j++) {
                if (queue.lastChild) queue.removeChild(queue.lastChild);
            }
        }
        
        // Movement logic
        if (mapData.isGreen) {
            const vehicles = Array.from(queue.children).filter(v => !v.classList.contains('moving'));
            if (vehicles.length > 0) {
                const first = vehicles[0];
                first.classList.add('moving');
                first.classList.add(`moving-${mapData.isH ? 'h' : 'v'}-${mapData.dir}`);
                setTimeout(() => {
                    if (queue.contains(first)) queue.removeChild(first);
                }, 800);
            }
        }
    }
}

function updateDeepAnalytics() {
    // Only update if analytics tab is active to save performance
    const activeTab = document.querySelector('.tab-content:not(.hidden)');
    if (activeTab && activeTab.id === 'analytics-tab') {
        // Here we could update more complex charts
    }
}

function updateLaneDistribution(laneStats) {
    if (!laneStats) return;
    for(let i=1; i<=4; i++) {
        const stats = laneStats[i.toString()];
        if(stats) {
            const subElem = document.getElementById(`lane-${i}-sub`);
            if(subElem) subElem.textContent = `${stats.count} Vehicles`;
            
            const denElem = document.getElementById(`lane-${i}-density`);
            if(denElem) denElem.textContent = `${Math.round(stats.density)}%`;
            
            const barElem = document.getElementById(`lane-${i}-bar`);
            if(barElem) {
                barElem.style.width = `${Math.min(stats.density, 100)}%`;
                if(stats.density > 80) barElem.className = 'h-full bg-error transition-all duration-500';
                else if(stats.density > 40) barElem.className = 'h-full bg-tertiary-fixed-dim transition-all duration-500';
                else barElem.className = 'h-full bg-primary transition-all duration-500';
            }
        }
    }
}

function initSidebar() {
    const links = document.querySelectorAll('nav a');
    const sections = {
        'overview-link': 'overview-tab',
        'analytics-link': 'analytics-tab',
        'history-link': 'history-tab',
        'security-link': 'security-tab'
    };

    links.forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            
            // Update Active Link State
            links.forEach(l => l.classList.remove('active', 'bg-tertiary/10', 'text-tertiary'));
            link.classList.add('active', 'bg-tertiary/10', 'text-tertiary');
            
            // Toggle Content
            const targetId = sections[link.id];
            Object.values(sections).forEach(id => {
                const el = document.getElementById(id);
                if (el) el.classList.add('hidden');
            });
            
            const targetEl = document.getElementById(targetId);
            if (targetEl) targetEl.classList.remove('hidden');
        });
    });
}

async function fetchHistory() {
    try {
        const response = await fetch(`${API_BASE}/results/history?limit=15`);
        const data = await response.json();
        
        const fullTable = document.getElementById('history-table-body-full');
        if (fullTable) fullTable.innerHTML = '';
        
        data.forEach(row => {
            const tr = document.createElement('tr');
            tr.className = 'border-b border-outline-variant/5 hover:bg-surface-container-high transition-colors';
            const time = new Date(row.timestamp).toLocaleTimeString([], { hour12: false });
            
            let trendColor = 'text-primary-container';
            if(row.trend === '↑') trendColor = 'text-error';
            if(row.trend === '↓') trendColor = 'text-[#4ADE80]';
            
            const fullTable = document.getElementById('history-table-body-full');
            if (fullTable) {
                const trFull = document.createElement('tr');
                trFull.className = 'border-b border-outline-variant/10 hover:bg-surface-container-high transition-all p-4';
                trFull.innerHTML = `
                    <td class="p-4 font-bold text-primary-container">${time}</td>
                    <td class="p-4">${row.vehicle_count} Objects Detected</td>
                    <td class="p-4">${parseFloat(row.avg_speed).toFixed(1)} km/h</td>
                    <td class="p-4"><span class="px-3 py-1 rounded-full bg-surface-container-high font-bold status-${row.congestion_level.toLowerCase()}">${row.congestion_level}</span></td>
                    <td class="p-4 font-bold ${trendColor}">${row.trend || '→'}</td>
                `;
                fullTable.appendChild(trFull);
            }
        });
    } catch (e) {}
}

function updateClock() {
    const now = new Date();
    document.getElementById('current-time').textContent = now.toLocaleTimeString([], { hour12: false });
}

// 3. Lifecycle
window.onload = () => {
    initCharts();
    updateClock();
    initSidebar();
    
    // Manual Overrides
    const btnRed = document.getElementById('btn-force-red');
    const btnGreen = document.getElementById('btn-force-green');
    const btnAuto = document.getElementById('btn-reset-auto');
    
    if (btnRed) btnRed.addEventListener('click', () => { manualOverride = 'RED'; });
    if (btnGreen) btnGreen.addEventListener('click', () => { manualOverride = 'GREEN'; });
    if (btnAuto) btnAuto.addEventListener('click', () => { manualOverride = 'AUTO'; });
    
    // Real-time loop (33ms polling for 30 FPS smooth video rendering)
    let isFetching = false;
    setInterval(async () => {
        if (isFetching) return;
        isFetching = true;
        try {
            await fetchLatest();
        } catch (e) {
            console.error('Fetch stall:', e);
        } finally {
            isFetching = false;
        }
    }, 33); 
    
    setInterval(fetchHistory, 5000);
    setInterval(updateClock, 1000);
};
