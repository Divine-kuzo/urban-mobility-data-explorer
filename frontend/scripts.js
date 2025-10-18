const API_BASE_URL = 'http://localhost:5000';

// Pagination state
let currentPage = 1;
let currentPerPage = 50;
let currentFilters = {};

async function fetchData(page = 1, perPage = 50) {
    currentPage = page;
    currentPerPage = perPage;
    
    const date = document.getElementById('date-filter').value;
    const minDistance = document.getElementById('min-distance-filter').value;
    
    // Store current filters
    currentFilters = {};
    if (date) currentFilters.date = date;
    if (minDistance) currentFilters.min_distance = minDistance;
    
    // Build URL with pagination and filters
    let url = `${API_BASE_URL}/api/trips?page=${page}&per_page=${perPage}`;
    
    if (date) url += `&date=${date}`;
    if (minDistance) url += `&min_distance=${minDistance}`;

    try {
        console.log('Fetching from:', url);
        
        // Show loading state
        document.getElementById('tripsTableBody').innerHTML = 
            '<tr><td colspan="5">Loading trips...</td></tr>';
        
        // Add timeout to prevent hanging
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), 30000);
        
        // Fetch trips
        const tripsResponse = await fetch(url, { signal: controller.signal });
        clearTimeout(timeoutId);
        
        if (!tripsResponse.ok) {
            throw new Error(`HTTP error! status: ${tripsResponse.status}`);
        }
        
        const tripsData = await tripsResponse.json();
        
        if (!tripsData.success) {
            throw new Error(`API Error: ${tripsData.error}`);
        }
        
        const trips = tripsData.trips;
        const pagination = tripsData.pagination;
        const tableBody = document.getElementById('tripsTableBody');
        
        // Update pagination info
        updatePaginationInfo(pagination);
        
        if (trips.length === 0) {
            tableBody.innerHTML = '<tr><td colspan="5">No trips found</td></tr>';
        } else {
            tableBody.innerHTML = trips.map(trip => `
                <tr>
                    <td>${trip.trip_id}</td>
                    <td>${new Date(trip.pickup_datetime).toLocaleString()}</td>
                    <td>${(trip.trip_distance || 0).toFixed(2)}</td>
                    <td>${(trip.speed_mph || 0).toFixed(2)}</td>
                    <td>${(trip.trip_duration_min || 0).toFixed(2)}</td>
                </tr>
            `).join('');
        }

        // Only fetch summary and insights on first page load
        if (page === 1) {
            await fetchMostRecentTrip();
            await fetchSummaryAndInsights();
        }

    } catch (error) {
        console.error('Error fetching data:', error);
        document.getElementById('tripsTableBody').innerHTML = 
            `<tr><td colspan="5">Error: ${error.message}</td></tr>`;
    }
}

async function fetchMostRecentTrip() {
    try {
        // Fetch the most recent trip
        const recentResponse = await fetch(`${API_BASE_URL}/api/trips?page=1&per_page=1`);
        const recentData = await recentResponse.json();
        
        if (recentData.success && recentData.trips.length > 0) {
            const recentTrip = recentData.trips[0];
            updateMostRecentTripCard(recentTrip);
        } else {
            updateMostRecentTripCard(null);
        }
    } catch (error) {
        console.error('Error fetching most recent trip:', error);
        updateMostRecentTripCard(null);
    }
}

function updateMostRecentTripCard(trip) {
    if (!trip) {
        document.getElementById('recent-pickup-time').textContent = 'No data';
        document.getElementById('recent-distance').textContent = 'No data';
        document.getElementById('recent-duration').textContent = 'No data';
        document.getElementById('recent-speed').textContent = 'No data';
        document.getElementById('recent-trip-id').textContent = 'ID: No data';
        return;
    }

    document.getElementById('recent-pickup-time').textContent = 
        new Date(trip.pickup_datetime).toLocaleString();
    document.getElementById('recent-distance').textContent = 
        `${(trip.trip_distance || 0).toFixed(2)} miles`;
    document.getElementById('recent-duration').textContent = 
        `${(trip.trip_duration_min || 0).toFixed(2)} minutes`;
    document.getElementById('recent-speed').textContent = 
        `${(trip.speed_mph || 0).toFixed(2)} mph`;
    document.getElementById('recent-trip-id').textContent = 
        `ID: ${trip.trip_id}`;
}

async function fetchSummaryAndInsights() {
    try {
        // Show loading state for chart
        showChartLoadingState();
        
        // Fetch summary
        const summaryResponse = await fetch(`${API_BASE_URL}/api/summary`);
        const summaryData = await summaryResponse.json();
        
        if (summaryData.success && summaryData.summary.length > 0) {
            // Hide loading state and show chart
            hideChartLoadingState();
            updateChart('tripsPerHourChart', 'bar', 'Trips per Hour', 
                       summaryData.summary.map(s => s.hour + ':00'), 
                       summaryData.summary.map(s => s.trip_count));
        } else {
            hideChartLoadingState(true);
        }

        // Fetch insights
        const insightsResponse = await fetch(`${API_BASE_URL}/api/insights`);
        const insightsData = await insightsResponse.json();
        
        if (insightsData.success) {
            const insightsDiv = document.getElementById('insights');
            insightsDiv.innerHTML = insightsData.insights.map(insight => `
                <div class="insight">
                    <h3>${insight.name}</h3>
                    <ul>${insight.data.map(d => `<li>${Object.values(d).join(': ')}</li>`).join('')}</ul>
                </div>
            `).join('');
        }
    } catch (error) {
        console.error('Error fetching summary/insights:', error);
        hideChartLoadingState(true);
    }
}

function showChartLoadingState() {
    const chartCanvas = document.getElementById('tripsPerHourChart');
    const placeholder = document.querySelector('.chart-placeholder');
    const loadingIndicator = document.querySelector('.loading-indicator');
    
    if (chartCanvas) chartCanvas.style.display = 'none';
    if (placeholder) placeholder.style.display = 'flex';
    if (loadingIndicator) {
        loadingIndicator.innerHTML = `
            <div class="loading-spinner"></div>
            <span class="loading-text">Loading, please wait...</span>
        `;
    }
}

function hideChartLoadingState(isError = false) {
    const chartCanvas = document.getElementById('tripsPerHourChart');
    const placeholder = document.querySelector('.chart-placeholder');
    const loadingIndicator = document.querySelector('.loading-indicator');
    
    if (placeholder) placeholder.style.display = 'none';
    if (chartCanvas) chartCanvas.style.display = 'block';
    if (loadingIndicator) {
        if (isError) {
            loadingIndicator.innerHTML = '<span style="color: #ff6b6b;">Failed to load chart</span>';
        } else {
            loadingIndicator.innerHTML = '<span style="color: #4CAF50;">✅ Chart loaded</span>';
        }
    }
}

function updatePaginationInfo(pagination) {
    // Update counts
    document.getElementById('showing-count').textContent = 
        Math.min(pagination.per_page, pagination.total_trips - (pagination.page - 1) * pagination.per_page);
    document.getElementById('total-count').textContent = pagination.total_trips;
    
    // Update page info
    document.getElementById('page-info').textContent = 
        `Page ${pagination.page} of ${pagination.total_pages}`;
    
    // Update button states
    document.getElementById('prev-page').disabled = !pagination.has_prev;
    document.getElementById('next-page').disabled = !pagination.has_next;
}

function updateChart(chartId, type, label, labels, data) {
    const ctx = document.getElementById(chartId);
    if (!ctx) {
        console.error(`Chart element ${chartId} not found`);
        return;
    }
    
    // Destroy existing chart if it exists
    if (ctx.chart) {
        ctx.chart.destroy();
    }
    
    ctx.chart = new Chart(ctx, {
        type: type,
        data: {
            labels: labels,
            datasets: [{
                label: label,
                data: data,
                backgroundColor: type === 'bar' ? 'rgba(75, 192, 192, 0.2)' : 'transparent',
                borderColor: 'rgba(75, 192, 192, 1)',
                borderWidth: 2,
                fill: type === 'line'
            }]
        },
        options: {
            responsive: true,
            scales: {
                y: { 
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: label
                    }
                },
                x: {
                    title: {
                        display: true,
                        text: 'Hour of Day'
                    }
                }
            }
        }
    });
}

// Event listeners
document.addEventListener('DOMContentLoaded', function() {
    // Filter button
    const applyButton = document.getElementById('apply-filters');
    if (applyButton) {
        applyButton.addEventListener('click', () => fetchData(1, currentPerPage));
    }
    
    // Pagination buttons
    document.getElementById('prev-page').addEventListener('click', () => {
        if (currentPage > 1) {
            fetchData(currentPage - 1, currentPerPage);
        }
    });
    
    document.getElementById('next-page').addEventListener('click', () => {
        fetchData(currentPage + 1, currentPerPage);
    });
    
    // Items per page selector
    document.getElementById('per-page').addEventListener('change', (e) => {
        fetchData(1, parseInt(e.target.value));
    });
    
    // Enter key in filter fields
    const filterInputs = document.querySelectorAll('.filters input');
    filterInputs.forEach(input => {
        input.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                fetchData(1, currentPerPage);
            }
        });
    });
    
    // Load initial data
    fetchData(1, 50);
});