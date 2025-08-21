<!-- frontend/src/shared/Download.svelte -->
<script lang="ts">
	import { Download } from "@gradio/icons";
	import { DownloadLink } from "@gradio/wasm/svelte";
	import { IconButton } from "@gradio/atoms";

	export let value: string;
	
	let download_value: string;
	$: if (value) download_value = URL.createObjectURL(new Blob([value]));
</script>

<DownloadLink
	download="logs.txt"
	href={download_value}
>
	<IconButton Icon={Download} />
</DownloadLink>