<script>
  import { onMount, onDestroy } from 'svelte';

  let container;
  let animationId;
  let startTime;

  function animate(timestamp) {
    if (!startTime) startTime = timestamp;
    const elapsed = (timestamp - startTime) / 1000;

    // Плавное изменение яркости
    const opacity1 = 0.7 + Math.sin(elapsed * 0.3) * 0.3;
    const opacity2 = 0.7 + Math.sin(elapsed * 0.25 + 1.5) * 0.3;

    if (container) {
      container.style.setProperty('--blob1-opacity', opacity1);
      container.style.setProperty('--blob2-opacity', opacity2);
    }

    animationId = requestAnimationFrame(animate);
  }

  onMount(() => {
    animationId = requestAnimationFrame(animate);
  });

  onDestroy(() => {
    if (animationId) {
      cancelAnimationFrame(animationId);
    }
  });
</script>

<div class="glow-background" bind:this={container}>
  <div class="blob blob-1"></div>
  <div class="blob blob-2"></div>
</div>

<style>
  .glow-background {
    --blob1-opacity: 0.5;
    --blob2-opacity: 0.5;
    
    position: absolute;
    top: -2px;
    left: 0;
    width: 100%;
    height: 900px;
    z-index: -1;
    overflow: hidden;
    pointer-events: none;
  }

  .blob {
    position: absolute;
    border-radius: 50%;
    filter: blur(120px);
    will-change: opacity;
    backface-visibility: hidden;
    transform: translate(-50%, -50%) translateZ(0);
  }

  .blob-1 {
    width: 550px;
    height: 450px;
    left: 45%;
    top: 30%;
    opacity: var(--blob1-opacity);
    background: radial-gradient(
      ellipse at center,
      rgba(35, 130, 120, 1) 0%,
      rgba(25, 100, 95, 0.5) 50%,
      transparent 100%
    );
  }

  .blob-2 {
    width: 480px;
    height: 420px;
    left: 55%;
    top: 35%;
    opacity: var(--blob2-opacity);
    background: radial-gradient(
      ellipse at center,
      rgba(65, 45, 120, 1) 0%,
      rgba(50, 35, 95, 0.5) 50%,
      transparent 100%
    );
  }

  @media (max-width: 768px) {
    .blob-1 {
      width: 380px;
      height: 320px;
    }
    .blob-2 {
      width: 330px;
      height: 290px;
    }
  }
</style>