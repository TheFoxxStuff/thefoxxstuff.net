<script>
  import { onMount, onDestroy } from 'svelte';

  let progress = $state(0);
  let mounted = $state(false);

  function update() {
    const scrollTop = window.scrollY;
    const docHeight = document.documentElement.scrollHeight - window.innerHeight;
    progress = docHeight > 0 ? Math.min(100, (scrollTop / docHeight) * 100) : 0;
  }

  onMount(() => {
    mounted = true;
    window.addEventListener('scroll', update, { passive: true });
    update();
  });

  onDestroy(() => {
    if (typeof window !== 'undefined') window.removeEventListener('scroll', update);
  });
</script>

{#if mounted && progress > 0}
  <div
    class="reading-progress"
    style="width: {progress}%"
    role="progressbar"
    aria-valuenow={Math.round(progress)}
    aria-valuemin="0"
    aria-valuemax="100"
    aria-label="Reading progress"
  ></div>
{/if}
