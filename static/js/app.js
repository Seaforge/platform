// ═══════════════════════════════════════════════════════
// SeaForge — Client Application
// ═══════════════════════════════════════════════════════

var ownShip = { lat: 51.4, lon: 3.2, cog: 45, sog: 8 };
var anchorWatch = { active: false, lat: null, lon: null, radius: 50, circle: null, marker: null };
var trainerIdx = -1, trainerCorrect = 0, trainerTotal = 0;
var lightsDb = [];
var map, vesselMarker, windMarkers, waveMarkers, currentMarkers, aisLayer;
var seamarkLayer, depthLayer, rainLayer, sstLayer, mpaLayer, eezLayer;
var fleetLayers = {}, fleetData = {}, fleetActive = {};
var fleetColors = {'CMB.TECH':'#4fc3f7', 'DEME':'#66bb6a', 'Heerema':'#ffa726'};

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

    // Resize map if switching to chart
    if (name === 'chart' && map) setTimeout(function() { map.invalidateSize(); }, 100);
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
    map = L.map('map', { center: [ownShip.lat, ownShip.lon], zoom: 10 });
    L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
        attribution: '&copy; CartoDB &copy; OSM', maxZoom: 19
    }).addTo(map);

    seamarkLayer = L.tileLayer('https://tiles.openseamap.org/seamark/{z}/{x}/{y}.png', {
        attribution: '&copy; OpenSeaMap', opacity: 0.85
    }).addTo(map);

    depthLayer = L.tileLayer.wms('https://ows.emodnet-bathymetry.eu/wms', {
        layers: 'emodnet:mean_atlas_land', format: 'image/png', transparent: true, opacity: 0.3
    });

    sstLayer = L.tileLayer.wms('https://coastwatch.pfeg.noaa.gov/erddap/wms/jplMURSST41/request', {
        layers: 'jplMURSST41:analysed_sst', format: 'image/png', transparent: true, opacity: 0.45, styles: 'rainbow'
    });

    mpaLayer = L.tileLayer.wms('https://geo.vliz.be/geoserver/MarineRegions/wms', {
        layers: 'MarineRegions:eez_boundaries', format: 'image/png', transparent: true, opacity: 0.4
    });

    eezLayer = L.tileLayer.wms('https://geo.vliz.be/geoserver/MarineRegions/wms', {
        layers: 'MarineRegions:eez', format: 'image/png', transparent: true, opacity: 0.2
    });

    windMarkers = L.layerGroup().addTo(map);
    waveMarkers = L.layerGroup();
    currentMarkers = L.layerGroup();
    aisLayer = L.layerGroup();

    // Own ship
    var vesselIcon = L.divIcon({
        html: '<svg width="28" height="28" viewBox="0 0 24 24"><polygon points="12,2 4,20 12,16 20,20" fill="#4fc3f7" stroke="#0d47a1" stroke-width="1.5"/></svg>',
        iconSize: [28, 28], iconAnchor: [14, 14], className: ''
    });
    vesselMarker = L.marker([ownShip.lat, ownShip.lon], {icon: vesselIcon}).addTo(map)
        .bindPopup('<b>Own Ship</b><br>COG: ' + ownShip.cog + '&deg; SOG: ' + ownShip.sog + ' kts');

    // GPS watch
    if (navigator.geolocation) {
        navigator.geolocation.watchPosition(function(pos) {
            ownShip.lat = pos.coords.latitude;
            ownShip.lon = pos.coords.longitude;
            if (pos.coords.heading) ownShip.cog = pos.coords.heading;
            if (pos.coords.speed) ownShip.sog = pos.coords.speed * 1.94384;
            vesselMarker.setLatLng([ownShip.lat, ownShip.lon]);
            checkAnchorWatch();
        }, function(){}, {enableHighAccuracy: true, maximumAge: 5000});
    }

    loadWind();
    loadRainRadar();
    map.on('moveend', loadWind);
    bindLayerToggles();
    setupMapClick();

    // Load lights data
    fetch('/api/lights').then(function(r){return r.json();}).then(function(d){ lightsDb = d; nextQuestion(); });
}

// ── Wind ──
function beaufortColor(ms) { return ms < 6 ? '#4fc3f7' : ms < 11 ? '#66bb6a' : ms < 17 ? '#ffa726' : '#ef5350'; }
function msToKnots(ms) { return (ms * 1.94384).toFixed(1); }
function msToBeaufort(ms) { var b=[0.5,1.6,3.4,5.5,8,10.8,13.9,17.2,20.8,24.5,28.5,32.7]; for(var i=0;i<b.length;i++) if(ms<b[i]) return i; return 12; }

function loadWind() {
    if (!document.getElementById('lyr-wind').checked) return;
    var c = map.getCenter(), z = map.getZoom();
    var step = z >= 10 ? 0.3 : z >= 8 ? 0.6 : 1.2;
    var pts = [];
    for (var dy=-1; dy<=1; dy++) for (var dx=-1; dx<=1; dx++) pts.push({lat:(c.lat+dy*step).toFixed(2), lon:(c.lng+dx*step).toFixed(2)});
    fetch('https://api.open-meteo.com/v1/forecast?latitude=' + pts.map(function(p){return p.lat;}).join(',') +
        '&longitude=' + pts.map(function(p){return p.lon;}).join(',') + '&current=wind_speed_10m,wind_direction_10m,wind_gusts_10m&wind_speed_unit=ms')
        .then(function(r){return r.json();}).then(function(data) {
            windMarkers.clearLayers();
            var results = Array.isArray(data) ? data : [data];
            results.forEach(function(d,i) {
                if (!d.current) return;
                var ws=d.current.wind_speed_10m, wd=d.current.wind_direction_10m, bft=msToBeaufort(ws), col=beaufortColor(ws);
                var icon = L.divIcon({
                    html:'<div style="transform:rotate('+wd+'deg);color:'+col+';font-size:20px;text-align:center;line-height:1;">&#8593;<div style="transform:rotate(-'+wd+'deg);font-size:9px;">'+bft+'</div></div>',
                    iconSize:[28,28], iconAnchor:[14,14], className:''
                });
                L.marker([parseFloat(pts[i].lat),parseFloat(pts[i].lon)],{icon:icon})
                    .bindPopup('<b>Wind</b><br>'+msToKnots(ws)+' kts ('+bft+' Bft)<br>Dir: '+wd+'&deg;')
                    .addTo(windMarkers);
            });
        }).catch(function(){});
}

function loadRainRadar() {
    fetch('https://api.rainviewer.com/public/weather-maps.json').then(function(r){return r.json();}).then(function(data) {
        var latest = data.radar.past[data.radar.past.length - 1];
        if (rainLayer) map.removeLayer(rainLayer);
        rainLayer = L.tileLayer(data.host + latest.path + '/256/{z}/{x}/{y}/4/1_1.png', { opacity: 0.5 });
        if (document.getElementById('lyr-rain').checked) rainLayer.addTo(map);
    });
}

// ── Navigation math ──
function bearingTo(lat1,lon1,lat2,lon2) { var dlon=toRad(lon2-lon1),la1=toRad(lat1),la2=toRad(lat2); return (toDeg(Math.atan2(Math.sin(dlon)*Math.cos(la2), Math.cos(la1)*Math.sin(la2)-Math.sin(la1)*Math.cos(la2)*Math.cos(dlon)))+360)%360; }
function rangeNm(lat1,lon1,lat2,lon2) { var dlat=toRad(lat2-lat1),dlon=toRad(lon2-lon1); var a=Math.pow(Math.sin(dlat/2),2)+Math.cos(toRad(lat1))*Math.cos(toRad(lat2))*Math.pow(Math.sin(dlon/2),2); return 2*Math.atan2(Math.sqrt(a),Math.sqrt(1-a))*3440.065; }
function computeCPA(own,tgt) { var tx=(tgt.lon-own.lon)*60*Math.cos(toRad(own.lat)),ty=(tgt.lat-own.lat)*60; var ovx=own.sog*Math.sin(toRad(own.cog)),ovy=own.sog*Math.cos(toRad(own.cog)); var tvx=tgt.sog*Math.sin(toRad(tgt.cog)),tvy=tgt.sog*Math.cos(toRad(tgt.cog)); var rvx=tvx-ovx,rvy=tvy-ovy,rv2=rvx*rvx+rvy*rvy; if(rv2<0.0001) return {cpa:Math.sqrt(tx*tx+ty*ty).toFixed(2),tcpa:999}; var t=-(tx*rvx+ty*rvy)/rv2; if(t<0) return {cpa:Math.sqrt(tx*tx+ty*ty).toFixed(2),tcpa:0}; var cx=tx+rvx*t,cy=ty+rvy*t; return {cpa:Math.sqrt(cx*cx+cy*cy).toFixed(2),tcpa:(t*60).toFixed(1)}; }
function classifyEncounter(ownCog,tgtCog,relBrg) { var cd=Math.abs((ownCog-tgtCog+180)%360-180); if(relBrg>112.5&&relBrg<247.5) return {situation:'overtaking',role:'stand-on',rule:'Rule 13',action:'Maintain course and speed.'}; if(cd>170&&(relBrg<6||relBrg>354)) return {situation:'head-on',role:'give-way',rule:'Rule 14',action:'Both alter to STARBOARD.'}; if(relBrg<112.5) return {situation:'crossing',role:'give-way',rule:'Rule 15',action:'Target on STBD. Alter to STARBOARD.'}; return {situation:'crossing',role:'stand-on',rule:'Rule 17',action:'Maintain course/speed.'}; }

// ── Anchor Watch ──
function toggleAnchorWatch() { var btn=document.getElementById('btn-anchor'); if(anchorWatch.active){anchorWatch.active=false;btn.classList.remove('active');if(anchorWatch.circle)map.removeLayer(anchorWatch.circle);if(anchorWatch.marker)map.removeLayer(anchorWatch.marker);}else{anchorWatch.active=true;anchorWatch.lat=ownShip.lat;anchorWatch.lon=ownShip.lon;btn.classList.add('active');btn.style.background='#e65100';anchorWatch.circle=L.circle([anchorWatch.lat,anchorWatch.lon],{radius:anchorWatch.radius,color:'#ffa726',fillColor:'#ffa726',fillOpacity:0.06,weight:2,dashArray:'8,6'}).addTo(map);anchorWatch.marker=L.marker([anchorWatch.lat,anchorWatch.lon],{icon:L.divIcon({html:'<div style="font-size:20px;">&#9875;</div>',iconSize:[20,20],iconAnchor:[10,10],className:''})}).addTo(map);} }
function checkAnchorWatch() { if(!anchorWatch.active)return; var d=rangeNm(anchorWatch.lat,anchorWatch.lon,ownShip.lat,ownShip.lon)*1852; if(d>anchorWatch.radius){anchorWatch.circle.setStyle({color:'#ef5350',fillColor:'#ef5350',fillOpacity:0.15});if('Notification' in window&&Notification.permission==='granted') new Notification('ANCHOR DRAGGING',{body:'Drift: '+d.toFixed(0)+'m!'});} }
if ('Notification' in window) Notification.requestPermission();

// ── Trainer ──
function nextQuestion() { if(!lightsDb.length) return; trainerIdx=Math.floor(Math.random()*lightsDb.length); var q=lightsDb[trainerIdx]; document.getElementById('trainerContent').innerHTML='<div class="scenario">'+q.scenario+'</div><div class="answer" id="trainerAnswer">'+q.answer+'<br><span class="rule-ref">'+q.rule+'</span></div>'; }
function showAnswer() { var el=document.getElementById('trainerAnswer'); if(el){el.style.display='block';trainerTotal++;document.getElementById('trainerScore').textContent='Questions: '+trainerTotal;} }

// ── Vessel Sidebar ──
function openVesselSidebar(t) { /* full implementation preserved from Flyntrea */ document.getElementById('vsb-name').textContent=t.name; document.getElementById('vsb-type').textContent=t.type; var html='<div class="vsb-section"><div class="vsb-section-title">Motion</div>'; html+='<div class="vsb-row"><span class="vsb-lbl">COG</span><span class="vsb-val highlight">'+t.cog+'&deg;</span></div>'; html+='<div class="vsb-row"><span class="vsb-lbl">SOG</span><span class="vsb-val highlight">'+t.sog+' kts</span></div></div>'; if(t._enc){html+='<div class="vsb-section"><div class="vsb-section-title">COLREGS</div><div class="vsb-colregs-box '+t._risk+'"><div class="vsb-colregs-rule">'+t._enc.rule+' - '+t._enc.role+'</div><div class="vsb-colregs-action">'+t._enc.action+'</div></div></div>';} document.getElementById('vsb-body').innerHTML=html; document.getElementById('vesselSidebar').classList.add('open'); }
function closeVesselSidebar() { document.getElementById('vesselSidebar').classList.remove('open'); }

// ── Layer toggles ──
function bindLayerToggles() {
    function bind(id,layer,loadFn) { document.getElementById(id).addEventListener('change',function(){if(this.checked){if(loadFn)loadFn();layer.addTo(map);}else map.removeLayer(layer);}); }
    bind('lyr-seamark',seamarkLayer); bind('lyr-depth',depthLayer); bind('lyr-wind',windMarkers,loadWind); bind('lyr-sst',sstLayer); bind('lyr-mpa',mpaLayer); bind('lyr-eez',eezLayer); bind('lyr-vessel',vesselMarker); bind('lyr-wave',waveMarkers); bind('lyr-current',currentMarkers);
    document.getElementById('lyr-rain').addEventListener('change',function(){if(this.checked){if(rainLayer)rainLayer.addTo(map);else loadRainRadar();}else{if(rainLayer)map.removeLayer(rainLayer);}});
    document.getElementById('lyr-ais').addEventListener('change',function(){if(this.checked){aisLayer.addTo(map);}else{map.removeLayer(aisLayer);}});
}

function setupMapClick() {
    map.on('click', function(e) {
        closeVesselSidebar();
        var lat=e.latlng.lat.toFixed(4), lon=e.latlng.lng.toFixed(4);
        var panel=document.getElementById('infoPanel'); panel.style.display='block';
        document.getElementById('infoPanelTitle').textContent='Loading...';
        Promise.all([
            fetch('https://api.open-meteo.com/v1/forecast?latitude='+lat+'&longitude='+lon+'&current=wind_speed_10m,wind_direction_10m,wind_gusts_10m,temperature_2m,pressure_msl&wind_speed_unit=ms').then(function(r){return r.json();}),
            fetch('https://marine-api.open-meteo.com/v1/marine?latitude='+lat+'&longitude='+lon+'&current=wave_height,wave_period,ocean_current_velocity,ocean_current_direction').then(function(r){return r.json();})
        ]).then(function(r) {
            var w=r[0].current||{}, m=r[1].current||{};
            document.getElementById('infoPanelTitle').textContent=lat+', '+lon;
            var h='';
            if(w.wind_speed_10m!=null) h+='<div class="row"><span class="lbl">Wind</span><span class="val">'+msToKnots(w.wind_speed_10m)+' kts '+msToBeaufort(w.wind_speed_10m)+' Bft</span></div>';
            if(w.temperature_2m!=null) h+='<div class="row"><span class="lbl">Air</span><span class="val">'+w.temperature_2m+'&deg;C</span></div>';
            if(w.pressure_msl!=null) h+='<div class="row"><span class="lbl">Pressure</span><span class="val">'+w.pressure_msl+' hPa</span></div>';
            if(m.wave_height!=null) h+='<div class="row"><span class="lbl">Waves</span><span class="val">'+m.wave_height+'m</span></div>';
            document.getElementById('infoPanelContent').innerHTML=h||'No marine data';
        });
    });
    map.on('dblclick', function(){document.getElementById('infoPanel').style.display='none';});
}

// ── Fleet ──
function toggleFleet(company, btn) {
    if(fleetActive[company]){map.removeLayer(fleetLayers[company]);fleetActive[company]=false;btn.style.background='transparent';btn.style.color=fleetColors[company];updateFleetTable();return;}
    btn.style.background=fleetColors[company];btn.style.color='#111820';fleetActive[company]=true;
    if(fleetData[company]){showFleet(company);return;}
    fetch('/api/fleet/'+encodeURIComponent(company)).then(function(r){return r.json();}).then(function(data){fleetData[company]=data;showFleet(company);});
}
function showFleet(company) { if(fleetLayers[company])map.removeLayer(fleetLayers[company]);fleetLayers[company]=L.layerGroup().addTo(map);updateFleetTable(); }
function updateFleetTable() {
    var active=Object.keys(fleetActive).filter(function(k){return fleetActive[k];});
    if(!active.length){document.getElementById('fleetTable').innerHTML='<p style="color:#78909c;font-size:12px;">Click a company to load.</p>';return;}
    var h='<table style="width:100%;border-collapse:collapse;font-size:11px;"><tr style="color:#4fc3f7;border-bottom:1px solid #1e2a3a;"><th style="text-align:left;padding:4px;">Vessel</th><th>Type</th><th>IMO</th><th>Flag</th></tr>';
    active.forEach(function(co){var vs=fleetData[co]||[];h+='<tr><td colspan="4" style="padding:6px 4px;color:'+fleetColors[co]+';font-weight:600;">'+co+' ('+vs.length+')</td></tr>';vs.forEach(function(v){h+='<tr style="border-bottom:1px solid #0d1117;color:#b0bec5;"><td style="padding:3px 4px;color:#e0e6ed;">'+v.name+'</td><td style="font-size:10px;">'+v.type+'</td><td style="font-family:monospace;font-size:10px;">'+v.imo+'</td><td style="text-align:center;">'+v.flag+'</td></tr>';});});
    h+='</table>';document.getElementById('fleetTable').innerHTML=h;
}

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
// DRILLS
// ═══════════════════════════════════════════════════════
function scheduleDrill() {
    api('POST', '/api/training/drills', {
        date: document.getElementById('drill-date').value || today(),
        type: document.getElementById('drill-type').value,
        title: document.getElementById('drill-title').value,
        scenario: document.getElementById('drill-scenario').value,
        status: 'scheduled'
    }).then(function() { document.getElementById('drill-title').value = ''; document.getElementById('drill-scenario').value = ''; loadDrills(); });
}

function completeDrill(id) {
    api('PATCH', '/api/training/drills/' + id, { status: 'completed' }).then(loadDrills);
}

function loadDrills() {
    api('GET', '/api/training/drills').then(function(drills) {
        var html = '';
        drills.forEach(function(d) {
            var statusBadge = d.status === 'completed' ? '<span class="badge badge-green">Done</span>' : '<span class="badge badge-amber">Scheduled</span>';
            html += '<div class="list-item">';
            html += '<span class="title">' + d.title + '</span>';
            html += '<span class="meta">' + d.date + '</span>';
            html += statusBadge;
            if (d.status !== 'completed') html += ' <button class="btn" style="padding:3px 8px;font-size:10px;" onclick="completeDrill(' + d.id + ')">Complete</button>';
            html += '</div>';
        });
        document.getElementById('drill-list').innerHTML = html || '<p style="color:#78909c;">No drills logged.</p>';
    });
}

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
