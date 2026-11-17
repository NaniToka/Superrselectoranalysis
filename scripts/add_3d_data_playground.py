import re
import sys

def add_3d_playground():
    with open('index.html', 'r', encoding='utf-8') as f:
        html = f.read()

    # 1. Add Three.js CDN in <head>
    three_scripts = """  <!-- THREE.JS & ORBITCONTROLS 3D DATA PLAYGROUND ENGINE -->
  <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
  <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>
</head>"""

    if 'three.min.js' not in html:
        html = html.replace('</head>', three_scripts)
        print("Added Three.js CDN scripts to <head>")

    # 2. Add 3D Playground Styles in <style>
    playground_css = """
/* =========================================================================
   3D DATA PLAYGROUND & CYBER-STADIUM SYSTEM
   ========================================================================= */
.btn-p3d-filter {
  background: rgba(4, 17, 38, 0.85);
  backdrop-filter: blur(8px);
  border: 1px solid rgba(255, 255, 255, 0.14);
  color: #CBD5E1;
  font-family: var(--font-sans);
  font-size: 11px;
  font-weight: 700;
  padding: 5px 12px;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.15s ease;
}
.btn-p3d-filter:hover {
  background: rgba(255, 255, 255, 0.18);
  color: #FFFFFF;
}
.btn-p3d-filter.active {
  background: var(--rr-pink);
  border-color: var(--rr-pink);
  color: #FFFFFF;
  box-shadow: 0 2px 10px rgba(229, 0, 125, 0.45);
}

.btn-p3d-action {
  background: rgba(4, 17, 38, 0.88);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.18);
  color: #F8FAFC;
  font-family: var(--font-sans);
  font-size: 11px;
  font-weight: 700;
  padding: 8px 14px;
  border-radius: 6px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 6px;
  transition: all 0.15s ease;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.35);
}
.btn-p3d-action:hover {
  background: rgba(255, 255, 255, 0.2);
  border-color: rgba(255, 255, 255, 0.35);
  color: #FFFFFF;
}

.btn-p3d-focus {
  background: rgba(4, 17, 38, 0.88);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.16);
  font-family: var(--font-mono);
  font-size: 10.5px;
  font-weight: 800;
  padding: 7px 11px;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.15s ease;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.35);
}
.btn-p3d-focus:hover {
  transform: translateY(-1px);
  border-color: #FFFFFF;
}
"""

    if '.btn-p3d-filter' not in html:
        html = html.replace('</style>', playground_css + '\n</style>')
        print("Added 3D Playground CSS styles")

    # 3. Add Header Button for 3D Playground
    header_target = """        <div class="toggle-group" id="toggle-container">
          <button id="btn-toggle-adj" class="toggle-btn active" onclick="setView('adjusted')">Opposition-Adjusted</button>
          <button id="btn-toggle-orig" class="toggle-btn" onclick="setView('original')">Original Model</button>
        </div>"""

    header_replacement = """        <div class="toggle-group" id="toggle-container">
          <button id="btn-toggle-adj" class="toggle-btn active" onclick="setView('adjusted')">Opposition-Adjusted</button>
          <button id="btn-toggle-orig" class="toggle-btn" onclick="setView('original')">Original Model</button>
        </div>

        <button onclick="switchTab('tab-3d-playground')" class="btn-header-action" title="Open 3D Data Universe Playground" style="background: linear-gradient(135deg, rgba(229,0,125,0.3) 0%, rgba(56,189,248,0.3) 100%); border-color: #38BDF8; box-shadow: 0 0 12px rgba(56,189,248,0.25);">
          <span>🌐 3D Playground</span>
        </button>"""

    if 'switchTab(\'tab-3d-playground\')' not in html and header_target in html:
        html = html.replace(header_target, header_replacement)
        print("Added 3D Playground button to broadcast header")

    # 4. Add Nav Rail Button
    nav_rail_target = """      <div class="nav-section-label">Core Evaluation</div>
      <button onclick="switchTab('tab-summary')" id="nav-tab-summary" class="nav-btn active">"""

    nav_rail_replacement = """      <div class="nav-section-label" style="color: #38BDF8;">3D Data Playground</div>
      <button onclick="switchTab('tab-3d-playground')" id="nav-tab-3d-playground" class="nav-btn" style="border: 1px solid rgba(56, 189, 248, 0.3); background: rgba(56, 189, 248, 0.08); margin-bottom: 6px;">
        <span class="nav-icon">🌐</span>
        <span style="display: flex; align-items: center; justify-content: space-between; width: 100%;">
          <span>3D Data Universe</span>
          <span style="background: linear-gradient(135deg, var(--rr-pink) 0%, #38BDF8 100%); color: #FFFFFF; font-size: 8px; font-weight: 900; padding: 1px 5px; border-radius: 4px;">3D LIVE</span>
        </span>
      </button>

      <div class="nav-section-label">Core Evaluation</div>
      <button onclick="switchTab('tab-summary')" id="nav-tab-summary" class="nav-btn active">"""

    if 'id="nav-tab-3d-playground"' not in html and nav_rail_target in html:
        html = html.replace(nav_rail_target, nav_rail_replacement)
        print("Added 3D Playground to left navigation rail")

    # 5. Add Launch Button in tab-summary hero card
    hero_btn_target = """            <button class="btn-hero-primary" onclick="switchTab('tab-leaderboards')">
              🏆 View Verified Top 10 Leaderboards
            </button>"""

    hero_btn_replacement = """            <button class="btn-hero-primary" onclick="switchTab('tab-3d-playground')" style="background: linear-gradient(135deg, var(--rr-pink) 0%, #38BDF8 100%); box-shadow: 0 4px 16px rgba(56, 189, 248, 0.4);">
              🌐 Launch 3D Data Universe
            </button>
            <button class="btn-hero-secondary" onclick="switchTab('tab-leaderboards')">
              🏆 View Verified Top 10 Leaderboards
            </button>"""

    if 'Launch 3D Data Universe' not in html and hero_btn_target in html:
        html = html.replace(hero_btn_target, hero_btn_replacement)
        print("Added 3D Playground launch button to tab-summary hero card")

    # 6. Add Section tab-3d-playground
    section_target = """      <!-- TAB 2: TOP 10 LEADERBOARDS -->
      <section id="tab-leaderboards" class="tab-pane">"""

    playground_section_html = """      <!-- TAB: 3D DATA PLAYGROUND -->
      <section id="tab-3d-playground" class="tab-pane">
        <div class="card" style="padding: 0; overflow: hidden; border: 1px solid rgba(56, 189, 248, 0.35); box-shadow: 0 12px 40px rgba(0,0,0,0.5);">
          
          <!-- 3D PLAYGROUND HEADER -->
          <div style="background: linear-gradient(135deg, #07152B 0%, #0A1E3D 100%); padding: 18px 24px; border-bottom: 1px solid rgba(255,255,255,0.08); display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 14px;">
            <div>
              <div style="display: flex; align-items: center; gap: 8px;">
                <span style="font-size: 20px;">🌐</span>
                <span style="font-size: 18px; font-weight: 800; color: #FFFFFF; letter-spacing: -0.01em;">3D Pressure Dynamics Universe</span>
                <span style="background: linear-gradient(135deg, var(--rr-pink) 0%, #38BDF8 100%); color: #FFFFFF; font-size: 10px; font-weight: 800; font-family: var(--font-mono); padding: 2px 8px; border-radius: 9999px;">WEBGL 3D HARDWARE ACCELERATED</span>
              </div>
              <div style="font-size: 12px; color: #94A3B8; margin-top: 4px;">
                Interactive 3D state-space manifold plotting all 202 qualified players (100 Batters &bull; 102 Bowlers). Rotate in 360&deg;, zoom, morph dimensions, and play live physics animations.
              </div>
            </div>

            <!-- PRESET DIMENSION SELECTORS -->
            <div style="display: flex; gap: 8px; flex-wrap: wrap;">
              <button id="p3d-btn-std" class="toggle-btn active" onclick="set3DDimension('std')">Standard 3D Clutch Space</button>
              <button id="p3d-btn-wp" class="toggle-btn" onclick="set3DDimension('wp')">Win Prob Manifold</button>
              <button id="p3d-btn-stability" class="toggle-btn" onclick="set3DDimension('stability')">Bootstrap Stability Cube</button>
            </div>
          </div>

          <!-- 3D INTERACTIVE CANVAS WRAPPER -->
          <div style="position: relative; width: 100%; height: 640px; background: radial-gradient(circle at 50% 50%, #08162B 0%, #020713 100%); overflow: hidden;">
            
            <!-- 3D WEBGL CONTAINER -->
            <div id="p3d-viewport" style="width: 100%; height: 100%; cursor: grab;"></div>

            <!-- 3D TOP-LEFT HUD OVERLAY -->
            <div style="position: absolute; top: 16px; left: 16px; pointer-events: none; z-index: 10; display: flex; flex-direction: column; gap: 8px;">
              <div style="background: rgba(4, 17, 38, 0.88); backdrop-filter: blur(12px); border: 1px solid rgba(255,255,255,0.12); border-radius: 8px; padding: 10px 14px; pointer-events: auto;">
                <div style="font-size: 9px; font-weight: 800; text-transform: uppercase; color: #38BDF8; letter-spacing: 0.08em; font-family: var(--font-mono);">Current 3D Axes</div>
                <div id="p3d-axes-legend" style="font-size: 11.5px; font-weight: 700; color: #FFFFFF; margin-top: 2px;">
                  X: HP Deliveries &bull; Y: Net/100 (Height) &bull; Z: &Delta; vs Baseline
                </div>
                <div style="display: flex; align-items: center; gap: 12px; margin-top: 6px; font-size: 10.5px;">
                  <span style="display: flex; align-items: center; gap: 4px; color: #FF85C0;"><span style="width: 8px; height: 8px; background: var(--rr-pink); border-radius: 50%;"></span> Batters (100)</span>
                  <span style="display: flex; align-items: center; gap: 4px; color: #7DD3FC;"><span style="width: 8px; height: 8px; background: #38BDF8; border-radius: 50%;"></span> Bowlers (102)</span>
                  <span style="display: flex; align-items: center; gap: 4px; color: #FDE68A;"><span style="width: 8px; height: 8px; background: #F59E0B; border-radius: 50%;"></span> #1 Rank Core</span>
                </div>
              </div>
            </div>

            <!-- 3D TOP-RIGHT FILTER PILLS -->
            <div style="position: absolute; top: 16px; right: 16px; z-index: 10; display: flex; gap: 6px; flex-wrap: wrap;">
              <button onclick="filter3DNodes('all')" class="btn-p3d-filter active" id="p3d-f-all">All 202</button>
              <button onclick="filter3DNodes('bat')" class="btn-p3d-filter" id="p3d-f-bat">🏏 Batters</button>
              <button onclick="filter3DNodes('bowl')" class="btn-p3d-filter" id="p3d-f-bowl">🎯 Bowlers</button>
              <button onclick="filter3DNodes('top10')" class="btn-p3d-filter" id="p3d-f-top10">🏆 Top 10 Only</button>
              <button onclick="filter3DNodes('rr')" class="btn-p3d-filter" id="p3d-f-rr">🏰 RR Assets (15)</button>
              <button onclick="filter3DNodes('clutch')" class="btn-p3d-filter" id="p3d-f-clutch">&Delta; &gt; 0 Surging</button>
            </div>

            <!-- 3D FLOATING HOLOGRAPHIC PLAYER CARD -->
            <div id="p3d-player-card" style="position: absolute; top: 120px; left: 16px; width: 280px; background: rgba(9, 26, 51, 0.94); backdrop-filter: blur(16px); border: 1px solid rgba(56, 189, 248, 0.45); border-radius: 10px; padding: 14px 16px; box-shadow: 0 10px 30px rgba(0,0,0,0.6); display: none; z-index: 20; transition: all 0.2s ease;">
              <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 8px;">
                <div>
                  <div id="p3d-card-rank" style="font-family: var(--font-mono); font-size: 10px; font-weight: 800; color: #F59E0B; text-transform: uppercase;">RANK #1 BATTER</div>
                  <div id="p3d-card-name" style="font-size: 15px; font-weight: 800; color: #FFFFFF; letter-spacing: -0.01em;">Suryakumar Yadav</div>
                  <div id="p3d-card-team" style="font-size: 11px; color: #94A3B8;">Mumbai Indians &bull; 🇮🇳 India</div>
                </div>
                <button onclick="document.getElementById('p3d-player-card').style.display='none'" style="background: transparent; border: none; color: #94A3B8; font-size: 16px; cursor: pointer;">&times;</button>
              </div>
              <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 8px; margin: 10px 0; padding: 8px; background: rgba(255,255,255,0.04); border-radius: 6px; font-family: var(--font-mono); font-size: 11px;">
                <div><span style="color: #94A3B8;">HP Balls:</span> <strong id="p3d-card-balls" style="color: #FFFFFF;">442</strong></div>
                <div><span style="color: #94A3B8;">Net/100:</span> <strong id="p3d-card-net" style="color: #34D399;">+17.2</strong></div>
                <div><span style="color: #94A3B8;">&Delta; Baseline:</span> <strong id="p3d-card-delta" style="color: #34D399;">+13.1</strong></div>
                <div><span style="color: #94A3B8;">Score:</span> <strong id="p3d-card-score" style="color: #FFB3D9;">0.672</strong></div>
              </div>
              <button id="p3d-card-view-btn" onclick="openPlayerFrom3D()" style="width: 100%; background: var(--rr-pink); border: none; color: #FFFFFF; font-weight: 700; font-size: 11px; padding: 7px; border-radius: 6px; cursor: pointer;">
                Open Full Tactical Match Log &rarr;
              </button>
            </div>

            <!-- 3D BOTTOM CONTROLS & ANIMATION TOOLBAR -->
            <div style="position: absolute; bottom: 16px; left: 16px; right: 16px; z-index: 10; display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 10px; pointer-events: none;">
              
              <!-- LEFT: ACTION BUTTONS -->
              <div style="display: flex; gap: 8px; flex-wrap: wrap; pointer-events: auto;">
                <button id="p3d-btn-animate" onclick="toggle3DPressureAnimation()" class="btn-p3d-action" style="background: linear-gradient(135deg, var(--rr-pink) 0%, #C4006A 100%); border-color: var(--rr-pink); color: #FFFFFF;">
                  <span>▶ Play Pressure Shift Vector Animation</span>
                </button>
                <button id="p3d-btn-orbit" onclick="toggle3DAutoOrbit()" class="btn-p3d-action">
                  <span>🔄 360&deg; Auto-Orbit: <strong id="p3d-orbit-status">ON</strong></span>
                </button>
                <button onclick="reset3DCamera()" class="btn-p3d-action">
                  <span>🎯 Reset Perspective</span>
                </button>
              </div>

              <!-- RIGHT: QUICK FOCUS TARGETS -->
              <div style="display: flex; gap: 6px; flex-wrap: wrap; pointer-events: auto;">
                <button onclick="focus3DPlayer('Suryakumar Yadav')" class="btn-p3d-focus" style="border-color: #F59E0B; color: #FDE68A;">
                  👑 Surya (#1)
                </button>
                <button onclick="focus3DPlayer('Sunil Narine')" class="btn-p3d-focus" style="border-color: #F59E0B; color: #FDE68A;">
                  👑 Narine (#1)
                </button>
                <button onclick="focus3DPlayer('Vaibhav Sooryavanshi')" class="btn-p3d-focus" style="border-color: var(--rr-pink); color: #FFB3D9;">
                  🏰 Vaibhav (RR #8)
                </button>
                <button onclick="focus3DPlayer('Jasprit Bumrah')" class="btn-p3d-focus" style="border-color: #38BDF8; color: #7DD3FC;">
                  🎳 Bumrah (Anomaly)
                </button>
              </div>

            </div>

          </div>

          <!-- 3D TELEMETRY & METHODOLOGY STRIP -->
          <div style="padding: 16px 20px; background: #06152B; border-top: 1px solid rgba(255,255,255,0.08); display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 14px; font-size: 11px;">
            <div style="display: flex; gap: 10px; align-items: center;">
              <span style="font-size: 20px;">🎲</span>
              <div>
                <div style="font-weight: 800; color: #FFFFFF; font-family: var(--font-mono);">3D STATE-SPACE FORMULATION</div>
                <div style="color: #94A3B8;">Continuous win-probability gradient mapped to 3-axis Euclidean spatial coordinates.</div>
              </div>
            </div>
            <div style="display: flex; gap: 10px; align-items: center;">
              <span style="font-size: 20px;">⚡</span>
              <div>
                <div style="font-weight: 800; color: #FFFFFF; font-family: var(--font-mono);">LEVERAGE SURFACE LI &ge; 1.32</div>
                <div style="color: #94A3B8;">49,276 deliveries in top quartile with 3.73 percentage points win-probability swing per ball.</div>
              </div>
            </div>
            <div style="display: flex; gap: 10px; align-items: center;">
              <span style="font-size: 20px;">🛡️</span>
              <div>
                <div style="font-weight: 800; color: #FFFFFF; font-family: var(--font-mono);">EMPIRICAL BAYES SHRINKAGE</div>
                <div style="color: #94A3B8;">Small sample volumes shrunk toward population priors to prevent spurious leaderboard spikes.</div>
              </div>
            </div>
            <div style="display: flex; gap: 10px; align-items: center;">
              <span style="font-size: 20px;">🏰</span>
              <div>
                <div style="font-weight: 800; color: #FFFFFF; font-family: var(--font-mono);">RAJASTHAN ROYALS DUGOUT</div>
                <div style="color: #94A3B8;">15 RR contracted players isolated and audited across Powerplay, Middle, and Death phases.</div>
              </div>
            </div>
          </div>

        </div>
      </section>

      <!-- TAB 2: TOP 10 LEADERBOARDS -->
      <section id="tab-leaderboards" class="tab-pane">"""

    if 'id="tab-3d-playground"' not in html and section_target in html:
        html = html.replace(section_target, playground_section_html)
        print("Added tab-3d-playground section to index.html")

    # 7. Add switchTab logic
    tab_hook_target = "if (tabId === 'tab-scatter') renderPressureScatter();"
    tab_hook_replacement = "if (tabId === 'tab-3d-playground') init3DPlayground();\n  else if (tabId === 'tab-scatter') renderPressureScatter();"

    if 'init3DPlayground()' not in html and tab_hook_target in html:
        html = html.replace(tab_hook_target, tab_hook_replacement)
        print("Added init3DPlayground() to switchTab()")

    # 8. Add Complete 3D Engine Code in <script>
    engine_js = """
// =========================================================================
// 3D DATA PLAYGROUND ENGINE (THREE.JS + PERSPECTIVE HARDWARE PROJECTION)
// =========================================================================
const P3D = {
  initialized: false,
  dimension: 'std',
  filter: 'all',
  autoOrbit: true,
  isAnimatingShift: false,
  shiftT: 0,
  hoveredMesh: null,
  selectedPlayerName: null,
  scene: null,
  camera: null,
  renderer: null,
  controls: null,
  playerMeshes: [],
  vectorLines: [],
  targetPositions: new Map(),
  basePositions: new Map(),
  clutchPositions: new Map(),
  animId: null
};

function init3DPlayground() {
  const container = document.getElementById('p3d-viewport');
  if (!container) return;
  if (P3D.initialized) {
    if (P3D.renderer && P3D.camera) {
      P3D.renderer.setSize(container.clientWidth, container.clientHeight);
      P3D.camera.aspect = container.clientWidth / container.clientHeight;
      P3D.camera.updateProjectionMatrix();
    }
    return;
  }

  // Check if THREE is available
  if (typeof THREE === 'undefined') {
    initFallback3DCanvas(container);
    return;
  }

  try {
    const width = container.clientWidth || 900;
    const height = container.clientHeight || 640;

    // 1. Scene, Camera, Renderer
    P3D.scene = new THREE.Scene();
    P3D.scene.background = new THREE.Color(0x040D1A);
    P3D.scene.fog = new THREE.FogExp2(0x040D1A, 0.0018);

    P3D.camera = new THREE.PerspectiveCamera(50, width / height, 1, 2000);
    P3D.camera.position.set(0, 180, 420);

    P3D.renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
    P3D.renderer.setSize(width, height);
    P3D.renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    container.innerHTML = '';
    container.appendChild(P3D.renderer.domElement);

    // 2. Controls
    if (typeof THREE.OrbitControls !== 'undefined') {
      P3D.controls = new THREE.OrbitControls(P3D.camera, P3D.renderer.domElement);
      P3D.controls.enableDamping = true;
      P3D.controls.dampingFactor = 0.05;
      P3D.controls.maxDistance = 800;
      P3D.controls.minDistance = 60;
      P3D.controls.autoRotate = P3D.autoOrbit;
      P3D.controls.autoRotateSpeed = 0.8;
      P3D.controls.target.set(0, 20, 0);
    }

    // 3. Lighting
    const ambientLight = new THREE.AmbientLight(0xFFFFFF, 0.7);
    P3D.scene.add(ambientLight);

    const dirLight1 = new THREE.DirectionalLight(0xE5007D, 1.2);
    dirLight1.position.set(200, 300, 200);
    P3D.scene.add(dirLight1);

    const dirLight2 = new THREE.DirectionalLight(0x38BDF8, 1.0);
    dirLight2.position.set(-200, 200, -200);
    P3D.scene.add(dirLight2);

    // 4. Cyber Cricket Stadium Grid Floor
    const gridHelper = new THREE.GridHelper(600, 30, 0x38BDF8, 0x132E58);
    gridHelper.position.y = -60;
    P3D.scene.add(gridHelper);

    // Pitch Strip Mesh (22 yards proportional)
    const pitchGeo = new THREE.PlaneGeometry(50, 180);
    const pitchMat = new THREE.MeshBasicMaterial({ 
      color: 0x0A2244, 
      side: THREE.DoubleSide, 
      wireframe: false 
    });
    const pitch = new THREE.Mesh(pitchGeo, pitchMat);
    pitch.rotation.x = -Math.PI / 2;
    pitch.position.y = -59.5;
    P3D.scene.add(pitch);

    // Pitch Crease Lines
    const creaseMat = new THREE.LineBasicMaterial({ color: 0x38BDF8 });
    const c1Geo = new THREE.BufferGeometry().setFromPoints([
      new THREE.Vector3(-25, -59, 70),
      new THREE.Vector3(25, -59, 70)
    ]);
    const c2Geo = new THREE.BufferGeometry().setFromPoints([
      new THREE.Vector3(-25, -59, -70),
      new THREE.Vector3(25, -59, -70)
    ]);
    P3D.scene.add(new THREE.Line(c1Geo, creaseMat));
    P3D.scene.add(new THREE.Line(c2Geo, creaseMat));

    // Outer Stadium Boundary Ring
    const ringGeo = new THREE.RingGeometry(250, 252, 64);
    const ringMat = new THREE.MeshBasicMaterial({ color: 0xE5007D, side: THREE.DoubleSide });
    const boundRing = new THREE.Mesh(ringGeo, ringMat);
    boundRing.rotation.x = -Math.PI / 2;
    boundRing.position.y = -59.8;
    P3D.scene.add(boundRing);

    // 5. Populate 202 Player Nodes
    build3DPlayerNodes();

    // 6. Setup Raycaster
    setup3DRaycaster(container);

    // 7. Resize Listener
    window.addEventListener('resize', onP3DResize);

    // 8. Animation Loop
    P3D.initialized = true;
    animate3D();
  } catch (err) {
    console.error('Three.js init error, falling back to Canvas 3D:', err);
    initFallback3DCanvas(container);
  }
}

function compute3DCoords(p, dim) {
  let x = 0, y = 0, z = 0;
  const n_hp = p.n_hp || 200;
  const net_hp = p.net_hp || 0;
  const net_np = p.net_np || 0;
  const delta = p.delta || 0;
  const wpa = (p.wpa_hp || 0) * 100;
  const score = p.adjusted_score || 0;
  const boot = (p.boot_top10_adj || 0) * 100;
  const cons = p.cons || 0.5;

  if (dim === 'std') {
    x = (n_hp - 350) * 0.55;
    y = net_hp * 2.8;
    z = delta * 4.2;
  } else if (dim === 'wp') {
    x = net_hp * 3.2;
    y = wpa * 18.0;
    z = score * 220.0 - 50.0;
  } else if (dim === 'stability') {
    x = (n_hp - 350) * 0.55;
    y = boot * 1.8 - 40.0;
    z = (cons - 0.5) * 450.0;
  }

  // Base coordinates for shift animation
  const baseY = net_np * 2.8;
  return { x, y, z, baseX: x, baseY, baseZ: 0 };
}

function build3DPlayerNodes() {
  if (!APP_DATA.adjusted_all_players) return;
  const players = APP_DATA.adjusted_all_players;

  // Clear existing meshes
  P3D.playerMeshes.forEach(m => P3D.scene.remove(m));
  P3D.playerMeshes = [];
  P3D.targetPositions.clear();
  P3D.basePositions.clear();
  P3D.clutchPositions.clear();

  const sphereGeo = new THREE.SphereGeometry(1, 16, 16);

  players.forEach(p => {
    const isBat = p.role === 'bat';
    const isTop1 = p.adjusted_rank === 1;
    const isTop3 = p.adjusted_rank <= 3;
    const isTop10 = p.adjusted_rank <= 10;
    const isRR = (p.ipl2026 || '').includes('Rajasthan');

    let radius = 3.6;
    let colorHex = isBat ? 0xE5007D : 0x38BDF8;

    if (isTop1) {
      radius = 8.5;
      colorHex = 0xF59E0B; // Royal Gold
    } else if (isTop3) {
      radius = 6.2;
      colorHex = isBat ? 0xFF2D9B : 0x00F0FF;
    } else if (isTop10) {
      radius = 5.0;
    }

    const mat = new THREE.MeshStandardMaterial({
      color: colorHex,
      emissive: colorHex,
      emissiveIntensity: isTop1 ? 0.8 : (isTop10 ? 0.5 : 0.25),
      roughness: 0.2,
      metalness: 0.8
    });

    const mesh = new THREE.Mesh(sphereGeo, mat);
    mesh.scale.set(radius, radius, radius);
    mesh.userData = { player: p, origRadius: radius, colorHex: colorHex };

    // Calculate position
    const coords = compute3DCoords(p, P3D.dimension);
    mesh.position.set(coords.x, coords.y, coords.z);

    P3D.targetPositions.set(p.name, new THREE.Vector3(coords.x, coords.y, coords.z));
    P3D.basePositions.set(p.name, new THREE.Vector3(coords.baseX, coords.baseY, coords.baseZ));
    P3D.clutchPositions.set(p.name, new THREE.Vector3(coords.x, coords.y, coords.z));

    // Add glowing orbital halo for Top 1 and RR assets
    if (isTop1 || (isRR && isTop10)) {
      const haloGeo = new THREE.RingGeometry(radius * 1.3, radius * 1.5, 32);
      const haloMat = new THREE.MeshBasicMaterial({ 
        color: isTop1 ? 0xF59E0B : 0x34D399, 
        side: THREE.DoubleSide 
      });
      const halo = new THREE.Mesh(haloGeo, haloMat);
      halo.rotation.x = Math.PI / 2;
      mesh.add(halo);
    }

    P3D.scene.add(mesh);
    P3D.playerMeshes.push(mesh);
  });
}

function set3DDimension(dim) {
  P3D.dimension = dim;
  ['std', 'wp', 'stability'].forEach(k => {
    const el = document.getElementById('p3d-btn-' + k);
    if (el) el.classList.toggle('active', k === dim);
  });

  const legend = document.getElementById('p3d-axes-legend');
  if (legend) {
    if (dim === 'std') legend.innerHTML = 'X: HP Deliveries &bull; Y: Net/100 (Height) &bull; Z: &Delta; vs Baseline';
    else if (dim === 'wp') legend.innerHTML = 'X: Net/100 &bull; Y: Win Prob Added WPA (Height) &bull; Z: EB Composite Score';
    else if (dim === 'stability') legend.innerHTML = 'X: HP Deliveries &bull; Y: Top 10% Bootstrap (Height) &bull; Z: Consistency';
  }

  // Update target positions for smooth interpolation
  P3D.playerMeshes.forEach(mesh => {
    const p = mesh.userData.player;
    const coords = compute3DCoords(p, dim);
    P3D.targetPositions.set(p.name, new THREE.Vector3(coords.x, coords.y, coords.z));
    P3D.clutchPositions.set(p.name, new THREE.Vector3(coords.x, coords.y, coords.z));
    P3D.basePositions.set(p.name, new THREE.Vector3(coords.baseX, coords.baseY, coords.baseZ));
  });
}

function filter3DNodes(f) {
  P3D.filter = f;
  ['all', 'bat', 'bowl', 'top10', 'rr', 'clutch'].forEach(k => {
    const el = document.getElementById('p3d-f-' + k);
    if (el) el.classList.toggle('active', k === f);
  });

  P3D.playerMeshes.forEach(mesh => {
    const p = mesh.userData.player;
    let visible = true;
    if (f === 'bat') visible = p.role === 'bat';
    else if (f === 'bowl') visible = p.role === 'bowl';
    else if (f === 'top10') visible = p.adjusted_rank <= 10;
    else if (f === 'rr') visible = (p.ipl2026 || '').includes('Rajasthan');
    else if (f === 'clutch') visible = (p.delta || 0) > 0;

    mesh.visible = visible;
  });
}

function toggle3DAutoOrbit() {
  P3D.autoOrbit = !P3D.autoOrbit;
  if (P3D.controls) P3D.controls.autoRotate = P3D.autoOrbit;
  const status = document.getElementById('p3d-orbit-status');
  if (status) status.innerText = P3D.autoOrbit ? 'ON' : 'OFF';
}

function reset3DCamera() {
  if (P3D.controls) {
    P3D.controls.target.set(0, 20, 0);
    P3D.camera.position.set(0, 180, 420);
    P3D.controls.update();
  }
}

function focus3DPlayer(name) {
  const mesh = P3D.playerMeshes.find(m => m.userData.player.name === name);
  if (!mesh) return;

  mesh.visible = true;
  show3DPlayerCard(mesh.userData.player);

  if (P3D.controls) {
    const pPos = mesh.position;
    P3D.controls.target.set(pPos.x, pPos.y, pPos.z);
    P3D.camera.position.set(pPos.x + 30, pPos.y + 20, pPos.z + 60);
    P3D.controls.update();
  }
}

function toggle3DPressureAnimation() {
  P3D.isAnimatingShift = !P3D.isAnimatingShift;
  P3D.shiftT = 0;
  const btn = document.getElementById('p3d-btn-animate');
  if (btn) {
    btn.innerHTML = P3D.isAnimatingShift 
      ? '<span>⏹ Reset to Clutch State</span>' 
      : '<span>▶ Play Pressure Shift Vector Animation</span>';
  }

  if (!P3D.isAnimatingShift) {
    // Snap back to clutch target
    P3D.playerMeshes.forEach(m => {
      const target = P3D.clutchPositions.get(m.userData.player.name);
      if (target) m.position.copy(target);
    });
  }
}

function show3DPlayerCard(p) {
  const card = document.getElementById('p3d-player-card');
  if (!card) return;

  P3D.selectedPlayerName = p.name;
  const rankEl = document.getElementById('p3d-card-rank');
  const nameEl = document.getElementById('p3d-card-name');
  const teamEl = document.getElementById('p3d-card-team');
  const ballsEl = document.getElementById('p3d-card-balls');
  const netEl = document.getElementById('p3d-card-net');
  const deltaEl = document.getElementById('p3d-card-delta');
  const scoreEl = document.getElementById('p3d-card-score');

  const roleText = p.role === 'bat' ? 'BATTER' : 'BOWLER';
  if (rankEl) rankEl.innerText = `ADJUSTED RANK #${p.adjusted_rank} ${roleText}`;
  if (nameEl) nameEl.innerText = p.name;
  if (teamEl) teamEl.innerText = `${p.ipl2026 || 'IPL'} • ${p.nationality || ''}`;
  if (ballsEl) ballsEl.innerText = p.n_hp || 0;
  if (netEl) netEl.innerText = (p.net_hp >= 0 ? '+' : '') + (p.net_hp || 0).toFixed(1);
  if (deltaEl) deltaEl.innerText = (p.delta >= 0 ? '+' : '') + (p.delta || 0).toFixed(1);
  if (scoreEl) scoreEl.innerText = (p.adjusted_score || 0).toFixed(3);

  card.style.display = 'block';
}

function openPlayerFrom3D() {
  if (P3D.selectedPlayerName) {
    openPlayerProfile(P3D.selectedPlayerName);
  }
}

function setup3DRaycaster(container) {
  const raycaster = new THREE.Raycaster();
  const mouse = new THREE.Vector2();

  container.addEventListener('mousemove', e => {
    const rect = container.getBoundingClientRect();
    mouse.x = ((e.clientX - rect.left) / container.clientWidth) * 2 - 1;
    mouse.y = -((e.clientY - rect.top) / container.clientHeight) * 2 + 1;

    raycaster.setFromCamera(mouse, P3D.camera);
    const intersects = raycaster.intersectObjects(P3D.playerMeshes.filter(m => m.visible));

    if (intersects.length > 0) {
      const hit = intersects[0].object;
      if (P3D.hoveredMesh !== hit) {
        if (P3D.hoveredMesh) {
          const origR = P3D.hoveredMesh.userData.origRadius;
          P3D.hoveredMesh.scale.set(origR, origR, origR);
        }
        P3D.hoveredMesh = hit;
        const newR = hit.userData.origRadius * 1.4;
        hit.scale.set(newR, newR, newR);
        show3DPlayerCard(hit.userData.player);
      }
    } else {
      if (P3D.hoveredMesh) {
        const origR = P3D.hoveredMesh.userData.origRadius;
        P3D.hoveredMesh.scale.set(origR, origR, origR);
        P3D.hoveredMesh = null;
      }
    }
  });

  container.addEventListener('click', e => {
    const rect = container.getBoundingClientRect();
    mouse.x = ((e.clientX - rect.left) / container.clientWidth) * 2 - 1;
    mouse.y = -((e.clientY - rect.top) / container.clientHeight) * 2 + 1;

    raycaster.setFromCamera(mouse, P3D.camera);
    const intersects = raycaster.intersectObjects(P3D.playerMeshes.filter(m => m.visible));
    if (intersects.length > 0) {
      const p = intersects[0].object.userData.player;
      focus3DPlayer(p.name);
    }
  });
}

function onP3DResize() {
  const container = document.getElementById('p3d-viewport');
  if (!container || !P3D.renderer || !P3D.camera) return;
  P3D.camera.aspect = container.clientWidth / container.clientHeight;
  P3D.camera.updateProjectionMatrix();
  P3D.renderer.setSize(container.clientWidth, container.clientHeight);
}

function animate3D() {
  P3D.animId = requestAnimationFrame(animate3D);

  if (P3D.controls) P3D.controls.update();

  // Smooth position interpolation for dimension morphing
  if (!P3D.isAnimatingShift) {
    P3D.playerMeshes.forEach(mesh => {
      const target = P3D.targetPositions.get(mesh.userData.player.name);
      if (target) {
        mesh.position.lerp(target, 0.08);
      }
    });
  } else {
    // Animate Baseline -> Clutch vector shift
    P3D.shiftT += 0.012;
    const progress = (Math.sin(P3D.shiftT) + 1) / 2; // oscillates 0 -> 1 -> 0
    P3D.playerMeshes.forEach(mesh => {
      const base = P3D.basePositions.get(mesh.userData.player.name);
      const clutch = P3D.clutchPositions.get(mesh.userData.player.name);
      if (base && clutch) {
        mesh.position.lerpVectors(base, clutch, progress);
      }
    });
  }

  if (P3D.renderer && P3D.scene && P3D.camera) {
    P3D.renderer.render(P3D.scene, P3D.camera);
  }
}

// Fallback Canvas 2D/3D Projection Engine (Bulletproof Network/Offline guarantee)
function initFallback3DCanvas(container) {
  container.innerHTML = '<canvas id="fallback-3d-cv" style="width:100%; height:100%;"></canvas>';
  const canvas = document.getElementById('fallback-3d-cv');
  if (!canvas) return;
  const ctx = canvas.getContext('2d');
  canvas.width = container.clientWidth || 900;
  canvas.height = container.clientHeight || 640;

  let rotX = 0.3, rotY = 0.5;
  let isDragging = false, lastMouseX = 0, lastMouseY = 0;

  canvas.addEventListener('mousedown', e => {
    isDragging = true;
    lastMouseX = e.clientX;
    lastMouseY = e.clientY;
  });
  window.addEventListener('mouseup', () => isDragging = false);
  canvas.addEventListener('mousemove', e => {
    if (!isDragging) return;
    const dx = e.clientX - lastMouseX;
    const dy = e.clientY - lastMouseY;
    rotY += dx * 0.008;
    rotX += dy * 0.008;
    lastMouseX = e.clientX;
    lastMouseY = e.clientY;
  });

  const players = APP_DATA.adjusted_all_players || [];

  function renderFallback() {
    ctx.fillStyle = '#040D1A';
    ctx.fillRect(0, 0, canvas.width, canvas.height);

    const cx = canvas.width / 2;
    const cy = canvas.height / 2;
    const fov = 400;

    // Sort players by projected Z for correct painter's algorithm
    const projected = players.map(p => {
      const n_hp = p.n_hp || 200;
      const net_hp = p.net_hp || 0;
      const delta = p.delta || 0;
      const x0 = (n_hp - 350) * 0.6;
      const y0 = -net_hp * 3.5;
      const z0 = delta * 4.5;

      // Rotate Y
      const x1 = x0 * Math.cos(rotY) + z0 * Math.sin(rotY);
      const z1 = -x0 * Math.sin(rotY) + z0 * Math.cos(rotY);
      // Rotate X
      const y2 = y0 * Math.cos(rotX) - z1 * Math.sin(rotX);
      const z2 = y0 * Math.sin(rotX) + z1 * Math.cos(rotX) + 500;

      const scale = fov / Math.max(z2, 10);
      const px = cx + x1 * scale;
      const py = cy + y2 * scale;
      const r = Math.max(p.adjusted_rank === 1 ? 9 : (p.adjusted_rank <= 10 ? 5 : 3), 2) * (scale / 1.2);

      return { p, px, py, z2, r };
    }).sort((a, b) => b.z2 - a.z2);

    projected.forEach(item => {
      ctx.beginPath();
      ctx.arc(item.px, item.py, item.r, 0, Math.PI * 2);
      ctx.fillStyle = item.p.adjusted_rank === 1 ? '#F59E0B' : (item.p.role === 'bat' ? '#E5007D' : '#38BDF8');
      ctx.shadowColor = ctx.fillStyle;
      ctx.shadowBlur = item.p.adjusted_rank <= 10 ? 12 : 4;
      ctx.fill();
    });

    if (P3D.autoOrbit) rotY += 0.005;
    requestAnimationFrame(renderFallback);
  }
  renderFallback();
}
"""

    if 'P3D = {' not in html:
        # Place before window.addEventListener('DOMContentLoaded')
        html = html.replace("window.addEventListener('DOMContentLoaded', () => {", engine_js + "\n\nwindow.addEventListener('DOMContentLoaded', () => {")
        print("Added complete 3D Data Playground engine code to <script>")

    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(html)
    print("3D Data Playground integration complete!")

if __name__ == '__main__':
    add_3d_playground()
