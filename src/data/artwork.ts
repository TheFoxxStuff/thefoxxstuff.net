import type { Image } from "./types/Image";
import { galleryBlob } from "./utils/blob";

const closeEncounters: Image = {
  id: "close-encounters",
  alt: "Ink drawing of UFOs",
  src: {
    compressed: galleryBlob("2844145_crisppyboat_king-o-the-cats-3-part-b-w-folktale-illu.jpg"),
    original: galleryBlob("2844145_crisppyboat_king-o-the-cats-3-part-b-w-folktale-illu.jpg"),
  },
  title: "Close Encounters",
  description: "Ink drawing of UFOs",
};

const mendotaMind: Image = {
  id: "mendota-mind",
  alt: "A chilly night on Lake Mendota",
  src: {
    compressed: galleryBlob("2844145_crisppyboat_king-o-the-cats-3-part-b-w-folktale-illu.jpg"),
    original: galleryBlob("2844145_crisppyboat_king-o-the-cats-3-part-b-w-folktale-illu.jpg"),
  },
  title: "Mendota Mind",
  description: "A chilly night on Lake Mendota",
};

const mendostaMind: Image = {
  id: "mendota-mssind",
  alt: "A chsake Mendota",
  src: {
    compressed: galleryBlob("2844145_crisppyboat_king-o-the-cats-3-part-b-w-folktale-illu.jpg"),
    original: galleryBlob("2844145_crisppyboat_king-o-the-cats-3-part-b-w-folktale-illu.jpg"),
  },
  title: "Mendota Mind",
  description: "A chilly night on Lake Mendota",
};

export const artwork: Image[] = [closeEncounters, mendotaMind, mendostaMind];
