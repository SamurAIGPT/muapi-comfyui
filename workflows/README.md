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

## Skill workflows
Each `MuAPI_Skill_*.json` mirrors one of the agent skills under
`muapiapp/skills/library/` so you get a working ComfyUI starting point for the
same pipeline.

### Visual / images
| Workflow | Skill / model |
|---|---|
| `MuAPI_Skill_NanoBanana.json` | nano-banana-pro (Gemini-3 style brief) |
| `MuAPI_Skill_NanoBanana2.json` | nano-banana-2 (reasoning-driven T2I) |
| `MuAPI_Skill_LogoGenerator.json` | flux-2-pro single-shot logo |
| `MuAPI_Skill_LogoBranding_Ideogram.json` | ideogram-v3-t2i + nano-banana-pro |
| `MuAPI_Skill_YouTubeThumbnail.json` | gpt-image-2-text-to-image, high-CTR |
| `MuAPI_Skill_BlogHeader.json` | gpt-image-2 banner 1200×628 |
| `MuAPI_Skill_InstagramPost.json` | nano-banana-2 square hero |
| `MuAPI_Skill_RedNoteCover.json` | bytedance-seedream-v4.5 RedNote/小红书 |
| `MuAPI_Skill_KeyboardArt.json` | ideogram-v3-t2i text-on-keycaps |
| `MuAPI_Skill_AdCreative.json` | nano-banana-pro 4:5 ad creative |
| `MuAPI_Skill_BrandKit.json` | 3-frame brand kit (logo + palette + type) |
| `MuAPI_Skill_Storyboard.json` | 3 keyframes via nano-banana-2 |
| `MuAPI_Skill_AmazonListing.json` | ai-product-shot + ai-product-photography |
| `MuAPI_Skill_MultiAngleShots.json` | nano-banana-2-edit × 3 angles |
| `MuAPI_Skill_MultiAngleReshoot.json` | nano-banana-pro-edit lens reshoot |
| `MuAPI_Skill_PhotoPackGenerator.json` | `photo-pack` identity-lock |
| `MuAPI_Skill_ActionFigure.json` | nano-banana-2-edit collectible packshot |
| `MuAPI_Skill_FashionTryOn.json` | qwen-image-edit-plus → seedance i2v |
| `MuAPI_Skill_UGCLifestyleTryOn.json` | ai-dress-change → kling-v3.0 i2v |
| `MuAPI_Skill_SelfieWithCelebrity.json` | nano-banana-2-edit → veo3.1 i2v |
| `MuAPI_Skill_FloorPlanRendering.json` | nano-banana-2-edit 2D→3D plan |
| `MuAPI_Skill_InteriorDesign.json` | flux-kontext redesign → kling i2v |
| `MuAPI_Skill_InteriorVisualizer.json` | gpt-image-2 empty → nano-banana furnish |
| `MuAPI_Skill_CoupleGrid.json` | qwen-image-edit-plus 6-cell grid |
| `MuAPI_Skill_Brochure.json` | seedream-v4.5 cover + spread |
| `MuAPI_Skill_UrlToDesign.json` | gpt4o-edit website redesign |
| `MuAPI_Skill_DesignGuide.json` | 3-page brand design system |
| `MuAPI_Skill_SocialPack.json` | nano-banana-2-edit reframe (IG/TT/X) |

### Motion / video
| Workflow | Skill / model |
|---|---|
| `MuAPI_Skill_Seedance2_T2V.json` | seedance-2-text-to-video director brief |
| `MuAPI_Skill_Seedance2_OmniReference.json` | seedance-2.0-omni-reference (3 refs) |
| `MuAPI_Skill_Seedance2_FirstLastFrame.json` | seedance-2-first-last-frame |
| `MuAPI_Skill_CinemaDirector.json` | kling-v3.0-pro-image-to-video |
| `MuAPI_Skill_DroneStyleVideo.json` | veo3.1 aerial drone t2v |
| `MuAPI_Skill_OneShotVideo.json` | veo3.1-i2v continuous single-take |
| `MuAPI_Skill_3DLogoAnimation.json` | nano-banana-2-edit → veo3.1-fast-i2v |
| `MuAPI_Skill_AnimalVideoGenerator.json` | anthropomorphic vlogger animal |
| `MuAPI_Skill_CartoonDance.json` | nano-banana-2-edit → kling motion-control |
| `MuAPI_Skill_CharacterStoryVideo.json` | nano + flux-kontext + kling chain |
| `MuAPI_Skill_GiantProductShowcase.json` | scale product to building size |
| `MuAPI_Skill_JewelryProductVideo.json` | luxury macro orbit (grok-imagine) |
| `MuAPI_Skill_MusicVideo.json` | keyframe → veo3.1 + suno-create-music |
| `MuAPI_Skill_ProductAdCinematic.json` | nano-banana-2 → kling-v3.0-standard |
| `MuAPI_Skill_ProductShowcaseVideo.json` | seedream-edit → seedance i2v |
| `MuAPI_Skill_ProductVideoAdMaker.json` | flux-2-pro-edit → wan2.5 i2v |
| `MuAPI_Skill_TalkingBabyVideo.json` | wan2.5 baby → grok-imagine i2v |
| `MuAPI_Skill_AiFightScene.json` | gpt-image-2 16-cell board → seedance i2v |
| `MuAPI_Skill_UGCAdsWorkflow.json` | gpt-image-2 UGC scene → veo3.1 |
| `MuAPI_Skill_SocialMediaVideo.json` | imagen4 hero → veo3.1 parallax |

### Edit / clipping
| Workflow | Skill / model |
|---|---|
| `MuAPI_Skill_AiClipping.json` | `ai-clipping` viral 9:16 detection |
| `MuAPI_Skill_YoutubeShorts.json` | `ai-clipping` with `num_clips`/duration |
| `MuAPI_Skill_ProductCampaign.json` | multi-stage campaign (image + video) |

### 3D
| Workflow | Skill / model |
|---|---|
| `MuAPI_Skill_ImageTo3D_Tripo.json` | tripo3d-p1-image-to-3d (textured asset) |
| `MuAPI_Skill_TextTo3D_Meshy.json` | meshy-6-text-to-3d (game-ready PBR) |

## Regenerating
The `_generate_workflows.py` script regenerates every `.json` from a single spec
table. Edit it to add new examples and run:

```bash
python3 workflows/_generate_workflows.py
```
