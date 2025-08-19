# Responsive Design Breakpoints Specification

## Primary Breakpoints

The chat application uses these primary breakpoints for responsive design testing:

| Breakpoint | Width Range | CSS Media Query | Device Category |
|------------|-------------|-----------------|-----------------|
| Desktop    | 1200px+     | `@media (min-width: 1200px)` | Desktop computers, large tablets |
| Tablet     | 768px - 1199px | `@media (min-width: 768px) and (max-width: 1199px)` | Tablets, small laptops |
| Mobile     | 320px - 767px | `@media (max-width: 767px)` | Smartphones, small tablets |

## Detailed Breakpoint Analysis

### Desktop (1200px+)
- **Description**: Full desktop experience with maximum content visibility
- **UI Characteristics**:
  - Full-width chat interface with spacious message containers
  - Drawer can be permanently visible alongside content
  - Multi-column layouts where appropriate
  - Hover states for interactive elements
  - Full keyboard shortcut support
- **Testing Focus**:
  - Efficient use of screen space
  - Proper spacing between elements
  - No unnecessary scrolling
  - Proper rendering of large images and code blocks

### Tablet (768px - 1199px)
- **Description**: Optimized experience for medium-sized screens
- **UI Characteristics**:
  - Slightly condensed layout compared to desktop
  - Drawer may be hidden by default but easily accessible
  - Touch-friendly targets for tablet users
  - Reduced whitespace compared to desktop
- **Testing Focus**:
  - Touch interactions work properly
  - UI adapts gracefully when rotating between portrait and landscape
  - Drawer opens/closes smoothly without layout issues
  - Input controls are properly sized for touch and keyboard input

### Mobile (320px - 767px)
- **Description**: Highly optimized experience for small screens
- **UI Characteristics**:
  - Single-column layout with stacked elements
  - Drawer hidden by default, accessible via hamburger menu
  - Larger touch targets for all interactive elements (min 44×44px)
  - Simplified UI with focus on core functionality
  - Virtual keyboard considerations for input fields
- **Testing Focus**:
  - Content readability on small screens
  - Touch targets are large enough for comfortable use
  - Performance optimizations are active
  - No horizontal scrolling on standard content
  - UI handles virtual keyboard appearance correctly

## Breakpoint Boundary Testing

Special attention should be paid to testing at the exact boundary points:

| Boundary Point | Width | Testing Focus |
|----------------|-------|---------------|
| Mobile/Tablet  | 768px | Verify layout changes correctly at exactly 768px width |
| Tablet/Desktop | 1200px | Verify layout changes correctly at exactly 1200px width |

When testing at boundary points:
1. Resize the viewport to exactly the boundary width
2. Verify that the correct layout is applied
3. Resize 1px smaller and 1px larger to ensure smooth transition
4. Check for any layout jumps, overflow issues, or rendering problems

## Device-Specific Breakpoints

In addition to the primary breakpoints, these device-specific widths should be tested:

### Mobile Devices
- **Small Mobile** (320px - 359px): iPhone SE, older Android phones
- **Medium Mobile** (360px - 389px): Most Android phones
- **Large Mobile** (390px - 428px): iPhone 13/14, larger Android phones
- **Mobile Landscape** (568px - 767px): Most phones in landscape orientation

### Tablet Devices
- **Small Tablet** (768px - 834px): iPad Mini, small Android tablets
- **Medium Tablet** (835px - 1023px): iPad Air/Pro in portrait
- **Large Tablet** (1024px - 1199px): iPad Pro, large Android tablets in landscape

### Desktop Devices
- **Small Desktop** (1200px - 1439px): Laptops, small monitors
- **Medium Desktop** (1440px - 1919px): Standard desktop monitors
- **Large Desktop** (1920px+): Large monitors, high-resolution displays

## Responsive Behavior Mapping

This table maps specific UI components to their expected behavior across breakpoints:

| UI Component | Mobile Behavior | Tablet Behavior | Desktop Behavior |
|--------------|----------------|-----------------|------------------|
| Chat Messages | Full width, compact | Full width, medium spacing | Centered with max-width, spacious |
| Drawer | Hidden, slides in from left | Hidden or visible, slides in | Visible by default, can be toggled |
| Input Area | Fixed at bottom, expands upward | Fixed at bottom, expands upward | Fixed at bottom, expands upward with more initial height |
| Code Blocks | Horizontally scrollable, smaller font | Horizontally scrollable, medium font | Fully visible or scrollable, larger font |
| Navigation | Hamburger menu | Hamburger or visible tabs | Fully visible navigation |
| Attachments | Stack vertically | Grid layout (2-3 columns) | Grid layout (3-4 columns) |

## Testing Tools for Breakpoints

- **Chrome DevTools**: Use the responsive design mode to test at specific breakpoints
- **Firefox Responsive Design Mode**: Similar to Chrome's tool with additional features
- **Browser Resize Testing**: Manually resize the browser window to test fluid responsiveness
- **BrowserStack**: Test on actual devices at their native resolutions

## Implementation Guidelines

When implementing CSS for these breakpoints:

1. Use a mobile-first approach, starting with mobile styles and adding complexity for larger screens
2. Avoid using device-specific media queries; stick to width-based breakpoints
3. Test both at exact breakpoints and at sizes between breakpoints
4. Ensure smooth transitions between breakpoints with fluid layouts where possible
5. Use relative units (rem, em, %) rather than fixed pixels for element sizing

## Breakpoint Testing Checklist

For each breakpoint, verify:

- [ ] All content is visible and accessible
- [ ] No horizontal scrolling on main content areas
- [ ] Interactive elements are appropriately sized for input method (touch vs. mouse)
- [ ] Text is readable without zooming
- [ ] Images and media scale appropriately
- [ ] Animations and transitions perform well
- [ ] Layout is visually balanced and aesthetically pleasing