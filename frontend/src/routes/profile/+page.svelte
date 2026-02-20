<script>
  import { onMount } from 'svelte';
  import { auth } from '$lib/stores/auth.js';
  import { goto } from '$app/navigation';

  onMount(() => {
    if (!$auth.user) { goto('/auth/login'); return; }
    goto(`/profile/${$auth.user.username}`, { replaceState: true });
  });
</script>
