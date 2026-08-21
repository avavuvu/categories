<script lang="ts">
	import favicon from '$lib/assets/favicon.ico';
	import "tailwindcss/preflight.css";
	import "./style.css"

	let { children } = $props();
</script>

<svelte:head>
	<link rel="icon" href={favicon} />
</svelte:head>

{@render children()}
