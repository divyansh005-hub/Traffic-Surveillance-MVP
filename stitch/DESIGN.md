# Design System Document: The Kinetic Intelligence Framework

## 1. Overview & Creative North Star: "The Neon Sentinel"
The Creative North Star for this design system is **"The Neon Sentinel."** In a futuristic smart city, the interface is not merely a dashboard; it is a living, breathing pulse of urban kinesis. This system rejects the static, "flat" look of 2020s SaaS in favor of an **Atmospheric Command Center** aesthetic.

We break the "template" look through **Intentional Asymmetry**—where data density is balanced by expansive, dark negative space. We utilize **Overlapping Glass Layers** to simulate a physical command deck. The goal is an authoritative, high-tech experience that feels like a precision instrument: cold, dark, and hyper-efficient, yet illuminated by the vital signals of the city.

---

## 2. Colors: The Luminous Void
Our palette is rooted in the depth of a midnight cityscape (`#10141a`), punctuated by the electric energy of transit data.

### Surface Hierarchy & Nesting
To achieve a "nested" depth, we abandon flat grids. We treat the UI as stacked sheets of polarized glass:
*   **Base Layer:** `surface` (#10141a) – The infinite city floor.
*   **Secondary Zones:** `surface-container-low` (#181c22) – Large structural areas.
*   **Primary Interaction Containers:** `surface-container` (#1c2026) – The main workspace.
*   **Active Elements:** `surface-container-high` (#262a31) – Elevated widgets or focused data sets.

### The "No-Line" Rule
**Strict Mandate:** Designers are prohibited from using 1px solid borders for sectioning. Boundaries must be defined solely through background color shifts or subtle tonal transitions. A `surface-container-low` panel sitting on a `surface` background is all the definition required.

### The "Glass & Gradient" Rule
Floating elements (modals, tooltips, hover-states) must use **Glassmorphism**. Apply `surface-variant` with a 60% opacity and a `20px` backdrop-blur. 
*   **Signature Textures:** For high-priority CTAs, use a linear gradient from `primary` (#c3f5ff) to `primary-container` (#00e5ff) at a 135-degree angle. This provides a "glow-wire" effect that flat colors cannot replicate.

---

## 3. Typography: Technical Precision
The typography is a dialogue between human-readable editorial and machine-precise data.

*   **Display & Headlines:** We use **Space Grotesk**. Its wide apertures and geometric construction feel architectural and futuristic. Use `display-lg` for macro-metrics (e.g., "City Traffic Flow: 94%") to establish authority.
*   **Body & Labels:** We use **Inter**. It is the "human" element—clean, neutral, and highly legible at small scales. 
*   **The Data Variant:** For coordinates, timestamps, and sensor readings, use Inter with `font-feature-settings: "tnum", "onum"` (Tabular Numerals) to ensure vertical alignment in shifting data streams.

---

## 4. Elevation & Depth: Tonal Layering
Traditional shadows have no place in a high-tech HUD. Depth is conveyed through light and transparency.

*   **The Layering Principle:** Instead of a shadow, place a `surface-container-lowest` card on a `surface-container-low` section to create a "recessed" effect, or `surface-container-highest` to create a "raised" effect.
*   **Ambient Shadows:** If an element must float (e.g., a critical alert pop-up), use a wide-spread shadow (32px blur) using a 10% opacity version of `primary-fixed-dim`. This simulates the "glow" of the screen reflecting off the component.
*   **The "Ghost Border":** For accessibility on interactive inputs, use the `outline-variant` (#3b494c) at **15% opacity**. It should be felt, not seen.

---

## 5. Components: The Command Suite

### Buttons: High-Energy Actuators
*   **Primary:** Solid `primary-container` background with `on-primary-container` text. Apply a subtle 2px outer glow (`primary`) on hover.
*   **Secondary:** Ghost style. No background, `outline-variant` (20% opacity) border, and `primary` text.
*   **Shape:** Use `rounded-md` (0.375rem) to maintain a technical, "machined" edge.

### Cards & Lists: The Stream
*   **Mandate:** No divider lines. Use `8px` (Spacing 2) or `12px` (Spacing 3) of vertical space to separate items.
*   **Hover State:** Change background from `surface-container` to `surface-bright` (#353940) to indicate selection.

### Data Visualization: Signal Colors
*   **Flowing (Green):** Use `tertiary-fixed-dim` for "Normal" flow.
*   **Congestion (Amber):** Use `tertiary-container` (#ffc948).
*   **Incident (Red):** Use `error` (#ffb4ab) with a pulsing opacity animation (100% to 60%).

### Input Fields: Telemetry Inputs
*   Background: `surface-container-lowest`.
*   Active State: The bottom border glows with a 1px `primary` line; the rest of the container remains borderless.

---

## 6. Do’s and Don’ts

### Do:
*   **DO** use intentional asymmetry. A heavy data table on the left can be balanced by a large, minimalist map view on the right.
*   **DO** use "Signal Colors" sparingly. If everything is glowing, nothing is important.
*   **DO** utilize the `Spacing 16` and `24` tokens to create "Breathing Rooms" between major system modules.

### Don't:
*   **DON'T** use pure white (#FFFFFF). All "white" text should be `on-surface` (#dfe2eb) to reduce eye strain in dark environments.
*   **DON'T** use standard 90-degree corners. Always use the `Roundedness Scale` to soften the tech-heavy look.
*   **DON'T** use opaque modal backdrops. Always use `backdrop-blur` to maintain the user's spatial awareness of the city map beneath.

---

## 7. Signature Interaction: The "Pulse"
When a new traffic incident occurs, the affected container should not just flash. It should trigger a "Pulse": a temporary `outline` using the `error` color that ripples outward and fades, utilizing the `surface-tint` logic to draw the operator's eye through light, not movement.