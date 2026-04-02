// Smart Traffic Intelligence Platform - STCS Terminal Alpha-9 Controller
const API_BASE = 'http://localhost:8001';
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
    countGradient.addColorStop(0, 'rgba(0, 229, 255, 0.4)');
    countGradient.addColorStop(1, 'rgba(0, 229, 255, 0)');

    intensityChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: chartData.labels,
            datasets: [
                {
                    label: 'Vehicle Count',
                    data: chartData.counts,
                    borderColor: '#00e5ff',
                    backgroundColor: countGradient,
                    fill: true,
                    tension: 0.4,
                    borderWidth: 3,
                    pointRadius: 0,
                    pointHoverRadius: 5,
                    pointHoverBackgroundColor: '#00e5ff',
                    pointHoverBorderColor: '#fff',
                    pointHoverBorderWidth: 2
                },
                {
                    label: 'Avg Speed',
                    data: chartData.speeds,
                    borderColor: '#fabd00',
                    fill: false,
                    tension: 0.4,
                    borderWidth: 2,
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
                    grid: { color: 'rgba(255,255,255,0.05)', drawBorder: false },
                    ticks: { color: '#849396', font: { family: "'Inter', sans-serif", size: 10 } }
                },
                y1: {
                    position: 'right',
                    beginAtZero: true,
                    grid: { display: false },
                    ticks: { color: '#fabd00', font: { family: "'Inter', sans-serif", size: 10 } }
                }
            },
            plugins: {
                legend: { display: false },
                tooltip: {
                    backgroundColor: 'rgba(28, 32, 38, 0.9)',
                    titleColor: '#00e5ff',
                    bodyColor: '#dfe2eb',
                    borderColor: 'rgba(0, 229, 255, 0.2)',
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
        document.getElementById('predicted-count').textContent = isNaN(predReal) ? 0 : predReal;
        document.getElementById('prediction-status').textContent = data.predicted_congestion === 'HIGH' ? 'CRITICAL' : 'OPTIMIZED';
        
        if (data.trend) {
            const trendEl = document.getElementById('prediction-trend');
            trendEl.textContent = data.trend;
            trendEl.className = `text-lg font-bold ${data.trend === '↑' ? 'text-error' : (data.trend === '↓' ? 'text-[#4ADE80]' : 'text-primary-container')}`;
        }

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
            updateZoneHealth(data.lane_stats);
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

function updateDeepAnalytics() {
    // Only update if analytics tab is active to save performance
    const activeTab = document.querySelector('.tab-content:not(.hidden)');
    if (activeTab && activeTab.id === 'analytics-tab') {
        // Here we could update more complex charts
    }
}

function updateZoneHealth(laneStats) {
    // Sector Alpha: Lane 1 + Lane 2
    const zone1Count = (laneStats["1"]?.count || 0) + (laneStats["2"]?.count || 0);
    const zone1Density = ((laneStats["1"]?.density || 0) + (laneStats["2"]?.density || 0)) / 2;
    
    // Zone 1 (Sector Alpha)
    document.getElementById('zone-1-sub').textContent = `${zone1Count} Vehicles`;
    document.getElementById('zone-1-bar').style.width = `${zone1Density}%`;
    const z1Status = document.getElementById('zone-1-status');
    if (zone1Density > 80) { z1Status.textContent = 'CRITICAL'; z1Status.className = 'text-[10px] font-bold text-error'; }
    else if (zone1Density > 40) { z1Status.textContent = 'MODERATE'; z1Status.className = 'text-[10px] font-bold text-tertiary-fixed-dim'; }
    else { z1Status.textContent = 'NORMAL'; z1Status.className = 'text-[10px] font-bold text-[#4ADE80]'; }

    // Sector Beta: Lane 3 + Lane 4
    const zone2Count = (laneStats["3"]?.count || 0) + (laneStats["4"]?.count || 0);
    const zone2Density = ((laneStats["3"]?.density || 0) + (laneStats["4"]?.density || 0)) / 2;
    
    // Zone 2 (Sector Beta)
    document.getElementById('zone-2-sub').textContent = `${zone2Count} Vehicles`;
    document.getElementById('zone-2-bar').style.width = `${zone2Density}%`;
    const z2Status = document.getElementById('zone-2-status');
    if (zone2Density > 80) { z2Status.textContent = 'CRITICAL'; z2Status.className = 'text-[10px] font-bold text-error'; }
    else if (zone2Density > 40) { z2Status.textContent = 'MODERATE'; z2Status.className = 'text-[10px] font-bold text-tertiary-fixed-dim'; }
    else { z2Status.textContent = 'NORMAL'; z2Status.className = 'text-[10px] font-bold text-[#4ADE80]'; }
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
        
        const tbody = document.getElementById('history-table-body');
        tbody.innerHTML = '';
        
        data.forEach(row => {
            const tr = document.createElement('tr');
            tr.className = 'border-b border-outline-variant/5 hover:bg-surface-container-high transition-colors';
            const time = new Date(row.timestamp).toLocaleTimeString([], { hour12: false });
            tr.innerHTML = `
                <td class="py-2">${time}</td>
                <td>${row.vehicle_count}</td>
                <td>${parseFloat(row.avg_speed).toFixed(1)}</td>
                <td class="status-${row.congestion_level.toLowerCase()}">${row.congestion_level}</td>
            `;
            tbody.appendChild(tr.cloneNode(true));
            
            // Also update full table in History tab
            const fullTable = document.getElementById('history-table-body-full');
            if (fullTable) {
                const trFull = document.createElement('tr');
                trFull.className = 'border-b border-outline-variant/10 hover:bg-surface-container-high transition-all p-4';
                trFull.innerHTML = `
                    <td class="p-4 font-bold text-primary-container">${time}</td>
                    <td class="p-4">${row.vehicle_count} Objects Detected</td>
                    <td class="p-4">${parseFloat(row.avg_speed).toFixed(1)} km/h</td>
                    <td class="p-4"><span class="px-3 py-1 rounded-full bg-surface-container-high font-bold status-${row.congestion_level.toLowerCase()}">${row.congestion_level}</span></td>
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
    
    // Real-time loop (50ms = 20 FPS for smooth video)
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
    }, 50); 
    
    setInterval(fetchHistory, 5000);
    setInterval(updateClock, 1000);
};
