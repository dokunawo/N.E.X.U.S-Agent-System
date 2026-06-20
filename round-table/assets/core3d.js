// core3d.js — R.A.M.B.O. tactical core visualization, renders into every .core-canvas
// Uses three.js r128 (loaded via cdnjs in page shells before this script).
(function () {
  if (typeof THREE === 'undefined') return;

  const reduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  const canvases = document.querySelectorAll('.core-canvas');

  canvases.forEach((canvas) => {
    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(45, 1, 0.1, 100);
    camera.position.z = 4.4;

    const renderer = new THREE.WebGLRenderer({ canvas: canvas, alpha: true, antialias: true });
    renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
    renderer.setClearColor(0x000000, 0);
    if (THREE.sRGBEncoding) renderer.outputEncoding = THREE.sRGBEncoding;

    function resize() {
      const size = canvas.parentElement.clientWidth;
      renderer.setSize(size, size, false);
      camera.aspect = 1;
      camera.updateProjectionMatrix();
    }
    resize();
    window.addEventListener('resize', resize);

    scene.add(new THREE.AmbientLight(0xf2f2f2, 0.32));
    const light = new THREE.PointLight(0xff2e2e, 1.35, 8);
    light.position.set(1.7, 1.4, 2.2);
    scene.add(light);

    const coreGeo = new THREE.IcosahedronGeometry(1.15, 2);
    const coreMat = new THREE.MeshBasicMaterial({ color: 0xff2e2e, wireframe: true, transparent: true, opacity: 0.84 });
    const core = new THREE.Mesh(coreGeo, coreMat);
    scene.add(core);

    const auraGeo = new THREE.SphereGeometry(1.55, 48, 32);
    const auraMat = new THREE.MeshBasicMaterial({
      color: 0xff2e2e,
      transparent: true,
      opacity: 0.055,
      blending: THREE.AdditiveBlending,
      depthWrite: false
    });
    const aura = new THREE.Mesh(auraGeo, auraMat);
    scene.add(aura);

    const glowGeo = new THREE.IcosahedronGeometry(1.04, 2);
    const glowMat = new THREE.MeshBasicMaterial({
      color: 0xff7a00,
      transparent: true,
      opacity: 0.075,
      blending: THREE.AdditiveBlending,
      depthWrite: false
    });
    const glow = new THREE.Mesh(glowGeo, glowMat);
    scene.add(glow);

    const ring1Geo = new THREE.TorusGeometry(1.9, 0.006, 8, 120);
    const ring1Mat = new THREE.MeshBasicMaterial({ color: 0xff2e2e, transparent: true, opacity: 0.38 });
    const ring1 = new THREE.Mesh(ring1Geo, ring1Mat);
    ring1.rotation.x = Math.PI / 2.2;
    scene.add(ring1);

    const ring2Geo = new THREE.TorusGeometry(2.25, 0.005, 8, 120);
    const ring2Mat = new THREE.MeshBasicMaterial({ color: 0xff7a00, transparent: true, opacity: 0.26 });
    const ring2 = new THREE.Mesh(ring2Geo, ring2Mat);
    ring2.rotation.x = Math.PI / 1.6;
    ring2.rotation.y = Math.PI / 5;
    scene.add(ring2);

    const filamentGeo = new THREE.BufferGeometry();
    const filamentCount = 46;
    const filamentPositions = new Float32Array(filamentCount * 2 * 3);
    for (let i = 0; i < filamentCount; i++) {
      const base = i * 6;
      const theta = Math.random() * Math.PI * 2;
      const phi = Math.acos((Math.random() * 2) - 1);
      const r1 = 1.55 + Math.random() * 0.75;
      const r2 = r1 + 0.35 + Math.random() * 0.65;
      filamentPositions[base] = r1 * Math.sin(phi) * Math.cos(theta);
      filamentPositions[base + 1] = r1 * Math.sin(phi) * Math.sin(theta);
      filamentPositions[base + 2] = r1 * Math.cos(phi);
      filamentPositions[base + 3] = r2 * Math.sin(phi + 0.16) * Math.cos(theta + 0.18);
      filamentPositions[base + 4] = r2 * Math.sin(phi + 0.16) * Math.sin(theta + 0.18);
      filamentPositions[base + 5] = r2 * Math.cos(phi + 0.16);
    }
    filamentGeo.setAttribute('position', new THREE.BufferAttribute(filamentPositions, 3));
    const filamentMat = new THREE.LineBasicMaterial({
      color: 0xffa14d,
      transparent: true,
      opacity: 0.18,
      blending: THREE.AdditiveBlending,
      depthWrite: false
    });
    const filaments = new THREE.LineSegments(filamentGeo, filamentMat);
    scene.add(filaments);

    const particleCount = 260;
    const positions = new Float32Array(particleCount * 3);
    for (let i = 0; i < particleCount; i++) {
      const r = 1.65 + Math.random() * 1.45;
      const theta = Math.random() * Math.PI * 2;
      const phi = Math.acos((Math.random() * 2) - 1);
      positions[i * 3] = r * Math.sin(phi) * Math.cos(theta);
      positions[i * 3 + 1] = r * Math.sin(phi) * Math.sin(theta);
      positions[i * 3 + 2] = r * Math.cos(phi);
    }
    const particleGeo = new THREE.BufferGeometry();
    particleGeo.setAttribute('position', new THREE.BufferAttribute(positions, 3));
    const particleMat = new THREE.PointsMaterial({
      color: 0xf2f2f2,
      size: 0.026,
      transparent: true,
      opacity: 0.72,
      blending: THREE.AdditiveBlending,
      depthWrite: false
    });
    const particles = new THREE.Points(particleGeo, particleMat);
    scene.add(particles);

    function render() {
      renderer.render(scene, camera);
    }

    if (reduced) {
      render();
      return;
    }

    function animate(t) {
      core.rotation.y = t * 0.00012;
      core.rotation.x = t * 0.00006;
      aura.rotation.y = -t * 0.000035;
      glow.rotation.y = t * 0.00009;
      ring1.rotation.z = t * 0.00018;
      ring2.rotation.z = -t * 0.00014;
      particles.rotation.y = t * 0.00004;
      filaments.rotation.y = -t * 0.00003;
      filaments.rotation.x = Math.sin(t * 0.00025) * 0.08;
      render();
      requestAnimationFrame(animate);
    }
    requestAnimationFrame(animate);
  });
})();
