import categoriesData from "$lib/assets/categories.json" with { type: "json" };
import type { Category } from "./types";

export const categories = (categoriesData as { categories: Category[] }).categories;

export const letters = [
    "a",
    "b",
    "c",
    "d",
    "e",
    "f",
    "g",
    "h",
    "i",
    "j",
    "k",
    "l",
    "m",
    "n",
    "o",
    "p",
    "r",
    "s",
    "t",
    "w",
] as const;


function shuffle<T>(items: T[]): T[] {
    const result = [...items];

    for (let i = result.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        [result[i], result[j]] = [result[j], result[i]];
    }

    return result;
}

export const initGame = () => {
    const targetLetter = letters[Math.floor(Math.random() * letters.length)];
    const targetCategories = shuffle(categories).slice(0, 8);

    return {
        targetLetter,
        targetCategories,
    };
};
