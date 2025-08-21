<!-- frontend/src/index.svelte -->

<script lang="ts">
	import type { Gradio } from "@gradio/utils";
	import { Block, BlockLabel } from "@gradio/atoms";	
	import { StatusTracker } from "@gradio/statustracker";
	import TerminalIcon   from "./icons/TerminalIcon.svelte";
	import type { LoadingStatus } from "@gradio/statustracker";
	import LiveLogPanel from "./shared/LiveLogPanel.svelte";

	export let gradio: Gradio<{ change: any, clear: any }>;
	export let value: Array<Record<string, any>> | null = null;
	export let label: string;
	export let height: number | string;
	export let autoscroll: boolean;
	export let line_numbers: boolean;
	export let background_color: string;
	export let display_mode: "full" | "log" | "progress";
	export let visible = true;
	export let show_label = true;
	export let show_download_button: boolean;
	export let show_copy_button: boolean;
	export let show_clear_button: boolean;
	export let elem_id = "";
	export let elem_classes: string[] = [];
	export let scale: number | null = null;
	export let min_width: number | undefined = undefined;
	export let loading_status: LoadingStatus;
</script>

<Block {visible} {elem_id} {elem_classes} {scale} {min_width} allow_overflow={false}>
	{#if show_label}
		<div class="block-label-wrapper">			
			<BlockLabel Icon={TerminalIcon} {show_label} {label} />
		</div>
	{/if}
	<StatusTracker {loading_status} autoscroll={gradio.autoscroll} i18n={gradio.i18n}/>
	
	<LiveLogPanel
		{value}
		{height}
		{autoscroll}
		{line_numbers}
		{background_color}
		{display_mode}
		{show_download_button} 
		{show_copy_button}
		{show_clear_button}
		on:clear={() => gradio.dispatch("clear")}
	/>
</Block>
<style>
	.block-label-wrapper {		
		padding-bottom: 24px; 
	}
</style>