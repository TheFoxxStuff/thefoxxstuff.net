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
        volume: typeof parsed.volume === 'number' ? parsed.volume : 0.8,
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
  tracks: [],
  release: null,
  currentIndex: -1,
  isPlaying: false,
  visible: false,
  repeat: 'none',
  volume: 0.8,
  ...loadPersistedState(),
};

function createPlayerStore() {
  const { subscribe, set, update } = writable(initial);

  function persist(state) {
    savePersistedState(state);
    return state;
  }

  // Find next playable track index starting from `from`, wrapping if needed
  function findNext(tracks, from, wrap = false) {
    let idx = from + 1;
    while (idx < tracks.length) {
      if (tracks[idx]?.audio_opus) return idx;
      idx++;
    }
    if (wrap) {
      idx = 0;
      while (idx < from) {
        if (tracks[idx]?.audio_opus) return idx;
        idx++;
      }
    }
    return -1;
  }

  function findPrev(tracks, from) {
    let idx = from - 1;
    while (idx >= 0) {
      if (tracks[idx]?.audio_opus) return idx;
      idx--;
    }
    return -1;
  }

  return {
    subscribe,
    playRelease(release, startIndex = 0) {
      const tracks = release.tracks || [];
      // Find first playable track at or after startIndex
      let idx = startIndex;
      while (idx < tracks.length && !tracks[idx]?.audio_opus) idx++;
      if (idx >= tracks.length) return; // no playable tracks at all
      update(s => persist({
        ...s,
        tracks,
        release: {
          title: release.title,
          slug: release.slug,
          _id: release._id,
          cover_image_info: release.cover_image_info,
          genre: release.genre
        },
        currentIndex: idx,
        isPlaying: true,
        visible: true
      }));
    },
    playIndex(index) {
      update(s => {
        if (index < 0 || index >= s.tracks.length || !s.tracks[index]?.audio_opus) return s;
        return persist({ ...s, currentIndex: index, isPlaying: true, visible: true });
      });
    },
    togglePlay() { update(s => ({ ...s, isPlaying: !s.isPlaying })); },
    pause() { update(s => ({ ...s, isPlaying: false })); },
    play() { update(s => ({ ...s, isPlaying: true })); },
    next() {
      update(s => {
        const next = findNext(s.tracks, s.currentIndex, s.repeat === 'all');
        if (next === -1) return { ...s, isPlaying: false };
        return { ...s, currentIndex: next, isPlaying: true };
      });
    },
    prev() {
      update(s => {
        const prev = findPrev(s.tracks, s.currentIndex);
        if (prev === -1) return s;
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
      update(s => persist({ ...s, volume: Math.max(0, Math.min(1, v)) }));
    },
    close() {
      update(s => persist({
        tracks: [], release: null, currentIndex: -1,
        isPlaying: false, visible: false,
        repeat: s.repeat, volume: s.volume
      }));
    },
    getAudioUrl(track) {
      return track?.audio_opus ? `${API_BASE}/upload/file/${track.audio_opus}` : null;
    }
  };
}

export const player = createPlayerStore();
export const currentTrack = derived(player, ($p) => {
  if ($p.currentIndex >= 0 && $p.currentIndex < $p.tracks.length) return $p.tracks[$p.currentIndex];
  return null;
});
