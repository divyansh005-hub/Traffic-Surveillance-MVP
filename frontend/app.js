const API_BASE_URL = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1' 
    ? "http://localhost:8000" 
    : window.location.origin;
let trendChart = null;

async function fetchLatest() {
    try {
        const response = await fetch(`${API_BASE_URL}/results/latest`);
        const data = await response.json();
        
        if (data && data.timestamp) {
            document.getElementById('latest-count').innerText = data.vehicle_count;
            document.getElementById('latest-source').innerText = `Source: ${data.source_id}`;
            
            const congestionEl = document.getElementById('latest-congestion');
            congestionEl.innerText = data.congestion_level;
            congestionEl.className = 'value'; // reset
            
            if (data.congestion_level === 'LOW') congestionEl.style.color = 'var(--low-color)';
            if (data.congestion_level === 'MEDIUM') congestionEl.style.color = 'var(--med-color)';
            if (data.congestion_level === 'HIGH') congestionEl.style.color = 'var(--high-color)';
            
            document.getElementById('latest-time').innerText = `Time: ${new Date(data.timestamp).toLocaleString()}`;
        }
    } catch (error) {
        console.error("Error fetching latest metrics", error);
    }
}

async function fetchHistory() {
    try {
        const response = await fetch(`${API_BASE_URL}/results/history?limit=10`);
        const data = await response.json();
        
        if (data && data.length > 0) {
            updateTable(data);
            updateChart(data.reverse()); // Chronological for chart
        }
    } catch (error) {
        console.error("Error fetching history", error);
    }
}

function updateTable(data) {
    const tbody = document.querySelector('#history-table tbody');
    tbody.innerHTML = '';
    
    data.reverse().forEach(row => {
        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td>${new Date(row.timestamp).toLocaleString()}</td>
            <td>${row.source_id}</td>
            <td>${row.vehicle_count}</td>
            <td><span class="badge ${row.congestion_level.toLowerCase()}">${row.congestion_level}</span></td>
        `;
        tbody.appendChild(tr);
    });
}

function updateChart(data) {
    const ctx = document.getElementById('trendChart').getContext('2d');
    
    const labels = data.map(d => {
        const date = new Date(d.timestamp);
        return `${date.getHours()}:${date.getMinutes()}:${date.getSeconds()}`;
    });
    const counts = data.map(d => d.vehicle_count);
    
    if (trendChart) {
        trendChart.data.labels = labels;
        trendChart.data.datasets[0].data = counts;
        trendChart.update();
    } else {
        trendChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Vehicle Count',
                    data: counts,
                    borderColor: '#3498db',
                    backgroundColor: 'rgba(52, 152, 219, 0.1)',
                    borderWidth: 2,
                    fill: true,
                    tension: 0.3
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: { beginAtZero: true }
                }
            }
        });
    }
}

function refreshData() {
    fetchLatest();
    fetchHistory();
}

// Initial fetch
refreshData();
// Poll every 1 second
setInterval(refreshData, 1000);

async function uploadDemoFile() {
    const fileInput = document.getElementById('demo-file');
    const sourceInput = document.getElementById('demo-source');
    const statusDiv = document.getElementById('upload-status');
    const btn = document.getElementById('upload-btn');
    
    if (fileInput.files.length === 0) {
        statusDiv.innerText = "Please select a file first.";
        statusDiv.style.color = "red";
        return;
    }
    
    const file = fileInput.files[0];
    const formData = new FormData();
    formData.append("file", file);
    
    const sourceName = sourceInput.value || "Demo_Camera";
    
    statusDiv.innerText = "Uploading and processing...";
    statusDiv.style.color = "var(--text-color)";
    btn.disabled = true;
    
    try {
        const response = await fetch(`${API_BASE_URL}/analyze/upload?source_name=${encodeURIComponent(sourceName)}`, {
            method: 'POST',
            body: formData
        });
        
        if (!response.ok) {
            throw new Error(`Server returned ${response.status}`);
        }
        
        const result = await response.json();
        statusDiv.innerText = `Success! Vehicle Count: ${result.data.vehicle_count}, Congestion: ${result.data.congestion_level}`;
        statusDiv.style.color = "green";
        
        // Force refresh
        refreshData();
    } catch (error) {
        statusDiv.innerText = `Error: ${error.message}`;
        statusDiv.style.color = "red";
    } finally {
        btn.disabled = false;
        fileInput.value = "";
    }
}
