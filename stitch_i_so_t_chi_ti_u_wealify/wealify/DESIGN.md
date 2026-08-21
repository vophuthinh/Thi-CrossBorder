---
name: Wealify
colors:
  surface: '#f9f9f9'
  surface-dim: '#dadada'
  surface-bright: '#f9f9f9'
  surface-container-lowest: '#ffffff'
  surface-container-low: '#f3f3f4'
  surface-container: '#eeeeee'
  surface-container-high: '#e8e8e8'
  surface-container-highest: '#e2e2e2'
  on-surface: '#1a1c1c'
  on-surface-variant: '#444651'
  inverse-surface: '#2f3131'
  inverse-on-surface: '#f0f1f1'
  outline: '#757682'
  outline-variant: '#c5c5d3'
  surface-tint: '#4059aa'
  primary: '#00236f'
  on-primary: '#ffffff'
  primary-container: '#1e3a8a'
  on-primary-container: '#90a8ff'
  inverse-primary: '#b6c4ff'
  secondary: '#505f76'
  on-secondary: '#ffffff'
  secondary-container: '#d0e1fb'
  on-secondary-container: '#54647a'
  tertiary: '#4b1c00'
  on-tertiary: '#ffffff'
  tertiary-container: '#6e2c00'
  on-tertiary-container: '#f39461'
  error: '#ba1a1a'
  on-error: '#ffffff'
  error-container: '#ffdad6'
  on-error-container: '#93000a'
  primary-fixed: '#dce1ff'
  primary-fixed-dim: '#b6c4ff'
  on-primary-fixed: '#00164e'
  on-primary-fixed-variant: '#264191'
  secondary-fixed: '#d3e4fe'
  secondary-fixed-dim: '#b7c8e1'
  on-secondary-fixed: '#0b1c30'
  on-secondary-fixed-variant: '#38485d'
  tertiary-fixed: '#ffdbcb'
  tertiary-fixed-dim: '#ffb691'
  on-tertiary-fixed: '#341100'
  on-tertiary-fixed-variant: '#773205'
  background: '#f9f9f9'
  on-background: '#1a1c1c'
  surface-variant: '#e2e2e2'
typography:
  display-lg:
    fontFamily: Inter
    fontSize: 36px
    fontWeight: '700'
    lineHeight: 44px
    letterSpacing: -0.02em
  headline-md:
    fontFamily: Inter
    fontSize: 24px
    fontWeight: '600'
    lineHeight: 32px
    letterSpacing: -0.01em
  headline-sm:
    fontFamily: Inter
    fontSize: 20px
    fontWeight: '600'
    lineHeight: 28px
  body-lg:
    fontFamily: Inter
    fontSize: 16px
    fontWeight: '400'
    lineHeight: 24px
  body-md:
    fontFamily: Inter
    fontSize: 14px
    fontWeight: '400'
    lineHeight: 20px
  body-sm:
    fontFamily: Inter
    fontSize: 13px
    fontWeight: '400'
    lineHeight: 18px
  label-md:
    fontFamily: Inter
    fontSize: 12px
    fontWeight: '600'
    lineHeight: 16px
    letterSpacing: 0.05em
  mono-data:
    fontFamily: monospace
    fontSize: 13px
    fontWeight: '400'
    lineHeight: 18px
rounded:
  sm: 0.125rem
  DEFAULT: 0.25rem
  md: 0.375rem
  lg: 0.5rem
  xl: 0.75rem
  full: 9999px
spacing:
  unit: 4px
  xs: 4px
  sm: 8px
  md: 16px
  lg: 24px
  xl: 32px
  container-max: 1440px
  gutter: 20px
---

## Brand & Style
The design system is engineered for high-precision financial operations and data reconciliation. The brand personality is authoritative, transparent, and hyper-functional. It prioritizes clarity over decoration, aiming to reduce the cognitive load associated with complex data auditing.

The visual style follows a **Corporate / Modern** aesthetic with a lean toward **Minimalism**. It utilizes expansive white space to separate dense data sets, a disciplined color application to highlight status changes, and a rigid structural grid to convey stability and institutional trust.

## Colors
This design system utilizes a high-contrast palette to ensure legibility and professional rigor. 

- **Primary (#1E3A8A):** Reserved for primary actions, active navigation states, and brand-critical touchpoints.
- **Secondary (#64748B):** Used for metadata, secondary icons, and de-emphasized text to create visual hierarchy.
- **Neutral (#FFFFFF):** The foundation for all containers and workspaces, ensuring the UI remains "breathable."
- **Semantic Colors:** Critical for reconciliation. Use Green for balanced accounts, Red for discrepancies, and Amber for pending reviews.
- **Background Subtle:** A very light slate tint used for page backgrounds to make white "Surface" cards pop.

## Typography
The system relies on **Inter** for its exceptional legibility in data-dense environments. The type scale is compact to maximize information density without sacrificing readability.

For financial figures and transaction IDs, implement a monospaced font alternative (or Inter’s tabular numbers feature) to ensure columns of numbers align vertically for easy scanning. Use `label-md` for table headers and section overlines to provide clear structural categorization.

## Layout & Spacing
The layout follows a **Fixed Grid** model for the main content area to maintain predictable data visualization, centering on a 12-column system.

- **Desktop (1280px+):** 12 columns, 24px margins, 20px gutters.
- **Tablet (768px - 1279px):** 8 columns, 16px margins. Sidebar collapses to icons only.
- **Mobile (Up to 767px):** 4 columns, 16px margins. Tables must transition to card-based views or horizontal scroll.

Spacing follows a strict 4px base unit. Use `md` (16px) for standard component padding and `lg` (24px) for spacing between major dashboard widgets.

## Elevation & Depth
In this design system, depth is communicated through **Tonal Layers** and **Low-contrast Outlines** rather than heavy shadows. 

The background is `background_subtle`. Individual modules (cards) sit on white surfaces with a 1px border of `Slate Gray` at 10-15% opacity. Shadows are used sparingly—only for floating elements like dropdown menus or modals—and are styled as "Ambient Shadows" (long blur, very low 5% opacity) to maintain a flat, professional profile.

## Shapes
The shape language is **Soft**. A 4px (`0.25rem`) corner radius is applied to buttons, input fields, and small UI widgets to appear modern but disciplined. Larger containers like dashboard cards should use `rounded-lg` (8px) to create a clear visual distinction between the page structure and interactive elements.

## Components
- **Buttons:** Primary buttons use `Deep Blue` with white text. Secondary buttons use a transparent background with a 1px `Slate Gray` border. Use "Compact" sizing (vertical padding 8px) for table actions.
- **Input Fields:** Use a solid white background with a 1px border in `Slate Gray`. On focus, the border shifts to `Deep Blue` with a 2px outer glow. Labels are always positioned above the input in `body-sm` bold.
- **Data Tables:** The core component. Use zebra-striping (alternating `background_subtle`) for rows. Headers are `label-md` with a subtle bottom border.
- **Status Chips:** Small, pill-shaped indicators with low-opacity backgrounds (e.g., light green background with dark green text) to indicate reconciliation status.
- **Reconciliation Cards:** Feature a left-border accent color (Blue for neutral, Red for error) to allow users to scan discrepancy lists rapidly.