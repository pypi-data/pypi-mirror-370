<svelte:options accessors={true} />

<script context="module" lang="ts">
    /**
     * Exports base components for reuse.
     */
    export { default as BaseImageUploader } from "./shared/ImageUploader.svelte";
    export { default as BaseStaticImage } from "./shared/ImagePreview.svelte";
    export { default as BaseExample } from "./Example.svelte";
    export { default as BaseImage } from "./shared/Image.svelte";
</script>

<script lang="ts">
    import type { Gradio, SelectData, ShareData } from "@gradio/utils";
    import StaticImage from "./shared/ImagePreview.svelte";
    import ImageUploader from "./shared/ImageUploader.svelte";
    import { afterUpdate } from "svelte";
    import { Block, Empty, UploadText } from "@gradio/atoms";
    import { Image } from "@gradio/icons";
    import { StatusTracker } from "@gradio/statustracker";
    import { upload, type FileData } from "@gradio/client";
    import type { LoadingStatus } from "@gradio/statustracker";

    type sources = "upload";

    /**
     * Props for the Index component.
     */
    export let value_is_output: boolean = false; // Whether the component is used as an output.
    export let elem_id: string = ""; // HTML element ID for the component.
    export let elem_classes: string[] = []; // HTML element classes for the component.
    export let visible: boolean = true; // Whether the component is visible.
    export let value: null | FileData = null; // Image data with URL and optional metadata.
    export let label: string; // Label displayed above the component.
    export let show_label: boolean; // Whether to display the label.
    export let show_download_button: boolean; // Whether to show the download button (for StaticImage).
    export let root: string; // Root URL for file uploads.
    export let only_custom_metadata: boolean = true; // Whether to filter out technical metadata.
    export let popup_metadata_width: number | string = 400; // Width of the metadata popup (pixels or CSS units).
    export let popup_metadata_height: number | string = 300; // Height of the metadata popup (pixels or CSS units).
    export let height: number | undefined; // Component height (pixels).
    export let width: number | undefined; // Component width (pixels).
    export let _selectable: boolean = false; // Whether the image is clickable for coordinate selection.
    export let container: boolean = true; // Whether to wrap the component in a container.
    export let scale: number | null = null; // Relative size compared to adjacent components.
    export let min_width: number | undefined = undefined; // Minimum width in pixels.
    export let loading_status: LoadingStatus; // Status of loading operations (e.g., upload, error).
    export let show_share_button: boolean = false; // Whether to show the share button (for StaticImage).
    export let sources: sources[] = ["upload"]; // Input sources (only "upload" supported).
    export let interactive: boolean; // Whether the component allows image uploads.
    export let pending: boolean; // Whether an operation is pending.
    export let placeholder: string | undefined = undefined; // Placeholder text for the upload area.
    export let show_fullscreen_button: boolean; // Whether to show the fullscreen button.
    export let gradio: Gradio<{
        input: never;
        change: never;
        error: string;
        edit: never;
        drag: never;
        upload: never;
        clear: never;
        select: SelectData;
        share: ShareData;
        clear_status: LoadingStatus;
        load_metadata: never;
    }>; // Gradio interface for event dispatching.

    let old_value: null | FileData = null; // Previous value for change detection.
    let fullscreen: boolean = false; // Whether the image is in fullscreen mode.
    let uploading: boolean = false; // Whether an upload is in progress.
    $: input_ready = !uploading; // Whether the input is ready (not uploading).
    let dragging: boolean; // Whether a file is being dragged over the component.
    let active_source: sources = "upload"; // Current input source (only "upload" supported).
    let upload_component: ImageUploader; // Reference to the ImageUploader component.

    // Reactive: Detects value changes and dispatches events.
    $: {
        if (JSON.stringify(value) !== JSON.stringify(old_value)) {
            old_value = value;
            gradio.dispatch("change");
            if (!value_is_output) {
                gradio.dispatch("input");
            }
        }
    }

    /**
     * Resets value_is_output after component updates.
     */
    afterUpdate(() => {
        value_is_output = false;
    });

    /**
     * Handles drag events to update dragging state.
     * @param event - Drag event (dragenter, dragover, dragleave).
     */
    const handle_drag_event = (event: Event): void => {
        const drag_event = event as DragEvent;
        drag_event.preventDefault();
        drag_event.stopPropagation();
        if (drag_event.type === "dragenter" || drag_event.type === "dragover") {
            dragging = true;
        } else if (drag_event.type === "dragleave") {
            dragging = false;
        }
    };

    /**
     * Handles file drop to initiate upload via ImageUploader.
     * @param event - Drag event containing dropped files.
     */
    const handle_drop = (event: Event): void => {
        if (interactive) {
            const drop_event = event as DragEvent;
            drop_event.preventDefault();
            drop_event.stopPropagation();
            dragging = false;

            if (upload_component) {
                upload_component.loadFilesFromDrop(drop_event);
            }
        }
    };

    /**
     * Dispatches the load_metadata event when triggered by child components.
     */
    function handle_load_metadata(): void {
        gradio.dispatch("load_metadata");
    }
</script>

{#if !interactive}
    <Block
        {visible}
        variant={"solid"}
        border_mode={dragging ? "focus" : "base"}
        padding={false}
        {elem_id}
        {elem_classes}
        height={height || undefined}
        {width}
        allow_overflow={false}
        {container}
        {scale}
        {min_width}
        bind:fullscreen
    >
        <StatusTracker
            autoscroll={gradio.autoscroll}
            i18n={gradio.i18n}
            {...loading_status}
        />
        <StaticImage
            on:select={({ detail }) => gradio.dispatch("select", detail)}
            on:share={({ detail }) => gradio.dispatch("share", detail)}
            on:error={({ detail }) => gradio.dispatch("error", detail)}
            on:load_metadata={handle_load_metadata}
            on:fullscreen={({ detail }) => {
                fullscreen = detail;
            }}
            {fullscreen}
            {value}
            {label}
            {show_label}
            {show_download_button}
            selectable={_selectable}
            {show_share_button}
            i18n={gradio.i18n}
            {show_fullscreen_button}
            {only_custom_metadata}
            {popup_metadata_width}
            {popup_metadata_height}
        />
    </Block>
{:else}
    <Block
        {visible}
        variant={value === null ? "dashed" : "solid"}
        border_mode={dragging ? "focus" : "base"}
        padding={false}
        {elem_id}
        {elem_classes}
        height={height || undefined}
        {width}
        allow_overflow={false}
        {container}
        {scale}
        {min_width}
        bind:fullscreen
        on:dragenter={handle_drag_event}
        on:dragleave={handle_drag_event}
        on:dragover={handle_drag_event}
        on:drop={handle_drop}
    >
        <StatusTracker
            autoscroll={gradio.autoscroll}
            i18n={gradio.i18n}
            {...loading_status}
            on:clear_status={() => gradio.dispatch("clear_status", loading_status)}
        />

        <ImageUploader
            bind:this={upload_component}
            bind:uploading
            bind:active_source
            bind:value
            bind:dragging
            selectable={_selectable}
            {root}
            {sources}
            {fullscreen}
            on:edit={() => gradio.dispatch("edit")}
            on:clear={() => {
                gradio.dispatch("clear");
            }}
            on:drag={({ detail }) => (dragging = detail)}
            on:upload={() => gradio.dispatch("upload")}
            on:select={({ detail }) => gradio.dispatch("select", detail)}
            on:share={({ detail }) => gradio.dispatch("share", detail)}
            on:load_metadata={handle_load_metadata}
            on:error={({ detail }) => {
                loading_status = loading_status || {};
                loading_status.status = "error";
                gradio.dispatch("error", detail);
            }}
            on:fullscreen={({ detail }) => {
                fullscreen = detail;
            }}
            {label}
            {show_label}
            {pending}
            {show_fullscreen_button}
            max_file_size={gradio.max_file_size}
            i18n={gradio.i18n}
            upload={(...args) => gradio.client.upload(...args)}
            stream_handler={gradio.client?.stream}
            {only_custom_metadata}
            {popup_metadata_width}
            {popup_metadata_height}
        >
            <UploadText i18n={gradio.i18n} type="image" {placeholder} />
        </ImageUploader>
    </Block>
{/if}