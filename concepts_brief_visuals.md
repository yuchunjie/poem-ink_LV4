# Vivid Ink Wash Scenes & Architectural Visual Portal Redesign

* **Author:** Google Antigravity Agent & User
* **Date:** 2026-11-24

## Overview

This project upgrades the visual assets and system documentation of Poem-Ink LV4 (我愛讀詩・水墨雅集) using Google Stitch. It addresses two core user needs: (1) replacing repetitive procedural canvas components (e.g., identical boats, mountain silhouettes, and bell towers) with unique, vivid Song Dynasty literati landscape scenes that sequentially unfold in synchronization with spoken poetry lines, and (2) transforming the dated, generic SVG architecture diagram (`architecture.svg` / `architecture.html`) into an elegant, interactive Song Dynasty Scholar Architecture Portal.

## Analysis

Four specialized evaluation lenses reviewed the proposal and defined precise technical requirements and safeguards:

### 1. Sequential Follow-Reading Synchronization (User Invariant & Codebase Lens)
* **Requirement:** In follow-reading mode (`isReadingMode = true`), visual elements must not be exposed all at once. They must appear sequentially as each sentence is recited.
* **Mechanism (4-Stage Ink Wash Masking):** 
  - The canvas logic maintains a 4-stage sequential reveal matching `LS` timestamps and `paintRead()`.
  - When sentence 1 is recited, distant mountains and sky washes soak into the Xuan paper via an ink diffusion mask.
  - When sentence 2 and 3 are recited, middle-ground rivers, dynamic boats, cottages, or figures emerge with active physical particles.
  - When sentence 4 finishes, the foreground vermilion cinnabar seal stamp settles into place, and the complete painting remains displayed.
  - If playback stops, all elements seamlessly blend into full view.

### 2. Dual-Pass Composite & Texture Harmonization (Design Lens)
* **Risk (Plastic Sticker Effect & Moire):** Superimposing digital particles over AI-generated bitmaps causes particles to look like harsh stickers, while dual paper textures create dirty moiré interference. Setting global multiply blending destroys white snow particles.
* **Resolution:**
  - Dark fluid elements (water ripples, ink fog, willow twigs) render with `globalCompositeOperation = 'multiply'` to bleed into the paper fiber.
  - Luminous particles (falling snow, fishing lantern glows, moonbeams) render with `globalCompositeOperation = 'screen'` using warm ivory tints (`rgba(255, 248, 235, 0.85)`).
  - Background artwork is color-calibrated to `--bg-rice: #fff9ee`, with top-layer paper fibers (`PAP`) unifying all layers onto a single physical plane.

### 3. Canvas Pipeline Insertion & 100% Graceful Fallback (Codebase Lens)
* **Insertion Point:** Background artwork renders in `frame_()` at `index.html:2101` immediately following `c.fillRect(0, 0, 1000, 600)` and before the procedural element loop at line 2104.
* **Fallback Guarantee:** An asynchronous image cache handles asset loading. If an asset is loading or missing, the pipeline falls back 100% to the original 63 procedural mathematical primitives, preventing black frames or broken layouts.

### 4. Single-File Zero-CORS Architecture & Asset Budget (Zoom-Out Lens)
* **Constraint:** The project must never sacrifice offline `file://` execution or inflate HTML files to unmanageable sizes with giant Base64 strings.
* **Staging Strategy:** Pilot the dual-layer pipeline on the first 4 curricular master poems:
  1. 賀知章《回鄉偶書》 (Narrative village axis: old scholar and playful children under ancient pagoda trees)
  2. 張繼《楓橋夜泊》 (Deep nocturnal axis: frosted red maples, midnight temple bell waves, lantern glow)
  3. 杜牧《秋夕》 (Courtyard autumn axis: cool stone stairs, fireflies, distant summer triangle stars)
  4. 王維《九月九日憶山東兄弟》 (High-angle alpine axis: towering peaks, solitary climber, scarlet cornel berries)
* **Asset Packaging:** Pilot artworks are formatted as optimized WebP or inline SVGs (target ≤ 200KB each), with zero external CDN dependencies.

### 5. Architectural DAG Semantic Precision (Design & Codebase Lenses)
* **Problem:** Existing `architecture.svg` displays obsolete stats (24 poems instead of 54, 28 primitives instead of 63, omitting 108 neural voice files). Conversely, over-artistic handscrolls often obscure directed dataflow.
* **Resolution:** The interactive portal adopts a dual-state semantic topology:
  - Nodes are styled as carved seals (Cinnabar, Celadon, Bronze) but clearly display standard technical terminology.
  - Connectors use directed "dry brush" (飛白渴筆) strokes that clearly indicate push/pull dataflow.
  - Interactive nodes reveal deep-dive technical specs on demand with zero background CPU overhead.

### 6. Song Dynasty Gongbi Realism & Hybrid 1+2 Layer Architecture (Grill-Me Decided)
* **Aesthetic Standard (宋代院體工筆淡彩)**:
  - Modeled after Song Dynasty masterworks (Zhang Zeduan 《清明上河圖》, Ma Yuan, Xia Gui, Li Tang).
  - Realistic figures: Delicate iron-wire drapery lines (鐵線描衣褶), lifelike facial expressions, wispy white beards and sideburns, traditional Song/Tang scholar robes, dynamic children's poses.
  - Realistic objects & architecture: Authentic bracket sets (榫卯斗拱), multi-tiered pagodas with flying eaves, wooden boat grain with ropes and oars, realistic cinnabar cornel berries, silver incense burners, and intricate folding silk screens.
* **Hybrid 1+2 Layer Composite Architecture**:
  - **Component 1 (Panoramic Environmental Masterplate)**: Soft misty Shanshui landscape establishing the atmospheric spatial tone.
  - **Component 2 (Discrete Transparent Gongbi Realistic Element Plates)**: Four discrete high-detail realistic figure/object plates corresponding to lines 1~4.
  - **Masking Mechanism**: The 4-Stage Ink Wash Mask smoothly soaks and reveals each realistic plate strictly as its sentence is recited (`sentRevealProgress[stage]`).
  - **Packaging**: Embedded directly as optimized Base64 WebP/SVG plates to preserve the single-file zero-CORS offline execution guarantee.

## Goals vs. Non-Goals

### In-Scope Goals
* **4-Poem Pilot Integration:** Implement dual-layer dynamic ink wash reveal for the first 4 poems in `index.html`, tied to millisecond audio timings.
* **Orthogonal Prompt Matrix:** Standardize non-repeating artistic prompt specifications for all 24 poems and 30 maxims in Poem-Ink LV4.
* **Modern Scholar Architecture Portal:** Rebuild `architecture.html` and update `architecture.svg` to accurately reflect the 54-work, 63-primitive, 108-audio architecture in the Modern Song Rice Paper aesthetic.
* **Zero-CORS Offline Stability:** Ensure complete compatibility with local `file://` double-click execution.

### Out-of-Scope Non-Goals
* **No Immediate 54-Image Bulk Generation:** Generating all 54 assets simultaneously risks rate limits and asset bloat; full expansion follows the established Pilot standard.
* **No Breaking Canvas Resolution Contract:** The `1500x900` internal resolution and `1000x600` coordinate space remain locked.

## Alternatives Weighed

1. **Static Pre-baked Image Cards without Dynamic Sync:**
   * *Rejected:* Breaks the core user requirement that visual elements must emerge strictly per recited sentence.
2. **Replacing Architecture Diagrams with an Overly Complex React Web App:**
   * *Rejected:* Creates high maintenance debt. Replaced with clean, standalone HTML/SVG matching the project design system.
3. **Heavy Global Multiply Blend Mode:**
   * *Rejected:* Causes dynamic snow and light reflections to vanish. Replaced with dual-pass Multiply/Screen rendering.

## Key Decisions & Staging for Next Steps

* **Decision 1:** Implement 4-Stage Ink Wash Masking in `index.html` linked to audio playback timestamps.
* **Decision 2:** Rebuild `architecture.html` into the Scholar Ink Architecture Portal with accurate LV4 metrics.
* **Decision 3:** Produce the 4 Pilot artworks for 《回鄉偶書》, 《楓橋夜泊》, 《秋夕》, 《九月九日憶山東兄弟》 and verify against the verification checklist.
