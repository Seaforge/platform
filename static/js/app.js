// ═══════════════════════════════════════════════════════
// SeaForge — Client Application (3D Prototype)
// ═══════════════════════════════════════════════════════

// Cesium ion access token
Cesium.Ion.defaultAccessToken = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJqdGkiOiI5N2Y4YjI0Yi03MWY3LTQxZDEtODJlOC03ZDliNmYyMDI2NTQiLCJpZCI6MjIzNjQ0LCJpYXQiOjE3MTkwMjc1MDh9.2YtBmkN5Pz3z5opd2oBguqP-fL8x93cO-aYm4ikjb58';

var ownShip = { lat: 51.4, lon: 3.2, cog: 45, sog: 8 };
var trainerIdx = -1, trainerCorrect = 0, trainerTotal = 0;
var lightsDb = [];
var viewer; // Cesium Viewer instance

// ── Helpers ──
function toRad(d) { return d * Math.PI / 180; }
function toDeg(r) { return r * 180 / Math.PI; }
function today() { return new Date().toISOString().split('T')[0]; }
function nowTime() { return new Date().toTimeString().slice(0,5); }

// ── API helpers ──
function api(method, url, data) {
    var opts = { method: method, headers: {'Content-Type':'application/json'} };
    if (data) opts.body = JSON.stringify(data);
    return fetch(url, opts).then(function(r) { return r.json(); });
}

// ═══════════════════════════════════════════════════════
// VIEW SWITCHING
// ═══════════════════════════════════════════════════════
function switchView(name) {
    document.querySelectorAll('.view').forEach(function(v) { v.classList.remove('active'); });
    document.querySelectorAll('.top-bar button').forEach(function(b) { b.classList.remove('active'); });
    var view = document.getElementById('view-' + name);
    if (view) view.classList.add('active');
    var btn = document.getElementById('btn-' + name);
    if (btn) btn.classList.add('active');

    // Load data for views
    if (name === 'dashboard') loadDashboard();
    if (name === 'wellbeing') loadCompliance();
    if (name === 'tasks') loadTasks();
    if (name === 'drills') loadDrills();
}

function toggleMapPanel(id) {
    switchView('chart');
    ['layerPanel','colregsPanel','trainerPanel','fleetPanel'].forEach(function(p) {
        var el = document.getElementById(p);
        if (el) el.style.display = (p === id && el.style.display !== 'block') ? 'block' : 'none';
    });
}

// ═══════════════════════════════════════════════════════
// MAP INITIALIZATION
// ═══════════════════════════════════════════════════════
function initMap() {
    viewer = new Cesium.Viewer('map', {
        terrainProvider: Cesium.createWorldTerrain({
            requestWaterMask: true,
            requestVertexNormals: true
        }),
        baseLayerPicker: false,
        animation: false,
        timeline: false,
        geocoder: false,
        homeButton: false,
        sceneModePicker: false,
        navigationHelpButton: false,
        infoBox: true,
        selectionIndicator: true,
        shouldAnimate: true
    });

    // Dark theme for the globe
    viewer.scene.globe.baseColor = Cesium.Color.fromCssColorString('#0a0e14');
    viewer.scene.globe.enableLighting = true;
    viewer.scene.fog.enabled = true;
    viewer.scene.fog.density = 0.0001;

    // Set initial camera view
    viewer.camera.flyTo({
        destination: Cesium.Cartesian3.fromDegrees(ownShip.lon, ownShip.lat, 15000),
        orientation: {
            heading: Cesium.Math.toRadians(0.0),
            pitch: Cesium.Math.toRadians(-45.0),
        }
    });

    // Add mock entities
    addMockEntities();

    // Load lights data
    fetch('/api/lights').then(function(r){return r.json();}).then(function(d){ lightsDb = d; nextQuestion(); });
}

function addMockEntities() {
    // 1. DP2 Tug (Main Vessel)
    const tugPosition = Cesium.Cartesian3.fromDegrees(ownShip.lon, ownShip.lat, 0);
    viewer.entities.add({
        name: 'DP2 Tug',
        position: tugPosition,
        model: {
            uri: 'https://assets.cesium.com/production/models/CesiumMilkTruck/CesiumMilkTruck-kmc.glb', // Placeholder model
            scale: 20.0,
            minimumPixelSize: 64,
        },
        description: '<h3>DP2 Tug</h3><p>Main vessel for the operation.</p>',
    });

    // 2. USV (Unmanned Surface Vehicle)
    const usvPosition = Cesium.Cartesian3.fromDegrees(ownShip.lon + 0.001, ownShip.lat + 0.001, 0);
    viewer.entities.add({
        name: 'USV',
        position: usvPosition,
        ellipsoid: {
            radii: new Cesium.Cartesian3(10.0, 5.0, 4.0),
            material: Cesium.Color.DODGERBLUE.withAlpha(0.8),
            outline: true,
            outlineColor: Cesium.Color.WHITE,
        },
        description: '<h3>USV</h3><p>Unmanned Surface Vehicle supporting the operation.</p>',
    });

    // 3. ROV (Remotely Operated Vehicle) - Submerged
    const rovPosition = Cesium.Cartesian3.fromDegrees(ownShip.lon + 0.0005, ownShip.lat - 0.0005, -200);
    viewer.entities.add({
        name: 'ROV',
        position: rovPosition,
        box: {
            dimensions: new Cesium.Cartesian3(5.0, 3.0, 2.0),
            material: Cesium.Color.ORANGE.withAlpha(0.9),
            outline: true,
            outlineColor: Cesium.Color.WHITE,
        },
        description: '<h3>ROV</h3><p>Submerged at 200m depth.</p>',
    });

    // 4. Tether Polyline (Dynamic Catenary Curve)
    var tetherTension = 0.5;
    // Function to calculate simple 3D Catenary points
    function getCatenaryPositions() {
        var start = Cesium.Cartographic.fromCartesian(tugPosition);
        var end = Cesium.Cartographic.fromCartesian(rovPosition);
        var pts = [];
        var segments = 40;
        var slack = 300.0 * (1.0 - tetherTension); // Slack increases as tension drops
        var baseDrop = Math.abs(start.height - end.height);
        
        for (var i = 0; i <= segments; i++) {
            var t = i / segments;
            var lon = Cesium.Math.lerp(start.longitude, end.longitude, t);
            var lat = Cesium.Math.lerp(start.latitude, end.latitude, t);
            // Linear depth interpolation
            var linearHeight = Cesium.Math.lerp(start.height, end.height, t);
            // Parabolic droop simulating catenary (deeper in middle)
            var droop = slack * Math.sin(t * Math.PI);
            var h = linearHeight - droop;
            if (h < end.height) h = end.height; // floor at anchor depth
            pts.push(Cesium.Cartesian3.fromRadians(lon, lat, h));
        }
        return pts;
    }

    viewer.entities.add({
        name: "ROV Tether",
        polyline: {
            positions: new Cesium.CallbackProperty(getCatenaryPositions, false),
            width: 4,
            material: new Cesium.PolylineDashMaterialProperty({
                color: new Cesium.CallbackProperty(function(time, result) {
                    var hue = tetherTension < 0.6 ? 0.33 : (tetherTension < 0.85 ? 0.16 : 0.0);
                    return Cesium.Color.fromHsl(hue, 1.0, 0.5, 1.0, result);
                }, false),
                dashLength: 16.0,
            }),
            clampToGround: false,
        },
    });

    viewer.zoomTo(viewer.entities);
    // 5. Phase-driven Entity Tinting & Tension (Bridging Mission Control)
    var currentPhase = 'Pre-Tow';
    var tugEntity = viewer.entities.getById('tug-entity'); // we need to add an id to it
    
    function pollPhase() {
        fetch('/api/ops/phase')
            .then(r => r.json())
            .then(data => {
                if (data.currentPhase && data.currentPhase !== currentPhase) {
                    currentPhase = data.currentPhase;
                    updateEntityBasedOnPhase();
                }
            }).catch(console.error);
    }
    setInterval(pollPhase, 2000);

    function updateEntityBasedOnPhase() {
        if (!tugEntity) tugEntity = viewer.entities.values.find(e => e.name === 'DP2 Tug');
        if (!tugEntity || !tugEntity.model) return;
        
        if (currentPhase === 'Pre-Tow') {
            tetherTension = 0.2;
            tugEntity.model.color = Cesium.Color.GREEN.withAlpha(0.7);
        } else if (currentPhase === 'Connect') {
            tetherTension = 0.5;
            tugEntity.model.color = Cesium.Color.YELLOW.withAlpha(0.7);
        } else if (currentPhase === 'Hold') {
            tetherTension = 0.95; // Red tension
            tugEntity.model.color = Cesium.Color.RED.withAlpha(0.7);
            
            // Add a temporary alert primitive above the tug
            if (!viewer.entities.getById('rest-alert')) {
                viewer.entities.add({
                    id: 'rest-alert',
                    position: Cesium.Cartesian3.fromDegrees(ownShip.lon, ownShip.lat, 50),
                    label: {
                        text: 'REST BREACH RISK\nHOLD PHASE',
                        font: 'bold 24px sans-serif',
                        fillColor: Cesium.Color.RED,
                        outlineColor: Cesium.Color.WHITE,
                        outlineWidth: 2,
                        style: Cesium.LabelStyle.FILL_AND_OUTLINE,
                        pixelOffset: new Cesium.Cartesian2(0, -50)
                    }
                });
            }
        } else if (currentPhase === 'Release') {
            tetherTension = 0.1;
            tugEntity.model.color = Cesium.Color.DODGERBLUE.withAlpha(0.7);
            viewer.entities.removeById('rest-alert');
        } else if (currentPhase === 'Complete') {
            tetherTension = 0.0;
            tugEntity.model.color = Cesium.Color.WHITE.withAlpha(1.0);
            viewer.entities.removeById('rest-alert');
        }
    }
    pollPhase(); // initial poll
}


// ── Trainer ──
function nextQuestion() { if(!lightsDb.length) return; trainerIdx=Math.floor(Math.random()*lightsDb.length); var q=lightsDb[trainerIdx]; document.getElementById('trainerContent').innerHTML='<div class="scenario">'+q.scenario+'</div><div class="answer" id="trainerAnswer">'+q.answer+'<br><span class="rule-ref">'+q.rule+'</span></div>'; }
function showAnswer() { var el=document.getElementById('trainerAnswer'); if(el){el.style.display='block';trainerTotal++;document.getElementById('trainerScore').textContent='Questions: '+trainerTotal;} }

// ── Vessel Sidebar ──
function openVesselSidebar(t) { /* full implementation preserved from Flyntrea */ document.getElementById('vsb-name').textContent=t.name; document.getElementById('vsb-type').textContent=t.type; var html='<div class="vsb-section"><div class="vsb-section-title">Motion</div>'; html+='<div class="vsb-row"><span class="vsb-lbl">COG</span><span class="vsb-val highlight">'+t.cog+'&deg;</span></div>'; html+='<div class="vsb-row"><span class="vsb-lbl">SOG</span><span class="vsb-val highlight">'+t.sog+' kts</span></div></div>'; if(t._enc){html+='<div class="vsb-section"><div class="vsb-section-title">COLREGS</div><div class="vsb-colregs-box '+t._risk+'"><div class="vsb-colregs-rule">'+t._enc.rule+' - '+t._enc.role+'</div><div class="vsb-colregs-action">'+t._enc.action+'</div></div></div>';} document.getElementById('vsb-body').innerHTML=html; document.getElementById('vesselSidebar').classList.add('open'); }
function closeVesselSidebar() { document.getElementById('vesselSidebar').classList.remove('open'); }

// Empty functions for features not yet implemented in 3D
function bindLayerToggles() {}
function setupMapClick() {}
function toggleFleet(company, btn) {}
function showFleet(company) {}
function updateFleetTable() {}

// ═══════════════════════════════════════════════════════
// WELLBEING API CALLS
// ═══════════════════════════════════════════════════════
function logRestHours() {
    api('POST', '/api/wellbeing/rest-hours', {
        date: document.getElementById('rest-date').value || today(),
        start_time: document.getElementById('rest-start').value,
        end_time: document.getElementById('rest-end').value,
        type: document.getElementById('rest-type').value
    }).then(function() { loadCompliance(); alert('Logged!'); });
}

function logMeal() {
    api('POST', '/api/wellbeing/meals', {
        date: today(), meal_type: document.getElementById('meal-type').value,
        description: document.getElementById('meal-desc').value,
        rating: parseInt(document.getElementById('meal-rating').value),
        is_galley: parseInt(document.getElementById('meal-galley').value)
    }).then(function() { document.getElementById('meal-desc').value = ''; alert('Logged!'); });
}

function logWorkout() {
    api('POST', '/api/wellbeing/workouts', {
        date: today(), type: document.getElementById('wo-type').value,
        exercise: document.getElementById('wo-exercise').value,
        duration_min: parseInt(document.getElementById('wo-duration').value) || null,
        notes: document.getElementById('wo-notes').value
    }).then(function() { document.getElementById('wo-exercise').value = ''; alert('Logged!'); });
}

function quickMood(level) {
    api('POST', '/api/wellbeing/mood', { date: today(), time: nowTime(), energy: level, mood: level })
        .then(function() { alert('Mood logged: ' + level + '/5'); });
}

function quickWorkout(type) {
    var exercise = prompt('Exercise name:');
    if (!exercise) return;
    api('POST', '/api/wellbeing/workouts', { date: today(), type: type, exercise: exercise })
        .then(function() { alert('Workout logged!'); });
}

function loadCompliance() {
    api('GET', '/api/wellbeing/rest-hours/compliance').then(function(data) {
        var el = document.getElementById('mlc-status');
        if (!el) return;
        var cls = 'status-' + (data.status === 'green' ? 'green' : data.status === 'amber' ? 'amber' : 'red');
        el.innerHTML = '<div class="stat ' + cls + '">' + data.rest_24h + 'h</div><div class="stat-label">rest in last 24h (' + (data.compliant_24h ? 'COMPLIANT' : 'NON-COMPLIANT') + ')</div>' +
            '<div style="margin-top:8px;"><span class="stat ' + cls + '" style="font-size:18px;">' + data.rest_7d + 'h</span> <span class="stat-label">in last 7d (' + (data.compliant_7d ? 'COMPLIANT' : 'NON-COMPLIANT') + ')</span></div>';
        // Update dashboard too
        var d24 = document.getElementById('dash-rest-24h');
        var d7d = document.getElementById('dash-rest-7d');
        if (d24) { d24.textContent = data.rest_24h + 'h'; d24.className = 'stat ' + cls; }
        if (d7d) d7d.textContent = data.rest_7d + 'h';
    });
}

// ═══════════════════════════════════════════════════════
// MAN OVERBOARD (MOB)
// ═══════════════════════════════════════════════════════
var mobActive = false;

function triggerMOB() {
    alert("MOB functionality not yet implemented in 3D view.");
}
function cancelMOB() {}
function mobSearchPattern(type) {}


// ═══════════════════════════════════════════════════════
// TASKS
// ═══════════════════════════════════════════════════════
function addTask() {
    var title = document.getElementById('new-task-title').value.trim();
    if (!title) return;
    api('POST', '/api/ops/tasks', { date: today(), title: title, category: document.getElementById('new-task-cat').value })
        .then(function() { document.getElementById('new-task-title').value = ''; loadTasks(); });
}

function quickAddTask() {
    var title = prompt('Task:');
    if (!title) return;
    api('POST', '/api/ops/tasks', { date: today(), title: title }).then(function() { loadDashboard(); });
}

function toggleTask(id, currentStatus) {
    var newStatus = currentStatus === 'done' ? 'todo' : 'done';
    api('PATCH', '/api/ops/tasks/' + id, { status: newStatus }).then(loadTasks);
}

function loadTasks() {
    api('GET', '/api/ops/tasks').then(function(tasks) {
        var html = '';
        tasks.forEach(function(t) {
            var done = t.status === 'done';
            html += '<div class="list-item">';
            html += '<input type="checkbox" ' + (done ? 'checked' : '') + ' onchange="toggleTask(' + t.id + ',\'' + t.status + '\')" style="accent-color:#4fc3f7;">';
            html += '<span class="title" style="' + (done ? 'text-decoration:line-through;opacity:0.5;' : '') + '">' + t.title + '</span>';
            html += '<span class="badge badge-blue">' + t.category + '</span>';
            html += '</div>';
        });
        document.getElementById('task-list').innerHTML = html || '<p style="color:#78909c;">No tasks. Add one above.</p>';
    });
}

// ═══════════════════════════════════════════════════════
// DRILLS - F5 Drill Log
// ═══════════════════════════════════════════════════════
function logDrill() {
    var conductedAt = document.getElementById('drill-conducted-at').value;
    if (!conductedAt) {
        // Default to current datetime if not set
        var now = new Date();
        conductedAt = now.toISOString().slice(0, 16);
    }
    
    var duration = parseInt(document.getElementById('drill-duration').value);
    if (!duration || duration < 1) {
        alert('Please enter a valid duration (minimum 1 minute)');
        return;
    }
    
    api('POST', '/api/training/drills', {
        type: document.getElementById('drill-type').value,
        conducted_at: conductedAt,
        duration_mins: duration,
        participant_count: parseInt(document.getElementById('drill-participants').value) || 1,
        outcome: document.getElementById('drill-outcome').value,
        officer_in_charge: document.getElementById('drill-officer').value || null,
        notes: document.getElementById('drill-notes').value || null,
        ctrb_section_ref: document.getElementById('drill-ctrb-ref').value || null
    }).then(function() {
        // Clear form
        document.getElementById('drill-duration').value = '';
        document.getElementById('drill-participants').value = '1';
        document.getElementById('drill-officer').value = '';
        document.getElementById('drill-ctrb-ref').value = '';
        document.getElementById('drill-notes').value = '';
        alert('Drill logged!');
        loadDrills();
    }).catch(function(err) {
        console.error('Failed to log drill:', err);
        alert('Error logging drill');
    });
}

function updateDrillFrequency() {
    var type = document.getElementById('drill-type').value;
    var frequency = {
        'abandon_ship': 'Monthly (all crew within 24h of departure if >25% new crew)',
        'fire': 'Monthly (alternating locations on the ship)',
        'mob': 'Monthly',
        'flooding': 'Monthly (as part of damage control)',
        'oil_spill': 'Quarterly (SOPEP)',
        'security': 'Quarterly (ISPS)',
        'medical': 'As required',
        'anchor': 'As required',
        'blackout': 'As required',
        'other': 'As required'
    };
    document.getElementById('drill-frequency').textContent = frequency[type] || 'Select drill type';
}

function loadDrills() {
    var typeFilter = document.getElementById('drill-filter-type').value;
    var outcomeFilter = document.getElementById('drill-filter-outcome').value;
    
    var url = '/api/training/drills?limit=20';
    if (typeFilter) url += '&type=' + encodeURIComponent(typeFilter);
    if (outcomeFilter) url += '&outcome=' + encodeURIComponent(outcomeFilter);
    
    api('GET', url).then(function(drills) {
        var html = '';
        if (drills.length === 0) {
            html = '<p style="color:#78909c;padding:20px;text-align:center;">No drills logged yet.</p>';
        } else {
            drills.forEach(function(d) {
                var conductedDate = new Date(d.conducted_at);
                var dateStr = conductedDate.toLocaleDateString('en-GB', {day:'2-digit', month:'short', year:'numeric'});
                var timeStr = conductedDate.toLocaleTimeString('en-GB', {hour:'2-digit', minute:'2-digit'});
                
                var typeLabels = {
                    'abandon_ship': 'Abandon Ship',
                    'fire': 'Fire',
                    'mob': 'Man Overboard',
                    'flooding': 'Flooding',
                    'oil_spill': 'Oil Spill',
                    'security': 'Security',
                    'medical': 'Medical',
                    'anchor': 'Emergency Anchor',
                    'blackout': 'Blackout',
                    'other': 'Other'
                };
                
                var outcomeBadges = {
                    'satisfactory': '<span class="badge badge-green">Satisfactory</span>',
                    'partial': '<span class="badge badge-amber">Partial</span>',
                    'unsatisfactory': '<span class="badge badge-red">Unsatisfactory</span>'
                };
                
                html += '<div class="list-item">';
                html += '<div style="flex:1;">';
                html += '<div style="display:flex;justify-content:space-between;align-items:center;">';
                html += '<strong>' + (typeLabels[d.type] || d.type) + '</strong>';
                html += '<span style="font-size:11px;color:#78909c;">' + dateStr + ' ' + timeStr + '</span>';
                html += '</div>';
                html += '<div style="font-size:11px;color:#b0bec5;margin-top:4px;">';
                html += d.officer_in_charge ? 'Officer: ' + d.officer_in_charge + ' • ' : '';
                html += d.duration_mins + ' min • ' + d.participant_count + ' participant' + (d.participant_count !== 1 ? 's' : '');
                html += '</div>';
                if (d.ctrb_section_ref) {
                    html += '<div style="font-size:10px;color:#4fc3f7;margin-top:2px;">CTRB: ' + d.ctrb_section_ref + '</div>';
                }
                if (d.notes) {
                    html += '<div style="font-size:11px;color:#90a4ae;margin-top:4px;font-style:italic;">' + d.notes + '</div>';
                }
                html += '</div>';
                html += '<div style="margin-left:8px;">' + (outcomeBadges[d.outcome] || '') + '</div>';
                html += '</div>';
            });
        }
        document.getElementById('drill-list').innerHTML = html;
    }).catch(function(err) {
        console.error('Failed to load drills:', err);
        document.getElementById('drill-list').innerHTML = '<p style="color:#ef5350;">Error loading drills</p>';
    });
}

// Initialize drill type frequency display
document.addEventListener('DOMContentLoaded', function() {
    var drillTypeSelect = document.getElementById('drill-type');
    if (drillTypeSelect) {
        drillTypeSelect.addEventListener('change', updateDrillFrequency);
        // Set default datetime to now
        var now = new Date();
        var nowLocal = new Date(now.getTime() - now.getTimezoneOffset() * 60000);
        document.getElementById('drill-conducted-at').value = nowLocal.toISOString().slice(0, 16);
        updateDrillFrequency();
    }
});

// ═══════════════════════════════════════════════════════
// LIVE AIS (Placeholder)
// ═══════════════════════════════════════════════════════
function loadAISVessels() {}
function startAISPolling() {}
function stopAISPolling() {}

// ═══════════════════════════════════════════════════════
// DASHBOARD
// ═══════════════════════════════════════════════════════
function loadDashboard() {
    loadCompliance();
    api('GET', '/api/ops/tasks?status=todo').then(function(tasks) {
        var el = document.getElementById('dash-tasks-count');
        if (el) el.textContent = tasks.length;
    });
}

// ═══════════════════════════════════════════════════════
// INIT
// ═══════════════════════════════════════════════════════
document.addEventListener('DOMContentLoaded', function() {
    // Set date defaults
    var dateInputs = document.querySelectorAll('input[type="date"]');
    dateInputs.forEach(function(el) { el.value = today(); });

    initMap();
    loadDashboard();
});
