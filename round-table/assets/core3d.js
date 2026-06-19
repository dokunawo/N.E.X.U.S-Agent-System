// core3d.js — N.E.X.U.S core visualization, renders into every .core-canvas
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

    function resize() {
      const size = canvas.parentElement.clientWidth;
      renderer.setSize(size, size, false);
      camera.aspect = 1;
      camera.updateProjectionMatrix();
    }
    resize();
    window.addEventListener('resize', resize);

    const coreGeo = new THREE.IcosahedronGeometry(1.15, 1);
    const coreMat = new THREE.MeshBasicMaterial({ color: 0x00e5ff, wireframe: true, transparent: true, opacity: 0.85 });
    const core = new THREE.Mesh(coreGeo, coreMat);
    scene.add(core);

    const glowGeo = new THREE.IcosahedronGeometry(1.0, 1);
    const glowMat = new THREE.MeshBasicMaterial({ color: 0x00e5ff, transparent: true, opacity: 0.05 });
    scene.add(new THREE.Mesh(glowGeo, glowMat));

    const ring1Geo = new THREE.TorusGeometry(1.9, 0.006, 8, 120);
    const ring1Mat = new THREE.MeshBasicMaterial({ color: 0x00e5ff, transparent: true, opacity: 0.35 });
    const ring1 = new THREE.Mesh(ring1Geo, ring1Mat);
    ring1.rotation.x = Math.PI / 2.2;
    scene.add(ring1);

    const ring2Geo = new THREE.TorusGeometry(2.25, 0.005, 8, 120);
    const ring2Mat = new THREE.MeshBasicMaterial({ color: 0xffb627, transparent: true, opacity: 0.22 });
    const ring2 = new THREE.Mesh(ring2Geo, ring2Mat);
    ring2.rotation.x = Math.PI / 1.6;
    ring2.rotation.y = Math.PI / 5;
    scene.add(ring2);

    const particleCount = 140;
    const positions = new Float32Array(particleCount * 3);
    for (let i = 0; i < particleCount; i++) {
      const r = 2.6 + Math.random() * 0.6;
      const theta = Math.random() * Math.PI * 2;
      const phi = Math.acos((Math.random() * 2) - 1);
      positions[i * 3] = r * Math.sin(phi) * Math.cos(theta);
      positions[i * 3 + 1] = r * Math.sin(phi) * Math.sin(theta);
      positions[i * 3 + 2] = r * Math.cos(phi);
    }
    const particleGeo = new THREE.BufferGeometry();
    particleGeo.setAttribute('position', new THREE.BufferAttribute(positions, 3));
    const particleMat = new THREE.PointsMaterial({ color: 0x6fd9ff, size: 0.018, transparent: true, opacity: 0.5 });
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
      ring1.rotation.z = t * 0.00018;
      ring2.rotation.z = -t * 0.00014;
      particles.rotation.y = t * 0.00004;
      render();
      requestAnimationFrame(animate);
    }
    requestAnimationFrame(animate);
  });
})();
