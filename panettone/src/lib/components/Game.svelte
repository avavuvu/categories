<script lang="ts">
    import Dice from "./Dice.svelte";
    import Logo from "./Logo.svelte";
    import categoriesJson from "$lib/assets/categories.json";
    const categories = categoriesJson.categories;

    const inputs = Array.from({ length: categories.length }, () => "");
</script>

<main>
    <Logo />
    <Dice />

    <div class="answers">
        {#each categories as category, index}
            <div class="category">
                <p class="label">
                    {category.label}
                </p>
                {#if category.facts}
                    <p class="source">
                        {category.facts}
                    </p>
                {/if}
                <div
                    class="input-box"
                    style="--color: var(--color-{index % 5})"
                >
                    <div class="box"></div>
                    <input bind:value={inputs[index]} />
                </div>
            </div>
        {/each}
    </div>
</main>

<style>
    main {
        max-width: 500px;
        margin: 0 auto;
    }


</style>
