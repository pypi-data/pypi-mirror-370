# 🎨 Licenzy Brand Guidelines

## Logo Usage

The Licenzy logo is available in the `assets/` directory and should be used consistently across all materials.

### Logo Files
- **Main Logo (SVG)**: `assets/licenzy.svg` - Primary vector logo for all digital use (preferred)
- **Main Logo (PNG)**: `assets/licenzy.png` - Raster backup for platforms that don't support SVG
- **Favicon**: Consider creating a 32x32 or 16x16 version for web favicon use

### Why SVG is Preferred
- **Scalable**: Looks crisp at any size
- **Smaller**: Better file size for web use
- **Editable**: Can be styled with CSS
- **Future-proof**: Vector format scales to any resolution

### Usage Guidelines

#### ✅ Do:
- Use the logo at recommended sizes (200px width for README headers)
- Maintain clear space around the logo
- Use on clean, contrasting backgrounds
- Keep the logo proportions intact

#### ❌ Don't:
- Stretch or distort the logo
- Use on busy backgrounds that reduce readability
- Change the logo colors without brand approval
- Use the logo smaller than 32px wide

### Recommended Placements

#### Documentation
- **README.md**: Top of file, centered, 200px width
- **Documentation sites**: Header, 150-200px width
- **API docs**: Small version in navigation (50-75px)

#### Package/Distribution
- **PyPI page**: As the project logo
- **Favicon**: 32x32 or 16x16 version for websites
- **Social media**: Profile images, sharing cards

#### Marketing Materials
- **Landing pages**: Hero section, various sizes
- **Blog posts**: Feature image or inline
- **Presentations**: Title slides, footer

### Integration Examples

#### Markdown (README/Docs)
```markdown
<div align="center">
  <img src="assets/licenzy.svg" alt="Licenzy Logo" width="200"/>
</div>
```

#### HTML
```html
<img src="assets/licenzy.svg" alt="Licenzy - Simple License Management" class="logo">
```

#### CSS Styling (SVG benefits)
```css
.logo {
  width: 200px;
  height: auto;
  /* SVG can be styled with CSS */
  filter: brightness(1.1);
  transition: transform 0.2s ease;
}

.logo:hover {
  transform: scale(1.05);
}
```

#### Python (CLI output)
Consider ASCII art version for terminal output:
```
🔑 LICENZY - Simple License Management
```

### Brand Consistency

The logo should reinforce Licenzy's brand values:
- **Simple & Clean**: Minimal design that's easy to recognize
- **Professional**: Trustworthy appearance for business use
- **Developer-Friendly**: Appeals to the technical audience
- **Modern**: Contemporary design that feels current

### File Organization
```
assets/
├── licenzy.svg          # Main logo - vector format (preferred)
├── licenzy.png          # Main logo - raster backup
├── licenzy-favicon.ico  # Future: Favicon for websites
├── licenzy-dark.svg     # Future: Dark theme variant
└── licenzy-light.svg    # Future: Light theme variant
```

### Technical Specifications

#### SVG Logo
- **Format**: Scalable Vector Graphics (.svg)
- **Recommended width**: 200px for headers, scales to any size
- **Benefits**: Crisp at any resolution, smaller file size, CSS styleable
- **Browser support**: All modern browsers

#### PNG Logo (Backup)
- **Format**: Portable Network Graphics (.png)
- **Recommended sizes**: 200px, 400px, 800px widths
- **Use cases**: Platforms that don't support SVG, email signatures
