/**
 * आयुCare (AyuCare) - 3D Healthcare Hero Animation
 * Powered by Three.js
 */

(function initThreeHero() {
  const container = document.getElementById("three-hero-container");
  const canvas = document.getElementById("three-hero-canvas");
  const fallback = document.querySelector(".hero-3d-fallback");

  if (!container || !canvas) return;

  // Accessibility: Respect reduced motion
  const prefersReducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  // WebGL Availability Check
  function isWebGLAvailable() {
    try {
      const glCanvas = document.createElement("canvas");
      return !!(window.WebGLRenderingContext && (glCanvas.getContext("webgl") || glCanvas.getContext("experimental-webgl")));
    } catch {
      return false;
    }
  }

  if (!isWebGLAvailable()) {
    if (fallback) fallback.style.display = "flex";
    if (canvas) canvas.style.display = "none";
    return;
  }

  // Three.js Scene Setup
  let scene, camera, renderer;
  let heartGroup, crossGroup, leavesGroup, particlesGroup;
  let mouseX = 0, mouseY = 0;
  let targetX = 0, targetY = 0;
  let windowHalfX = window.innerWidth / 2;
  let windowHalfY = window.innerHeight / 2;
  let clock;

  function init() {
    clock = new THREE.Clock();

    // Scene
    scene = new THREE.Scene();

    // Camera
    const width = container.clientWidth || 500;
    const height = container.clientHeight || 450;
    camera = new THREE.PerspectiveCamera(45, width / height, 0.1, 1000);
    camera.position.set(0, 0, 14);

    // Renderer
    renderer = new THREE.WebGLRenderer({
      canvas: canvas,
      alpha: true,
      antialias: true,
      powerPreference: "high-performance"
    });
    renderer.setSize(width, height);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));

    // Lights
    const ambientLight = new THREE.AmbientLight(0xffffff, 0.85);
    scene.add(ambientLight);

    const dirLight1 = new THREE.DirectionalLight(0x1565C0, 1.2);
    dirLight1.position.set(5, 8, 7);
    scene.add(dirLight1);

    const dirLight2 = new THREE.DirectionalLight(0x66BB6A, 1.0);
    dirLight2.position.set(-5, -6, 5);
    scene.add(dirLight2);

    const pointLight = new THREE.PointLight(0xffffff, 0.9, 50);
    pointLight.position.set(0, 2, 8);
    scene.add(pointLight);

    // 1. Floating 3D Medical Heart
    createHeart();

    // 2. Rotating 3D Medical Cross
    createCross();

    // 3. Subtle Green Botanical Leaves
    createLeaves();

    // 4. Glowing Blue-Green Ambient Particles
    createParticles();

    // Mouse Parallax Event
    window.addEventListener("mousemove", onDocumentMouseMove, false);
    window.addEventListener("resize", onWindowResize, false);

    // Start Animation Loop
    animate();
  }

  // Construct 3D Heart Shape
  function createHeart() {
    heartGroup = new THREE.Group();

    const x = 0, y = 0;
    const heartShape = new THREE.Shape();
    heartShape.moveTo(x + 2.5, y + 2.5);
    heartShape.bezierCurveTo(x + 2.5, y + 2.5, x + 2.0, y, x, y);
    heartShape.bezierCurveTo(x - 3.0, y, x - 3.0, y + 3.5, x - 3.0, y + 3.5);
    heartShape.bezierCurveTo(x - 3.0, y + 5.5, x - 1.0, y + 7.7, x + 2.5, y + 9.5);
    heartShape.bezierCurveTo(x + 6.0, y + 7.7, x + 8.0, y + 5.5, x + 8.0, y + 3.5);
    heartShape.bezierCurveTo(x + 8.0, y + 3.5, x + 8.0, y, x + 5.0, y);
    heartShape.bezierCurveTo(x + 3.5, y, x + 2.5, y + 2.5, x + 2.5, y + 2.5);

    const extrudeSettings = {
      depth: 1.2,
      bevelEnabled: true,
      bevelSegments: 4,
      steps: 2,
      bevelSize: 0.5,
      bevelThickness: 0.5
    };

    const geometry = new THREE.ExtrudeGeometry(heartShape, extrudeSettings);
    geometry.center();

    const material = new THREE.MeshPhongMaterial({
      color: 0xE53935,
      emissive: 0x4A0000,
      specular: 0xFF8A80,
      shininess: 90
    });

    const heartMesh = new THREE.Mesh(geometry, material);
    heartMesh.scale.set(0.35, 0.35, 0.35);
    heartMesh.rotation.z = Math.PI;

    heartGroup.add(heartMesh);
    heartGroup.position.set(-1.8, 0.4, 0);
    scene.add(heartGroup);
  }

  // Construct 3D Medical Cross
  function createCross() {
    crossGroup = new THREE.Group();

    const crossMat = new THREE.MeshStandardMaterial({
      color: 0x2E7D32,
      emissive: 0x0D3158,
      metalness: 0.25,
      roughness: 0.3
    });

    // Vertical bar
    const vertGeo = new THREE.BoxGeometry(0.7, 2.5, 0.5);
    const vertMesh = new THREE.Mesh(vertGeo, crossMat);

    // Horizontal bar
    const horizGeo = new THREE.BoxGeometry(2.5, 0.7, 0.5);
    const horizMesh = new THREE.Mesh(horizGeo, crossMat);

    crossGroup.add(vertMesh);
    crossGroup.add(horizMesh);

    crossGroup.position.set(2.2, -0.3, -1);
    crossGroup.scale.set(0.9, 0.9, 0.9);
    scene.add(crossGroup);
  }

  // Construct Subtle Botanical Leaves
  function createLeaves() {
    leavesGroup = new THREE.Group();

    const leafShape = new THREE.Shape();
    leafShape.moveTo(0, 0);
    leafShape.quadraticCurveTo(0.6, 1.2, 0, 2.4);
    leafShape.quadraticCurveTo(-0.6, 1.2, 0, 0);

    const leafGeo = new THREE.ShapeGeometry(leafShape);
    const leafMat = new THREE.MeshStandardMaterial({
      color: 0x66BB6A,
      side: THREE.DoubleSide,
      transparent: true,
      opacity: 0.85,
      roughness: 0.4
    });

    for (let i = 0; i < 7; i++) {
      const leaf = new THREE.Mesh(leafGeo, leafMat);
      const angle = (i / 7) * Math.PI * 2;
      const radius = 3.6 + (i % 3) * 0.5;

      leaf.position.x = Math.cos(angle) * radius;
      leaf.position.y = Math.sin(angle) * radius * 0.7;
      leaf.position.z = (Math.random() - 0.5) * 3;

      leaf.rotation.x = Math.random() * Math.PI;
      leaf.rotation.y = Math.random() * Math.PI;
      leaf.rotation.z = Math.random() * Math.PI;
      leaf.scale.setScalar(0.45 + Math.random() * 0.3);

      leaf.userData = {
        speedX: 0.004 + Math.random() * 0.006,
        speedY: 0.006 + Math.random() * 0.008,
        rotSpeed: 0.01 + Math.random() * 0.015,
        baseX: leaf.position.x,
        baseY: leaf.position.y
      };

      leavesGroup.add(leaf);
    }

    scene.add(leavesGroup);
  }

  // Construct Glowing Blue-Green Ambient Particles
  function createParticles() {
    particlesGroup = new THREE.Group();
    const particleCount = 45;
    const geometry = new THREE.SphereGeometry(0.06, 8, 8);

    for (let i = 0; i < particleCount; i++) {
      const color = i % 2 === 0 ? 0x1565C0 : 0x66BB6A;
      const material = new THREE.MeshBasicMaterial({
        color: color,
        transparent: true,
        opacity: 0.65
      });

      const particle = new THREE.Mesh(geometry, material);
      particle.position.set(
        (Math.random() - 0.5) * 12,
        (Math.random() - 0.5) * 8,
        (Math.random() - 0.5) * 6
      );

      particle.userData = {
        driftSpeed: 0.005 + Math.random() * 0.01,
        angle: Math.random() * Math.PI * 2
      };

      particlesGroup.add(particle);
    }

    scene.add(particlesGroup);
  }

  function onDocumentMouseMove(event) {
    mouseX = (event.clientX - windowHalfX) * 0.0012;
    mouseY = (event.clientY - windowHalfY) * 0.0012;
  }

  function onWindowResize() {
    if (!container || !renderer || !camera) return;
    const width = container.clientWidth || 500;
    const height = container.clientHeight || 450;
    windowHalfX = window.innerWidth / 2;
    windowHalfY = window.innerHeight / 2;

    camera.aspect = width / height;
    camera.updateProjectionMatrix();
    renderer.setSize(width, height);
  }

  // Animation Loop
  function animate() {
    requestAnimationFrame(animate);

    const delta = clock.getDelta();
    const time = clock.getElapsedTime();

    if (!prefersReducedMotion) {
      // 1. Heartbeat Rhythm Animation (systole + diastole)
      if (heartGroup) {
        const beat = Math.sin(time * 3.2) + 0.35 * Math.sin(time * 6.4);
        const scale = 1 + 0.09 * Math.max(0, beat);
        heartGroup.scale.set(scale, scale, scale);
        heartGroup.rotation.y = Math.sin(time * 0.8) * 0.3;
        heartGroup.position.y = 0.4 + Math.sin(time * 1.5) * 0.15;
      }

      // 2. Medical Cross Gentle Float & Rotate
      if (crossGroup) {
        crossGroup.rotation.y += 0.009;
        crossGroup.rotation.x = Math.sin(time * 0.9) * 0.2;
        crossGroup.position.y = -0.3 + Math.sin(time * 1.2) * 0.2;
      }

      // 3. Subtle Floating Leaves
      if (leavesGroup) {
        leavesGroup.children.forEach((leaf, idx) => {
          leaf.rotation.x += leaf.userData.rotSpeed;
          leaf.rotation.y += leaf.userData.rotSpeed * 0.8;
          leaf.position.y = leaf.userData.baseY + Math.sin(time * 1.5 + idx) * 0.35;
          leaf.position.x = leaf.userData.baseX + Math.cos(time * 1.2 + idx) * 0.25;
        });
      }

      // 4. Ambient Floating Particles
      if (particlesGroup) {
        particlesGroup.children.forEach((p) => {
          p.position.y += Math.sin(time * 2 + p.userData.angle) * 0.006;
          p.position.x += Math.cos(time * 1.5 + p.userData.angle) * 0.004;
        });
      }

      // Smooth Camera Parallax Lerp
      targetX += (mouseX - targetX) * 0.05;
      targetY += (mouseY - targetY) * 0.05;
      camera.position.x = targetX * 4;
      camera.position.y = -targetY * 4;
      camera.lookAt(scene.position);
    }

    renderer.render(scene, camera);
  }

  // Initialize
  init();
})();
