<!-- frontend/src/shared/LiveLogPanel.svelte -->

<script lang="ts">
    import { afterUpdate, createEventDispatcher } from "svelte";
    import { tick } from "svelte";
    import Widgets from "./Widgets.svelte";

    // -------------------------------------------------------------------------
    // Props received from the Gradio backend
    // -------------------------------------------------------------------------

    /** The incoming value from Gradio. Can be null (for clearing), an array, or a single object. */
    export let value: Record<string, any> | Array<Record<string, any>> | null = null;
    /** The height of the component. */
    export let height: number | string;
    /** Whether to automatically scroll to the latest log entry. */
    export let autoscroll: boolean;
    /** Whether to display line numbers next to log entries. */
    export let line_numbers: boolean;
    /** The background color of the log display area. */
    export let background_color: string;
    /** The current display mode: "full", "log", or "progress". */
    export let display_mode: "full" | "log" | "progress";
    /** Toggles the visibility of the download button. */
	export let show_download_button: boolean;
    /** Toggles the visibility of the copy button. */
	export let show_copy_button: boolean;
    /** Toggles the visibility of the clear button. */
	export let show_clear_button: boolean;
    
    const dispatch = createEventDispatcher();
    let log_container: HTMLElement;

    // -------------------------------------------------------------------------
    // Internal component state
    // -------------------------------------------------------------------------

    /** Holds the current state of the progress bar. */
    let progress = { visible: true, current: 0, total: 100, desc: "", percentage: 0, rate: 0.0, status: "running", rate_unit: 'it/s', extra_info:''};
    /** Accumulates all received log lines. */
    let log_lines: { level: string; content: string }[] = [];
    /** A plain text representation of all logs for the utility buttons. */
    let all_logs_as_text = "";
    /** A reactive variable to control the component's height. */
    let height_style: string;
    /** Stores the initial, fixed description sent from the backend for the progress bar. */
    let initial_desc: string = "Processing...";

    // -------------------------------------------------------------------------
    // Reactive Logic
    // -------------------------------------------------------------------------

    // Dynamically adjust the component's height style based on the display mode.
    $: {
        if (display_mode === 'progress' && progress.visible) {
            height_style = 'auto'; // Shrink to fit only the progress bar content.
        } else {
            height_style = typeof height === 'number' ? height + 'px' : height;
        }
    }

    // This is the core reactive block that processes incoming `value` updates from Gradio.
    // It uses a debounce to batch rapid updates and prevent UI flickering.
    let debounceTimeout: NodeJS.Timeout;
    $: {
        if (value !== null) {
            clearTimeout(debounceTimeout);
            debounceTimeout = setTimeout(async () => {
                if (value === null) {                    
                    log_lines = [];                    
                    progress = { 
                        visible: false, current: 0, total: 100, desc: "", percentage: 0, 
                        rate: 0.0, status: "running", rate_unit: 'it/s', extra_info: '' 
                    };
                    all_logs_as_text = "";
                    initial_desc = "Processing...";
                } else if (value) {
                    if (Array.isArray(value)) {
                        // Handles an initial state load if the backend provides a full list.
                        log_lines = [];
                        progress.visible = false;
                        for (const item of value) {
                            if (item.type === "log") {
                                log_lines = [...log_lines, { level: item.level || 'INFO', content: item.content }];
                            } else if (item.type === "progress") {
                                progress.visible = true;
                                progress.current = item.current;
                                progress.total = item.total || 100;
                                if (item.current === 0 && item.desc && initial_desc === "Processing...") {
                                    initial_desc = item.desc;
                                }
                                progress.desc = display_mode === "progress" && log_lines.length > 0 
                                    ? log_lines[log_lines.length - 1].content 
                                    : initial_desc;
                                progress.rate = item.rate || 0.0;                              
                                progress.rate_unit = item.rate_unit || 'it/s';
                                progress.extra_info = item.extra_info || '';
                                progress.percentage = progress.total > 0 ? ((item.current / progress.total) * 100) : 0;
                                progress.status = item.status || "running";
                            }
                        }
                    } else if (typeof value === 'object' && value.type) {                        
                        if (value.type === "log") {
                            log_lines = [...log_lines, { level: value.level || 'INFO', content: value.content }];
                        } else if (value.type === "progress") {
                            progress.visible = true;
                            progress.current = value.current;
                            progress.total = value.total || 100;
                            if (value.current === 0 && value.desc && initial_desc === "Processing...") {
                                initial_desc = value.desc;
                            }
                            progress.desc = display_mode === "progress" && log_lines.length > 0 
                                ? log_lines[log_lines.length - 1].content 
                                : initial_desc;
                            progress.rate = value.rate || 0.0;                            
                            progress.rate_unit = value.rate_unit || 'it/s';
                            progress.extra_info = value.extra_info || '';
                            progress.percentage = progress.total > 0 ? ((value.current / value.total) * 100) : 0;
                            progress.status = value.status || "running";
                            
                            log_lines = Array.isArray(value.logs) ? value.logs.map(log => ({
                                level: log.level || 'INFO',
                                content: log.content
                            })) : log_lines;
                        }
                    }
                    all_logs_as_text = log_lines.map(l => l.content).join('\n');
                }
                await tick();
            }, 50);
        }
    }

    // This lifecycle function runs after the DOM has been updated.
    afterUpdate(() => {
        if (autoscroll && log_container && display_mode !== 'progress') {
            // Scroll the log container to the bottom to show the latest entry.
            log_container.scrollTop = log_container.scrollHeight;
        }
    });
</script>

<div class="panel-container" style:height={height_style}>
    <!-- Conditionally render the log view based on the display_mode prop. -->
    <div class="log-view-container" style:display={display_mode === 'progress' ? 'none' : 'flex'}>
        <div class="header">
            <Widgets 
                bind:value={all_logs_as_text} 
                on:clear={() => dispatch('clear')}
                {show_download_button}
                {show_copy_button}
                {show_clear_button}
            />
        </div>
        <div class="log-panel" bind:this={log_container} style="background-color: {background_color};">
            {#each log_lines as log, i}
                <div class="log-line">
                    {#if line_numbers}<span class="line-number">{i + 1}</span>{/if}
                    <pre class="log-content log-level-{log.level.toLowerCase()}">{log.content}</pre>
                </div>
            {/each}
        </div>
    </div>

    <!-- Conditionally render the progress bar view. -->
    {#if progress.visible && (display_mode === 'full' || display_mode === 'progress')}
        <div class="progress-container">
            <div class="progress-label-top">
                <span>{progress.desc}</span>
                 <span class="rate-info">
                    {progress.rate.toFixed(2)} {progress.rate_unit}
                    {#if progress.extra_info}
                        <span class="extra-info">({progress.extra_info})</span>
                    {/if}
                </span> 
            </div>
            <div class="progress-bar-background">
                <!-- Conditionally apply CSS classes based on the progress status. -->
                <div 
                    class="progress-bar-fill" 
                    class:success={progress.status === 'success'}
                    class:error={progress.status === 'error'}
                    style="width: {progress.percentage.toFixed(1)}%;"
                ></div>
            </div>
            <div class="progress-label-bottom">
                <span>{Math.round(progress.percentage)}%</span>
                <span>{progress.current} / {progress.total}</span>
            </div>
        </div>
    {/if}
</div>

<style>
    .panel-container {
        display: flex;
        flex-direction: column;
        border: 1px solid var(--border-color-primary);
        border-radius: 0 !important;
        background-color: var(--background-fill-primary);
        overflow: hidden;
    }
    .log-view-container {
        display: flex;
        flex-direction: column;
        flex-grow: 1;
        min-height: 0;
    }
    .header {		
        border-bottom: 1px solid var(--border-color-primary);
        background-color: var(--background-fill-secondary);
        display: flex;
        justify-content: flex-end;
        flex-shrink: 0;
    }
    .log-panel {
        flex-grow: 1;
        font-family: var(--font-mono, monospace);
        font-size: var(--text-sm);
        overflow-y: auto;
        color: #f8f8f8;
    }
    .log-line { 
        display: flex; 
    }
    .line-number { 
        opacity: 0.6; 
        padding-right: var(--spacing-lg); 
        user-select: none; 
        text-align: right; 
        min-width: 3ch; 
    }
    .log-content { 
        margin: 0; 
        padding-left: 5px;
        white-space: pre-wrap; 
        word-break: break-word; 
    }
    
    /* Styles for different log levels */
    .log-level-info { color: inherit; }
    .log-level-debug { color: #888888; }
    .log-level-warning { color: #facc15; }
    .log-level-error { color: #ef4444; }
    .log-level-critical { 
        background-color: #ef4444; 
        color: white; 
        font-weight: bold; 
        padding: 0 0.25rem;
    }
    .log-level-success { color: #22c55e; }
    
    .progress-container { 
        padding: var(--spacing-sm) var(--spacing-md); 
        border-top: 1px solid var(--border-color-primary); 
        background: var(--background-fill-secondary);
    }
    .progress-label-top, .progress-label-bottom {
        display: flex;
        justify-content: space-between;
        font-size: var(--text-sm);
        color: var(--body-text-color-subdued);
    }
    .progress-label-top {
        margin-bottom: var(--spacing-xs);
    }
    .progress-label-bottom {
        margin-top: var(--spacing-xs);
    }
    .progress-bar-background { 
        width: 100%; 
        height: 8px; 
        background-color: var(--background-fill-primary); 
        border-radius: var(--radius-full); 
        overflow: hidden; 
    }
    .progress-bar-fill { 
        height: 100%; 
        background-color: var(--color-accent); /* Default "running" color */
        border-radius: var(--radius-full); 
        transition: width 0.1s linear, background-color 0.3s ease;
    }

    /* Styles for different progress bar statuses */
    .progress-bar-fill.success {
        background-color: var(--color-success, #22c55e);
    }
    .progress-bar-fill.error {
        background-color: var(--color-error, #ef4444);
    }
    .rate-info {
        display: flex;
        align-items: center;
        gap: 0.5ch;
    }
    .extra-info {
        color: var(--body-text-color-subdued); 
        font-size: 0.9em;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
        max-width: 200px;
    }
</style>