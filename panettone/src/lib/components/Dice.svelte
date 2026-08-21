<script lang="ts">
    import { createTimeline } from 'animejs';

    let { isRolling = $bindable(false), letter = $bindable('a'), size = 200 } = $props();

    const ANGLE = 53;
    const RING_ANGLE = -11;
    const SIDE_ANGLE = 72;

    const SPIN_DURATION_MS = 3000;
    const LAND_DURATION_MS = 1300;
    const SPIN_DELTA = { x: 7_920, y: 1080, z: 360 };

    const faces: Record<number, string> = {
        1: "a",
        2: "b",
        3: "c",
        4: "d",
        5: "e",
        6: "f",
        7: "g",
        8: "h",
        9: "i",
        10: "j",
        11: "k",
        12: "l",
        13: "m",
        14: "n",
        15: "o",
        16: "p",
        17: "r",
        18: "s",
        19: "t",
        20: "w",
    } as const

    const rotation = { x: 0, y: 0, z: 0 };

    let diceElement: HTMLDivElement;

    function containerAngles(face: number) {
        if (face <= 5) {
            const m = face - 1;
            return { x: -ANGLE, y: SIDE_ANGLE * m, z: 0 };
        }
        if (face >= 16) {
            const m = face - 15;
            return { x: -ANGLE + 180, y: -SIDE_ANGLE * m, z: 0 };
        }
        if (face <= 10) {
            const m = face - 6;
            return { x: -RING_ANGLE, y: SIDE_ANGLE * m, z: 180 };
        }
        const m = face - 8;
        return { x: -RING_ANGLE, y: -SIDE_ANGLE * m - SIDE_ANGLE / 2, z: 0 };
    }

    function faceTransform(face: number) {
        if (face <= 5) {
            const m = face - 1;
            return `rotateY(${-SIDE_ANGLE * m}deg) translateZ(var(--translate-z)) translateY(var(--translate-y)) rotateX(${ANGLE}deg)`;
        }
        if (face >= 16) {
            const m = face - 18;
            return `rotateY(${SIDE_ANGLE * m + SIDE_ANGLE / 2}deg) translateZ(var(--translate-lower-z)) translateY(var(--translate-lower-y)) rotateZ(180deg) rotateX(${ANGLE}deg)`;
        }
        if (face <= 10) {
            const m = face - 11;
            return `rotateY(${-SIDE_ANGLE * m}deg) translateZ(var(--translate-ring-z)) translateY(var(--translate-ring-y)) rotateZ(180deg) rotateX(${RING_ANGLE}deg)`;
        }
        const m = face - 8;
        return `rotateY(${SIDE_ANGLE * m + SIDE_ANGLE / 2}deg) translateZ(var(--translate-ring-z)) translateY(var(--translate-ring-y)) rotateX(${RING_ANGLE}deg)`;
    }

    function randomFace(exclude: number) {
        let face;
        do {
            face = Math.floor(Math.random() * 20) + 1;
        } while (face === exclude);
        return face;
    }

    function faceForLetter(target: string) {
        const entry = Object.entries(faces).find(([, l]) => l === target);
        return entry ? Number(entry[0]) : 1;
    }

    function applyRotation() {
        diceElement.style.transform = `rotateX(${rotation.x}deg) rotateZ(${rotation.z}deg) rotateY(${rotation.y}deg)`;
    }

    export function rollTo(targetLetter: string) {
        if (isRolling) return;

        isRolling = true;
        letter = targetLetter;

        const face = faceForLetter(targetLetter);
        const targetAngles = containerAngles(face);
        const afterSpin = {
            x: rotation.x + SPIN_DELTA.x,
            y: rotation.y + SPIN_DELTA.y,
            z: rotation.z + SPIN_DELTA.z
        };

        const landDelta = {
            x: targetAngles.x - afterSpin.x,
            y: targetAngles.y - afterSpin.y,
            z: targetAngles.z - afterSpin.z
        };

        return createTimeline({
            onComplete: () => {
                isRolling = false;
            }
        })
            .add(rotation, {
                x: `+=${SPIN_DELTA.x}`,
                z: `+=${SPIN_DELTA.z}`,
                duration: SPIN_DURATION_MS,
                ease: 'linear',
                onUpdate: applyRotation
            })
            .add(rotation, {
                x: `+=${landDelta.x}`,
                y: `+=${landDelta.y}`,
                z: `+=${landDelta.z}`,
                duration: LAND_DURATION_MS,
                ease: 'outQuint',
                onUpdate: applyRotation
            });
    }
</script>

<div class="stage" style:--size="{size}px" role="button" tabindex="0">
    <div bind:this={diceElement}  class="die">
        {#each Object.entries(faces) as [face, faceLetter], index}
            {@const faceNumber = Number(face)}
            <figure
                class="face"
                class:selected={letter === faceLetter && !isRolling}
                style:transform={faceTransform(faceNumber)}>
                <span class="face-letter">{faceLetter}</span>
            </figure>
        {/each}
    </div>
</div>

<style>
    .stage {
        --face-w: calc(var(--size) * 0.5);
        --face-h: calc(var(--face-w) * 0.86);
        --translate-z: calc(var(--face-w) * 0.335);
        --translate-y: calc(var(--face-h) * -0.15);
        --translate-ring-z: calc(var(--face-w) * 0.75);
        --translate-ring-y: calc(var(--face-h) * 0.78 + var(--translate-y));
        --translate-lower-z: var(--translate-z);
        --translate-lower-y: calc(
            var(--face-h) * 0.78 + var(--translate-ring-y)
        );

        position: relative;
        width: var(--size);
        height: var(--size);
        perspective: calc(var(--size) * 7.5);
        cursor: pointer;
        user-select: none;

        &:focus-visible {
            outline: 2px solid var(--color-muted, #fff);
            outline-offset: 4px;
        }
    }

    .die {
        position: absolute;
        inset: 0;
        transform-style: preserve-3d;
    }

    .face {
        position: absolute;
        left: 50%;
        top: 0;
        margin: 0 calc(var(--face-w) * -0.5);
        border-left: calc(var(--face-w) * 0.5) solid transparent;
        border-right: calc(var(--face-w) * 0.5) solid transparent;
        border-bottom: var(--face-h) solid var(--color-3);
        width: 0;
        height: 0;
        transform-style: preserve-3d;
        backface-visibility: hidden;
        transition: border-bottom 400ms;

        &.selected {
            border-bottom: var(--face-h) solid var(--color-surface);

            & .face-letter {
                color: var(--color-3);
            }
        }

        & .face-letter {
            position: absolute;
            top: calc(var(--face-h) * 0.17);
            left: calc(var(--face-w) * -1);
            width: calc(var(--face-w) * 2);
            height: var(--face-h);
            font-size: calc(var(--face-h) * 0.5);
            line-height: calc(var(--face-h) * 0.9);
            text-align: center;
            color: var(--color-surface);
            transition: color 400ms;

        }
    }

</style>
