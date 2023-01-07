import { useSanityClient } from "astro-sanity";

// export async function getAllPosts() {
//   const query = `*[_type == 'post']{"categoryData": categories[]->{slug, title},author -> {name}, ...} | order(publishedAt desc)`;
//   const data = await useSanityClient().fetch(query);
//   return data;
// }


export async function getAllPosts() {
    const query = `*[_type == 'post']{..., "categoryData": categories[]->{slug, title},author -> {name, slug, image, bio}} | order(publishedAt desc)`;
    const data = await useSanityClient().fetch(query);
    return data;
}

export async function getAllCategoriesWithPosts() {
    const query = `*[_type == 'category']{"posts": *[_type == "post" && references(^._id)] | order(publishedAt desc), ...}`;
    const data = await useSanityClient().fetch(query);
    return data;
}

export async function getAllRel() {
    const query = `*[_type == 'music']{...,author -> {trackname, tracknumber, trackduration}} | order(publishedAt desc)`;
    const data = await useSanityClient().fetch(query);
    return data;
}

export async function getAllArts() {
    const query = `*[_type == 'art']`;
    const data = await useSanityClient().fetch(query);
    return data;
}