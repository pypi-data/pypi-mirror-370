// Floating Particles Background
document.addEventListener('DOMContentLoaded', () => {
  const canvas = document.getElementById('particles');
  const ctx = canvas.getContext('2d');
  let particles = [];

  const resizeCanvas = () => {
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;
    createParticles();
  };

  resizeCanvas();
  window.addEventListener('resize', resizeCanvas);

  // Create particles
  function createParticles() {
    particles = [];
    const particleCount = Math.floor((canvas.width * canvas.height) / 8000);
    const centerX = canvas.width / 2;
    const centerY = canvas.height / 2;

    for (let i = 0; i < particleCount; i++) {
      const size = Math.random() * 8 + 4; // Ukuran lebih besar (4-12)
      const angle = Math.random() * Math.PI * 2;
      const speed = Math.random() * 7 + 3; // Kecepatan awal lebih tinggi (3-10)
      const initialSpreadRadius = 80; // Area awal lebih luas
      const initialX = centerX + (Math.random() - 0.5) * initialSpreadRadius;
      const initialY = centerY + (Math.random() - 0.5) * initialSpreadRadius;

      particles.push({
        x: initialX,
        y: initialY,
        size,
        opacity: 0.1 + Math.random() * 0.3,
        vx: Math.cos(angle) * speed,
        vy: Math.sin(angle) * speed
      });
    }
  }

  // Animate particles
  function animate() {
    requestAnimationFrame(animate);
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    const centerX = canvas.width / 2;
    const centerY = canvas.height / 2;
    const attractionStrength = 0.0015; // Tarikan ke pusat lebih lemah
    const maxDistance = Math.max(canvas.width, canvas.height) * 2.2; // Jangkauan lebih luas

    particles.forEach(p => {
      const dx = centerX - p.x;
      const dy = centerY - p.y;
      const distance = Math.sqrt(dx * dx + dy * dy);

      p.vx += dx * attractionStrength * (distance / maxDistance);
      p.vy += dy * attractionStrength * (distance / maxDistance);

      p.x += p.vx;
      p.y += p.vy;

      if (distance > maxDistance || (distance < 10 && (p.vx < 0.1 && p.vy < 0.1))) {
        const angle = Math.random() * Math.PI * 2;
        const speed = Math.random() * 7 + 3;
        const initialSpreadRadius = 80;
        p.x = centerX + (Math.random() - 0.5) * initialSpreadRadius;
        p.y = centerY + (Math.random() - 0.5) * initialSpreadRadius;
        p.vx = Math.cos(angle) * speed;
        p.vy = Math.sin(angle) * speed;
      }

      ctx.beginPath();
      ctx.arc(p.x, p.y, p.size, 0, Math.PI * 2);
      const gradient = ctx.createRadialGradient(p.x, p.y, 0, p.x, p.y, p.size);
      gradient.addColorStop(0, `rgba(99, 102, 241, ${p.opacity})`);
      gradient.addColorStop(1, `rgba(99, 102, 241, 0)`);
      ctx.fillStyle = gradient;
      ctx.fill();
    });
  }

  createParticles();
  animate();
});
