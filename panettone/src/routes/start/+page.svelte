<script lang="ts">
    import { createTimeline, stagger } from 'animejs';
    import Dice from '$lib/components/Dice.svelte';
    import Logo from '$lib/components/Logo.svelte';
    import { onMount, tick } from 'svelte';
    import { initGame } from '$lib/game.svelte';

    const GAME_DURATION_SECONDS = 90;

    let dice: Dice;
    let logo: Logo;
    let categoryEls: HTMLDivElement[] = [];
    let resultEls: HTMLSpanElement[] = [];
    let scoreSheet: HTMLDivElement | undefined = $state();
    let diceLetter = $state('a');
    let diceRolling = $state(false);
    let timeLeft = $state(GAME_DURATION_SECONDS);
    let timeUp = $state(false);
    let results: (boolean | null)[] = $state([]);

    const allChecked = $derived(results.length > 0 && results.every((r) => r !== null));
    const score = $derived(results.filter((r) => r === true).length);

    const formattedTime = $derived.by(() => {
        const minutes = Math.floor(timeLeft / 60);
        const seconds = timeLeft % 60;
        return `${minutes}:${seconds.toString().padStart(2, '0')}`;
    });

    const startAnimation = () => {
        if (diceRolling) return;

        const rollTimeline = dice.rollTo(gameSession.targetLetter);
        if (!rollTimeline) return;

        const logoTimeline = logo.launch();

        createTimeline({ onComplete: startTimer })
            .sync(rollTimeline, 0)
            .sync(logoTimeline, 0)
            .add(categoryEls, {
                translateX: [-40, 0],
                opacity: [0, 1],
                delay: stagger(120),
                duration: 500,
                ease: 'outQuint'
            }, '+=200');
    }

    let gameSession = initGame()
    const inputs = Array.from({length: gameSession.targetCategories.length}, () => "")
    results = Array.from({length: gameSession.targetCategories.length}, () => null)

    function startTimer() {
        const timerId = setInterval(() => {
            timeLeft -= 1;

            if (timeLeft <= 0) {
                timeLeft = 0;
                clearInterval(timerId);
                finishGame();
            }
        }, 1000);
    }

    async function checkAnswer(category: string, guess: string) {
        if (!guess.trim()) return false;

        try {
            const response = await fetch("/api/check-answer", {
                method: "POST",
                headers: { "content-type": "application/json" },
                body: JSON.stringify({ category, guess })
            });

            if (!response.ok) return false;

            const data = await response.json();
            return Boolean(data.correct);
        } catch {
            return false;
        }
    }

    async function finishGame() {
        timeUp = true;

        results = await Promise.all(
            gameSession.targetCategories.map((category, index) =>
                checkAnswer(category.label, inputs[index])
            )
        );

        await tick();

        createTimeline()
            .add(resultEls, {
                opacity: [0, 1],
                scale: [0.4, 1],
                delay: stagger(150),
                duration: 400,
                ease: 'outBack'
            })
            .add(scoreSheet!, {
                opacity: [0, 1],
                translateY: [20, 0],
                duration: 500,
                ease: 'outQuint'
            });
    }

    function playAgain() {
        location.reload();
    }

    onMount(() => {
        startAnimation()
    })
</script>

<main>
    <Logo bind:this={logo}/>
    <Dice bind:this={dice} bind:letter={diceLetter} bind:isRolling={diceRolling} />

    <p class="timer">{formattedTime}</p>

    <div class="answers">
        {#each gameSession.targetCategories as category, index}
            <div class="category" bind:this={categoryEls[index]}>
                <p class="label">
                    {category.label}
                </p>
                {#if category.facts}
                    <p class="source">
                        {category.facts}
                    </p>
                {/if}
                <div class="input-box" style="--color: var(--color-{index % 5})">
                    <div
                        class="box"></div>
                    <input bind:value={inputs[index]} disabled={timeUp}/>
                    {#if results[index] !== null}
                        <span
                            class="result {results[index] ? 'correct' : 'incorrect'}"
                            bind:this={resultEls[index]}
                            >{results[index] ? '✓' : '✗'}</span
                        >
                    {/if}
                </div>
            </div>
        {/each}
    </div>

    {#if allChecked}
        <div class="score-sheet" bind:this={scoreSheet}>
            <p class="score">{score} / {gameSession.targetCategories.length} correct</p>
            <img src="/cat-win.png" alt=""/>
            <button onclick={playAgain}>Play again</button>
        </div>
    {/if}
</main>

<style>
    main {
        display: grid;
        justify-items: center;
        width: 100%;
        max-width: 500px;
        margin: 0 auto;
        padding: 3rem 1rem;
    }

    .timer {
        font-size: 1.5rem;
        font-weight: bold;
    }

    .answers {
        display: grid;
        gap: 1em;
        .category {
            opacity: 0;

            & .label {
                font-weight: bold;
            }
            & .source {
                color: var(--color-muted);
            }

            & .input-box {
                border: 2px solid var(--color);
                display: flex;
                align-items: center;

                &:has(input:focus-within) {
                    outline: 2px solid var(--color);
                }

                & .box {
                    width: 1em;
                    align-self: stretch;
                    background-color: var(--color);
                }

                & input {
                    padding: 1em;
                    height: 100%;
                    width: 100%;

                    outline: none;
                    color: var(--color);

                    &:disabled {
                        opacity: 0.6;
                    }
                }

                & .result {
                    opacity: 0;
                    padding: 0 1em;
                    font-weight: bold;

                    &.correct {
                        color: var(--color-0);
                    }

                    &.incorrect {
                        color: var(--color-4);
                    }
                }
            }
        }
    }

    .score-sheet {
        opacity: 0;
        display: grid;
        justify-items: center;
        gap: 1em;
        margin-top: 1em;

        & .score {
            font-size: 1.5rem;
            font-weight: bold;
        }

        & button {
            font: inherit;
            padding: 0.75em 2em;
            border: 2px solid var(--color-0);
            background: none;
            color: var(--color-0);
            cursor: pointer;
        }
    }
</style>
