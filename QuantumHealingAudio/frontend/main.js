// main.js
let scene, camera, renderer, mandala;

// Target values from WebSocket
let targetBandPowers = {
    delta: 0,
    theta: 0,
    alpha: 0,
    beta: 0,
    gamma: 0
};

// Smoothed values for animation
let smoothedBandPowers = { ...targetBandPowers };

const smoothingFactor = 0.05; // Lower for smoother, higher for more responsive

init();
animate();

function init() {
    scene = new THREE.Scene();
    camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
    camera.position.z = 5;

    renderer = new THREE.WebGLRenderer({ antialias: true });
    renderer.setPixelRatio(window.devicePixelRatio);
    renderer.setSize(window.innerWidth, window.innerHeight);
    document.body.appendChild(renderer.domElement);
    document.body.style.margin = '0';
    document.body.style.overflow = 'hidden';
    document.body.style.background = '#000';


    // Mandala: torus geometry with wireframe
    const geometry = new THREE.TorusGeometry(1, 0.2, 64, 128); // Adjusted segments for performance if needed
    const material = new THREE.MeshBasicMaterial({ color: 0xffffff, wireframe: true });
    mandala = new THREE.Mesh(geometry, material);
    scene.add(mandala);

    window.addEventListener('resize', onWindowResize);

    // WebSocket to Python server
    const socket = new WebSocket('ws://localhost:8765');
    socket.onopen = () => console.log('🔌 WebSocket connected to ws://localhost:8765');
    socket.onerror = error => console.error('🛑 WebSocket error:', error);
    socket.onmessage = event => {
        // console.log('📨 Received data:', event.data); // Can be too verbose
        try {
            const data = JSON.parse(event.data);
            if (data.band_powers) {
                // console.log('📊 Parsed band powers:', data.band_powers); 
                targetBandPowers = data.band_powers;
            } else {
                console.warn('Received data does not contain band_powers:', data);
            }
        } catch (e) {
            console.error('Error parsing WebSocket message:', e, 'Raw data:', event.data);
        }
    };
    socket.onclose = event => {
        console.log('🔴 WebSocket closed. Code:', event.code, 'Reason:', event.reason);
        // Optionally, try to reconnect here
    };
}

function animate() {
    requestAnimationFrame(animate);

    // Smooth band power values
    for (const band in targetBandPowers) {
        smoothedBandPowers[band] += (targetBandPowers[band] - smoothedBandPowers[band]) * smoothingFactor;
    }

    // Normalize band powers (these are heuristic and need tuning based on observed data ranges)
    // Assuming band powers are roughly in 0-100 range, but can vary a lot.
    // For robust normalization, we might need min/max calibration over time.
    const normAlpha = Math.min(Math.max(smoothedBandPowers.alpha / 50, 0), 1); // Example: 50 is a guessed typical max
    const normTheta = Math.min(Math.max(smoothedBandPowers.theta / 50, 0), 1);
    const normBeta = Math.min(Math.max(smoothedBandPowers.beta / 30, 0), 1);
    // const normDelta = Math.min(Math.max(smoothedBandPowers.delta / 100, 0), 1);
    // const normGamma = Math.min(Math.max(smoothedBandPowers.gamma / 20, 0), 1);

    // 1. Scale based on Alpha power
    const targetScale = 0.5 + normAlpha * 1.5; // Scale from 0.5 to 2.0
    mandala.scale.lerp(new THREE.Vector3(targetScale, targetScale, targetScale), smoothingFactor * 2);

    // 2. Color based on Theta/Alpha ratio or dominant band
    // Example: Hue shifts from blue (calm/theta) to green/yellow (focused/alpha)
    let hue = 0.66; // Default to blue
    if (normAlpha > 0.05 || normTheta > 0.05) { // Avoid division by zero or tiny values
         // More alpha = warmer color (e.g. towards green/yellow), more theta = cooler (blue/purple)
        const ratio = normAlpha / (normAlpha + normTheta + 0.01); // Add small epsilon
        hue = 0.66 - (ratio * 0.33); // Range from blue (0.66) to green (0.33)
    }
    mandala.material.color.setHSL(hue, 0.8, 0.6);

    // 3. Rotation speed based on Beta power
    const baseRotation = 0.001;
    const betaEffect = normBeta * 0.02;
    mandala.rotation.x += baseRotation + betaEffect * 0.5;
    mandala.rotation.y += baseRotation + betaEffect * 0.3;
    mandala.rotation.z += baseRotation + betaEffect;

    renderer.render(scene, camera);
}

function onWindowResize() {
    camera.aspect = window.innerWidth / window.innerHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(window.innerWidth, window.innerHeight);
}
