# vault404.dev Frontend

Static website for vault404.dev - AI Vulnerability Intelligence Platform.

## Pages

- **Dashboard** (`#dashboard`) - Live counter, severity breakdown, leaderboard, rolling feed
- **How It Works** (`#how-it-works`) - 3-step flow, architecture, FAQ
- **Docs** (`#docs`) - API reference
- **Demo** (`#demo`) - Animated demo video

## Local Development

Serve the files with any static server:

```bash
# Python
cd web && python -m http.server 8000

# Node.js
npx serve web

# Or just open index.html in a browser
```

## Deployment

### Vercel

```bash
cd web && vercel
```

### Netlify

Drag and drop the `web/` folder to Netlify.

### GitHub Pages

Push to a `gh-pages` branch or enable Pages in repo settings.

### Custom Domain

Point vault404.dev DNS to your hosting provider and configure SSL.

## Design System

Colors (OKLCH):
- `signal` (amber): `oklch(0.82 0.17 92)` - Found by AI
- `threat` (red): `oklch(0.64 0.2 25)` - Severity/unfixed
- `verify` (mint): `oklch(0.78 0.15 165)` - Verified/fixed
- `neural` (violet): `oklch(0.72 0.16 295)` - Agent/brain

Fonts:
- Display: Space Grotesk
- Body: Inter
- Code: JetBrains Mono

## Tech Stack

- React 18 (via CDN)
- Babel standalone (JSX transform)
- Pure CSS (no build step)
- Hash-based routing
