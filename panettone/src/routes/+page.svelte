<script lang="ts">
    import Logo from "$lib/components/Logo.svelte";
</script>

<main>
    <Logo />

    <div class="play" >
        <a href="/start">Play!</a>
    </div>
</main>

<style>
    .play {
        margin-top: 4em;

        & a {
            font: inherit;
            padding: 0.75em 2em;
            border: 2px solid var(--color-0);
            background: none;
            color: var(--color-0);
            cursor: pointer;
        }
    }

    main {
        display: grid;
        justify-items: center;
        width: 100%;
        max-width: 500px;
        margin: 0 auto;
        padding: 3rem 1rem;
    }
</style>
