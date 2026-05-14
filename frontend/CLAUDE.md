# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
npm run dev       # Start Vite dev server with HMR
npm run build     # Type-check (tsc -b) then Vite production build
npm run lint      # ESLint across all files
npm run preview   # Serve the production build locally
```

## Architecture

This is a React 19 + TypeScript + Vite frontend for an "Eco Assistant" voice chat bot UI ("Ekologiya Qo'mitasi" — Ecology Committee in Uzbek). It is a presentation-layer app with no backend calls — all state is local.

### State machine

`App.tsx` owns a single `botState` value: `"listening" | "thinking" | "speaking"`. A config object maps each state to a label, color, and icon. The bottom control buttons call `setBotState()` to cycle between states.

### Component roles

- **`App.tsx`** — Root layout, state machine, and button controls.
- **`BotCharacter.tsx`** — Animated SVG robot. Receives `botState` as a prop and renders state-specific Framer Motion animations:
  - `listening` → green (#10b981), expanding pulse rings
  - `thinking` → amber (#f59e0b), orbiting dots, blinking eyes
  - `speaking` → blue (#3b82f6), animated mouth, vertical bars below
- **`NatureBackground.tsx`** — Emerald gradient background, no logic.

### Animation

All animation is done with **Framer Motion** (`framer-motion` v12). Animations are infinite-repeat timelines defined inline in JSX. `@lottiefiles/react-lottie-player` is installed but not currently used.

### Styling

**Tailwind CSS v4** via the `@tailwindcss/vite` plugin (no `tailwind.config.*` file needed). Custom per-component CSS lives in `src/index.css`.

### TypeScript config

`tsconfig.app.json` targets ES2023 with strict lint flags (`noUnusedLocals`, `noUnusedParameters`, `noFallthroughCasesInSwitch`). `tsc -b` runs before every production build.
