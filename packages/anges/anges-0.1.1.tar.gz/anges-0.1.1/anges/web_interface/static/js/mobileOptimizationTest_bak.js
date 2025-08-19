/**
 * Mobile Optimization Test Script
 * 
 * This script tests the mobile optimizations implemented in mobileOptimizations.js
 * It verifies that:
 * 1. Device detection works correctly
 * 2. Performance optimizations are applied
 * 3. Animations are reduced on mobile devices
 * 4. Scroll performance is improved
 */

// Self-executing function to avoid global namespace pollution
// Self-executing function to avoid global namespace pollution
(function() {
  console.log('Mobile Optimization Test Script Running...');
  
  // Check if MobileOptimizations exists before proceeding
  if (typeof MobileOptimizations === 'undefined') {
    console.warn('MobileOptimizations not found! Tests will run when it becomes available.');
    
    // Set up a check that will run the tests once MobileOptimizations is available
    const checkInterval = setInterval(() => {
      if (typeof MobileOptimizations !== 'undefined') {
        console.log('MobileOptimizations now available, running tests...');
        clearInterval(checkInterval);
        runTests();
      }
    }, 500);
  } else {
    // MobileOptimizations is already available, run tests directly
    runTests();
  }
  
  // Test device detection
  function testDeviceDetection() {
    console.log('Testing device detection...');
    console.log('isMobile:', MobileOptimizations.isMobile);
    console.log('isLowPoweredDevice:', MobileOptimizations.isLowPoweredDevice);
    
    // Verify that the mobile class is added to the body if on mobile
    if (MobileOptimizations.isMobile) {
      console.assert(
        document.body.classList.contains('mobile-device'),
        'Mobile class not added to body'
      );
    }
    
    // Verify that the low-power class is added if on a low-powered device
    if (MobileOptimizations.isLowPoweredDevice) {
      console.assert(
        document.body.classList.contains('low-powered-device'),
        'Low-powered device class not added to body'
      );
    }
    
    console.log('Device detection test complete');
  }
  
  // Test scroll optimization
  function testScrollOptimization() {
    console.log('Testing scroll optimization...');
    
    // Create a test element to verify passive event listeners
    const testDiv = document.createElement('div');
    testDiv.style.height = '100px';
    testDiv.style.overflow = 'auto';
    
    let passiveSupported = false;
    try {
      const options = Object.defineProperty({}, 'passive', {
        get: function() {
          passiveSupported = true;
          return true;
        }
      });
      testDiv.addEventListener('test', null, options);
    } catch (err) {}
    
    console.log('Passive event listeners supported:', passiveSupported);
    
    // Test if scroll handlers are properly throttled
    const scrollContainer = document.querySelector('.chat-messages-container');
    if (scrollContainer) {
      console.log('Testing scroll throttling on chat container...');
      
      // Simulate rapid scrolling
      for (let i = 0; i < 100; i++) {
        const event = new WheelEvent('wheel', { deltaY: 10 });
        scrollContainer.dispatchEvent(event);
      }
      
      console.log('Scroll optimization test complete');
    } else {
      console.log('Chat container not found, skipping scroll test');
    }
  }
  
  // Test animation reduction
  function testAnimationReduction() {
    console.log('Testing animation reduction...');
    
    // Check if CSS variables for animation duration are properly set
    const computedStyle = getComputedStyle(document.documentElement);
    const animationDuration = computedStyle.getPropertyValue('--animation-duration').trim();
    
    console.log('Animation duration CSS variable:', animationDuration);
    
    if (MobileOptimizations.isMobile) {
      console.assert(
        animationDuration === '0.2s' || animationDuration === '0.15s',
        'Animation duration not reduced on mobile'
      );
    }
    
    // Test if will-change property is applied to animated elements
    const animatedElements = document.querySelectorAll('.chat-history-item, .message');
    if (animatedElements.length > 0) {
      const sampleElement = animatedElements[0];
      const willChange = getComputedStyle(sampleElement).willChange;
      
      console.log('will-change property on animated element:', willChange);
      console.assert(
        willChange.includes('transform') || willChange.includes('opacity'),
        'will-change property not properly set on animated elements'
      );
    }
    
    console.log('Animation reduction test complete');
  }
  
  function runTests() {
    console.log('Starting mobile optimization tests...');
    
    if (typeof MobileOptimizations === 'undefined') {
      console.error('MobileOptimizations not found! Make sure mobileOptimizations.js is loaded before this script.');
      return;
    }
    
    // Run tests
    testDeviceDetection();
    testScrollOptimization();
    testAnimationReduction();
    
    console.log('All mobile optimization tests complete');
    
    // Add a visual indicator that tests have run
    const testResults = document.createElement('div');
    testResults.style.position = 'fixed';
    testResults.style.bottom = '10px';
    testResults.style.right = '10px';
    testResults.style.background = 'rgba(0,0,0,0.7)';
    testResults.style.color = '#fff';
    testResults.style.padding = '10px';
    testResults.style.borderRadius = '5px';
    testResults.style.zIndex = '9999';
    testResults.style.fontSize = '12px';
    testResults.innerHTML = 'Mobile optimization tests complete.<br>Check console for results.';
    document.body.appendChild(testResults);
    
    // Auto-remove after 10 seconds
    setTimeout(() => {
      testResults.remove();
    }, 10000);
  }
  
  // Run all tests when DOM is fully loaded
  document.addEventListener('DOMContentLoaded', function() {
    // Wait a bit to ensure MobileOptimizations has initialized
    setTimeout(() => {
      if (typeof MobileOptimizations !== 'undefined') {
        runTests();
      }
    }, 1000);
  });
})();
