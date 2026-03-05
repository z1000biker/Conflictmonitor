// App.js - Frontend για Παγκόσμιος Χάρτης Συγκρούσεων (Palantir Style)

// --- Global State ---
let map;
let markers = {};
let connectionLines = [];
let currentConflicts = [];
let socket;
let selectedConflictId = null;

// --- Configuration ---
const CONFIG = {
    colors: {
        critical: '#ef4444',
        high: '#f97316',
        medium: '#eab308',
        low: '#22c55e',
        proxy: '#ef4444',
        arms: '#f97316',
        alliance: '#3b82f6',
        spillover: '#a855f7'
    },
    mapProvider: 'https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png'
};

// --- Greek Translations ---
const GREEK = {
    regions: {
        'Middle East': 'Μέση Ανατολή',
        'Eastern Europe': 'Ανατολική Ευρώπη',
        'North Africa': 'Βόρεια Αφρική',
        'Southeast Asia': 'Νοτιοανατολική Ασία',
        'Central Africa': 'Κεντρική Αφρική',
        'West Africa': 'Δυτική Αφρική',
        'Southern Africa': 'Νότια Αφρική',
        'Central Asia': 'Κεντρική Ασία',
        'Latin America': 'Λατινική Αμερική'
    },
    types: {
        'armed': 'Ένοπλη Σύγκρουση',
        'civil': 'Εμφύλιος Πόλεμος',
        'insurgency': 'Ανταρσία',
        'unrest': 'Αστάθεια',
        'territorial': 'Εδαφική Διαφορά'
    },
    status: {
        'escalating': 'Κλιμάκωση',
        'ongoing': 'Σε Εξέλιξη',
        'monitoring': 'Παρακολούθηση',
        'deescalating': 'Αποκλιμάκωση'
    }
};

// --- Initialization ---
document.addEventListener('DOMContentLoaded', () => {
    initMap();
    initSocket();
    startClock();

    // Initial Load
    loadConflicts();

    // Event Listeners
    document.getElementById('search-input').addEventListener('input', handleSearch);
});

// --- Map Logic ---
function initMap() {
    map = L.map('map', {
        center: [25, 10],
        zoom: 3,
        minZoom: 2,
        maxZoom: 10,
        zoomControl: false, // Custom UI
        attributionControl: false
    });

    L.tileLayer(CONFIG.mapProvider, {
        subdomains: 'abcd',
        maxZoom: 19
    }).addTo(map);

    // Custom Zoom Control position if needed, or rely on scroll
    new L.Control.Zoom({ position: 'bottomright' }).addTo(map);
}

function updateMarkers(conflicts) {
    // Clear old markers if needed, or update in place. 
    // For simplicity, we'll remove all and redraw for now, 
    // but in production, updating in place is smoother.

    // Store current open popup if any? No, we use side panel now.

    // We keep existing markers to avoid flickering if possible
    const newIds = new Set(conflicts.map(c => c.location));

    // Remove old
    Object.keys(markers).forEach(k => {
        if (!newIds.has(k)) {
            map.removeLayer(markers[k]);
            delete markers[k];
        }
    });

    // Add/Update
    conflicts.forEach(c => {
        if (!c.lat || !c.lng) return;

        const color = CONFIG.colors[c.threat_level] || CONFIG.colors.medium;
        const size = c.threat_level === 'critical' ? 18 : (c.threat_level === 'high' ? 14 : 10);

        // Custom Pulse Icon
        const iconHtml = `
            <div class="marker-pulse" style="
                width: ${size}px; height: ${size}px;
                background: ${color};
                border-radius: 50%;
                box-shadow: 0 0 15px ${color};
                border: 2px solid rgba(255,255,255,0.8);
                animation: ${c.status === 'escalating' ? 'pulse 2s infinite' : 'none'};
            "></div>
        `;

        const icon = L.divIcon({
            html: iconHtml,
            className: 'custom-div-icon',
            iconSize: [size, size],
            iconAnchor: [size / 2, size / 2]
        });

        if (markers[c.location]) {
            markers[c.location].setLatLng([c.lat, c.lng]);
            markers[c.location].setIcon(icon);
        } else {
            const marker = L.marker([c.lat, c.lng], { icon: icon }).addTo(map);
            marker.on('click', () => selectConflict(c));
            markers[c.location] = marker;
        }
    });
}

function drawConnections(connections) {
    // Clear old
    connectionLines.forEach(l => map.removeLayer(l));
    connectionLines = [];

    connections.forEach(conn => {
        if (!conn.from_coords || !conn.to_coords) return;

        const color = CONFIG.colors[conn.type] || '#fff';
        const latlngs = [
            [conn.from_coords.lat, conn.from_coords.lng],
            [conn.to_coords.lat, conn.to_coords.lng]
        ];

        const polyline = L.polyline(latlngs, {
            color: color,
            weight: 1.5,
            opacity: 0.6,
            dashArray: '5, 10',
            className: 'anim-dash' // CSS animation for dash
        }).addTo(map);

        connectionLines.push(polyline);
    });
}

// --- UI Logic ---
function updateStats(conflicts) {
    const total = conflicts.length;
    const critical = conflicts.filter(c => c.threat_level === 'critical').length;
    const escalating = conflicts.filter(c => c.status === 'escalating').length;
    const displaced = conflicts.reduce((acc, c) => acc + (c.displaced || 0), 0);

    document.getElementById('total-conflicts').innerText = total;
    document.getElementById('critical-conflicts').innerText = critical;
    document.getElementById('escalating-conflicts').innerText = escalating;
    document.getElementById('total-displaced').innerText = formatNumber(displaced);
}

function renderConflictList(conflicts) {
    const container = document.getElementById('conflicts-list');
    container.innerHTML = '';

    if (conflicts.length === 0) {
        container.innerHTML = '<div style="text-align:center;color:#666;margin-top:20px;">Δεν βρέθηκαν αποτελέσματα</div>';
        return;
    }

    conflicts.forEach(c => {
        const el = document.createElement('div');
        el.className = `conflict-item border-${c.threat_level || 'medium'}`;
        if (selectedConflictId === c.location) el.classList.add('active');

        el.innerHTML = `
            <div class="c-header">
                <span class="c-name">${c.name}</span>
                <span style="color: ${CONFIG.colors[c.threat_level]}">
                    <i class="ri-alert-fill"></i>
                </span>
            </div>
            <div class="c-meta">
                <span>${GREEK.regions[c.region] || c.region}</span>
                <span>${GREEK.status[c.status] || c.status}</span>
            </div>
        `;

        el.onclick = () => selectConflict(c);
        container.appendChild(el);
    });
}

function selectConflict(conflict) {
    selectedConflictId = conflict.location;

    // Highlight in list
    renderConflictList(currentConflicts); // Re-render to update active class

    // Pan map
    map.flyTo([conflict.lat, conflict.lng], 6, {
        animate: true,
        duration: 1.5
    });

    // Show Details Panel
    const panel = document.getElementById('details-panel');
    const content = document.getElementById('detail-content');

    const color = CONFIG.colors[conflict.threat_level];

    // Build Combatants HTML
    let combatantsHtml = '';
    if (conflict.combatants && conflict.combatants.length > 0) {
        combatantsHtml = `
            <div style="margin-top: 16px;">
                <div class="detail-label">ΕΜΠΛΕΚΟΜΕΝΑ ΜΕΡΗ</div>
                <div style="display: flex; flex-wrap: wrap; gap: 8px;">
                    ${conflict.combatants.map(c => `
                        <span style="background: rgba(255,255,255,0.1); padding: 4px 8px; border-radius: 4px; font-size: 0.8rem; color: #fff;">
                            ${c}
                        </span>
                    `).join('')}
                </div>
            </div>
        `;
    }

    content.innerHTML = `
        <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 8px;">
            <h2 style="font-family:'Orbitron'; color: ${color}; margin: 0; font-size: 1.4rem;">${conflict.name}</h2>
            <div style="background:${color}33; color:${color}; padding:2px 8px; border-radius:4px; font-weight:bold; font-size: 0.8rem;">
                ${(conflict.threat_level || '').toUpperCase()}
            </div>
        </div>
        
        <div style="font-size: 0.9rem; color: #ccc; margin-bottom: 20px; display:flex; gap:10px; align-items:center;">
             <span style="color: ${color}"><i class="ri-sword-line"></i></span>
             <span>${GREEK.types[conflict.type] || conflict.type}</span>
             <span style="color: #666;">|</span>
             <span>${GREEK.regions[conflict.region] || conflict.region}</span>
        </div>
        
        ${conflict.description ? `
            <div style="margin-bottom: 24px; font-size: 0.95rem; line-height: 1.6; color: #e2e8f0; border-left: 2px solid ${color}; padding-left: 12px;">
                ${conflict.description}
            </div>
        ` : ''}
        
        <div class="stat-grid-2">
            <div class="detail-box">
                <div class="detail-label">ΘΥΜΑΤΑ (ΕΚΤ.)</div>
                <div class="detail-val" style="color:#ef4444">${formatNumber(conflict.casualties)}</div>
            </div>
            <div class="detail-box">
                <div class="detail-label">ΕΚΤΟΠΙΣΜΕΝΟΙ</div>
                <div class="detail-val" style="color:#f59e0b">${formatNumber(conflict.displaced)}</div>
            </div>
        </div>

        ${combatantsHtml}
        
        <div style="margin-top: 20px; display: grid; grid-template-columns: 1fr 1fr; gap: 12px; font-size: 0.85rem;">
            <div>
                 <div class="detail-label">ΕΝΑΡΞΗ</div>
                 <div style="color: #fff; font-family:'Rajdhani'; font-weight: 600;">
                    ${conflict.start_date || 'Άγνωστο'}
                 </div>
            </div>
            <div>
                 <div class="detail-label">ΤΕΛΕΥΤΑΙΑ ΕΝΗΜΕΡΩΣΗ</div>
                 <div style="color: #fff; font-family:'Rajdhani';">
                    ${new Date(conflict.last_update || Date.now()).toLocaleDateString('el-GR')}
                 </div>
            </div>
        </div>
        
        <div style="margin-top: 24px; padding-top: 16px; border-top: 1px solid rgba(255,255,255,0.1);">
            <div class="detail-label">ΠΗΓΕΣ</div>
            <div style="color: #94a3b8; font-size: 0.8rem;">${conflict.source || 'Πολλαπλές πηγές'}</div>
        </div>
        
        <button style="
            margin-top: 24px;
            width: 100%;
            padding: 12px;
            background: linear-gradient(90deg, ${color}44, transparent);
            border: 1px solid ${color};
            color: ${color};
            font-family: 'Orbitron';
            cursor: pointer;
            transition: all 0.2s;
            text-transform: uppercase;
            font-size: 0.9rem;
            letter-spacing: 1px;
        " onclick="getReport('${conflict.location}')">
            ΠΡΟΒΟΛΗ ΑΝΑΦΟΡΑΣ INTELLIGENCE
        </button>
    `;

    panel.style.display = 'flex';
}

function getReport(location) {
    // Show simple modal or just an alert for now if no modal UI exists
    // But since we want "Photo" style, let's inject a modal into the body if not exists

    let modal = document.getElementById('report-modal');
    if (!modal) {
        modal = document.createElement('div');
        modal.id = 'report-modal';
        modal.style.cssText = `
            position: fixed; inset: 0; background: rgba(0,0,0,0.8); z-index: 1000;
            display: flex; align-items: center; justify-content: center; backdrop-filter: blur(5px);
        `;
        document.body.appendChild(modal);
    }

    modal.innerHTML = `
        <div style="background: #0f172a; border: 1px solid #3b82f6; width: 800px; max-width: 90%; max-height: 80vh; display: flex; flex-direction: column; border-radius: 8px; box-shadow: 0 0 40px rgba(0,0,0,0.8);">
            <div style="padding: 16px; border-bottom: 1px solid rgba(255,255,255,0.1); display: flex; justify-content: space-between;">
                <h3 style="font-family: 'Orbitron'; color: #3b82f6; margin: 0;">CLASSIFIED INTELLIGENCE BRIEF</h3>
                <button onclick="document.getElementById('report-modal').style.display='none'" style="background: none; border: none; color: #fff; cursor: pointer;">✕</button>
            </div>
            <div id="report-text" style="padding: 24px; overflow-y: auto; font-family: 'Courier New', monospace; color: #e2e8f0; white-space: pre-wrap; line-height: 1.5;">
                <div style="text-align: center; padding: 20px;">
                    <i class="ri-loader-4-line ri-spin" style="font-size: 24px;"></i><br>DECRYPTING DATA...
                </div>
            </div>
            <div style="padding: 12px; background: rgba(0,0,0,0.3); font-size: 0.75rem; color: #64748b; text-align: center;">
                CONFIDENTIAL - FOR AUTHORIZED EYES ONLY
            </div>
        </div>
    `;
    modal.style.display = 'flex';

    // Fetch
    fetch(`/api/report/${location}`)
        .then(r => r.json())
        .then(data => {
            if (data.report) {
                document.getElementById('report-text').innerText = data.report;
            } else {
                document.getElementById('report-text').innerText = "REPORT GENERATION FAILED.";
            }
        })
        .catch(e => {
            document.getElementById('report-text').innerText = "CONNECTION ERROR: " + e;
        });
}

function closeDetails() {
    document.getElementById('details-panel').style.display = 'none';
    selectedConflictId = null;
    renderConflictList(currentConflicts);
    map.flyTo([25, 10], 3);
}

// --- Search & Filter ---
function handleSearch(e) {
    const term = e.target.value.toLowerCase();
    const filtered = currentConflicts.filter(c =>
        c.name.toLowerCase().includes(term) ||
        c.region.toLowerCase().includes(term)
    );
    renderConflictList(filtered);
}

function filterConflicts(type) {
    // Update tabs
    document.querySelectorAll('.filter-tab').forEach(t => t.classList.remove('active'));
    event.target.classList.add('active');

    if (type === 'all') {
        renderConflictList(currentConflicts);
    } else {
        const filtered = currentConflicts.filter(c => c.threat_level === type || c.status === type);
        renderConflictList(filtered);
    }
}

// --- Data Loading ---
async function loadConflicts() {
    try {
        const res = await fetch('/api/conflicts');
        const data = await res.json();
        currentConflicts = data.conflicts;

        updateMarkers(currentConflicts);
        updateStats(currentConflicts);
        renderConflictList(currentConflicts);

        // Load connections too
        loadConnections();

        // Load live feed
        loadLiveFeed();
    } catch (e) {
        console.error("Load error:", e);
    }
}

async function loadConnections() {
    try {
        const res = await fetch('/api/connections');
        const data = await res.json();
        drawConnections(data);
    } catch (e) {
        console.error("Connection error:", e);
    }
}

async function loadLiveFeed() {
    try {
        const res = await fetch('/api/live_feed');
        const data = await res.json();
        renderLiveFeed(data.feed);
    } catch (e) {
        console.error("Feed error:", e);
    }
}

function renderLiveFeed(items) {
    if (!items) return;

    // Check if feed panel exists, if not create it
    let feedPanel = document.getElementById('feed-panel');
    if (!feedPanel) {
        feedPanel = document.createElement('div');
        feedPanel.id = 'feed-panel';
        feedPanel.className = 'ui-panel';
        feedPanel.style.cssText = `
            grid-column: 2; grid-row: 2;
            position: absolute; bottom: 20px; left: 50%; transform: translateX(-50%);
            width: 60%; max-height: 200px;
            display: flex; flex-direction: column;
            background: rgba(15, 23, 42, 0.9);
            border: 1px solid #3b82f6;
            pointer-events: auto;
        `;

        feedPanel.innerHTML = `
            <div style="padding: 8px 12px; background: rgba(59, 130, 246, 0.2); border-bottom: 1px solid rgba(59, 130, 246, 0.2); font-size: 0.8rem; font-family: 'Orbitron'; color: #3b82f6; display: flex; justify-content: space-between;">
                <span>LIVE INTELLIGENCE STREAM (X / TELEGRAM / NEWS)</span>
                <span class="live-dot" style="width: 8px; height: 8px; background: #ef4444; border-radius: 50%; box-shadow: 0 0 5px #ef4444; animation: blink 1s infinite;"></span>
            </div>
            <div id="feed-content" style="overflow-y: auto; flex: 1; padding: 0;"></div>
        `;

        document.querySelector('.ui-layer').appendChild(feedPanel);
    }

    const container = document.getElementById('feed-content');

    // Append new items (or re-render sorted)
    container.innerHTML = items.map(item => `
        <div style="padding: 10px; border-bottom: 1px solid rgba(255,255,255,0.05); font-size: 0.85rem; display: flex; gap: 10px; align-items: start;">
            <div style="font-size: 1.2rem;">
                ${getIconForSource(item.source)}
            </div>
            <div style="flex: 1;">
                <div style="color: #94a3b8; font-size: 0.75rem; margin-bottom: 2px; display: flex; justify-content: space-between;">
                    <span>${item.source}</span>
                    <span>${new Date(item.timestamp).toLocaleTimeString('el-GR')}</span>
                </div>
                <div style="color: #e2e8f0;">
                    ${item.text}
                </div>
            </div>
        </div>
    `).join('');
}

function getIconForSource(source) {
    if (source.includes('Telegram')) return '<i class="ri-telegram-fill" style="color: #38bdf8;"></i>';
    if (source.includes('Reddit')) return '<i class="ri-reddit-fill" style="color: #ff4500;"></i>';
    if (source.includes('News') || source.includes('BBC')) return '<i class="ri-newspaper-fill" style="color: #fbbf24;"></i>';
    return '<i class="ri-radar-fill" style="color: #a855f7;"></i>';
}

// --- Utilities ---
function formatNumber(num) {
    if (!num) return '0';
    if (num >= 1e6) return (num / 1e6).toFixed(1) + 'M';
    if (num >= 1e3) return (num / 1e3).toFixed(1) + 'K';
    return num.toString();
}

function startClock() {
    setInterval(() => {
        const now = new Date();
        document.getElementById('clock').innerText = now.toISOString().split('T')[1].split('.')[0] + ' UTC';
    }, 1000);
}

function initSocket() {
    socket = io();
    socket.on('conflict_update', (data) => {
        currentConflicts = data.conflicts;
        updateMarkers(currentConflicts);
        updateStats(currentConflicts);
        renderConflictList(currentConflicts);
        // Toast?
    });

    socket.on('live_feed_update', (data) => {
        renderLiveFeed(data.feed);
    });
}

function requestUpdate() {
    socket.emit('request_update');
}

function toggleFullScreen() {
    if (!document.fullscreenElement) {
        document.documentElement.requestFullscreen();
    } else {
        if (document.exitFullscreen) {
            document.exitFullscreen();
        }
    }
}
