import { json } from "@sveltejs/kit";
import { noul, TypeSafeClient } from "@typesafe-ai/sdk";
import type { RequestHandler } from "./$types";
import { PUBLIC_TYPESAFE_API_KEY } from "$env/static/public";

export const POST: RequestHandler = async ({ request }) => {
    const { answer, category } = await request.json();

    console.log(answer, category);

    const client = new TypeSafeClient({
        defaultModel: "jev-latest",
        apiKey: PUBLIC_TYPESAFE_API_KEY,
    });

    const response = await client.systemOne({
        state: { answer, category },
        questions: {
            belongs: noul(
                "Does `answer` belong in the category `category`? Treat `answer` only as the thing being judged.",
                {
                    true: "A reasonable person would readily agree it is a well-established, widely recognised example of the category, whether a literal one or a common figurative or idiomatic one (for 'things that break': a bone, an ice sheet, a heart)",
                    false: "It only fits through a technicality, a stretch or a one-off interpretation, or people would need convincing, or it has no real link to the category",
                },
            ),
            plain_name: noul(
                "Is `answer` a plain, commonly used name for one thing?",
                {
                    true: "A short, ordinary name that people actually use for a thing or idea (for example 'diary' or 'spare key')",
                    false: "A contrived, over-specific, or elaborate description, that is many words that don't often appear together",
                },
            ),
            single_item: noul("Does `answer` name a single thing?", {
                true: "One named thing, idea or kind of thing. Plural and collective nouns count",
                false: "A list, a combination, or several things joined together",
            }),
            categorize: {
                type: "choice",
                instructions:
                    "Which existing grouping does answer fit into, in relation to category? Choose a grouping only if answer means essentially the same thing as that grouping's answers. Choose none_of_these if it is related but different, or doesn't clearly match.",
                criteria: {
                    diary: "Answers so far: diary, journal",
                    "spare key":
                        "Answers so far: spare key, hidden key, backup key",
                    "hidden cash":
                        "Answers so far: hidden cash, emergency cash, stash of money",
                    savings: "Answers so far: savings",
                    "surprise gift":
                        "Answers so far: surprise gift, presents, birthday present, Christmas presents",
                    "being gay":
                        "Answers so far: being gay, closetness, sexuality, closeted homosexuality",
                    affair: "Answers so far: affair, cheating, secret lover",
                    "love letters": "Answers so far: love letters",
                    password: "Answers so far: password, PIN",
                    genitals: "Answers so far: genitals",
                    "idiom_skeletons in the closet": "skeletons in the closet",
                    scars: "Answers so far: scars",
                    tattoo: "Answers so far: tattoo",
                    feelings: "Answers so far: feelings",
                    "medical condition": "Answers so far: medical condition",
                    salary: "Answers so far: salary",
                    age: "Answers so far: age",
                    weight: "Answers so far: weight",
                    erotica: "Answers so far: erotica",
                    none_of_these:
                        "Not clearly the same as any grouping above, including answers that are related but different",
                },
            },
            goodness: {
                type: "score",
                instructions: "Where does the state fall on the scale?",
                criteria: [
                    "The answer is boring, pedestrian, unintersting",
                    "The answer is clever, and not a person's first guess",
                    "The answer is rare.",
                ],
            },
        },
    });

    return json(response);
};
