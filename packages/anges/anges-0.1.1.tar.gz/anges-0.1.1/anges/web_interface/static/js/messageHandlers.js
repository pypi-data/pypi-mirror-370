function useMessageHandlers(coreState, historyState) {
    // Function to extract chatId from URL
    const getChatIdFromUrl = () => {
        const urlParams = new URLSearchParams(window.location.search);
        return urlParams.get('chatId');
    };
    const handleSubmit = async (e) => {
        // Check if event object exists before calling preventDefault
        if (e && e.preventDefault) {
            e.preventDefault();
        }
        
        // For normal submissions (not resuming a task), require non-empty input
        // For resuming a task, we allow empty input
        const isResumingTask = coreState.hasActiveTask && (!coreState.userInput || !coreState.userInput.trim());
        if (!isResumingTask && (!coreState.userInput || !coreState.userInput.trim())) return;
        
        // Only add a user message if we're not resuming a task
        if (!isResumingTask) {
            coreState.setMessages(prev => [...prev, { type: 'user', content: coreState.userInput }]);
        }
        
        // Always set loading state when submitting or resuming
        coreState.setIsLoading(true);
        // Get chatId from URL
        const chatId = getChatIdFromUrl();

        try {
            // If no chatId exists, create a new chat first
            let currentChatId = chatId;
            if (!currentChatId) {
                try {
                    const newChatResponse = await fetch('/new-chat');
                    
                    if (newChatResponse.ok) {
                        const data = await newChatResponse.json();
                        
                        if (data && data.chat_id) {
                            // Update the URL with the new chat ID
                            window.history.pushState({}, '', `?chatId=${data.chat_id}`);
                            
                            // Set the current chat ID to the new one
                            currentChatId = data.chat_id;
                            
                            // Update state
                            historyState.setSelectedChat(data.chat_id);
                            
                            // Update chat history
                            historyState.fetchChatHistory();
                        } else {
                            console.error('No chat ID returned from server');
                            alert('Failed to create new chat: No chat ID returned');
                            coreState.setIsLoading(false);
                            return;
                        }
                    } else {
                        alert(`Failed to create new chat: ${newChatResponse.status} - ${newChatResponse.statusText}`);
                        coreState.setIsLoading(false);
                        return;
                    }
                } catch (error) {
                    console.error('Error creating new chat:', error);
                    alert(`Error creating new chat: ${error.message}`);
                    coreState.setIsLoading(false);
                    return;
                }
            }

            // Get current chat's MCP configuration before submitting
            let mcpConfig = {};
            try {
                const chatResponse = await fetch(`/load-chat/${currentChatId}`);
                if (chatResponse.ok) {
                    const chatData = await chatResponse.json();
                    if (chatData.status === 'success' && chatData.mcp_config) {
                        mcpConfig = chatData.mcp_config;
                    }
                }
            } catch (error) {
                console.warn('Failed to load MCP config for message submission:', error);
            }

            // Now submit the message using the current chat ID (either existing or newly created)
            const response = await fetch(`/submit/${currentChatId}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    message: coreState.userInput,
                    cmd_init_dir: coreState.workingDir,
                    prefix_cmd: coreState.prefixCmd,
                    model: coreState.modelType,
                    agent_type: coreState.agentType,
                    notes: coreState.notes,
                    mcp_config: mcpConfig
                })
            });

            if (!response.ok) {
                alert(`Failed to send chat message: ${response.status} - ${response.statusText}`);
                coreState.setIsLoading(false);
                return;
            }

            // Set up event source for streaming the response
            const streamUrl = `/stream/${currentChatId}`;
            const newEventSource = new EventSource(streamUrl);
            coreState.setEventSource(newEventSource);

            newEventSource.onmessage = (event) => {
                const data = JSON.parse(event.data);
                if (data.message === 'STREAM_COMPLETE') {
                    newEventSource.close();
                    coreState.setEventSource(null);
                    coreState.setIsLoading(false);
                    coreState.setHasActiveTask(false); // Reset active task status when stream completes
                    historyState.fetchChatHistory();
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
                coreState.setHasActiveTask(false); // Reset active task status on error too
            };
        } catch (error) {
            console.error('Error:', error);
            coreState.setIsLoading(false);
        }

        coreState.setUserInput('');
    };

    const handleInterrupt = async () => {
        // Get chatId from URL
        const chatId = getChatIdFromUrl();
        
        try {
            // Include chatId in interrupt URL if available
            const interruptUrl = chatId ? `/interrupt/${chatId}` : '/interrupt';
            const response = await fetch(interruptUrl, { method: 'POST' });
            
            if (response.ok) {
                if (coreState.eventSource) {
                    coreState.eventSource.close();
                    coreState.setEventSource(null);
                }
                coreState.setIsLoading(false);
            }
        } catch (error) {
            console.error('Error interrupting:', error);
        }
    };

    const handleNewChat = async () => {
        try {
            const response = await fetch('/new-chat');
            
            if (response.ok) {
                // Parse the response to get the new chat ID
                const data = await response.json();

                if (data && data.chat_id) {
                    // Navigate to the new chat
                    window.history.pushState({}, '', `?chatId=${data.chat_id}`);
                    
                    // Update state
                    coreState.setSelectedChat(data.chat_id);
                    coreState.setMessages([]);
                    
                    if (coreState.eventSource) {
                        coreState.eventSource.close();
                        coreState.setEventSource(null);
                    }

                    // Update chat history
                    historyState.fetchChatHistory();
                } else {
                    console.error('No chat ID returned from server');
                    alert('Failed to create new chat: No chat ID returned');
                }
            } else {
                alert(`Failed to create new chat: ${response.status} - ${response.statusText}`);
            }
        } catch (error) {
            console.error('Error creating new chat:', error);
            alert(`Error creating new chat: ${error.message}`);
        }
    };
    return {
        handleSubmit,
        handleInterrupt,
        handleNewChat,
        getCoreState: () => coreState,
        getHistoryState: () => historyState
    };
}
