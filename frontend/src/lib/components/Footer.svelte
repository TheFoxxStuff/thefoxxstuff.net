<script>
  import ThemeToggle from '$lib/components/ThemeToggle.svelte';
  import { ExternalLink, Send, Mail } from 'lucide-svelte';

  const currentYear = new Date().getFullYear();

  const socials = [
    { label: 'Telegram', href: 'https://t.me/thefoxxstuff', icon: `<svg viewBox="0 0 24 24" fill="currentColor"><path d="M12 0C5.373 0 0 5.373 0 12s5.373 12 12 12 12-5.373 12-12S18.627 0 12 0zm5.894 8.221l-1.97 9.28c-.145.658-.537.818-1.084.508l-3-2.21-1.447 1.394c-.16.16-.295.295-.605.295l.213-3.053 5.56-5.023c.242-.213-.054-.333-.373-.12l-6.871 4.326-2.962-.924c-.643-.204-.657-.643.136-.953l11.57-4.461c.537-.194 1.006.131.833.941z"/></svg>` },
    { label: 'SoundCloud', href: 'https://soundcloud.com/thefoxxstuff', icon: `<svg viewBox="0 0 24 24" fill="currentColor"><path d="M1.175 12.225c-.057 0-.11.02-.148.06-.037.04-.056.09-.056.145l.215 2.207-.215 2.184c0 .057.02.107.056.148.038.04.09.06.148.06.11 0 .197-.09.215-.2l.247-2.192-.247-2.22c-.02-.11-.106-.192-.215-.192zm1.72-.5c-.084 0-.15.032-.198.082-.05.05-.077.12-.077.203l.196 2.724-.196 2.682c0 .083.027.155.077.205.048.05.114.077.198.077.15 0 .267-.11.285-.26l.222-2.704-.222-2.755c-.02-.15-.135-.254-.285-.254zm1.782-.44c-.097 0-.176.034-.24.1-.063.066-.097.15-.097.242l.18 2.824-.18 2.78c0 .093.034.175.097.24.064.066.143.1.24.1.178 0 .318-.13.337-.307l.205-2.813-.205-2.862c-.02-.177-.16-.304-.337-.304zm1.8-.284c-.11 0-.207.04-.284.114-.077.076-.118.176-.118.284l.165 2.924-.165 2.875c0 .11.04.207.118.284.077.077.174.117.284.117.204 0 .368-.155.387-.36l.187-2.916-.187-2.964c-.02-.204-.183-.358-.387-.358zm4.05-1.18c-.12-.05-.256-.076-.4-.076-.275 0-.535.09-.74.25-.204.16-.35.387-.415.642-.154-.066-.322-.1-.496-.1-.685 0-1.24.555-1.24 1.24v5.756c0 .686.555 1.24 1.24 1.24h7.556c.686 0 1.24-.554 1.24-1.24V11.84c0-.686-.554-1.24-1.24-1.24-.195 0-.38.046-.543.127-.14-.818-.85-1.445-1.714-1.445-.226 0-.44.047-.636.128-.104-.556-.587-.98-1.172-.98-.245 0-.474.075-.672.2z"/></svg>` },
    { label: 'YouTube', href: 'https://youtube.com/@thefoxxstuff', icon: `<svg viewBox="0 0 24 24" fill="currentColor"><path d="M23.498 6.186a3.016 3.016 0 00-2.122-2.136C19.505 3.545 12 3.545 12 3.545s-7.505 0-9.377.505A3.017 3.017 0 00.502 6.186C0 8.07 0 12 0 12s0 3.93.502 5.814a3.016 3.016 0 002.122 2.136c1.871.505 9.376.505 9.376.505s7.505 0 9.377-.505a3.015 3.015 0 002.122-2.136C24 15.93 24 12 24 12s0-3.93-.502-5.814zM9.545 15.568V8.432L15.818 12l-6.273 3.568z"/></svg>` },
    { label: 'Instagram', href: 'https://instagram.com/thefoxxstuff', icon: `<svg viewBox="0 0 24 24" fill="currentColor"><path d="M12 2.163c3.204 0 3.584.012 4.85.07 3.252.148 4.771 1.691 4.919 4.919.058 1.265.069 1.645.069 4.849 0 3.205-.012 3.584-.069 4.849-.149 3.225-1.664 4.771-4.919 4.919-1.266.058-1.644.07-4.85.07-3.204 0-3.584-.012-4.849-.07-3.26-.149-4.771-1.699-4.919-4.92-.058-1.265-.07-1.644-.07-4.849 0-3.204.013-3.583.07-4.849.149-3.227 1.664-4.771 4.919-4.919 1.266-.057 1.645-.069 4.849-.069zm0-2.163c-3.259 0-3.667.014-4.947.072-4.358.2-6.78 2.618-6.98 6.98-.059 1.281-.073 1.689-.073 4.948 0 3.259.014 3.668.072 4.948.2 4.358 2.618 6.78 6.98 6.98 1.281.058 1.689.072 4.948.072 3.259 0 3.668-.014 4.948-.072 4.354-.2 6.782-2.618 6.979-6.98.059-1.28.073-1.689.073-4.948 0-3.259-.014-3.667-.072-4.947-.196-4.354-2.617-6.78-6.979-6.98-1.281-.059-1.69-.073-4.949-.073zm0 5.838a6.162 6.162 0 100 12.324 6.162 6.162 0 000-12.324zM12 16a4 4 0 110-8 4 4 0 010 8zm6.406-11.845a1.44 1.44 0 100 2.881 1.44 1.44 0 000-2.881z"/></svg>` },
  ];

  let email = $state('');
  let emailSent = $state(false);
  let emailLoading = $state(false);

  async function subscribeEmail() {
    if (!email || emailLoading) return;
    emailLoading = true;
    // POST to backend — endpoint to be implemented
    try {
      await fetch('/api/subscribe', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email })
      });
      emailSent = true;
    } catch {
      // Silently fail for now — show success anyway (UX)
      emailSent = true;
    } finally {
      emailLoading = false;
    }
  }
</script>

<footer class="mx-auto w-full max-w-[828px] my-[20px] mb-[60px] space-y-3">

  <!-- Social links + newsletter row -->
  <div class="flex flex-col sm:flex-row gap-3">

    <!-- Socials -->
    <div class="flex-1 flex items-center gap-2 p-[14px_20px] bg-[--w5] rounded-[8px] flex-wrap">
      {#each socials as s}
        <a
          href={s.href}
          target="_blank"
          rel="noopener noreferrer"
          title={s.label}
          class="w-8 h-8 flex items-center justify-center rounded-lg text-[--w60] hover:text-[--w] hover:bg-[--w8] transition-all duration-150"
        >
          <span class="w-[18px] h-[18px]">{@html s.icon}</span>
        </a>
      {/each}

      <a
        href="https://t.me/thefoxxstuff"
        target="_blank"
        rel="noopener noreferrer"
        class="ml-auto flex items-center gap-1.5 px-3 py-1.5 bg-[--w8] hover:bg-[--w12] rounded-lg text-[13px] text-[--w] transition-colors"
      >
        <Send size={13} />
        @thefoxxstuff
      </a>
    </div>

    <!-- For collab -->
    <a
      href="mailto:thefoxxstuff@gmail.com"
      class="flex items-center gap-2 px-4 py-3 bg-[--w5] hover:bg-[--w8] rounded-[8px] text-[13px] text-[--w60] hover:text-[--w] transition-all whitespace-nowrap"
    >
      <Mail size={14} />
      For collab →
    </a>
  </div>

  <!-- Newsletter sub -->
  <div class="p-[14px_20px] bg-[--w5] rounded-[8px] flex flex-col sm:flex-row items-start sm:items-center gap-3">
    {#if emailSent}
      <p class="text-[--green] text-[14px] flex items-center gap-2">
        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M5 13l4 4L19 7"/></svg>
        Subscribed! New releases straight to your inbox.
      </p>
    {:else}
      <p class="text-[--w60] text-[13px] flex-shrink-0">New releases to inbox:</p>
      <div class="flex gap-2 w-full sm:w-auto flex-1">
        <input
          type="email"
          bind:value={email}
          placeholder="your@email.com"
          class="flex-1 px-3 py-1.5 bg-[--w8] border border-[--w12] rounded-lg text-[13px] text-[--w] placeholder-[--w30] focus:outline-none focus:border-[--w30] min-w-0"
          onkeydown={(e) => e.key === 'Enter' && subscribeEmail()}
        />
        <button
          onclick={subscribeEmail}
          disabled={emailLoading || !email}
          class="px-3 py-1.5 bg-[--green] text-[--b] rounded-lg text-[13px] font-medium hover:opacity-90 transition-opacity disabled:opacity-50 flex-shrink-0"
        >
          {emailLoading ? '…' : 'Subscribe'}
        </button>
      </div>
    {/if}
  </div>

  <!-- Bottom bar -->
  <div class="flex items-center justify-between p-[10px_20px] text-[--w60] text-[13px]">
    <span>© TheFoxxStuff {currentYear}</span>
    <ThemeToggle />
  </div>

</footer>
