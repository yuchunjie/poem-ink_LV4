# Poem-Ink LV4 Responsive Web Redesign with Google Stitch

* **Author:** Google Antigravity Agent & User
* **Date:** 2026-11-24

## Overview

This project redesigns Poem-Ink LV4 (我愛讀詩・水墨雅集) into a fully responsive web application serving desktop, tablet, and mobile devices while preserving all existing offline audio and dynamic ink wash canvas assets. Poem-Ink LV4 contains 24 classical Tang/Song poems and 30 educational maxims, 108 neural voice audio recordings, and 63 procedural dynamic canvas animations. The redesign uses Google Stitch to establish modern layout prototypes and tokens, and injects clean, zero-dependency CSS and UI components into the standalone `index.html` file without disrupting audio synchronization or canvas rendering.

## Analysis

Four specialized evaluation lenses reviewed the initial concept and identified core technical challenges and mitigation strategies:

### 1. Rendering Performance & Mobile Compositor Pipeline (Design & Zoom-Out Lenses)
* **Risk:** Running a 60 FPS full-screen procedural Canvas (`1500x900`) underneath active `backdrop-filter: blur()` cards on mobile devices forces GPU readbacks every frame. On mid-tier Android devices and iOS WebKit, this causes frame rate drops from 60 FPS to 15-20 FPS, device heating, and potential WebProcess out-of-memory crashes.
* **Resolution:** On mobile viewports (`< 768px`), live CSS backdrop blur is replaced by a high-opacity faux frosted rice paper texture (`background: rgba(253, 250, 242, 0.92)`). The dynamic canvas rAF loop is isolated on a dedicated compositing layer (`contain: strict; will-change: transform; transform: translateZ(0);`).

### 2. Canvas Geometry & Composition Preservation (Design & Codebase Lenses)
* **Risk:** The canvas logic is hardcoded to a 5:3 aspect ratio (`1500x900` pixels, internally mapped from a `1000x600` coordinate space scaled by 1.5x in `frame_()`). Forcing this canvas into a vertical 9:19.5 smartphone screen via simple `object-fit: cover` clips over 70% of the horizontal scene, cutting off mountains, boats, and the seal signature located at `(958, 558)`.
* **Resolution:** Desktop and horizontal tablets maintain the 5:3 side-by-side dual-pane layout. Mobile vertical screens implement an anchored responsive layout: the canvas maintains an upper stage or center-weighted transform, while calligraphy text cards adapt in high contrast below or floating in the center. The HTML canvas resolution attributes (`width="1500" height="900"`) remain untouched to prevent breaking logical coordinate arrays.

### 3. Vertical Calligraphy Typography & Gestures (Design Lens)
* **Risk:** Vertical text layout (`writing-mode: vertical-rl`) inside compact mobile viewports causes lines to wrap awkwardly when vertical space is under 300px. Additionally, horizontal leftward scrolling in `vertical-rl` conflicts with iOS edge-swipe gestures and bottom sheet drag events.
* **Resolution:** Typography sizing is clamped via `font-size: clamp(14px, 3.8vh, 18px)` and `line-height: 1.8` so 28-character poems (such as seven-character quatrains) fit entirely without scrolling. Long texts fall back cleanly to smooth horizontal page snapping. Standard CJK upright orientation rules (`text-orientation: upright; font-feature-settings: "vert" 1;`) ensure correct punctuation positioning in mobile browsers.

### 4. DOM Stability & Zero-CDN Constraint (Implementation Readiness Lens)
* **Risk:** Directly inserting React or Tailwind code from Stitch into the 4,781-line standalone `index.html` would introduce build tool dependencies or CDN latency, violating the offline `file://` execution invariant. Renaming or wrapping existing IDs breaks the 80ms audio polling loop (`setInterval` at lines 4525-4553) that synchronizes `LS` and `elems` arrays.
* **Resolution:** The codebase adheres to a strict 12-ID lock contract (`#cv`, `#poem`, `#pr`, `#nx`, `#sp`, `#ss`, `#rp`, `#rt`, `#exb`, `#au`, `#ex`, `#exs`). Stitch outputs are flattened into vanilla CSS and scoped HTML wrappers. No external CDN scripts or fonts are permitted.

### 5. Stacking Context & Modal Management (Codebase Lens)
* **Risk:** Introducing a mobile Bottom Sheet navigation drawer while retaining the existing explanation drawer (`#ex`) causes z-index collisions and gesture trapping. Stored `localStorage.exOpen` would also cause the explanation drawer to obstruct the screen on page load.
* **Resolution:** A unified z-index hierarchy is enforced: Canvas (`z-index: 0`), Foreground Stage (`10`), Control Dock (`50`), Backdrop (`100`), Nav Bottom Sheet (`110`), and Explanation Sheet (`120`). Mutual exclusion ensures opening one drawer dismisses the other. Auto-opening `#ex` from localStorage is disabled on screens narrower than 768px.

## Goals vs. Non-Goals

### In-Scope Goals
* **Stitch Prototype Generation:** Generate responsive UI prototypes for Desktop, Tablet, and Mobile in Google Stitch, capturing modern typography, cards, buttons, and navigation patterns.
* **Modern Song Rice Paper Design System:** Upgrade design tokens in `:root` (rice paper beige, five ink wash gradations, cinnabar accent, gold highlights, and frosted paper surfaces).
* **Multi-Device RWD Architecture:** Support full responsive layouts:
  * Desktop (>= 1024px): Side-by-side layout (Canvas left, vertical calligraphy right).
  * Tablet (768px - 1023px): Adaptive flex layout with responsive typography.
  * Mobile (< 768px): Stage-and-sheet layout with mobile bottom sheet navigation and floating control capsule.
  * Landscape (< 500px height): Horizontal split with right-side mini dock.
* **Complete Asset & Feature Preservation:** Retain all 108 neural voice audio files, millisecond-level follow-reading highlight synchronization, 63 procedural canvas animations, and offline `file://` single-file execution.

### Out-of-Scope Non-Goals
* **No Build Tools or CDN Dependencies:** No Webpack, Vite, React, or Tailwind runtime in the production file. The output remains a single HTML file.
* **No Audio Re-generation or Timing Schema Changes:** Existing audio clips and `timings.json` data structures remain unmodified.
* **No Internal Canvas Rewrite:** The 63 procedural animation algorithms inside `frame_()` are not rewritten; only their viewport styling and frame throttling are adjusted.

## Alternatives Weighed

1. **Full Rewrite as React/Vue Web App:**
   * *Rejected:* Adds compilation steps, breaks standalone `file://` double-click offline execution, and requires rewriting thousands of lines of canvas animation math.
2. **Pure Live Fullscreen Backdrop Blur over Canvas on Mobile:**
   * *Rejected:* Severe GPU readback overhead causes dropped frames (15 FPS) and battery drain on mobile devices. Replaced with faux frosted rice paper styling.
3. **Permanent Left Sidebar Navigation on Mobile:**
   * *Rejected:* Consumes valuable horizontal viewport space on mobile and tablet portrait screens. Replaced with an on-demand Bottom Sheet drawer.
4. **Modifying HTML Canvas Resolution (`cv.width = window.innerWidth`):**
   * *Rejected:* Breaks the 1.5x scaling transform and coordinates of 63 procedural ink wash components and pre-rendered offscreen canvases (`PAP`, `VIG`, `FOG`).

## Key Decisions & Staging for Next Steps

* **Decision 1:** Use Google Stitch MCP to create project `Poem-Ink RWD Redesign` and generate three screens: Desktop, Tablet, and Mobile.
* **Decision 2:** Extract design tokens, card styles, and bottom sheet DOM structures from Stitch.
* **Decision 3:** Integrate styles into `index.html` via vanilla CSS overrides, preserving the 12 locked DOM IDs and the 1500x900 canvas coordinate contract.
* **Staging Plan:**
  1. Initialize project in Google Stitch via `call_mcp_tool(create_project)`.
  2. Generate Desktop, Tablet, and Mobile screens with tailored Chinese ink-wash aesthetic prompts via `generate_screen_from_text`.
  3. Extract component CSS and HTML layouts.
  4. Apply responsive CSS and Bottom Sheet drawer to `index.html`.
  5. Validate against the 4-stage verification checklist.
