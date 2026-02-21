<!-- <script>
  import { onMount } from 'svelte';
  
  export let containerId = "particles-js";
  
  onMount(() => {
    const initParticles = () => {
      if (window.particlesJS) {
        window.particlesJS(containerId, {
          particles: {
            number: { 
              value: 50, 
              density: { enable: true, value_area: 1920 }
            },
            color: { value: "#ffffff" },
            shape: { type: "circle" },
            opacity: {
              value: 1,
              random: true,
              anim: { enable: true, speed: 1, opacity_min: 0, sync: false }
            },
            size: {
              value: 1,
              random: true,
              anim: { enable: true, speed: 1, size_min: 1, sync: false }
            },
            line_linked: { enable: false },
            move: {
              enable: true,
              speed: 0.6,
              direction: "none",
              random: true,
              straight: false,
              out_mode: "out",
              bounce: false
            }
          },
          interactivity: {
            detect_on: "canvas",
            events: {
              onclick: { enable: false },
              resize: true
            }
          },
          retina_detect: false
        });
      }
    };
    
    if (!window.particlesJS) {
      const script = document.createElement('script');
      script.src = "https://cdn.jsdelivr.net/particles.js/2.0.0/particles.min.js";
      script.async = true;
      script.onload = initParticles;
      document.head.appendChild(script);
    } else {
      initParticles();
    }
  });
</script>

<div class="bg-wrapper">
  <div id={containerId} class="bg-container"></div>
  <div class="overlay"></div>
</div>

<style>
  .bg-wrapper {
    position: absolute;
    top: 0;
    left: 50%;
    transform: translateX(-50%);
    width: 100vw;
    height: 1080px;
    z-index: 9999;
    overflow: visible;
    pointer-events: none;
  }

  .bg-container {
    position: absolute;
    top: 0;
    left: 50%;
    transform: translateX(-50%);
    width: 1920px;
    min-width: 100vw;
    height: 100%;
  }
  
  .overlay {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    z-index: 1;
    pointer-events: none;
  }
  
  :global(.bg-container canvas) {
    display: block;
    width: 100% !important;
    height: 100% !important;
  }
</style> -->