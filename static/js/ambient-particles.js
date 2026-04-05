(function () {
  const container = document.getElementById('ambient-particles');
  if (!container) return;

  const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)');

  function randomBetween(min, max) {
    return min + Math.random() * (max - min);
  }

  function buildParticle() {
    const particle = document.createElement('span');
    const size = randomBetween(1.1, 4.6);
    const duration = randomBetween(18, 42);
    const delay = -randomBetween(0, duration);
    const startY = randomBetween(-125, 110);
    const startX = randomBetween(-7, 7);
    const driftA = randomBetween(-22, 22);
    const driftB = randomBetween(-36, 36);
    const driftC = randomBetween(-18, 18);
    const opacity = randomBetween(0.12, 0.52);
    const blur = randomBetween(0, 1.6);
    const twinkle = randomBetween(3.2, 9.5);
    const hue = Math.random() > 0.7 ? 'rgba(137, 218, 236, 1)' : 'rgba(237, 247, 255, 1)';

    particle.className = 'ambient-particle';
    particle.style.setProperty('--size', `${size}px`);
    particle.style.setProperty('--left', `${randomBetween(0, 100)}%`);
    particle.style.setProperty('--start-y', `${startY}vh`);
    particle.style.setProperty('--duration', `${duration}s`);
    particle.style.setProperty('--delay', `${delay}s`);
    particle.style.setProperty('--drift-start', `${startX}px`);
    particle.style.setProperty('--drift-a', `${driftA}px`);
    particle.style.setProperty('--drift-b', `${driftB}px`);
    particle.style.setProperty('--drift-c', `${driftC}px`);
    particle.style.setProperty('--opacity', opacity.toFixed(3));
    particle.style.setProperty('--blur', `${blur}px`);
    particle.style.setProperty('--twinkle-duration', `${twinkle}s`);
    particle.style.setProperty('--particle-color', hue);

    return particle;
  }

  function populate() {
    container.replaceChildren();
    const count = reduceMotion.matches ? 0 : 72;
    for (let i = 0; i < count; i += 1) {
      container.appendChild(buildParticle());
    }
  }

  populate();
  if (typeof reduceMotion.addEventListener === 'function') {
    reduceMotion.addEventListener('change', populate);
  }
})();
