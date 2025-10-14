// ===========================
// DOM Elements
// ===========================
const startDateInput = document.getElementById("start-date");
const endDateInput = document.getElementById("end-date");
const minDistanceInput = document.getElementById("min-distance");
const maxDistanceInput = document.getElementById("max-distance");
const minFareInput = document.getElementById("min-fare");
const maxFareInput = document.getElementById("max-fare");
const applyButton = document.getElementById("apply-filters");

// ===========================
// Chart.js Placeholders
// ===========================
let tripsPerHourChart, fareVsDistanceChart, paymentTypeChart;
let tripsData = []; // Will store data from API

// ===========================
// Helper Functions
// ===========================
async function fetchData(endpoint, params = '') {
    try {
        const res = await fetch(`${endpoint}${params}`);
        return await res.json();
    } catch (err) {
        console.error('Error fetching data:', err);
        return [];
    }
}

function initCharts(data) {
    if(tripsPerHourChart) tripsPerHourChart.destroy();
    if(fareVsDistanceChart) fareVsDistanceChart.destroy();
    if(paymentTypeChart) paymentTypeChart.destroy();

    // Trips per Hour
    const hours = data.map(trip => new Date(trip.pickup_datetime).getHours());
    const hourCounts = {};
    for (let h = 0; h < 24; h++) hourCounts[h] = 0;
    hours.forEach(h => hourCounts[h]++);

    const ctx1 = document.getElementById("tripsPerHourChart").getContext("2d");
    tripsPerHourChart = new Chart(ctx1, {
        type: 'bar',
        data: {
            labels: Object.keys(hourCounts),
            datasets: [{ label: "Trips per Hour", data: Object.values(hourCounts), backgroundColor: "#1e3d59" }]
        },
        options: { responsive: true, plugins: { legend: { display: true }, tooltip: { enabled: true } }, scales: { y: { beginAtZero: true } } }
    });

    // Fare vs Distance (scatter)
    const ctx2 = document.getElementById("fareVsDistanceChart").getContext("2d");
    fareVsDistanceChart = new Chart(ctx2, {
        type: 'scatter',
        data: {
            datasets: [{
                label: "Fare vs Distance",
                data: data.map(trip => ({ x: trip.trip_distance, y: trip.fare_amount })),
                backgroundColor: "#ff6e40"
            }]
        },
        options: {
            responsive: true,
            scales: { x: { title: { display: true, text: "Distance (km)" } }, y: { title: { display: true, text: "Fare ($)" } } }
        }
    });

    // Payment Type Pie Chart
    const paymentCounts = {};
    data.forEach(trip => paymentCounts[trip.payment_type] = (paymentCounts[trip.payment_type] || 0) + 1);
    const ctx3 = document.getElementById("paymentTypeChart").getContext("2d");
    paymentTypeChart = new Chart(ctx3, {
        type: 'pie',
        data: { labels: Object.keys(paymentCounts), datasets: [{ data: Object.values(paymentCounts), backgroundColor: ["#ff6e40","#1e3d59","#f5a623"] }] },
        options: { responsive: true }
    });
}

function populateTable(data) {
    const tbody = document.querySelector("#data-table tbody");
    tbody.innerHTML = "";
    data.forEach(trip => {
        tbody.innerHTML += `
            <tr>
                <td>${trip.pickup_datetime}</td>
                <td>${trip.dropoff_datetime}</td>
                <td>${trip.trip_distance}</td>
                <td>${trip.fare_amount}</td>
                <td>${trip.passenger_count}</td>
                <td>${trip.payment_type}</td>
            </tr>
        `;
    });
}

function generateInsights(data) {
    const insightsDiv = document.getElementById("insights");
    insightsDiv.innerHTML = "";

    if(data.length === 0){
        insightsDiv.innerHTML = "<p>No data available for insights.</p>";
        return;
    }

    const totalTrips = data.length;
    const avgDistance = (data.reduce((sum, t) => sum + t.trip_distance, 0)/totalTrips).toFixed(2);
    const avgFare = (data.reduce((sum, t) => sum + t.fare_amount, 0)/totalTrips).toFixed(2);
    const busiestHour = (() => {
        const hours = data.map(trip => new Date(trip.pickup_datetime).getHours());
        const counts = {};
        hours.forEach(h => counts[h] = (counts[h] || 0) + 1);
        return Object.keys(counts).reduce((a,b) => counts[a] > counts[b] ? a : b);
    })();
    const longestTrip = data.reduce((max,t) => t.trip_distance > max ? t.trip_distance : max, 0);
    const shortestTrip = data.reduce((min,t) => t.trip_distance < min ? t.trip_distance : min, Infinity);
    const highestFare = data.reduce((max,t) => t.fare_amount > max ? t.fare_amount : max, 0);
    const avgPassengers = (data.reduce((sum,t)=>sum+t.passenger_count,0)/totalTrips).toFixed(2);

    const paymentCounts = {};
    data.forEach(t => paymentCounts[t.payment_type] = (paymentCounts[t.payment_type] || 0) + 1);
    const paymentPercent = {};
    Object.keys(paymentCounts).forEach(k => paymentPercent[k] = ((paymentCounts[k]/data.length)*100).toFixed(1));

    insightsDiv.innerHTML = `
        <p><strong>Total Trips:</strong> ${totalTrips}</p>
        <p><strong>Average Distance:</strong> ${avgDistance} km</p>
        <p><strong>Average Fare:</strong> $${avgFare}</p>
        <p><strong>Busiest Hour:</strong> ${busiestHour}:00</p>
        <p><strong>Longest Trip:</strong> ${longestTrip} km</p>
        <p><strong>Shortest Trip:</strong> ${shortestTrip} km</p>
        <p><strong>Highest Fare:</strong> $${highestFare}</p>
        <p><strong>Average Passengers:</strong> ${avgPassengers}</p>
        <p><strong>Payment Distribution:</strong> ${Object.entries(paymentPercent).map(([k,v]) => `${k}: ${v}%`).join(", ")}</p>
    `;
}

// ===========================
// Filter Function
// ===========================
async function applyFilters() {
    const params = new URLSearchParams();
    if(startDateInput.value) params.append('start_date', startDateInput.value);
    if(endDateInput.value) params.append('end_date', endDateInput.value);
    if(minDistanceInput.value) params.append('min_distance', minDistanceInput.value);
    if(maxDistanceInput.value) params.append('max_distance', maxDistanceInput.value);
    if(minFareInput.value) params.append('min_fare', minFareInput.value);
    if(maxFareInput.value) params.append('max_fare', maxFareInput.value);

    // Fetch filtered trips from backend
    tripsData = await fetchData('/filter?' + params.toString());

    initCharts(tripsData);
    populateTable(tripsData);
    generateInsights(tripsData);
}

// ===========================
// Event Listener
// ===========================
applyButton.addEventListener("click", applyFilters);

// ===========================
// Load initial data on page load
// ===========================
window.onload = async function() {
    tripsData = await fetchData('/trips');
    initCharts(tripsData);
    populateTable(tripsData);
    generateInsights(tripsData);
};
