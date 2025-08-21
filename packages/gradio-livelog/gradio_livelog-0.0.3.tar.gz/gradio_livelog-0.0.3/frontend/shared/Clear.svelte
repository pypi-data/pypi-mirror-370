<script lang="ts">
    import { createEventDispatcher } from "svelte";
    import { Trash } from "@gradio/icons";
    import { IconButton } from "@gradio/atoms";
    const dispatch = createEventDispatcher();
</script>

<IconButton Icon={Trash} on:click={() => dispatch('click')} />