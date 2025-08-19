// anges/web_interface/static/js/SettingsPanel.js

// Assuming React is global or otherwise available (e.g. via <script> tag)
// Assuming MaterialUI is global or otherwise available (e.g. via <script> tag)

const {
    Drawer, Paper, Typography, TextField, Select, MenuItem,
    FormControl, InputLabel, Button, Modal, Box, List, ListItem,
    ListItemText, ListItemSecondaryAction, IconButton, Divider,
    Tooltip, CircularProgress, Snackbar
} = MaterialUI;

function SettingsPanel({ coreState, onClose }) {
    // Add null check for coreState to prevent "Cannot read properties of undefined" error
    const modelType = coreState?.modelType || '';
    const agentType = coreState?.agentType || '';
    const workingDir = coreState?.workingDir || '';
    const prefixCmd = coreState?.prefixCmd || '';
    
    // Notes state management - ensure notes is always an array
    const rawNotes = coreState?.notes;
    const [notesModalOpen, setNotesModalOpen] = React.useState(false);
    const notes = Array.isArray(rawNotes) ? rawNotes : [];
    const [currentNote, setCurrentNote] = React.useState(null);
    const [noteForm, setNoteForm] = React.useState({
        title: '',
        content: '',
        scope: 'agent'
    });
    
    // MCP state management
    const [mcpClients, setMcpClients] = React.useState([]);
    const [mcpConfig, setMcpConfig] = React.useState({});
    const [mcpConfigModalOpen, setMcpConfigModalOpen] = React.useState(false);
    const [mcpConfigJson, setMcpConfigJson] = React.useState('{}');
    const [mcpLoading, setMcpLoading] = React.useState(false);
    const [refreshingMcp, setRefreshingMcp] = React.useState(false);
    
    // Snackbar state for notifications
    const [snackbar, setSnackbar] = React.useState({
        open: false,
        message: '',
        severity: 'info' // 'success', 'error', 'warning', 'info'
    });
    
    // Safely handle setters with null checks
    const handleModelChange = (e) => {
        if (coreState && coreState.setModelType) {
            coreState.setModelType(e.target.value);
        }
    };
    
    const handleAgentChange = (e) => {
        if (coreState && coreState.setAgentType) {
            coreState.setAgentType(e.target.value);
        }
    };
    
    const handleWorkingDirChange = (e) => {
        if (coreState && coreState.setWorkingDir) {
            coreState.setWorkingDir(e.target.value);
        }
    };
    
    const handlePrefixCmdChange = (e) => {
        if (coreState && coreState.setPrefixCmd) {
            coreState.setPrefixCmd(e.target.value);
        }
    };
    
    // Notes management functions
    const handleOpenNotesModal = () => {
        setNotesModalOpen(true);
        setCurrentNote(null);
        setNoteForm({ title: '', content: '', scope: 'agent' });
    };
    
    const handleCloseNotesModal = () => {
        setNotesModalOpen(false);
        setCurrentNote(null);
        setNoteForm({ title: '', content: '', scope: 'agent' });
    };
    
    const handleEditNote = (note) => {
        setCurrentNote(note);
        setNoteForm({
            title: note.title,
            content: note.content,
            scope: note.scope
        });
        setNotesModalOpen(true);
    };
    
    const handleSaveNote = () => {
        if (!noteForm.title.trim()) return;
        
        const newNote = {
            id: currentNote ? currentNote.id : Date.now().toString(),
            title: noteForm.title.trim(),
            content: noteForm.content.trim(),
            scope: noteForm.scope,
            timestamp: currentNote ? currentNote.timestamp : new Date().toISOString()
        };
        
        let updatedNotes;
        if (currentNote) {
            // Edit existing note
            updatedNotes = notes.map(note => 
                note.id === currentNote.id ? newNote : note
            );
        } else {
            // Add new note
            updatedNotes = [...notes, newNote];
        }
        
        // Update coreState.notes
        if (coreState && coreState.setNotes) {
            coreState.setNotes(updatedNotes);
        }
        
        handleCloseNotesModal();
    };
    
    const handleDeleteNote = (noteId) => {
        const updatedNotes = notes.filter(note => note.id !== noteId);
        if (coreState && coreState.setNotes) {
            coreState.setNotes(updatedNotes);
        }
    };
    
    const handleNoteFormChange = (field, value) => {
        setNoteForm(prev => ({
            ...prev,
            [field]: value
        }));
    };
    
    // MCP management functions
    const loadMcpData = async () => {
        try {
            const currentChatId = coreState?.selectedChat;
            if (!currentChatId) {
                setMcpConfig({});
                setMcpClients([]);
                return;
            }

            const response = await fetch(`/load-chat/${currentChatId}`);
            if (response.ok) {
                const data = await response.json();
                if (data.status === 'success') {
                    setMcpConfig(data.mcp_config || {});
                    setMcpClients(data.mcp_clients || []);
                }
            }
        } catch (error) {
            console.error('Failed to load MCP data:', error);
        }
    };

    const refreshMcpClients = async () => {
        try {
            setRefreshingMcp(true);
            const response = await fetch('/api/mcp/refresh', {
                method: 'POST'
            });
            if (response.ok) {
                const data = await response.json();
                // Update local state with refreshed client data
                setMcpClients(data.mcp_clients || []);
                showNotification('MCP clients refreshed successfully', 'success');
            } else {
                const errorData = await response.json();
                showNotification(`Failed to refresh MCP clients: ${errorData.message || 'Unknown error'}`, 'error');
            }
        } catch (error) {
            console.error('Failed to refresh MCP clients:', error);
            showNotification('Failed to refresh MCP clients', 'error');
        } finally {
            setRefreshingMcp(false);
        }
    };
    
    const handleOpenMcpConfigModal = () => {
        // Load current MCP config into the modal
        setMcpConfigJson(JSON.stringify(mcpConfig, null, 2));
        setMcpConfigModalOpen(true);
    };
    
    const handleCloseMcpConfigModal = () => {
        setMcpConfigModalOpen(false);
    };
    
    const handleSaveMcpConfig = async () => {
        try {
            // Validate JSON format
            const parsedConfig = JSON.parse(mcpConfigJson);
            
            setMcpLoading(true);
            const response = await fetch('/api/mcp/config', {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ mcp_config: parsedConfig })
            });
            
            if (response.ok) {
                // Update local state with new configuration
                setMcpConfig(parsedConfig);
                
                // Refresh client status to get updated connection info
                await refreshMcpClients();
                
                handleCloseMcpConfigModal();
                showNotification('MCP configuration updated successfully', 'success');
            } else {
                const errorData = await response.json();
                showNotification(`Failed to save MCP configuration: ${errorData.message || 'Unknown error'}`, 'error');
            }
        } catch (error) {
            if (error instanceof SyntaxError) {
                showNotification('Invalid JSON format. Please check your configuration.', 'error');
            } else {
                console.error('Failed to save MCP configuration:', error);
                showNotification('Failed to save MCP configuration', 'error');
            }
        } finally {
            setMcpLoading(false);
        }
    };
    
    const handleRefreshMcp = async () => {
        await refreshMcpClients();
    };
    
    // Notification functions
    const showNotification = (message, severity = 'info') => {
        setSnackbar({
            open: true,
            message: message,
            severity: severity
        });
    };
    
    const handleCloseSnackbar = (event, reason) => {
        if (reason === 'clickaway') {
            return;
        }
        setSnackbar(prev => ({ ...prev, open: false }));
    };
    
    // Load MCP data when settings panel opens or selected chat changes
    React.useEffect(() => {
        if (coreState?.showSettings) {
            loadMcpData();
        }
    }, [coreState?.showSettings, coreState?.selectedChat]);
    
    return React.createElement(MaterialUI.Drawer, {
        anchor: "right",
        open: coreState?.showSettings || false,
        onClose: undefined, // Disable onClose to prevent outside click closing
        variant: "persistent", // Use persistent variant to push content aside
        hideBackdrop: true, // Remove backdrop/overlay
        sx: {
            '& .MuiDrawer-paper': {
                zIndex: (theme) => theme.zIndex.drawer, // Ensure proper z-index below AppBar
            }
        }
    },
        React.createElement(Paper, {
            sx: {
                p: 3,
                pt: 11, // Add top padding to account for AppBar (64px + some extra spacing)
                width: 320,
                height: '100%', 
                overflow: 'auto'
            }
        },
            React.createElement(Typography, {
                variant: 'h6',
                sx: { mb: 2 }
            }, 'Settings'),
            
            // Model selection
            React.createElement(FormControl, { fullWidth: true, sx: { mb: 2 } },
                React.createElement(InputLabel, null, 'Model'),
                React.createElement(Select, {
                    value: modelType,
                    label: 'Model',
                    onChange: handleModelChange
                },
                    React.createElement(MenuItem, { value: 'agent_default' }, 'Default'),
                    React.createElement(MenuItem, { value: 'claude' }, 'Claude'),
                    React.createElement(MenuItem, { value: 'vertex_claude' }, 'VertexClaude'),
                    React.createElement(MenuItem, { value: 'gemini' }, 'Gemini'),
                    React.createElement(MenuItem, { value: 'openai' }, 'OpenAI'),
                    React.createElement(MenuItem, { value: 'deepseek' }, 'DeepSeek'),
                )
            ),
            
            // Agent Type selection
            React.createElement(FormControl, { fullWidth: true, sx: { mb: 2 } },
                React.createElement(InputLabel, null, 'Agent Type'),
                React.createElement(Select, {
                    value: agentType,
                    label: 'Agent Type',
                    onChange: handleAgentChange
                },
                    React.createElement(MenuItem, { value: 'default' }, 'Default'),
                    React.createElement(MenuItem, { value: 'task_executor' }, 'TaskExecutor'),
                    React.createElement(MenuItem, { value: 'task_analyzer' }, 'TaskAnalyzer'),
                    React.createElement(MenuItem, { value: 'orchestrator' }, 'Orchestrator')
                )
            ),
            
            // Working Directory
            React.createElement(TextField, {
                fullWidth: true,
                label: 'Working Directory',
                value: workingDir,
                onChange: handleWorkingDirChange,
                variant: 'outlined',
                sx: { mb: 2 }
            }),
            
            // Prefix Command
            React.createElement(TextField, {
                fullWidth: true,
                label: 'Prefix Command',
                value: prefixCmd,
                onChange: handlePrefixCmdChange,
                variant: 'outlined',
                sx: { mb: 3 }
            }),
            
            // Notes section
            React.createElement(Divider, { sx: { my: 3 } }),
            React.createElement(Box, {
                sx: { 
                    display: 'flex', 
                    alignItems: 'center', 
                    justifyContent: 'space-between',
                    mb: 2 
                }
            },
                React.createElement(Typography, {
                    variant: 'h6'
                }, 'Notes'),
                React.createElement(IconButton, {
                    size: 'small',
                    onClick: handleOpenNotesModal,
                    sx: { 
                        ml: 1,
                        color: 'primary.main'
                    }
                }, '+')
            ),
            
            // Notes list
            notes.length > 0 && React.createElement(List, { dense: true },
                notes.map(note => 
                    React.createElement(ListItem, { 
                        key: note.id,
                        sx: { px: 0 }
                    },
                        React.createElement(ListItemText, {
                            primary: note.title,
                            secondary: `Scope: ${note.scope}`,
                            primaryTypographyProps: { variant: 'body2' },
                            secondaryTypographyProps: { variant: 'caption' }
                        }),
                        React.createElement(ListItemSecondaryAction, null,
                            React.createElement(IconButton, {
                                size: 'small',
                                onClick: () => handleEditNote(note),
                                sx: { mr: 1 }
                            }, '✏️'),
                            React.createElement(IconButton, {
                                size: 'small',
                                onClick: () => handleDeleteNote(note.id)
                            }, '🗑️')
                        )
                    )
                )
            ),
            
            // MCP section
            React.createElement(Divider, { sx: { my: 3 } }),
            React.createElement(Box, {
                sx: { 
                    display: 'flex', 
                    alignItems: 'center', 
                    justifyContent: 'space-between',
                    mb: 2 
                }
            },
                React.createElement(Typography, {
                    variant: 'h6'
                }, 'MCP'),
                React.createElement(Box, { sx: { display: 'flex', gap: 1 } },
                    React.createElement(IconButton, {
                        size: 'small',
                        onClick: handleOpenMcpConfigModal,
                        sx: { 
                            color: 'primary.main'
                        }
                    }, '✏️'),
                    React.createElement(IconButton, {
                        size: 'small',
                        onClick: handleRefreshMcp,
                        disabled: refreshingMcp,
                        sx: { 
                            color: 'primary.main'
                        }
                    }, refreshingMcp ? React.createElement(CircularProgress, { size: 16 }) : '🔄')
                )
            ),
            
            // MCP clients list
            mcpClients.length > 0 ? React.createElement(List, { dense: true },
                mcpClients.map(mcp => {
                    // 从status字段读取状态，True为绿灯，False为灰灯
                    const statusIcon = mcp.status === true || mcp.status === 'True' ? '🟢' : '⚪';
                    const toolsTooltip = mcp.tools && mcp.tools.length > 0 
                        ? mcp.tools.map(tool => tool.name).join(', ')
                        : 'No tools available';
                    
                    return React.createElement(Tooltip, {
                        key: mcp.name,
                        title: toolsTooltip,
                        placement: 'left'
                    },
                        React.createElement(ListItem, { 
                            sx: { 
                                px: 0
                            }
                        },
                            React.createElement(ListItemText, {
                                primary: React.createElement(Box, {
                                    sx: { display: 'flex', alignItems: 'center', gap: 1 }
                                },
                                    React.createElement(Typography, { 
                                        variant: 'body2',
                                        sx: { fontSize: '16px' }
                                    }, statusIcon),
                                    React.createElement(Typography, { variant: 'body2' }, mcp.name)
                                ),
                                secondary: `Status: ${mcp.status ? 'Connected' : 'Disconnected'}`,
                                primaryTypographyProps: { variant: 'body2' },
                                secondaryTypographyProps: { variant: 'caption' }
                            })
                        )
                    );
                })
            ) : React.createElement(Typography, { 
                variant: 'body2', 
                color: 'text.secondary',
                sx: { textAlign: 'center', py: 2 }
            }, 'No MCP clients configured'),
            
            // MCP Configuration Modal
            React.createElement(Modal, {
                open: mcpConfigModalOpen,
                onClose: handleCloseMcpConfigModal,
                ariaLabelledby: 'mcp-config-modal-title'
            },
                React.createElement(Box, {
                    sx: {
                        position: 'absolute',
                        top: '50%',
                        left: '50%',
                        transform: 'translate(-50%, -50%)',
                        width: 700,
                        bgcolor: 'background.paper',
                        border: '2px solid #000',
                        boxShadow: 24,
                        p: 4,
                        borderRadius: 1,
                        maxHeight: '80vh',
                        overflow: 'auto'
                    }
                },
                    React.createElement(Typography, {
                        id: 'mcp-config-modal-title',
                        variant: 'h6',
                        component: 'h2',
                        sx: { mb: 2 }
                    }, 'Edit MCP Configuration'),
                    
                    React.createElement(Typography, {
                        variant: 'body2',
                        color: 'text.secondary',
                        sx: { mb: 2 }
                    }, 'Edit the MCP configuration as JSON. Format: {"server_name": {"command": "...", "args": ["arg1", "arg2"]}}'),
                    
                    React.createElement(TextField, {
                        fullWidth: true,
                        label: 'MCP Configuration (JSON)',
                        value: mcpConfigJson,
                        onChange: (e) => setMcpConfigJson(e.target.value),
                        variant: 'outlined',
                        multiline: true,
                        rows: 15,
                        sx: { mb: 3, fontFamily: 'monospace' },
                        InputProps: {
                            style: { fontFamily: 'JetBrains Mono, Consolas, Monaco, monospace' }
                        }
                    }),
                    
                    React.createElement(Box, { sx: { display: 'flex', gap: 2, justifyContent: 'flex-end' } },
                        React.createElement(Button, {
                            onClick: handleCloseMcpConfigModal
                        }, 'Cancel'),
                        React.createElement(Button, {
                            variant: 'contained',
                            onClick: handleSaveMcpConfig,
                            disabled: mcpLoading
                        }, mcpLoading ? React.createElement(CircularProgress, { size: 20 }) : 'Save')
                    )
                )
            ),
            
            // Notes Modal
            React.createElement(Modal, {
                open: notesModalOpen,
                onClose: handleCloseNotesModal,
                ariaLabelledby: 'notes-modal-title'
            },
                React.createElement(Box, {
                    sx: {
                        position: 'absolute',
                        top: '50%',
                        left: '50%',
                        transform: 'translate(-50%, -50%)',
                        width: 500,
                        bgcolor: 'background.paper',
                        border: '2px solid #000',
                        boxShadow: 24,
                        p: 4,
                        borderRadius: 1
                    }
                },
                    React.createElement(Typography, {
                        id: 'notes-modal-title',
                        variant: 'h6',
                        component: 'h2',
                        sx: { mb: 2 }
                    }, currentNote ? 'Edit Note' : 'Add New Note'),
                    
                    React.createElement(TextField, {
                        fullWidth: true,
                        label: 'Title',
                        value: noteForm.title,
                        onChange: (e) => handleNoteFormChange('title', e.target.value),
                        variant: 'outlined',
                        sx: { mb: 2 }
                    }),
                    
                    React.createElement(TextField, {
                        fullWidth: true,
                        label: 'Content',
                        value: noteForm.content,
                        onChange: (e) => handleNoteFormChange('content', e.target.value),
                        variant: 'outlined',
                        multiline: true,
                        rows: 4,
                        sx: { mb: 2 }
                    }),
                    
                    React.createElement(FormControl, { fullWidth: true, sx: { mb: 3 } },
                        React.createElement(InputLabel, null, 'Scope'),
                        React.createElement(Select, {
                            value: noteForm.scope,
                            label: 'Scope',
                            onChange: (e) => handleNoteFormChange('scope', e.target.value)
                        },
                            React.createElement(MenuItem, { value: 'agent' }, 'Agent'),
                            React.createElement(MenuItem, { value: 'global' }, 'Global')
                        )
                    ),
                    
                    React.createElement(Box, { sx: { display: 'flex', gap: 2, justifyContent: 'flex-end' } },
                        React.createElement(Button, {
                            onClick: handleCloseNotesModal
                        }, 'Cancel'),
                        React.createElement(Button, {
                            variant: 'contained',
                            onClick: handleSaveNote,
                            disabled: !noteForm.title.trim()
                        }, currentNote ? 'Update' : 'Add')
                    )
                )
            ),
            
            // Snackbar for notifications
            React.createElement(Snackbar, {
                open: snackbar.open,
                autoHideDuration: 6000,
                onClose: handleCloseSnackbar,
                anchorOrigin: { vertical: 'bottom', horizontal: 'center' },
                message: snackbar.message,
                sx: {
                    zIndex: 9999, // Ensure it's above other elements
                    position: 'fixed'
                },
                ContentProps: {
                    sx: {
                        backgroundColor: 
                            snackbar.severity === 'success' ? '#4caf50' :
                            snackbar.severity === 'error' ? '#f44336' :
                            snackbar.severity === 'warning' ? '#ff9800' :
                            '#2196f3', // info
                        color: 'white',
                        fontWeight: 500,
                        boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1)',
                        borderRadius: '8px'
                    }
                }
            })
        )
    );
}

// Make SettingsPanel globally available
window.Anges = window.Anges || {};
window.Anges.SettingsPanel = SettingsPanel;
