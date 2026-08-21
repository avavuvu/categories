<script lang="ts">
    import Logo from "$lib/components/Logo.svelte";
</script>

<main>
    <p>
        Happy Birthday Zara!
    </p>

    <img src="/love/0.webp" alt=""/>
    <img src="/love/1.webp" alt=""/>
    <img src="/love/2.webp" alt=""/>
    <img src="/love/3.webp" alt=""/>
    <img src="/love/4.webp" alt=""/>
    <img src="/love/5.webp" alt=""/>
    <img src="/love/6.webp" alt=""/>

    <p>
        Hi Doc
    </p>

    <p>
        Hope you're doing super awesome on this lovely day... which is not your birthday. My mother would say that's bad luck, very presumptuous.
    </p>

    <p>
        Your gift is this funny little game I made. I hope you like it. It is loosely (and by that I mean very heavily) based on Scattergories. The issue with it is the fun part of Scattergories is yelling at your friends about why "bung knee" is actually a valid type of disease that starts with B. Obviously I could not recreate that on a computer.
    </p>

    <p>
        Anyway, I know you like feeling smart and listing things--you wouldn't be able to do two hours of anki cards otherwise--so I hope this scratches that itch for you.
    </p>

     <p>
        You are such a kind and lovely friend. I know you are such a busy busy bee nowadays, but you still find so much time to support me in all my strange little endevours. I want to move closer to the city next year, and I hope I move slightly closer to you.
    </p>

    <p>
        I love you lots and lots,
    </p>
    <p>
        Ava
    </p>

    <Logo />

    <div class="play" >
        <a href="/start">Play!</a>
    </div>
</main>

<style>
    p, img {
        margin-bottom: 1em;
    }

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
