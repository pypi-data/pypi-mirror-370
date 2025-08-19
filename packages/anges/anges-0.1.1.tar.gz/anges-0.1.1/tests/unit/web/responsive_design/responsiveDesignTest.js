/**
 * Responsive Design Testing Framework
 * 
 * This file implements automated tests for verifying responsive design functionality
 * across different viewport sizes based on the defined breakpoints:
 * - Desktop: 1200px+
 * - Tablet: 768px - 1199px
 * - Mobile: 320px - 767px
 * 
 * The tests use Puppeteer to simulate different viewport sizes and test critical UI components.
 */

const puppeteer = require('puppeteer');
const { expect } = require('chai');

// Define breakpoints according to our specification
const BREAKPOINTS = {
  mobile: { width: 375, height: 667 },  // iPhone 8/SE size
  tablet: { width: 768, height: 1024 }, // iPad size
  desktop: { width: 1440, height: 900 } // Standard desktop
};

// Secondary test points for edge cases
const EDGE_BREAKPOINTS = {
  smallMobile: { width: 320, height: 568 },    // iPhone 5/SE
  largeMobile: { width: 428, height: 926 },    // iPhone 13 Pro Max
  tabletLandscape: { width: 1024, height: 768 }, // iPad landscape
  smallDesktop: { width: 1200, height: 800 }   // Minimum desktop
};

describe('Responsive Design Tests', function() {
  this.timeout(30000); // Increase timeout for browser tests
  let browser;
  let page;

  before(async function() {
    browser = await puppeteer.launch({
      headless: true,
      args: ['--no-sandbox', '--disable-setuid-sandbox']
    });
  });

  after(async function() {
    await browser.close();
  });

  beforeEach(async function() {
    page = await browser.newPage();
    // Navigate to the chat application
    await page.goto('http://localhost:5000/chat', { waitUntil: 'networkidle2' });
  });

  afterEach(async function() {
    await page.close();
  });

  /**
   * Helper function to take screenshots for visual comparison
   */
  async function takeScreenshot(page, name) {
    const viewport = page.viewport();
    await page.screenshot({ 
      path: `./tests/unit/web/responsive_design/screenshots/${name}_${viewport.width}x${viewport.height}.png` 
    });
  }

  /**
   * Test Suite 1: Chat Interface Responsiveness
   */
  describe('Chat Interface Responsiveness', function() {
    
    it('should adapt message container to desktop viewport', async function() {
      await page.setViewport(BREAKPOINTS.desktop);
      
      // Wait for chat interface to load
      await page.waitForSelector('.message-container');
      
      // Measure message container width
      const containerWidth = await page.evaluate(() => {
        return document.querySelector('.message-container').offsetWidth;
      });
      
      // On desktop, container should have a max-width and not span full viewport
      expect(containerWidth).to.be.lessThan(BREAKPOINTS.desktop.width);
      
      await takeScreenshot(page, 'message_container_desktop');
    });

    it('should adapt message container to tablet viewport', async function() {
      await page.setViewport(BREAKPOINTS.tablet);
      
      await page.waitForSelector('.message-container');
      
      const containerWidth = await page.evaluate(() => {
        return document.querySelector('.message-container').offsetWidth;
      });
      
      // On tablet, container should use most of the available width
      expect(containerWidth).to.be.closeTo(BREAKPOINTS.tablet.width, 50);
      
      await takeScreenshot(page, 'message_container_tablet');
    });

    it('should adapt message container to mobile viewport', async function() {
      await page.setViewport(BREAKPOINTS.mobile);
      
      await page.waitForSelector('.message-container');
      
      const containerWidth = await page.evaluate(() => {
        return document.querySelector('.message-container').offsetWidth;
      });
      
      // On mobile, container should use full width with minimal margins
      expect(containerWidth).to.be.closeTo(BREAKPOINTS.mobile.width, 20);
      
      await takeScreenshot(page, 'message_container_mobile');
    });

    it('should properly render code blocks on different viewports', async function() {
      // Test code block rendering on desktop
      await page.setViewport(BREAKPOINTS.desktop);
      
      // Send a message with a code block
      await page.waitForSelector('.message-input');
      await page.type('.message-input', '```javascript\nfunction test() {\n  console.log("Hello world");\n  return true;\n}\n```');
      await page.click('.send-button');
      
      // Wait for code block to render
      await page.waitForSelector('pre code');
      
      // Verify code block is visible and properly formatted
      const codeBlockVisible = await page.evaluate(() => {
        const codeBlock = document.querySelector('pre code');
        return codeBlock && window.getComputedStyle(codeBlock).display !== 'none';
      });
      
      expect(codeBlockVisible).to.be.true;
      await takeScreenshot(page, 'code_block_desktop');
      
      // Repeat for mobile viewport
      await page.setViewport(BREAKPOINTS.mobile);
      
      // Verify code block adapts to mobile
      const codeBlockWidth = await page.evaluate(() => {
        return document.querySelector('pre').offsetWidth;
      });
      
      // Code block should fit within mobile viewport
      expect(codeBlockWidth).to.be.lessThanOrEqual(BREAKPOINTS.mobile.width);
      await takeScreenshot(page, 'code_block_mobile');
    });
  });

  /**
   * Test Suite 2: Drawer Functionality
   */
  describe('Drawer Functionality', function() {
    
    it('should display drawer appropriately on desktop', async function() {
      await page.setViewport(BREAKPOINTS.desktop);
      
      // Check if drawer is visible by default on desktop
      const drawerVisibleByDefault = await page.evaluate(() => {
        const drawer = document.querySelector('.drawer');
        return drawer && window.getComputedStyle(drawer).display !== 'none';
      });
      
      // If drawer is hidden, toggle it
      if (!drawerVisibleByDefault) {
        await page.click('.drawer-toggle');
        await page.waitForSelector('.drawer', { visible: true });
      }
      
      // Verify drawer is displayed correctly
      const drawerVisible = await page.evaluate(() => {
        const drawer = document.querySelector('.drawer');
        return drawer && window.getComputedStyle(drawer).display !== 'none';
      });
      
      expect(drawerVisible).to.be.true;
      await takeScreenshot(page, 'drawer_desktop');
    });

    it('should toggle drawer correctly on mobile', async function() {
      await page.setViewport(BREAKPOINTS.mobile);
      
      // On mobile, drawer should be hidden by default
      const drawerHiddenByDefault = await page.evaluate(() => {
        const drawer = document.querySelector('.drawer');
        return drawer && window.getComputedStyle(drawer).display === 'none';
      });
      
      expect(drawerHiddenByDefault).to.be.true;
      
      // Open drawer
      await page.click('.drawer-toggle');
      await page.waitForTimeout(500); // Wait for animation
      
      // Verify drawer is now visible
      const drawerVisible = await page.evaluate(() => {
        const drawer = document.querySelector('.drawer');
        return drawer && window.getComputedStyle(drawer).display !== 'none';
      });
      
      expect(drawerVisible).to.be.true;
      await takeScreenshot(page, 'drawer_mobile_open');
      
      // Close drawer
      await page.click('.drawer-close');
      await page.waitForTimeout(500); // Wait for animation
      
      // Verify drawer is hidden again
      const drawerHiddenAgain = await page.evaluate(() => {
        const drawer = document.querySelector('.drawer');
        return drawer && window.getComputedStyle(drawer).display === 'none';
      });
      
      expect(drawerHiddenAgain).to.be.true;
    });
  });

  /**
   * Test Suite 3: Input Controls
   */
  describe('Input Controls Responsiveness', function() {
    
    it('should adapt input area to different viewports', async function() {
      // Test on desktop
      await page.setViewport(BREAKPOINTS.desktop);
      
      await page.waitForSelector('.message-input');
      
      const desktopInputWidth = await page.evaluate(() => {
        return document.querySelector('.message-input').offsetWidth;
      });
      
      // Test on mobile
      await page.setViewport(BREAKPOINTS.mobile);
      
      const mobileInputWidth = await page.evaluate(() => {
        return document.querySelector('.message-input').offsetWidth;
      });
      
      // Input should be wider on desktop than mobile
      expect(desktopInputWidth).to.be.greaterThan(mobileInputWidth);
      
      // Input should take most of the available width on mobile
      expect(mobileInputWidth).to.be.closeTo(BREAKPOINTS.mobile.width, 40);
      
      await takeScreenshot(page, 'input_area_mobile');
    });

    it('should have appropriate touch target sizes on mobile', async function() {
      await page.setViewport(BREAKPOINTS.mobile);
      
      // Check send button size
      const sendButtonSize = await page.evaluate(() => {
        const button = document.querySelector('.send-button');
        const rect = button.getBoundingClientRect();
        return { width: rect.width, height: rect.height };
      });
      
      // Touch targets should be at least 44x44px on mobile
      expect(sendButtonSize.width).to.be.at.least(44);
      expect(sendButtonSize.height).to.be.at.least(44);
    });
  });

  /**
   * Test Suite 4: Performance Optimizations
   */
  describe('Mobile Performance Optimizations', function() {
    
    it('should apply mobile optimizations on small viewports', async function() {
      await page.setViewport(BREAKPOINTS.mobile);
      
      // Check if mobile optimizations are applied
      const optimizationsApplied = await page.evaluate(() => {
        // This assumes MobileOptimizations is exposed globally
        return typeof MobileOptimizations !== 'undefined' && 
               MobileOptimizations.isEnabled && 
               MobileOptimizations.isMobileDevice;
      });
      
      expect(optimizationsApplied).to.be.true;
    });

    it('should not apply mobile optimizations on desktop', async function() {
      await page.setViewport(BREAKPOINTS.desktop);
      
      // Check if mobile optimizations are not applied on desktop
      const optimizationsNotApplied = await page.evaluate(() => {
        return typeof MobileOptimizations !== 'undefined' && 
               (!MobileOptimizations.isEnabled || !MobileOptimizations.isMobileDevice);
      });
      
      expect(optimizationsNotApplied).to.be.true;
    });
  });

  /**
   * Test Suite 5: Breakpoint Boundary Tests
   */
  describe('Breakpoint Boundary Tests', function() {
    
    it('should correctly transition at mobile/tablet boundary', async function() {
      // Test just below tablet breakpoint
      await page.setViewport({ width: 767, height: 800 });
      
      // Capture mobile layout characteristics
      const mobileLayout = await page.evaluate(() => {
        return {
          isMobileLayout: document.body.classList.contains('mobile-layout') || 
                          window.getComputedStyle(document.body).getPropertyValue('--is-mobile') === 'true'
        };
      });
      
      // Test just at tablet breakpoint
      await page.setViewport({ width: 768, height: 800 });
      
      // Capture tablet layout characteristics
      const tabletLayout = await page.evaluate(() => {
        return {
          isMobileLayout: document.body.classList.contains('mobile-layout') || 
                          window.getComputedStyle(document.body).getPropertyValue('--is-mobile') === 'true'
        };
      });
      
      // Layout should change at the breakpoint
      expect(mobileLayout.isMobileLayout).to.not.equal(tabletLayout.isMobileLayout);
      
      await takeScreenshot(page, 'mobile_tablet_boundary');
    });
  });
});

// Export test utilities for use in other test files
module.exports = {
  BREAKPOINTS,
  EDGE_BREAKPOINTS
};