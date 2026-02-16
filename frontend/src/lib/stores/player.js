import { writable, derived } from 'svelte/store';
import { API_BASE } from '$lib/api';

function createPlayerStore() {
  const { subscribe, set, update } = writable({
    tracks: [],
    release: null,
    currentIndex: -1,
    isPlaying: false,
    visible: false,
    repeat: 'none', // 'none' | 'all' | 'one'
    volume: 0.8,
  });

  return {
    subscribe,
    playRelease(release, startIndex = 0) {
      const audioTracks = (release.tracks || []).filter(t => t.audio_opus);
      if (audioTracks.length === 0) return;
      update(s => ({
        ...s,
        tracks: release.tracks || [],
        release: { title: release.title, slug: release.slug, _id: release._id, cover_image_info: release.cover_image_info, genre: release.genre },
        currentIndex: startIndex,
        isPlaying: true,
        visible: true
      }));
    },
    playIndex(index) {
      update(s => {
        if (index < 0 || index >= s.tracks.length || !s.tracks[index]?.audio_opus) return s;
        return { ...s, currentIndex: index, isPlaying: true, visible: true };
      });
    },
    togglePlay() { update(s => ({ ...s, isPlaying: !s.isPlaying })); },
    pause() { update(s => ({ ...s, isPlaying: false })); },
    play() { update(s => ({ ...s, isPlaying: true })); },
    next() {
      update(s => {
        let next = s.currentIndex + 1;
        while (next < s.tracks.length && !s.tracks[next]?.audio_opus) next++;
        if (next >= s.tracks.length) {
          if (s.repeat === 'all') {
            // Loop back to first playable track
            next = 0;
            while (next < s.tracks.length && !s.tracks[next]?.audio_opus) next++;
            if (next >= s.tracks.length) return { ...s, isPlaying: false };
            return { ...s, currentIndex: next, isPlaying: true };
          }
          return { ...s, isPlaying: false };
        }
        return { ...s, currentIndex: next, isPlaying: true };
      });
    },
    prev() {
      update(s => {
        let prev = s.currentIndex - 1;
        while (prev >= 0 && !s.tracks[prev]?.audio_opus) prev--;
        if (prev < 0) return s;
        return { ...s, currentIndex: prev, isPlaying: true };
      });
    },
    toggleRepeat() {
      update(s => {
        const modes = ['none', 'all', 'one'];
        const idx = (modes.indexOf(s.repeat) + 1) % modes.length;
        return { ...s, repeat: modes[idx] };
      });
    },
    setVolume(v) { update(s => ({ ...s, volume: Math.max(0, Math.min(1, v)) })); },
    close() { set({ tracks: [], release: null, currentIndex: -1, isPlaying: false, visible: false, repeat: 'none', volume: 0.8 }); },
    getAudioUrl(track) { return track?.audio_opus ? `${API_BASE}/upload/file/${track.audio_opus}` : null; }
  };
}

export const player = createPlayerStore();
export const currentTrack = derived(player, ($p) => {
  if ($p.currentIndex >= 0 && $p.currentIndex < $p.tracks.length) return $p.tracks[$p.currentIndex];
  return null;
});
