<script lang="ts">
	import { createEventDispatcher } from "svelte";
	import Copy from "./Copy.svelte";
	import Download from "./Download.svelte";
	import Clear from "./Clear.svelte"; 
	import { IconButtonWrapper } from "@gradio/atoms";
	export let value: string;
	export let show_download_button: boolean;
	export let show_copy_button: boolean;
	export let show_clear_button: boolean;
	const dispatch = createEventDispatcher();

</script>

<IconButtonWrapper>
	{#if show_clear_button}
		<Clear on:click={() => dispatch('clear')} />
	{/if}
	{#if show_copy_button}
		<Copy {value} />
	{/if}
	{#if show_download_button}
		<Download {value} />
	{/if}
</IconButtonWrapper>
