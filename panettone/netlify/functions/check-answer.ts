import postgres from "postgres";
import categoriesData from "../../src/lib/assets/categories.json" with { type: "json" };
import type { Config, Context } from "@netlify/functions"
import type { Category } from "../../src/lib/types"


const categories = (categoriesData as { categories: Category[] }).categories;

const SIMILARITY_THRESHOLD = 0.5;

const sql = postgres(process.env.DATABASE_URL as string);

export default async (req: Request) => {
	if (req.method !== "POST") {
		return new Response(JSON.stringify({ error: "method not allowed" }), {
			status: 405,
			headers: { "content-type": "application/json" }
		});
	}

	const body = await req.json();
	const category = body.category as string | undefined;
	const guess = body.guess as string | undefined;

	if (!category || !guess) {
		return new Response(JSON.stringify({ error: "category and guess are required" }), {
			status: 400,
			headers: { "content-type": "application/json" }
		});
	}

	const entry = categories.find((c) => c.label === category);
	if (!entry) {
		return new Response(JSON.stringify({ error: "unknown category" }), {
			status: 404,
			headers: { "content-type": "application/json" }
		});
	}

	const fuzzy = entry.fuzzy !== false;

	const whereQuery = entry.query ? `${entry.query} AND` : "";

	const matchCondition = fuzzy
		? `similarity(name, normalize_text($1)) > $2`
		: `name = normalize_text($1)`;

	const rows = await sql.unsafe(
		`SELECT EXISTS (
			SELECT 1 FROM ${entry.table}
			WHERE ${whereQuery}
				${matchCondition}
		) AS found`,
		fuzzy ? [guess, SIMILARITY_THRESHOLD] : [guess]
	);

	const correct = Boolean(rows[0].found);

	return new Response(JSON.stringify({ correct }), {
		headers: { "content-type": "application/json" }
	});
};


export const config: Config = {
    path: "/api/check-answer",
}
