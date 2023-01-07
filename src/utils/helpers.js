import { parseISO, format } from 'date-fns';
import { useSanityClient, createImageBuilder } from 'astro-sanity';

const builder = createImageBuilder(useSanityClient());

export function formatBlogPostDate(date) {
    const dateString = parseISO(date, 'YYYY/MM/Do');
    const formattedDateString = format(dateString, 'MMMM dd, yyyy');
    return `${formattedDateString}`;
}

export function formatMusicPerv(date) {
    const dateString = parseISO(date, 'YYYY/MM/Do');
    const formattedDateString = format(dateString, 'yyyy');
    return `${formattedDateString}`;
}


export function getSanityImageURL(source) {
    return builder.image(source);
}