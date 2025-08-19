const {
    AppBar, Toolbar, Typography, Button, TextField,
    Paper, Container, Box, CircularProgress, Select, MenuItem,
    FormControl, InputLabel, Collapse, Drawer, List, ListItem, ListItemText,
    IconButton, Dialog, DialogTitle, DialogContent, DialogActions
} = MaterialUI;

function convertTokenNumber(num) {
    if (num >= 1000000) {
      const formatted = (num / 1000000).toFixed(1);
      return parseFloat(formatted) + 'M';
    } else if (num >= 1000) {
      const formatted = (num / 1000).toFixed(1);
      return parseFloat(formatted) + 'K';
    } else {
      return num.toString();
    }
  }


function useChatCore() {
    const [messages, setMessages] = React.useState([]);
    const [messageFilterMode, setMessageFilterMode] = React.useState('all');
    const [userInput, setUserInput] = React.useState('');
    const [isLoading, setIsLoading] = React.useState(false);
    const [showSettings, setShowSettings] = React.useState(false);
    const [modelType, setModelType] = React.useState('agent_default');
    const [agentType, setAgentType] = React.useState('default');
    const [workingDir, setWorkingDir] = React.useState('~');
    const [prefixCmd, setPrefixCmd] = React.useState('');
    const [eventSource, setEventSource] = React.useState(null);
    const [selectedChat, setSelectedChat] = React.useState(null);
    const [hasActiveTask, setHasActiveTask] = React.useState(false);
    const [notes, setNotes] = React.useState([]);
    const messagesEndRef = React.useRef(null);
    const [isAtBottom, setIsAtBottom] = React.useState(true);

    // Function to filter messages based on current filter mode
    const getFilteredMessages = () => {
        if (messageFilterMode === 'all') {
            return messages;
        } else if (messageFilterMode === 'simplified') {
            return messages.filter(message => {
                // Always show user messages
                if (message.type === 'user') {
                    return true;
                }
                // For agent messages, only show those with no parent IDs (direct parent messages)
                if (message.type === 'agent') {
                    const parentCount = window.chatIndentation ? 
                        window.chatIndentation.getParentCount(message.content) : 0;
                    return parentCount === 0;
                }
                return false;
            });
        }
        return messages;
    };
    // Function to check if user is scrolled to bottom
    const checkIfAtBottom = () => {
        const chatContainer = document.querySelector('.chat-messages');
        if (chatContainer) {
            // Calculate how far from bottom (with a small threshold for rounding errors)
            const isScrolledToBottom = 
                chatContainer.scrollHeight - chatContainer.scrollTop - chatContainer.clientHeight < 50;
            setIsAtBottom(isScrolledToBottom);
        }
    };

    // Add scroll event listener to track user scroll position
    React.useEffect(() => {
        const chatContainer = document.querySelector('.chat-messages');
        if (chatContainer) {
            chatContainer.addEventListener('scroll', checkIfAtBottom);
            return () => chatContainer.removeEventListener('scroll', checkIfAtBottom);
        }
    }, []);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    };

    // Function to check if a chat has an active task
    const checkActiveTask = async (chatId) => {
        if (!chatId) return false;
        
        try {
            const response = await fetch(`/check_stream/${chatId}`);
            const data = await response.json();
            
            if (data.status === 'success') {
                setHasActiveTask(data.has_active_task);
                return data.has_active_task;
            }
            return false;
        } catch (error) {
            console.error('Error checking active task:', error);
            return false;
        }
    };

    const handleChatSelect = async (chatId) => {
        if (isLoading) return; // Prevent selection while loading
        
        try {
            const response = await fetch(`/load-chat/${chatId}`);
            const data = await response.json();
            if (data.status === 'success') {
                // Update the URL parameter to reflect the selected chat
                const newUrl = new URL(window.location.href);
                newUrl.searchParams.set('chatId', chatId);
                window.history.replaceState({}, '', newUrl.toString());

                const est_input_token = convertTokenNumber(data.est_input_token || 0);
                const est_output_token = convertTokenNumber(data.est_output_token || 0);
                console.log(`Loaded Event Stream ${chatId}\nTotal Events: ${data.events.length}\nEst Input Token: ${est_input_token}\nEst Output Token: ${est_output_token}`)

                // Update agent settings if provided
                if (data.agent_settings) {
                    const settings = data.agent_settings;
                    if (settings.cmd_init_dir) setWorkingDir(settings.cmd_init_dir);
                    if (settings.model) setModelType(settings.model);
                    if (settings.prefix_cmd) setPrefixCmd(settings.prefix_cmd);
                    if (settings.agent_type) setAgentType(settings.agent_type);
                    if (settings.notes) setNotes(settings.notes);
                    else setNotes([]);
                    
                    // Add debug logging
                    console.log('Updated agent settings:', {
                        workingDir: settings.cmd_init_dir,
                        modelType: settings.model,
                        prefixCmd: settings.prefix_cmd,
                        agentType: settings.agent_type,
                        notes: settings.notes
                    });
                } else {
                    // Reset notes to empty array when no agent settings exist
                    setNotes([]);
                }

                setSelectedChat(chatId);
                // Transform events into message format
                setMessages(data.events.map(event => ({
                    type: ["new_request", "follow_up_request"].includes(event.type) ? 'user' : 'agent',
                    content: event.message
                })));
                
                // Check if the chat has an active task
                await checkActiveTask(chatId);
                
                return true;
            }
            return false; 
        } catch (error) {
            console.error('Error loading chat:', error);
            return false;
        }
    };

    // Only scroll to bottom when messages change if user was already at the bottom
    React.useEffect(() => {
        if (isAtBottom) {
            scrollToBottom();
        }
    }, [messages, isAtBottom]);
    
    return {
        messages, setMessages,
        messageFilterMode, setMessageFilterMode,
        getFilteredMessages,
        userInput, setUserInput,
        isLoading, setIsLoading,
        showSettings, setShowSettings,
        modelType, setModelType,
        agentType, setAgentType,
        workingDir, setWorkingDir,
        prefixCmd, setPrefixCmd,
        eventSource, setEventSource,
        selectedChat, setSelectedChat,
        hasActiveTask, setHasActiveTask,
        notes, setNotes,
        messagesEndRef,
        scrollToBottom,
        handleChatSelect,
        checkActiveTask
    };
}
