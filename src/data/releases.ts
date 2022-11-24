import type { Photo } from "./types/Photo";
import { galleryBlob } from "./utils/blob";

const raggiDelPianeta: Photo = {
  id: "raggi-del-pianeta",
  alt: "Golden sunset over a snowy mountain",
  src: {
    compressed: galleryBlob("https://bafybeicvvx3nfkmz7nsbza5fr3m4ov2zw6y4r3gjacdukpjgt7lhmmm7s4.ipfs.w3s.link/73c4d0_AI-League-scaled-1.jpg"),
    original: galleryBlob("https://bafybeicvvx3nfkmz7nsbza5fr3m4ov2zw6y4r3gjacdukpjgt7lhmmm7s4.ipfs.w3s.link/73c4d0_AI-League-scaled-1.jpg"),
  },
  title: "Raggi del Pianeta",
  description:
    "Golden sunset over a snowy mountain at North Cascades National Park",
  location: "North Cascades National Park",
  date: new Date("2022-01-09"),
};

export const photos: Photo[] = [
  raggiDelPianeta,
];
