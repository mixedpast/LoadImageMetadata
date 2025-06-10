````markdown
# ComfyUI Metadata Reporter Toolkit

This repository contains **two interconnected custom nodes** designed to work together in ComfyUI to extract, parse, and display metadata from images—whether freshly generated or loaded from disk.

- 🔄 `LoadImageWithMetadata`: A smart loader that extracts embedded metadata from PNG images (or their paired `.json` files if needed).
- 📝 `FinalMetadataReporter`: A flexible reporter node that formats metadata for readable display, including model, prompts, resolution, LoRA, and other key workflow details.

---

## 📦 Included Nodes

### 1. `LoadImageWithMetadata`

Extracts metadata from:

- The most recently saved image
- A user-specified image file
- An incoming image input (with embedded metadata)

Returns both an `IMAGE` and a `DICT` containing parsed metadata.

### 2. `FinalMetadataReporter`

Receives metadata as `DICT` input and outputs a cleanly formatted report as a `STRING`, ready for preview or export.

Handles:

- Full workflow JSON parsing
- Raw image metadata
- Missing or malformed metadata gracefully

---

## 🔧 Requirements

- ComfyUI
- Python 3.8+
- `Pillow` (usually already bundled with ComfyUI)

---

## 💾 Installation

```bash
cd ComfyUI/custom_nodes/
git clone https://github.com/your-username/LoadImageMetadata.git
````

> This repo installs both nodes together. Restart ComfyUI after cloning.

---

## 🚀 Usage

### For Loaded Images:

1. Use the **`LoadImageWithMetadata`** node with:

   * `source_type = file` → to pick a file
   * or `source_type = direct_input` → to auto-load the most recent PNG

2. Pass its `metadata` output to **`FinalMetadataReporter`**

3. Preview the `metadata_text` string result.

### For Generated Images:

If your workflow outputs an image with embedded metadata:

* You can skip `LoadImageWithMetadata` and pass metadata directly to the reporter (optional, depending on structure).

---

## 📌 Example Workflow

```
LoadImageWithMetadata
        ⬇
   metadata (DICT)
        ⬇
FinalMetadataReporter
        ⬇
  metadata_text (STRING)
```

---

## 📍 Why Use Both?

These nodes were built as a **companion pair**:

* `LoadImageWithMetadata` ensures robust metadata extraction, even from older files or PNGs without full prompt info.
* `FinalMetadataReporter` provides rich formatting, workflow node parsing, LoRA detection, and even ControlNet/IPAdapter summaries.

---

## 🧪 Example Output

```
--- Workflow Metadata Report ---
Model: dreamshaper_8.safetensors
LoRAs:
  - more_details (Model: 0.6, CLIP: 0.6)
  - realistic_lighting (Model: 0.4, CLIP: 0.4)
Resolution: 512x768

Positive Prompt:
  portrait of a woman with blue eyes, detailed face, freckles, natural lighting, detailed skin

Negative Prompt:
  (Empty)

--- Sampler Details ---
Seed: 1234567890
Steps: 30
Sampler Name: euler_a
Cfg: 7.0
Denoise: 0.7
Scheduler: ddim
```

---

## 🙋 Troubleshooting

* **No Metadata Found?**

  * Ensure image was generated in ComfyUI or A1111 with metadata embedded.
  * Try direct mode in `LoadImageWithMetadata`.

* **Partial Metadata?**

  * The image may have been re-saved, stripping EXIF info.
  * Look for a `.json` file next to the image.

---

## 🤝 Contributing

PRs and improvements welcome. Open an issue or submit a pull request.

---

## 📜 License

MIT

---

If this toolkit helps your workflow, star the repo or share it with other ComfyUI users!
