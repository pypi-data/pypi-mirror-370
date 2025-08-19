const {
    AppBar, Toolbar, Typography, Button, TextField,
    Paper, Container, Box, CircularProgress, Select, MenuItem,
    FormControl, InputLabel, Collapse, Drawer, List, ListItem, ListItemText,
    IconButton, Dialog, DialogTitle, DialogContent, DialogActions
} = MaterialUI;


function OriginalTextDialog({ open, content, onClose }) {
    return React.createElement(Dialog, {
        open: open,
        onClose: onClose,
        maxWidth: 'md',
        fullWidth: true
    },
        React.createElement(DialogContent, null,
            React.createElement(TextField, {
                multiline: true,
                fullWidth: true,
                value: content,
                InputProps: { readOnly: true },
                variant: 'outlined',
                rows: 10
            })
        ),
        React.createElement(DialogActions, null,
            React.createElement(Button, {
                onClick: onClose,
                variant: 'contained'
            }, 'Close')
        )
    );
}

function MessageItem({ message }) {
    const [showOriginal, setShowOriginal] = React.useState(false);
    const messageRef = React.useRef(null);

    React.useEffect(() => {
        if (messageRef.current) {
            // Apply indentation
            window.chatIndentation.applyMessageIndentation(messageRef.current);
            
            // Apply syntax highlighting to code blocks
            const codeBlocks = messageRef.current.querySelectorAll('pre code');
            codeBlocks.forEach((block) => {
                // Apply highlight.js
                hljs.highlightElement(block);
                
                // Add copy button to each code block
                const pre = block.parentNode;
                if (!pre.querySelector('.code-header')) {
                    // Create code block header
                    const header = document.createElement('div');
                    header.className = 'code-header';
                    
                    // Add language display if detected
                    const language = block.className.split(/\s+/).find(cls => cls.startsWith('language-'));
                    if (language) {
                        const langLabel = document.createElement('span');
                        langLabel.className = 'code-language';
                        langLabel.textContent = language.replace('language-', '');
                        header.appendChild(langLabel);
                    }
                    
                    // Add copy button
                    const copyBtn = document.createElement('button');
                    copyBtn.className = 'code-copy-btn';
                    copyBtn.innerHTML = '<span class="material-icons">content_copy</span>';
                    copyBtn.title = 'Copy code';
                    copyBtn.onclick = (e) => {
                        e.stopPropagation();
                        navigator.clipboard.writeText(block.textContent);
                        
                        // Show "Copied!" feedback
                        copyBtn.innerHTML = '<span class="material-icons">check</span>';
                        copyBtn.classList.add('copied');
                        setTimeout(() => {
                            copyBtn.innerHTML = '<span class="material-icons">content_copy</span>';
                            copyBtn.classList.remove('copied');
                        }, 1500);
                    };
                    header.appendChild(copyBtn);
                    
                    // Insert header before the code block
                    pre.insertBefore(header, pre.firstChild);
                    
                    // Add the enhanced class to the pre element
                    pre.classList.add('enhanced-code-block');
                }
            });
        }
    }, [message.content]);

    const handleCopy = (e) => {
        e.stopPropagation();
        navigator.clipboard.writeText(message.content);
    };

    const handleEdit = (e) => {
        e.stopPropagation();
        if (message.type === 'agent') {
            setShowOriginal(true);
        }
    };

    return React.createElement('div', {
            className: `message ${message.type === 'user' ? 'user-message' : 'agent-message'}`,
            ref: messageRef
        },
        React.createElement('div', {
            className: 'message-content',
            dangerouslySetInnerHTML: { __html: marked.parse(message.content) }
        }),
        message.type === 'agent' && React.createElement('div', { className: 'message-controls' },
            React.createElement(IconButton, {
                className: 'copy-button',
                onClick: handleCopy,
                size: 'small',
                title: 'Copy original text'
            },
                React.createElement('span', { className: 'material-icons' }, 'content_copy')
            ),
            React.createElement(IconButton, {
                className: 'edit-button',
                onClick: handleEdit,
                size: 'small',
                title: 'View original text'
            },
                React.createElement('span', { className: 'material-icons' }, 'edit')
            )
        ),
        message.type === 'agent' && React.createElement(OriginalTextDialog, {
            open: showOriginal,
            content: message.content,
            onClose: () => setShowOriginal(false)
        })
    );
}

function TypingIndicator() {
    return React.createElement('div', { className: 'typing-indicator' },
        React.createElement('div', { className: 'typing-dot' }),
        React.createElement('div', { className: 'typing-dot' }),
        React.createElement('div', { className: 'typing-dot' })
    );
}

function MessageList({ messages, isLoading, messagesEndRef }) {
    // Use state to track if typing indicator should be shown
    const [showTypingIndicator, setShowTypingIndicator] = React.useState(false);
    
    // Effect to handle typing indicator animation
    React.useEffect(() => {
        if (isLoading) {
            // Show loading dots first
            setShowTypingIndicator(false);
            
            // After a short delay, show typing indicator
            const timer = setTimeout(() => {
                setShowTypingIndicator(true);
            }, 1000);
            
            return () => clearTimeout(timer);
        } else {
            setShowTypingIndicator(false);
        }
    }, [isLoading]);

    return React.createElement(Box, {
        className: 'chat-messages',
        sx: { flexGrow: 1, mb: 2 }
    },
        messages.map((message, index) =>
            React.createElement(MessageItem, {
                key: index,
                message: message
            })
        ),
        // Show loading dots for initial loading
        isLoading && !showTypingIndicator && React.createElement('div', { className: 'loading-dots' },
            React.createElement('div', { className: 'dot' }),
            React.createElement('div', { className: 'dot' }),
            React.createElement('div', { className: 'dot' })
        ),
        // Show typing indicator when agent is "thinking"
        showTypingIndicator && React.createElement(TypingIndicator),
        React.createElement('div', { ref: messagesEndRef })
    );
}

// Import InputForm component from separate file
// This will be loaded via script tag in HTML

function EditDialog({ open, title, setTitle, onClose, onSubmit }) {
    return React.createElement(Dialog, {
        open: open,
        onClose: onClose
    },
        React.createElement(DialogTitle, null, 'Edit Chat Title'),
        React.createElement(DialogContent, null,
            React.createElement(TextField, {
                autoFocus: true,
                margin: 'dense',
                label: 'Chat Title',
                type: 'text',
                fullWidth: true,
                value: title || '',
                onChange: (e) => setTitle(e.target.value)
            })
        ),
        React.createElement(DialogActions, null,
            React.createElement(Button, { onClick: onClose }, 'Cancel'),
            React.createElement(Button, { onClick: onSubmit }, 'Save')
        )
    );
}
