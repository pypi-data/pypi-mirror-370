// inputForm.js - Enhanced Chat Input Component
const { TextField, Box, IconButton, Paper, CircularProgress, Tooltip, Fade, Zoom } = MaterialUI;

/**
 * InputForm Component
 * Renders an enhanced chat input field with modern styling and improved user experience.
 * Features:
 * - Auto-expanding input area
 * - Modern styling with theme colors
 * - Input status indicators
 * - Enhanced send button with animations
 * - Responsive design for all screen sizes
 * - Responsive width adjustment for settings drawer
 * @param {Object} props - Component props
 * @param {string} props.userInput - Current input value
 * @param {Function} props.setUserInput - Function to update input value
 * @param {boolean} props.isLoading - Loading state indicator
 * @param {Object} props.handlers - Event handlers for form submission
 * @param {boolean} props.hasActiveTask - Whether there's an active task
 * @param {boolean} props.isSettingsOpen - Whether the settings drawer is open
 */
function InputForm({ userInput, setUserInput, isLoading, handlers, hasActiveTask, isSettingsOpen }) {
    // State for tracking input focus and typing status
    const [isFocused, setIsFocused] = React.useState(false);
    const [isTyping, setIsTyping] = React.useState(false);
    const typingTimerRef = React.useRef(null);
    
    // Get current theme from Material-UI
    const theme = MaterialUI.useTheme();
    const isDarkMode = theme.palette.mode === 'dark';
    
    // Handler for key down events in the text field
    const handleKeyDown = (e) => {
        if (e.key === 'Enter' && !e.shiftKey && !isLoading) {
            e.preventDefault(); // Prevent default newline on Enter
            if (userInput && userInput.trim()) {
                handlers.handleSubmit(e);
            }
        }
    };
    
    // Handler for input changes with typing indicator
    const handleInputChange = (e) => {
        setUserInput(e.target.value);
        
        // Show typing indicator
        setIsTyping(true);
        
        // Clear previous timer
        if (typingTimerRef.current) {
            clearTimeout(typingTimerRef.current);
        }
        
        // Set timer to hide typing indicator after 1 second of inactivity
        typingTimerRef.current = setTimeout(() => {
            setIsTyping(false);
        }, 1000);
    };
    
    // Clean up timer on unmount
    React.useEffect(() => {
        return () => {
            if (typingTimerRef.current) {
                clearTimeout(typingTimerRef.current);
            }
        };
    }, []);

    // Main component structure using React.createElement
    return React.createElement(Paper, {
        elevation: isDarkMode ? 4 : 3, // Slightly higher elevation in dark mode
        sx: {
            // Container Styling
            display: 'flex',
            flexDirection: 'column', // Stack input and controls vertically
            borderRadius: '24px', // More pronounced rounded corners
            padding: '12px 16px 10px 16px', // Increased padding
            backgroundColor: 'background.paper',
            border: isDarkMode 
                ? '1px solid rgba(255, 255, 255, 0.12)' 
                : '1px solid rgba(0, 0, 0, 0.08)',
            boxShadow: isFocused
                ? (isDarkMode 
                    ? '0 4px 12px rgba(0, 0, 0, 0.3), 0 0 0 2px rgba(84, 114, 211, 0.3)' 
                    : '0 4px 12px rgba(13, 71, 161, 0.1), 0 0 0 2px rgba(13, 71, 161, 0.2)')
                : undefined, // Dynamic shadow based on focus state
            overflow: 'hidden', // Keep content within rounded corners
            margin: '10px', // Increased margin around the input box
            position: 'relative', // Context for positioning elements
            transition: 'all 0.2s ease-in-out', // Smooth transition for hover/focus effects
            '&:hover': {
                boxShadow: !isFocused && (isDarkMode 
                    ? '0 4px 8px rgba(0, 0, 0, 0.25)' 
                    : '0 4px 8px rgba(0, 0, 0, 0.08)'),
            },
        }
    },
        // Input status indicator (typing/sending)
        isTyping && !isLoading && React.createElement(Box, {
            sx: {
                position: 'absolute',
                top: '8px',
                left: '16px',
                fontSize: '0.75rem',
                color: 'text.secondary',
                opacity: 0.7,
                display: 'flex',
                alignItems: 'center',
                gap: '4px',
            }
        }, 
            React.createElement('span', {
                className: 'material-icons',
                style: { fontSize: '14px' }
            }, 'edit'),
            "Typing..."
        ),
        
        // TextField for user input
        React.createElement(TextField, {
            fullWidth: true,
            multiline: true,
            minRows: 1,
            maxRows: 10, // Limit max rows before scrolling kicks in
            value: userInput || '',
            onChange: handleInputChange,
            onKeyDown: handleKeyDown,
            onFocus: () => setIsFocused(true),
            onBlur: () => setIsFocused(false),
            placeholder: isLoading ? "AI is responding..." : "Type your message here...",
            variant: 'standard', // Use standard variant for cleaner look
            disabled: isLoading, // Disable input while loading
            InputProps: {
                disableUnderline: true, // Remove the default underline
                sx: {
                    fontSize: '1rem',
                    lineHeight: '1.5',
                    color: isLoading ? 'text.disabled' : 'text.primary',
                    transition: 'color 0.2s ease',
                }
            },
            sx: {
                // Styling for the TextField wrapper
                overflowY: 'auto', // Enable vertical scroll when maxRows/maxHeight is exceeded
                maxHeight: '40vh', // Limit overall height
                scrollbarWidth: 'thin', // For Firefox
                '&::-webkit-scrollbar': { // For Chrome, Safari, Edge
                    width: '6px',
                },
                '&::-webkit-scrollbar-thumb': {
                    backgroundColor: isDarkMode ? 'rgba(255,255,255,.2)' : 'rgba(0,0,0,.1)',
                    borderRadius: '3px',
                },
                mt: isTyping ? '16px' : 0, // Add margin top when typing indicator is shown
                transition: 'margin-top 0.2s ease',
            }
        }),
        
        // Controls area with send/stop button
        React.createElement(Box, {
            sx: {
                display: 'flex',
                justifyContent: 'space-between', // Space between typing indicator and buttons
                alignItems: 'center', // Vertically center elements
                minHeight: '36px', // Ensure minimum height for controls row
                paddingTop: '8px', // Add space above the button
                marginTop: '2px', // Add space between input and controls
            }
        },
            // Left side - AI response indicator
            isLoading && React.createElement(Box, {
                sx: {
                    display: 'flex',
                    alignItems: 'center',
                    gap: '8px',
                    color: 'text.secondary',
                    fontSize: '0.875rem',
                }
            },
                React.createElement(CircularProgress, {
                    size: 16,
                    thickness: 4,
                    sx: { color: 'primary.main' }
                }),
                "AI is responding..."
            ),
            
            // Right side - Buttons
            React.createElement(Box, {
                sx: {
                    display: 'flex',
                    gap: '8px',
                    alignItems: 'center',
                    ml: 'auto', // Push to right side
                }
            },
                // If there's an active task, show a resume button
                hasActiveTask && !isLoading ? 
                // Resume button for active tasks
                React.createElement(MaterialUI.Button, {
                    variant: 'contained',
                    color: 'primary',
                    onClick: () => {
                        // Directly connect to the streaming endpoint instead of using submit handler
                        const chatId = new URLSearchParams(window.location.search).get('chatId');
                        if (chatId) {
                            // Set up event source for streaming the response
                            const streamUrl = `/stream/${chatId}`;
                            const newEventSource = new EventSource(streamUrl);
                            
                            // Access the correct methods through the handlers object
                            // These methods are passed from coreState to messageHandlers
                            const coreState = handlers.getCoreState();
                            coreState.setEventSource(newEventSource);
                            coreState.setIsLoading(true);
                
                            newEventSource.onmessage = (event) => {
                                const data = JSON.parse(event.data);
                                if (data.type === 'complete') {
                                    newEventSource.close();
                                    coreState.setEventSource(null);
                                    coreState.setIsLoading(false);
                                    // Fetch chat history after completion
                                    handlers.getHistoryState().fetchChatHistory();
                                } else {
                                    // Display the entire message at once instead of streaming
                                    const content = data.content;
                                    
                                    coreState.setMessages(prev => {
                                        // Always add a new message box for each new message
                                        return [...prev, { type: 'agent', content: content, isStreaming: false }];
                                    });
                                }
                            };
                
                            newEventSource.onerror = (error) => {
                                console.error('SSE Error:', error);
                                newEventSource.close();
                                coreState.setEventSource(null);
                                coreState.setIsLoading(false);
                            };
                        }
                    },
                    startIcon: React.createElement('span', {
                        className: 'material-icons',
                    }, 'play_arrow'),
                    sx: {
                        borderRadius: '20px',
                        padding: '6px 16px',
                        boxShadow: '0 2px 5px rgba(0,0,0,0.1)',
                        transition: 'all 0.2s ease',
                        '&:hover': {
                            transform: 'translateY(-1px)',
                            boxShadow: '0 4px 8px rgba(0,0,0,0.15)',
                        },
                        '&:active': {
                            transform: 'translateY(1px)',
                            boxShadow: '0 1px 3px rgba(0,0,0,0.1)',
                        }
                    }
                }, "Resume Streaming") : null,
                
                // Send / Stop Button with enhanced styling and tooltip
                React.createElement(Tooltip, {
                    title: isLoading ? "Stop generating" : "Send message",
                    placement: "top",
                    TransitionComponent: Zoom,
                    arrow: true
                },
                    React.createElement(Fade, {
                        in: true,
                    },
                        React.createElement(IconButton, {
                            size: 'medium',
                            onClick: isLoading ? handlers.handleInterrupt : handlers.handleSubmit,
                            disabled: !isLoading && (!userInput || !userInput.trim()),
                            sx: {
                                backgroundColor: isLoading 
                                    ? 'error.light' 
                                    : 'primary.main',
                                color: '#fff',
                                width: '40px',
                                height: '40px',
                                transition: 'all 0.2s ease',
                                '&:hover': {
                                    backgroundColor: isLoading 
                                        ? 'error.main' 
                                        : 'primary.dark',
                                    transform: 'scale(1.05)',
                                },
                                '&:active': {
                                    transform: 'scale(0.95)',
                                },
                                '&.Mui-disabled': {
                                    backgroundColor: isDarkMode 
                                        ? 'rgba(255, 255, 255, 0.12)' 
                                        : 'rgba(0, 0, 0, 0.12)',
                                    color: isDarkMode 
                                        ? 'rgba(255, 255, 255, 0.3)' 
                                        : 'rgba(0, 0, 0, 0.26)',
                                }
                            }
                        },
                            // Icon inside the button
                            React.createElement('span', {
                                className: 'material-icons',
                                style: { 
                                    fontSize: '20px',
                                    transition: 'transform 0.2s ease'
                                }
                            },
                                isLoading ? 'stop' : 'send' // Use stop or send icon
                            )
                        )
                    )
                )
            )
        )
    );
}

// Export the component
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { InputForm };
} else {
    window.InputForm = InputForm;
}
