import type { Photo } from "./types/Photo";
import { galleryBlob } from "./utils/blob";

const raggiDelPianeta: Photo = {
  id: "raggi-del-pianeta",
  alt: "Golden sunset over a snowy mountain",
  src: {
    compressed: galleryBlob("2844145_crisppyboat_king-o-the-cats-3-part-b-w-folktale-illu.jpg"),
    original: galleryBlob("2844145_crisppyboat_king-o-the-cats-3-part-b-w-folktale-illu.jpg"),
  },
  title: "Raggi del Pianeta",
  description:
    "Golden sunset over a snowy mountain at North Cascades National Park",
  location: "North Cascades National Park",
  date: new Date("2022-01-09"),
};

const rivederLeStelle: Photo = {
  id: "riveder-le-stelle",
  alt: "Glimpse of the Milky Way hovering over the Cascades",
  src: {
    compressed: ("https://bafybeicvvx3nfkmz7nsbza5fr3m4ov2zw6y4r3gjacdukpjgt7lhmmm7s4.ipfs.w3s.link/73c4d0_AI-League-scaled-1.jpg"),
    original: ("https://bafybeicvvx3nfkmz7nsbza5fr3m4ov2zw6y4r3gjacdukpjgt7lhmmm7s4.ipfs.w3s.link/73c4d0_AI-League-scaled-1.jpg"),
  },
  title: "Riveder le Stelle",
  description: "Glimpse of the Milky Way hovering over the Cascades",
  location: "North Cascades National Park",
  date: new Date("2021-09-03"),
};


export const photos: Photo[] = [
  raggiDelPianeta,
  rivederLeStelle,
];



