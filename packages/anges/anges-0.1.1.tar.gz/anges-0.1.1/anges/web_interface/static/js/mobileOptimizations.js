/**
 * Mobile Performance Optimizations
 * 
 * This file contains optimizations specifically for mobile devices to improve
 * performance, reduce animations, and provide a smoother experience on
 * low-powered devices.
 */

// Immediately detect device capabilities and set appropriate flags
const MobileOptimizations = (function() {
    // Device detection
    const isMobile = /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);
    const isLowPoweredDevice = isMobile && (
        // iOS detection - older devices or low power mode
        (/iPhone|iPad|iPod/.test(navigator.userAgent) && !window.devicePixelRatio) ||
        // Android detection - check for low memory
        (/Android/.test(navigator.userAgent) && navigator.deviceMemory && navigator.deviceMemory < 4)
    );
    
    // Feature detection
    const supportsPassiveEvents = (function() {
        let supportsPassive = false;
        try {
            const opts = Object.defineProperty({}, 'passive', {
                get: function() {
                    supportsPassive = true;
                    return true;
                }
            });
            window.addEventListener('testPassive', null, opts);
            window.removeEventListener('testPassive', null, opts);
        } catch (e) {}
        return supportsPassive;
    })();
    
    // Add a class to the body for CSS targeting
    if (document.body) {
        document.body.classList.toggle('mobile-device', isMobile);
        document.body.classList.toggle('low-powered-device', isLowPoweredDevice);
    } else {
        // If document.body is not available yet, wait for DOMContentLoaded
        document.addEventListener('DOMContentLoaded', () => {
            document.body.classList.toggle('mobile-device', isMobile);
            document.body.classList.toggle('low-powered-device', isLowPoweredDevice);
        });
    }
    
    
    // Utility functions
    
    /**
     * Debounce function to limit how often a function can be called
     */
    function debounce(func, wait) {
        let timeout;
        return function(...args) {
            const context = this;
            clearTimeout(timeout);
            timeout = setTimeout(() => func.apply(context, args), wait);
        };
    }
    
    /**
     * Throttle function to limit the rate at which a function can fire
     */
    function throttle(func, limit) {
        let inThrottle;
        return function(...args) {
            const context = this;
            if (!inThrottle) {
                func.apply(context, args);
                inThrottle = true;
                setTimeout(() => inThrottle = false, limit);
            }
        };
    }
    
    /**
     * Optimize scroll performance by using passive event listeners and throttling
     */
    function optimizeScrolling(scrollableElement) {
        if (!scrollableElement) return;
        
        // Use passive event listeners if supported
        const scrollOptions = supportsPassiveEvents ? { passive: true } : false;
        
        // Throttled scroll handler
        const throttledScrollHandler = throttle(() => {
            // This empty function ensures the browser's native scrolling is used
            // without JS interference, while still allowing us to hook into the event
        }, 100);
        
        // Add optimized event listener
        scrollableElement.addEventListener('scroll', throttledScrollHandler, scrollOptions);
        
        return {
            destroy: () => {
                scrollableElement.removeEventListener('scroll', throttledScrollHandler, scrollOptions);
            }
        };
    }
    
    /**
     * Optimize touch events for better performance
     */
    function optimizeTouchEvents(element) {
        if (!element || !isMobile) return;
        
        // Use passive event listeners for touch events if supported
        const touchOptions = supportsPassiveEvents ? { passive: true } : false;
        
        // Add touch event listeners with passive option
        element.addEventListener('touchstart', () => {}, touchOptions);
        element.addEventListener('touchmove', () => {}, touchOptions);
        element.addEventListener('touchend', () => {}, touchOptions);
        
        return {
            destroy: () => {
                element.removeEventListener('touchstart', () => {}, touchOptions);
                element.removeEventListener('touchmove', () => {}, touchOptions);
                element.removeEventListener('touchend', () => {}, touchOptions);
            }
        };
    }
    
    /**
     * Lazy load elements using Intersection Observer
     */
    function setupLazyLoading(elements, loadCallback, options = {}) {
        if (!elements || !elements.length) return;
        
        const defaultOptions = {
            root: null,
            rootMargin: '100px 0px',
            threshold: 0.1
        };
        
        const observerOptions = {...defaultOptions, ...options};
        
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    loadCallback(entry.target);
                    observer.unobserve(entry.target);
                }
            });
        }, observerOptions);
        
        elements.forEach(element => {
            observer.observe(element);
        });
        
        return {
            destroy: () => {
                observer.disconnect();
            }
        };
    }
    
    /**
     * Optimize message rendering for mobile devices
     */
    function optimizeMessageRendering() {
        // Find all message elements
        const messages = document.querySelectorAll('.message');
        if (!messages.length) return;
        
        // For low-powered devices, simplify markdown rendering
        if (isLowPoweredDevice) {
            // Replace the marked renderer with a simpler version for low-powered devices
            if (window.marked) {
                const originalMarked = window.marked.parse;
                window.marked.parse = function(text, options) {
                    // For low-powered devices, skip rendering complex elements like tables
                    // or limit the number of elements rendered
                    if (text.length > 5000) {
                        // For very long messages, simplify the rendering
                        text = text.substring(0, 5000) + '...';
                    }
                    return originalMarked(text, options);
                };
            }
        }
        
        // Setup lazy loading for messages
        return setupLazyLoading(
            messages,
            (message) => {
                // When a message comes into view, ensure it's fully rendered
                message.classList.add('fully-rendered');
            }
        );
    }
    
    /**
     * Initialize all mobile optimizations
     */
    function init() {
        // Find scrollable elements
        const chatMessages = document.querySelector('.chat-messages');
        if (chatMessages) {
            optimizeScrolling(chatMessages);
            optimizeTouchEvents(chatMessages);
        }
        
        // Optimize message rendering
        const messageOptimizer = optimizeMessageRendering();
        
        // Optimize input form for mobile
        const inputForm = document.querySelector('.resizable-input');
        if (inputForm) {
            optimizeTouchEvents(inputForm);
        }
        
        // Reduce animation complexity on low-powered devices
        if (isLowPoweredDevice) {
            document.body.classList.add('reduce-animations');
        }
        
        // Optimize resize handling
        const debouncedResize = debounce(() => {
            // Re-run optimizations on resize
            if (messageOptimizer) {
                messageOptimizer.destroy();
                optimizeMessageRendering();
            }
        }, 250);
        
        window.addEventListener('resize', debouncedResize);
        
        // Return cleanup function
        return function cleanup() {
            window.removeEventListener('resize', debouncedResize);
            if (messageOptimizer) {
                messageOptimizer.destroy();
            }
        };
    }
    
    // Public API
    return {
        isMobile,
        isLowPoweredDevice,
        init,
        debounce,
        throttle,
        optimizeScrolling,
        optimizeTouchEvents,
        setupLazyLoading
    };
})();

// Initialize optimizations when DOM is ready
document.addEventListener('DOMContentLoaded', MobileOptimizations.init);