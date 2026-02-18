<script>
  import { onMount, onDestroy } from 'svelte';

  let container;
  let animationId;
  let startTime;

  function animate(timestamp) {
    if (!startTime) startTime = timestamp;
    const t = (timestamp - startTime) / 1000;

    const opacity1 = 0.55 + Math.sin(t * 0.28) * 0.25;
    const opacity2 = 0.55 + Math.sin(t * 0.22 + 1.8) * 0.25;
    const opacity3 = 0.35 + Math.sin(t * 0.18 + 0.9) * 0.2;

    // Subtle movement
    const x1 = 44 + Math.sin(t * 0.12) * 4;
    const y1 = 28 + Math.sin(t * 0.09) * 5;
    const x2 = 58 + Math.sin(t * 0.15 + 2) * 4;
    const y2 = 36 + Math.sin(t * 0.11 + 1) * 4;

    if (container) {
      container.style.setProperty('--blob1-opacity', opacity1);
      container.style.setProperty('--blob2-opacity', opacity2);
      container.style.setProperty('--blob3-opacity', opacity3);
      container.style.setProperty('--blob1-x', x1 + '%');
      container.style.setProperty('--blob1-y', y1 + '%');
      container.style.setProperty('--blob2-x', x2 + '%');
      container.style.setProperty('--blob2-y', y2 + '%');
    }

    animationId = requestAnimationFrame(animate);
  }

  onMount(() => { animationId = requestAnimationFrame(animate); });
  onDestroy(() => { if (animationId) cancelAnimationFrame(animationId); });
</script>

<div class="glow-background" bind:this={container}>
  <div class="blob blob-1"></div>
  <div class="blob blob-2"></div>
  <div class="blob blob-3"></div>
</div>

<style>
  .glow-background {
    --blob1-opacity: 0.5;
    --blob2-opacity: 0.5;
    --blob3-opacity: 0.3;
    --blob1-x: 44%;
    --blob1-y: 28%;
    --blob2-x: 58%;
    --blob2-y: 36%;

    position: absolute;
    top: -2px;
    left: 0;
    width: 100%;
    height: 1000px;
    z-index: -1;
    overflow: hidden;
    pointer-events: none;
  }

  .blob {
    position: absolute;
    border-radius: 50%;
    filter: blur(100px);
    will-change: opacity, transform;
    transform: translate(-50%, -50%) translateZ(0);
    transition: left 4s ease, top 4s ease;
  }

  .blob-1 {
    width: 600px;
    height: 500px;
    left: var(--blob1-x);
    top: var(--blob1-y);
    opacity: var(--blob1-opacity);
    background: radial-gradient(
      ellipse at center,
      rgba(35, 138, 125, 0.9) 0%,
      rgba(20, 95, 90, 0.5) 50%,
      transparent 100%
    );
  }

  .blob-2 {
    width: 520px;
    height: 460px;
    left: var(--blob2-x);
    top: var(--blob2-y);
    opacity: var(--blob2-opacity);
    background: radial-gradient(
      ellipse at center,
      rgba(72, 48, 130, 0.9) 0%,
      rgba(55, 35, 100, 0.5) 50%,
      transparent 100%
    );
  }

  .blob-3 {
    width: 400px;
    height: 350px;
    left: 25%;
    top: 60%;
    opacity: var(--blob3-opacity);
    background: radial-gradient(
      ellipse at center,
      rgba(65, 35, 110, 0.7) 0%,
      transparent 70%
    );
  }

  @media (max-width: 768px) {
    .blob-1 { width: 380px; height: 320px; }
    .blob-2 { width: 330px; height: 290px; }
    .blob-3 { width: 250px; height: 220px; }
  }
</style>
