# MuAPI Example Workflows

Drop-in `*.json` workflows for the MuAPI ComfyUI node pack. Open ComfyUI → drag any
`.json` file onto the canvas (or use **Workflow → Load**).

> **API key:** every node has an empty `api_key` field. Run `muapi auth configure --api-key YOUR_KEY`
> once and all workflows pick up the key from `~/.muapi/config.json`. Or paste your key into
> any one node's `api_key` field per workflow.

## Text → Image
| Workflow | Model |
|---|---|
| `MuAPI_Basic_TextToImage_Flux.json` | flux-dev-image (great default) |
| `MuAPI_TextToImage_Imagen4.json` | google-imagen4-ultra |
| `MuAPI_TextToImage_Seedream5.json` | seedream-5.0 |
| `MuAPI_TextToImage_GPT_Image.json` | gpt-image-1.5 |
| `MuAPI_TextToImage_HiDream.json` | hidream_i1_full_image |

## Image → Image (edit)
| Workflow | Model |
|---|---|
| `MuAPI_ImageToImage_FluxKontext.json` | flux-kontext-pro-i2i |
| `MuAPI_ImageToImage_Seededit.json` | bytedance-seededit-image |
| `MuAPI_ImageToImage_GPT4o_Edit.json` | gpt4o-edit |

## Text → Video
| Workflow | Model |
|---|---|
| `MuAPI_TextToVideo_Seedance.json` | seedance-v2.0-t2v |
| `MuAPI_TextToVideo_Veo3.json` | veo3.1-text-to-video |
| `MuAPI_TextToVideo_Kling.json` | kling-v2.6-pro-t2v |

> **Wiring video into the saver:** the `MuAPIVideoSaver` node takes `video_url` as a
> string widget. After loading a T2V workflow, right-click the saver's `video_url`
> field → **Convert to input**, then drag a link from the T2V node's `video_url`
> output to the new input slot. (Some workflows already have this hooked up — see
> the `Chain_*` examples.)

## Image → Video
| Workflow | Notes |
|---|---|
| `MuAPI_ImageToVideo_Seedance.json` | LoadImage → Seedance i2v |
| `MuAPI_ImageToVideo_Veo3.json` | LoadImage → Veo 3.1 i2v |
| `MuAPI_ImageToVideo_4References.json` | 4 reference images → Seedance Omni |

## Video extend / edit
| Workflow | Notes |
|---|---|
| `MuAPI_ExtendVideo.json` | Generate then extend the same clip |
| `MuAPI_VideoEdit_Effects.json` | `video-effects` style transfer |
| `MuAPI_VideoUpscale_Topaz.json` | Topaz Labs video upscale |
| `MuAPI_Lipsync_Sync.json` | Sync.ai lipsync |

## Image enhance
| Workflow | Model |
|---|---|
| `MuAPI_FaceSwap.json` | ai-image-face-swap (2 inputs: base + face) |
| `MuAPI_Upscale_Topaz.json` | topaz-image-upscale (4×) |
| `MuAPI_BackgroundRemover.json` | ai-background-remover |
| `MuAPI_Ghibli_Style.json` | ai-ghibli-style |
| `MuAPI_ProductShot.json` | ai-product-shot |

## Audio
| Workflow | Model |
|---|---|
| `MuAPI_Audio_Suno.json` | suno-create-music |

## Chains (multi-step pipelines)
| Workflow | Pipeline |
|---|---|
| `MuAPI_Chain_T2I_to_I2V.json` | Flux 2 Pro → Veo 3.1 i2v |
| `MuAPI_Chain_I2I_then_Upscale.json` | Flux Kontext edit → Topaz 2× upscale |

## Generic / advanced
| Workflow | Notes |
|---|---|
| `MuAPI_Generic_RawJSON.json` | Call any endpoint with raw JSON + `__file_N__` placeholders |
| `MuAPI_ApiKey_Hub.json` | API Key node wired to a T2I — paste your key once |

## Regenerating
The `_generate_workflows.py` script regenerates every `.json` from a single spec
table. Edit it to add new examples and run:

```bash
python3 workflows/_generate_workflows.py
```
