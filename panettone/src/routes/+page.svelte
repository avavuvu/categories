<script lang="ts">
    const category = "things you keep hidden";

    let answer = $state("bone");
    let response: any = $state({});

    async function callClient() {
        const res = await fetch("/api/submit", {
            method: "POST",
            headers: { "content-type": "application/json" },
            body: JSON.stringify({ answer, category }),
        });
        response = await res.json();
    }
</script>

<pre>{JSON.stringify(answer, null, 2)}</pre>

<h2>
    {category}
</h2>

<label for="answer">Answer</label>
<input id="answer" name="answer" type="text" bind:value={answer} />

<button onclick={callClient} type="submit">submit</button>

<output>
    <pre>{JSON.stringify(response, null, 2)}</pre>
</output>
