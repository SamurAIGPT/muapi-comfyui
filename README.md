# Awesome Nano Banana [![Awesome](https://awesome.re/badge.svg)](https://awesome.re)

A curated collection of official and community resources for **Nano Banana** – Google’s Gemini 2.5 Flash Image model (released Aug 2025).  
Nano Banana is a state-of-the-art image generation and editing model known for **realistic image creation, multi-image composition, character consistency**, and conversational edits.  
This “awesome list” aggregates announcements, docs, tutorials, example projects, demos, prompts, and discussions for anyone interested in building with Nano Banana.

---

## Table of Contents

- [Official Resources](#official-resources)  
- [Access and Documentation](#access-and-documentation)  
- [Tutorials and Guides](#tutorials-and-guides)  
- [Example Projects and Libraries](#example-projects-and-libraries)  
- [Demos and Notebooks](#demos-and-notebooks)  
- [Prompt Guides & Examples](#prompt-guides--examples)  
- [Integrations](#integrations)  
- [Community & Social Media](#community--social-media)  
- [Related Lists & Collections](#related-lists--collections)  

---

## Official Resources

- **Google Blog – [Image editing in Gemini just got a major upgrade](https://blog.google/products/gemini/flash-image-nano-banana/)** (Aug 26, 2025) – Official Google announcement introducing Nano Banana in the Gemini app.  
- **Google Developers Blog – [Introducing Gemini 2.5 Flash Image](https://developers.googleblog.com/gemini-25-flash-image/)** (Aug 26, 2025) – Technical launch post detailing Nano Banana’s features, and access via Gemini API, AI Studio, and Vertex AI.  
- **Gemini API Documentation** – [Image Generation with Gemini](https://ai.google.dev/gemini-api/docs/image-generation) – Official API guide for Nano Banana (Gemini 2.5 Flash Image) including code samples and usage examples.  
- **DeepMind Models Page** – [Gemini 2.5 Flash Image](https://deepmind.google/models/gemini/2-5-flash-image/) – Overview of Nano Banana capabilities (character consistency, composition, editing).  
- **Model Card (Aug 2025)** – *Gemini 2.5 Flash Image Model Card* – Detailed specs, training, and eval results for Nano Banana. Notes GA status and #1 benchmark performance.  
- **Vertex AI Docs (Google Cloud)** – [Gemini 2.5 Flash](https://cloud.google.com/vertex-ai/generative-ai/docs/models/gemini/2-5-flash) – Google Cloud documentation. Lists the Nano Banana model ID `gemini-2.5-flash-image-preview` and usage limits.  

---

## Access and Documentation

- **Gemini API (Image)** – Use the Nano Banana model with `model="gemini-2.5-flash-image-preview"`.  
- **Google AI Studio (Gemini)** – [AI Studio](https://aistudio.google.com/) lets you experiment with Nano Banana. Select *Gemini-2.5-flash-image* from the model picker to generate images for free.  
- **Vertex AI (Google Cloud)** – Enterprise access to Nano Banana via Vertex AI. Model ID: *gemini-2.5-flash-image-preview*.  
- **SynthID Watermark** – All Nano Banana outputs include an invisible *SynthID* digital watermark (to mark AI-generated content).  

---

## Tutorials and Guides

- **How to Build with Nano Banana** – [DEV.to tutorial](https://dev.to/google/how-to-build-with-nano-banana) (Google AI, Sep 2025). Comprehensive walkthrough of API usage, image generation, editing, prompts and best practices.  
- **DataCamp Tutorial** – *Gemini 2.5 Flash Image (Nano Banana): A Complete Guide* (Aug 2025). Step-by-step tutorial with practical examples: setup, prompt engineering, editing workflows.  
- **Anangsha Blog** – *[Nano Banana Tutorial: How to Use Google’s AI Image Editing Model](https://anangsha.blog/nano-banana-tutorial)*. Beginner-friendly guide with examples in Gemini and Imogen apps.  
- **KDnuggets Article** – *[Google’s Nano-Banana Just Unlocked a New Era of Image Generation](https://kdnuggets.com/nano-banana-google-ai/)*. Explainer and tutorial highlighting realistic generations and editing workflows.  
- **Hugging Face (Video Tutorial)** – *Nano Banana (Gemini 2.5 Flash Image) Full Tutorial — 27 Unique Cases vs Qwen Image Edit* (MonsterMMORPG). Includes prompts and comparisons.  
- **YouTube Tutorials** – e.g. *Learn to Build with Gemini Nano-Banana* (Google Devs), *INSANE Product Photos with Nano Banana* (Thomas AI).  

---

## Example Projects and Libraries

- **[google-gemini/nano-banana-hackathon-kit](https://github.com/google-gemini/nano-banana-hackathon-kit)** – Official hackathon starter kit. Includes setup, API examples, prompt guides, cookbooks, and demo apps.  
- **[minimaxir/gemimg](https://github.com/minimaxir/gemimg)** – Lightweight Python library for Nano Banana (Gemini API).   
- **PhotoFusion** – Demo project showcasing image merging with Nano Banana.  
- **Magic Banana** – “Natural Language Photoshop” demo app for text-based edits.  
- **gemini-gradio-image-editor** – Gradio app for editing images with Nano Banana.  
- **Hugging Face Spaces** – [Nano Banana Space](https://huggingface.co/spaces/multimodalart/nano-banana). Interactive interface (requires HF PRO).  
- **HF Dataset** – [Nano-Banana Generated Images](https://huggingface.co/datasets/bitmind/nano-banana). 9,457 community-generated images.  

---

## Demos and Notebooks

- **AI Studio Applets (Google)** – Templates like *GemBooth*, *Home Canvas*, *Past Forward*, *PixShop*. Showcases of character consistency, style transfer, inpainting.  
- **Google AI Studio Quickstarts** – Colab notebooks and recipes linked from the hackathon kit.  
- **Kaggle Nano Banana Challenge** – Official hackathon with $400k prizes (Sept 2025). Provided free API access and tutorials.  
- **Community Colabs** – GitHub and Gist notebooks using the Gemini API with Nano Banana.  

---

## Prompt Guides & Examples

- **Official Prompt Guide** – [Gemini API Prompting Strategies](https://ai.google.dev/gemini-api/docs/prompting). Covers descriptive prompts, specifying composition, style, and context.  
- **Community Prompt Examples** – Blog posts, HF Spaces, and X threads share creative prompts.  
- **Sample Use Case** – “Restore and colorize this image from 1932” – Google’s tutorial shows Nano Banana restoring a B&W image to realistic color.  

---

## Integrations

- **Hugging Face** – Nano Banana model accessible via Spaces and API.  
- **OpenRouter.ai** – Third-party API aggregator offering Nano Banana.  
- **Partner Platforms** – Google partnerships (e.g. fal.ai) exposing Nano Banana.  
- **Diffusers** – No official weights, but community wrappers exist for API usage.  

---

## Community & Social Media

- **Reddit (r/Nanobanana_AI)** – Discussions on Nano Banana features and prompt tips.  
- **YouTube & Twitter (X)** – AI influencers showcase Nano Banana capabilities.  
- **Hugging Face Forum** – Community tutorials, demos, and prompt sharing.  
- **Google AI Forum** – [Discuss AI Google](https://discuss.ai.google.dev) for Q&A.  

---

## Related Lists & Collections

- **[AI-Collection/ai-collection](https://github.com/AI-Collection/AI-Collection)** – Generative AI landscape list (mentions Gemini family).  
- **[steven2358/awesome-generative-ai](https://github.com/steven2358/awesome-generative-ai)** – Broader generative AI resources.  

---

### Contributing
Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for details.  

---
