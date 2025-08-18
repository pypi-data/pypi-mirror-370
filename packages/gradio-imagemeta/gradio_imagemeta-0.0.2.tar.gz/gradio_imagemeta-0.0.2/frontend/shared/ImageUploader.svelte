<script lang="ts">
    import { createEventDispatcher, tick } from "svelte";
    import { BlockLabel, IconButtonWrapper, IconButton } from "@gradio/atoms";
    import { Clear, Image as ImageIcon, Info } from "@gradio/icons";
    import { FullscreenButton } from "@gradio/atoms";
    import { Upload } from "@gradio/upload";
    import type { Client } from "@gradio/client";
    import Image from "./Image.svelte";
    import * as exifr from "exifr";
    import { get_coordinates_of_clicked_image } from "./utils";

    /**
     * Props for the ImageUploader component.
     */
    export let value: null | any = null; // Image data with URL, path, and optional metadata.
    export let label: string | undefined = undefined; // Label displayed above the component.
    export let show_label: boolean; // Whether to display the label.
    export let selectable: boolean = false; // Whether the image is clickable for coordinate selection.
    export let root: string; // Root URL for file uploads.
    export let i18n: any; // Formatter for internationalization.
    export let max_file_size: number | null = null; // Maximum file size for uploads (in bytes).
    export let upload: Client["upload"]; // Function to handle file uploads.
    export let stream_handler: Client["stream"]; // Function to handle webcam streaming.
    export let show_fullscreen_button: boolean = true; // Whether to show the fullscreen button.
    export let height: number | string | undefined = undefined; // Component height (pixels or CSS units).
    export let width: number | string | undefined = undefined; // Component width (pixels or CSS units).
    export let only_custom_metadata: boolean = true; // Whether to filter out technical metadata.
    export let popup_metadata_width: number | string = 400; // Width of the metadata popup (pixels or CSS units).
    export let popup_metadata_height: number | string = 300; // Height of the metadata popup (pixels or CSS units).

    let upload_input: Upload; // Reference to the Upload component.
    export let uploading: boolean = false; // Whether an upload is in progress.
    export let active_source: "upload" = "upload"; // Current input source (only "upload" supported).
    export let fullscreen: boolean = false; // Whether the image is in fullscreen mode.
    let metadata: Record<string, any> | null = null; // Extracted image metadata.
    let showMetadataPopup: boolean = false; // Whether the metadata popup is visible.
    let image_container: HTMLElement; // Reference to the image container element.
    export let dragging: boolean = false; // Whether a file is being dragged over the component.

    // Event dispatcher for component events.
    const dispatch = createEventDispatcher<{
        change?: never; // Triggered when the image changes.
        clear?: never; // Triggered when the image is cleared.
        drag: boolean; // Triggered when dragging state changes.
        upload?: never; // Triggered after a successful upload.
        select: any; // Triggered when clicking the image with coordinates.
        load_metadata: never; // Triggered when loading metadata.
    }>();

    // Reactive: Dispatches drag event when dragging state changes.
    $: dispatch("drag", dragging);

    // List of technical metadata keys to filter out when only_custom_metadata is true.
    const technicalMetadata: string[] = [
        "ImageWidth",
        "ImageHeight",
        "BitDepth",
        "ColorType",
        "Compression",
        "Filter",
        "Interlace"
    ];

    // Reactive: Filters metadata based on only_custom_metadata.
    $: filteredMetadata = only_custom_metadata
        ? Object.fromEntries(
              Object.entries(metadata || {}).filter(([key]) => !technicalMetadata.includes(key))
          )
        : metadata;

    // Reactive: Calculates maximum popup width based on component width.
    $: maxPopupWidth = typeof width === 'number' ? width - 20 : typeof width === 'string' ? `calc(${width} - 20px)` : '380px';

    // Reactive: Extracts metadata when value changes (e.g., from gr.Examples).
    $: if (value) {
        // Use preloaded metadata if available, otherwise extract from URL
        if (value.metadata) {
            metadata = value.metadata;
        } else {
            extractMetadata(value);
        }
    } else {
        metadata = null;
    }

    /**
     * Extracts metadata from the image file.
     * @param fileData - Image data containing the URL or path.
     */
    async function extractMetadata(fileData: any): Promise<void> {
        if (!fileData?.url) {
            metadata = null;
            return;
        }

        if (fileData.url.toLowerCase().endsWith(".svg")) {
            metadata = null;
        } else if (
            fileData.url.toLowerCase().endsWith(".png") ||
            fileData.url.toLowerCase().endsWith(".jpg") ||
            fileData.url.toLowerCase().endsWith(".jpeg")
        ) {
            try {
                const exifData = await exifr.parse(fileData.url, {
                    exif: true,
                    iptc: true,
                    xmp: true,
                });
                metadata = {};
                if (exifData) {
                    for (const [key, value] of Object.entries(exifData)) {
                        if (typeof value === "string" || typeof value === "number" || typeof value === "boolean") {
                            metadata[key] = value;
                        }
                    }
                }
            } catch (error) {
                metadata = { error: "Failed to extract metadata" };
            }
        } else {
            metadata = { error: "Unsupported file type" };
        }
    }

    /**
     * Handles file upload and extracts metadata for supported image formats.
     * @param event - Custom event containing uploaded file data.
     */
    async function handle_upload({ detail }: CustomEvent<any>): Promise<void> {
        let extractedMetadata = null;
        if (detail.path?.toLowerCase().endsWith(".svg") && detail.url) {
            const response = await fetch(detail.url);
            const svgContent = await response.text();
            value = {
                ...detail,
                url: `data:image/svg+xml,${encodeURIComponent(svgContent)}`,
                metadata: null
            };
            extractedMetadata = null;
        } else if (
            detail.url &&
            (detail.path?.toLowerCase().endsWith(".png") ||
                detail.path?.toLowerCase().endsWith(".jpg") ||
                detail.path?.toLowerCase().endsWith(".jpeg"))
        ) {
            try {
                const exifData = await exifr.parse(detail.url, {
                    exif: true,
                    iptc: true,
                    xmp: true,
                });
                extractedMetadata = {};
                if (exifData) {
                    for (const [key, value] of Object.entries(exifData)) {
                        if (typeof value === "string" || typeof value === "number" || typeof value === "boolean") {
                            extractedMetadata[key] = value;
                        }
                    }
                }
            } catch (error) {
                extractedMetadata = { error: "Failed to extract metadata" };
            }
        } else {
            extractedMetadata = { error: "Unsupported file type" };
        }

        value = {
            ...detail,
            metadata: extractedMetadata
        };
        metadata = extractedMetadata;
        await tick();
        dispatch("upload");
        dispatch("change", value);
    }

    /**
     * Clears the current image and metadata.
     */
    function handle_clear(): void {
        value = null;
        metadata = null;
        showMetadataPopup = false;
        dispatch("clear");
        dispatch("change", null);
    }

    /**
     * Handles image click to dispatch select event with coordinates.
     * @param evt - Mouse event from clicking the image.
     */
    function handle_click(evt: MouseEvent): void {
        let coordinates = get_coordinates_of_clicked_image(evt);
        if (coordinates) {
            dispatch("select", { index: coordinates, value: null });
        }
    }

    /**
     * Handles drag-over event to enable file drop.
     * @param evt - Drag event.
     */
    function on_drag_over(evt: DragEvent): void {
        evt.preventDefault();
        evt.stopPropagation();
        if (evt.dataTransfer) {
            evt.dataTransfer.dropEffect = "copy";
        }
        dragging = true;
    }

    /**
     * Handles file drop to initiate upload.
     * @param evt - Drag event containing dropped files.
     */
    async function on_drop(evt: DragEvent): Promise<void> {
        evt.preventDefault();
        evt.stopPropagation();
        dragging = false;

        if (value) {
            handle_clear();
            await tick();
        }

        active_source = "upload";
        await tick();
        upload_input.load_files_from_drop(evt);
    }

    /**
     * Toggles the visibility of the metadata popup.
     */
    function toggleMetadataPopup(): void {
        if (metadata !== null) {
            showMetadataPopup = !showMetadataPopup;
        }
    }

    /**
     * Dispatches the load_metadata event and closes the popup.
     */
    function dispatchLoadMetadata(): void {
        if (metadata !== null) {
            dispatch("load_metadata");
            closePopup();
        }
    }

    /**
     * Closes the metadata popup.
     */
    function closePopup(): void {
        showMetadataPopup = false;
    }
</script>

<BlockLabel {show_label} Icon={ImageIcon} label={label || "Image"} />

<div data-testid="image" class="image-container" bind:this={image_container} style:height style:width>
    <IconButtonWrapper>
        {#if value?.url}
            {#if show_fullscreen_button}
                <FullscreenButton {fullscreen} on:fullscreen />
            {/if}
            {#if metadata !== null}
                <IconButton
                    Icon={Info}
                    label="View Metadata"
                    aria-label="View and send image metadata"
                    on:click={(event) => {
                        toggleMetadataPopup();
                        event.stopPropagation();
                    }}
                />
            {/if}
            <IconButton
                Icon={Clear}
                label="Remove Image"
                on:click={(event) => {
                    handle_clear();
                    event.stopPropagation();
                }}
            />
        {/if}
    </IconButtonWrapper>
    <!-- svelte-ignore a11y-no-static-element-interactions -->
    <div
        class="upload-container"
        style:width={value ? "auto" : "100%"}
        on:dragover={on_drag_over}
        on:drop={on_drop}
    >
        <Upload
            hidden={value !== null}
            bind:this={upload_input}
            bind:uploading
            bind:dragging
            filetype="image/*"
            on:load={handle_upload}
            on:error
            {root}
            {max_file_size}
            disable_click={value !== null}
            {upload}
            {stream_handler}
            aria_label={i18n("image.drop_to_upload")}
        >
            {#if value === null}
                <slot />
            {/if}
        </Upload>
        {#if value !== null}
            <!-- svelte-ignore a11y-click-events-have-key-events-->
            <!-- svelte-ignore a11y-no-static-element-interactions-->
            <div class:selectable class="image-frame" on:click={handle_click}>
                <Image src={value.url} alt={value.alt_text} />
            </div>
        {/if}
    </div>
</div>

{#if showMetadataPopup && filteredMetadata !== null}
    <div
        class="metadata-popup"
        style:width={typeof popup_metadata_width === 'number' ? `${Math.min(popup_metadata_width, parseFloat(maxPopupWidth))}px` : `min(${popup_metadata_width}, ${maxPopupWidth})`}
        style:height={typeof popup_metadata_height === 'number' ? `${popup_metadata_height}px` : popup_metadata_height}
    >
        <div class="popup-content">
            <button class="close-button" on:click={closePopup}>X</button>
            <h3 class="popup-title">Image Metadata</h3>
            {#if filteredMetadata.error}
                <p>{filteredMetadata.error}</p>
            {:else}
                <div class="metadata-table-container">
                    <table class="metadata-table">
                        <tbody>
                            {#each Object.entries(filteredMetadata) as [key, val]}
                                {#if val}
                                    <tr>
                                        <td class="metadata-label">{key}</td>
                                        <td class="metadata-value">{val}</td>
                                    </tr>
                                {/if}
                            {/each}
                        </tbody>
                    </table>
                </div>
                <button class="load-metadata-button" on:click={dispatchLoadMetadata}>Load Metadata</button>
            {/if}
        </div>
    </div>
{/if}

<style>
    .image-frame :global(img) {
        width: var(--size-full);
        height: var(--size-full);
        object-fit: scale-down;
    }

    .upload-container {
        display: flex;
        align-items: center;
        justify-content: center;
        height: 100%;
        flex-shrink: 1;
        max-height: 100%;
    }

    .image-container {
        display: flex;
        height: 100%;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        max-height: 100%;
        position: relative;
    }

    .selectable {
        cursor: crosshair;
    }

    .image-frame {
        object-fit: cover;
        width: 100%;
        height: 100%;
    }

    .metadata-popup {
        position: absolute;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        background: var(--background-fill-primary, white);
        border: 1px solid var(--border-color-primary);
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
        z-index: 1000;
        border-radius: 8px;
        overflow: hidden;
    }

    .popup-content {
        position: relative;
        padding: 1rem;
        display: flex;
        flex-direction: column;
        height: 100%;
    }

    .popup-title {
        font-weight: bold;
        margin: 0 0 1rem 0;        
    }

    .close-button {
        position: absolute;
        top: 0.5rem;
        right: 0.5rem;
        background: none;
        border: none;
        font-size: 1rem;
        cursor: pointer;        
    }

    .metadata-table-container {
        flex: 1;
        overflow: auto;
    }

    .metadata-table {
        width: 100%;
        border-collapse: collapse;
    }

    .metadata-label {
        background: var(--background-fill-secondary, #f5f5f5);
        padding: 0.5rem;
        font-weight: bold;
        text-align: left;
        vertical-align: top;
        width: 40%;
    }

    .metadata-value {
        padding: 0.5rem;
        white-space: nowrap;
        vertical-align: top;
    }

    .load-metadata-button {
        margin-top: 1rem;
        padding: 0.5rem 1rem;
        background-color: var(--button-primary-border-color);
        color: var(--button-primary-text-color);
        border: none;
        border-radius: 4px;
        cursor: pointer;
        align-self: center;
    }

    .load-metadata-button:hover {
        background-color: var(--button-primary-background-fill-hover);
    }
</style>