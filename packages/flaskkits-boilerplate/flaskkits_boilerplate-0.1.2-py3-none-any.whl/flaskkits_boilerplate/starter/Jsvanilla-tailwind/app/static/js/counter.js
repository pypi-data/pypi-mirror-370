document.addEventListener('DOMContentLoaded', () => {
  let count = 0;
  const counterEl = document.getElementById('counter');
  const incrementBtn = document.getElementById('increment');
  const decrementBtn = document.getElementById('decrement');
  const resetBtn = document.getElementById('reset');
  const randomizeBtn = document.getElementById('randomize');
  const lightModeBtn = document.getElementById('light-mode');
  const darkModeBtn = document.getElementById('dark-mode');

  // Update counter with animation
  const render = () => {
    counterEl.textContent = count;
    
    // Animate counter change
    counterEl.animate([
      { transform: 'scale(1.2)', opacity: 0.8 },
      { transform: 'scale(1)', opacity: 1 }
    ], {
      duration: 300,
      easing: 'ease-out'
    });
  };

  // Button click animations
  const animateButton = (btn) => {
    btn.animate([
      { transform: 'scale(1)' },
      { transform: 'scale(0.9)' },
      { transform: 'scale(1)' }
    ], {
      duration: 300,
      easing: 'ease-in-out'
    });
  };

  // Create particle effect
  const createParticles = (x, y, color) => {
    const particles = [];
    const particleCount = 15;
    
    for (let i = 0; i < particleCount; i++) {
      particles.push({
        x,
        y,
        size: Math.random() * 4 + 2,
        speedX: (Math.random() - 0.5) * 6,
        speedY: (Math.random() - 0.5) * 6,
        color,
        life: 40 + Math.random() * 20
      });
    }
    
    window.particles = window.particles ? window.particles.concat(particles) : particles;
  };

  // Theme switching
  const setTheme = (theme) => {
    document.documentElement.classList.remove('light', 'dark');
    document.documentElement.classList.add(theme);
    lightModeBtn.classList.toggle('active', theme === 'light');
    darkModeBtn.classList.toggle('active', theme === 'dark');
    localStorage.setItem('theme', theme);
  };

  // Initialize theme
  const savedTheme = localStorage.getItem('theme') || 'dark';
  setTheme(savedTheme);

  // Event Listeners
  incrementBtn.addEventListener('click', () => { 
    count++; 
    render(); 
    animateButton(incrementBtn);
    const rect = incrementBtn.getBoundingClientRect();
    createParticles(rect.left + rect.width/2, rect.top + rect.height/2, '#10b981');
  });
  
  decrementBtn.addEventListener('click', () => { 
    if (count === 0) return;
    count--; 
    render(); 
    animateButton(decrementBtn);
    const rect = decrementBtn.getBoundingClientRect();
    createParticles(rect.left + rect.width/2, rect.top + rect.height/2, '#ef4444');
  });
  
  resetBtn.addEventListener('click', () => { 
    count = 0; 
    render(); 
    animateButton(resetBtn);
    const rect = resetBtn.getBoundingClientRect();
    createParticles(rect.left + rect.width/2, rect.top + rect.height/2, '#64748b');
  });
  
  randomizeBtn.addEventListener('click', () => { 
    count = Math.floor(Math.random() * 1000);
    render(); 
    animateButton(randomizeBtn);
    const rect = randomizeBtn.getBoundingClientRect();
    createParticles(rect.left + rect.width/2, rect.top + rect.height/2, '#8b5cf6');
  });
  
  lightModeBtn.addEventListener('click', () => setTheme('light'));
  darkModeBtn.addEventListener('click', () => setTheme('dark'));

  render();
});
