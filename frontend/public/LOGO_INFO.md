# CareOps Logo Assets

## Files

- **careops-logo.svg** - Full logo (512x512) for social media and large displays
- **careops-icon.svg** - Favicon/icon (32x32) for browser tabs
- **manifest.json** - PWA manifest for installable web app

## Logo Design

The CareOps logo combines:
- **Medical Cross** - Representing care and healthcare services
- **Operations Gear** - Representing operational efficiency and automation
- **Blue Color (#3B82F6)** - Trust, professionalism, and technology

## Usage

### In HTML
```html
<link rel="icon" type="image/svg+xml" href="/careops-icon.svg" />
```

### In React Components
```tsx
import logo from '/careops-logo.svg';

<img src={logo} alt="CareOps" />
```

### As Background
```css
background-image: url('/careops-logo.svg');
```

## Color Palette

- **Primary Blue**: #3B82F6
- **White**: #FFFFFF
- **Dark Text**: #1F2937

## Customization

To customize the logo:
1. Open the SVG file in any text editor
2. Modify the `fill` attributes to change colors
3. Adjust dimensions in the `viewBox` attribute
4. Save and refresh your browser

## Brand Guidelines

- Always maintain the aspect ratio
- Minimum size: 32x32 pixels
- Use on light or dark backgrounds
- Don't distort or rotate the logo
- Maintain clear space around the logo
