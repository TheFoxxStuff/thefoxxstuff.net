import { useSanityClient } from "astro-sanity";

// export async function getAllPosts() {
//   const query = `*[_type == 'post']{"categoryData": categories[]->{slug, title},author -> {name}, ...} | order(publishedAt desc)`;
//   const data = await useSanityClient().fetch(query);
//   return data;
// }


// export async function getAllPosts() {
//     const query = `*[_type == 'post']{..., "categoryData": categories[]->{slug, title},author -> {name, slug, image, bio}} | order(publishedAt desc)`;
//     const data = await useSanityClient().fetch(query);
//     return data;
// }

// export async function getAllCategoriesWithPosts() {
//     const query = `*[_type == 'category']{"posts": *[_type == "post" && references(^._id)] | order(publishedAt desc), ...}`;
//     const data = await useSanityClient().fetch(query);
//     return data;
// }

export async function getAllRel() {
    const query = `*[_type == 'music']{...,author -> {trackname, tracknumber, trackduration}} | order(released desc)`;
    const data = await useSanityClient().fetch(query);
    return data;
}

export async function getAllRelinner() {
    const query = `*[_type == 'music']`;
    const data = await useSanityClient().fetch(query);
    return data;
}

// export async function getAllArts() {
//     const query = `*[_type == 'art']{..., "images": images[]->{slug, image, ...}} | order(publishedAt desc)`;
//     const data = await useSanityClient().fetch(query);
//     return data;
// }

export async function getAllArts() {
    const query = `*[_type == 'art']{..., "images": images[]->{slug, image, ...}, date}|order(date desc)`;
    const data = await useSanityClient().fetch(query);
    return data;
}

export async function getAllArtinner() {
    const query = `*[_type == 'arts']`;
    const data = await useSanityClient().fetch(query);
    return data;
}



// export async function getGalaryMainPage() {
//     const query = `*[_type == 'gallarymainpage']{
//         piccc->{
//           _id,
//           title,
//           ...,
//           image{
//             asset->
//           }
//         }
//       }`;
//     const data = await useSanityClient().fetch(query);
//     return data;
// }

export async function getGalaryMainPage() {
    const query = `*[_type == 'gallarymainpage']{"Big1": pic1-> {title, ...},"RightUp1": pic2-> {title, ...},"RightUp2": pic3-> {title, ...},"RightDown1": pic4-> {title, ...},"RightDown2": pic5-> {title, ...}} | order(publishedAt desc)`;
    const data = await useSanityClient().fetch(query);
    return data;
}

// export async function getGalaryMainPage() {
//     const query = `*[_type == 'gallarymainpage']{piccc}`;
//     const data = await useSanityClient().fetch(query);
//     const picccId = data[0].piccc._ref
//     const picccQuery = `*[_id == $picccId]`;
//     const picccParams = { picccId };
//     const piccc = await useSanityClient().fetch(picccQuery, picccParams)
//     return piccc;
// }