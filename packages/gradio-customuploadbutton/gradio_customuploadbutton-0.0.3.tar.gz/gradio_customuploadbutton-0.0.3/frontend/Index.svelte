<script lang="ts" context="module">
	export { default as BaseUploadButton } from "./shared/UploadButton.svelte";
</script>

<script lang="ts">
	import type { Gradio } from "@gradio/utils";
	import { FileData } from "@gradio/client";
	import UploadButton from "./shared/UploadButton.svelte";
	import type { UploadResponse } from "@gradio/client";
	export let elem_id = "";
	export let elem_classes: string[] = [];
	export let visible = true;
	export let label: string | null;
	export let value: null | FileData | FileData[];
	export let file_count: string;
	export let file_types: string[] = [];
	export let root: string;
	export let size: "sm" | "lg" = "lg";
	export let scale: number | null = null;
	export let icon: FileData | null = null;
	export let min_width: number | undefined = undefined;
	export let variant: "primary" | "secondary" | "stop" = "secondary";
	export let gradio: Gradio<{
		change: never;
		upload: never;
		click: never;
		error: string;
	}>;
	export let interactive: boolean;

	$: disabled = !interactive;

	async function custom_upload_files(
		root_url: string,
		files: (Blob | File)[],
	): Promise<UploadResponse> {
		const chunkSize = 1000;
		const uploadResponses = [];
		for (let i = 0; i < files.length; i += chunkSize) {
			const file = files.slice(i, i + chunkSize);
			const formData = new FormData();
			file.forEach((element) => {
				formData.append("files", element);
			});
			const endpoint = `${root_url}/upload_files`;
			let res: Response;
			try {
				res = await fetch(endpoint, {
					method: "POST",
					body: formData,
				});
			} catch (e: any) {
				throw new Error(`Network error: ${e?.message ?? e}`);
			}
			if (!res.ok) {
				const errorText = await res.text();
				throw new Error(`Upload failed: ${errorText}`);
			}
			const jsonResponse = await res.json();
			const output: UploadResponse["files"] = jsonResponse["files"];
			if (output?.length) {
				uploadResponses.push(...output);
			}
		}
		return { files: uploadResponses };
	}

	async function customUpload(
		file_data: FileData[],
		root_url: string,
		upload_id?: string,
		max_file_size?: number,
	): Promise<(FileData | null)[] | null> {
		let files = (Array.isArray(file_data) ? file_data : [file_data]).map(
			(file_data) => file_data.blob!,
		);
		const oversized_files = files.filter(
			(f) => f.size > (max_file_size ?? Infinity),
		);
		if (oversized_files.length) {
			throw new Error(
				`File size exceeds the maximum allowed size of ${max_file_size} bytes: ${oversized_files
					.map((f) => f.name)
					.join(", ")}`,
			);
		}
		return await Promise.all(
			await custom_upload_files(root_url, files).then(
				async (response: { files?: string[]; error?: string }) => {
					if (response.error) {
						throw new Error(response.error);
					} else {
						if (response.files) {
							return response.files.map((f, i) => {
								const file = new FileData({
									...file_data[i],
									path: f,
									url: `${f}`,
								});
								return file;
							});
						}
						return [];
					}
				},
			),
		);
	}

	async function handle_event(
		detail: null | FileData | FileData[],
		event: "change" | "upload" | "click",
	): Promise<void> {
		value = detail;
		gradio.dispatch(event);
	}
</script>

<UploadButton
	{elem_id}
	{elem_classes}
	{visible}
	{file_count}
	{file_types}
	{size}
	{scale}
	{icon}
	{min_width}
	{root}
	{value}
	{disabled}
	{variant}
	{label}
	max_file_size={gradio.max_file_size}
	on:click={() => gradio.dispatch("click")}
	on:change={({ detail }) => handle_event(detail, "change")}
	on:upload={({ detail }) => handle_event(detail, "upload")}
	on:error={({ detail }) => {
		gradio.dispatch("error", detail);
	}}
	upload={(...args) => {
		return customUpload(...args);
	}}
>
	{label ?? ""}
</UploadButton>
