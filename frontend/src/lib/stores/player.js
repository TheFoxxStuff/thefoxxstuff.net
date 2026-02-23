import { writable, derived } from 'svelte/store';
import { browser } from '$app/environment';
import { API_BASE } from '$lib/api';

const STORAGE_KEY = 'player_state';
const PERSIST_FIELDS = ['volume', 'repeat'];

function loadPersistedState() {
  if (!browser) return {};
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (raw) {
      const parsed = JSON.parse(raw);
      return {
        // FIX: валидируем диапазон volume — не принимаем мусорные значения
        volume: typeof parsed.volume === 'number' && parsed.volume >= 0 && parsed.volume <= 1
          ? parsed.volume : 0.8,
        repeat: ['none', 'all', 'one'].includes(parsed.repeat) ? parsed.repeat : 'none',
      };
    }
  } catch {}
  return {};
}

function savePersistedState(state) {
  if (!browser) return;
  try {
    const data = {};
    for (const k of PERSIST_FIELDS) data[k] = state[k];
    localStorage.setItem(STORAGE_KEY, JSON.stringify(data));
  } catch {}
}

const initial = {
  tracks: [], release: null, currentIndex: -1,
  isPlaying: false, visible: false,
  repeat: 'none', volume: 0.8,
  ...loadPersistedState(),
};

function createPlayerStore() {
  const { subscribe, set, update } = writable(initial);

  function persist(state) { savePersistedState(state); return state; }

  return {
    subscribe,

    playRelease(release, startIndex = 0) {
      const audioTracks = (release.tracks || []).filter(t => t.audio_opus);
      if (audioTracks.length === 0) return;
      update(s => persist({
        ...s,
        tracks: release.tracks || [],
        release: {
          title: release.title, slug: release.slug, _id: release._id,
          cover_image_info: release.cover_image_info, genre: release.genre,
        },
        currentIndex: startIndex,
        isPlaying: true, visible: true,
      }));
    },

    playIndex(index) {
      update(s => {
        if (index < 0 || index >= s.tracks.length || !s.tracks[index]?.audio_opus) return s;
        return persist({ ...s, currentIndex: index, isPlaying: true, visible: true });
      });
    },

    togglePlay() { update(s => ({ ...s, isPlaying: !s.isPlaying })); },
    pause()      { update(s => ({ ...s, isPlaying: false })); },
    play()       { update(s => ({ ...s, isPlaying: true  })); },

    next() {
      update(s => {
        let next = s.currentIndex + 1;
        while (next < s.tracks.length && !s.tracks[next]?.audio_opus) next++;
        if (next >= s.tracks.length) {
          if (s.repeat === 'all') {
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
        return persist({ ...s, repeat: modes[idx] });
      });
    },

    setVolume(v) {
      // FIX: всегда зажимаем в [0,1] и проверяем что это число
      const vol = typeof v === 'number' && !isNaN(v) ? Math.max(0, Math.min(1, v)) : 0.8;
      update(s => persist({ ...s, volume: vol }));
    },

    close() {
      update(s => persist({
        tracks: [], release: null, currentIndex: -1,
        isPlaying: false, visible: false,
        repeat: s.repeat, volume: s.volume,
      }));
    },

    getAudioUrl(track) {
      return track?.audio_opus ? `${API_BASE}/upload/file/${track.audio_opus}` : null;
    },
  };
}

export const player = createPlayerStore();
export const currentTrack = derived(player, ($p) => {
  if ($p.currentIndex >= 0 && $p.currentIndex < $p.tracks.length) return $p.tracks[$p.currentIndex];
  return null;
});
