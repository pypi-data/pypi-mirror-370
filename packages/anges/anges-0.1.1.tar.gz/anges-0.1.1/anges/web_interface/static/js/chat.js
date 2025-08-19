const {
  AppBar, Toolbar, Typography, Button, TextField,
  Paper, Container, Box, CircularProgress, Select, MenuItem,
  FormControl, InputLabel, Collapse, Drawer, List, ListItem, ListItemText,
  IconButton, Dialog, DialogTitle, DialogContent, DialogActions,
  useTheme, Switch, useMediaQuery, Tooltip
} = MaterialUI;

// Create a context for color mode toggling
const ColorModeContext = React.createContext({ toggleColorMode: () => {} });

function ChatApp() {
  const coreState = useChatCore();
  const historyState = useChatHistory();
  const messageHandlers = useMessageHandlers(coreState, historyState);
  
  // Expose coreState to window for testing purposes
  React.useEffect(() => {
    window.coreState = coreState;
  }, [coreState]);

  // Access theme context for theme toggling
  const { toggleColorMode } = React.useContext(ColorModeContext);
  const theme = useTheme();
  const isDarkMode = theme.palette.mode === 'light'; // Preserving original logic

  // Handle settings button click
  const handleSettingsClick = () => { // Modified to toggle settings drawer
    coreState.setShowSettings(!coreState.showSettings);
  };

  // Handle settings close
  const handleSettingsClose = () => { // Modified (setSettingsAnchorEl removed)
    coreState.setShowSettings(false);
  };
  
  const toggleChatHistory = () => {
    historyState.setShowChatHistory(!historyState.showChatHistory);
  };
  
  // Use a ref so we only load once
  const loadedRef = React.useRef(false);
  
  React.useEffect(() => {
    // If already loaded, do nothing
    if (loadedRef.current) return;

    // Mark as loaded
    loadedRef.current = true;
    
    // 1. Load chat from the "loadChat" custom event if triggered
    const handleLoadChat = async (event) => {
      const { chatId } = event.detail;
      await coreState.handleChatSelect(chatId);
    };
    window.addEventListener('loadChat', handleLoadChat);

    // 2. Also check the URL for a ?chatId=123 type of query param
    const searchParams = new URLSearchParams(window.location.search);
    const chatIdFromUrl = searchParams.get('chatId');
    if (chatIdFromUrl) {
      coreState.handleChatSelect(chatIdFromUrl);
    }

    // Cleanup
    return () => {
      window.removeEventListener('loadChat', handleLoadChat);
    };
  }, [coreState.handleChatSelect]);

  return (
    React.createElement(Box, { 
      sx: { 
        display: 'flex',
        height: '100vh',
        overflow: 'hidden',
        backgroundColor: theme.palette.background.default
      } 
    },
      // Chat History Drawer
      React.createElement(ChatDrawer, {
        showChatHistory: historyState.showChatHistory,
        chatHistory: historyState.chatHistory,
        handlers: {
          ...historyState,
          handleChatSelect: (chatId) => coreState.handleChatSelect(chatId),
          setMessages: coreState.setMessages,
          setIsLoading: coreState.setIsLoading,
          toggleChatHistory: toggleChatHistory,
          handleExportClick: historyState.handleExportClick
        },
        selectedChat: coreState.selectedChat,
        isLoading: coreState.isLoading
      }),

      // Main Content Area
      React.createElement(Box, { 
        sx: { 
          flexGrow: 1, 
          display: 'flex', 
          flexDirection: 'column',
          height: '100vh',
          overflow: 'hidden',
          transition: theme.transitions.create(['margin', 'width'], {
            easing: theme.transitions.easing.sharp,
            duration: theme.transitions.duration.leavingScreen,
          }),
          ...(historyState.showChatHistory && {
            transition: theme.transitions.create(['margin', 'width'], {
              easing: theme.transitions.easing.easeOut,
              duration: theme.transitions.duration.enteringScreen,
            }),
          }),
          // Add margin adjustment for settings drawer
          ...(coreState.showSettings && {
            marginRight: '320px', // Match the drawer width
            transition: theme.transitions.create(['margin', 'width'], {
              easing: theme.transitions.easing.easeOut,
              duration: theme.transitions.duration.enteringScreen,
            }),
          }),
        }
      },
      
      // App Bar
      React.createElement(AppBar, {
          position: 'fixed',
          elevation: 2,
          sx: { 
            bgcolor: 'primary.main', 
            zIndex: (theme) => theme.zIndex.drawer + 1,
            transition: theme.transitions.create(['margin', 'width'], {
              easing: theme.transitions.easing.sharp,
              duration: theme.transitions.duration.leavingScreen,
            }),
            ...(historyState.showChatHistory && {
            }),
            // Add width adjustment for settings drawer
            ...(coreState.showSettings && {
            }),
          },
        },
          React.createElement(Toolbar, null,
            // Menu button - only visible on mobile or when drawer is closed
            React.createElement(IconButton, {
              color: 'inherit',
              onClick: toggleChatHistory,
              edge: 'start',
            },
              React.createElement('span', { className: 'material-icons' }, 'menu')
            ),
            
            React.createElement(Typography, {
              variant: 'h6',
              component: 'div',
              sx: { 
                flexGrow: 1,
                whiteSpace: 'nowrap',
                overflow: 'hidden',
                textOverflow: 'ellipsis'
              }
            }, 'Anges AI'),
            // Message Filter Toggle with tooltip
            React.createElement(Tooltip, {
              title: coreState.messageFilterMode === 'all' ? "Show only user & direct messages" : "Show all messages",
              arrow: true,
              placement: "bottom"
            },
              React.createElement(IconButton, {
                color: 'inherit',
                onClick: () => coreState.setMessageFilterMode(coreState.messageFilterMode === 'all' ? 'simplified' : 'all'),
                sx: { mr: 1 }
              },
                React.createElement('span', { 
                  className: 'material-icons'
                }, coreState.messageFilterMode === 'all' ? 'filter_list' : 'filter_list_off')
              )
            ),
            
            // Theme toggle button with tooltip
            React.createElement(Tooltip, {
              title: isDarkMode ? "Switch to light theme" : "Switch to dark theme", // Preserving original logic
              arrow: true,
              placement: "bottom"
            },
              React.createElement(IconButton, {
                color: 'inherit',
                onClick: toggleColorMode,
                sx: { mr: 1 }
              },
                React.createElement('span', { 
                  className: 'material-icons'
                }, isDarkMode ? 'dark_mode' : 'light_mode') // Preserving original logic
              )
            ),
            
            // Settings button with tooltip
            React.createElement(Tooltip, {
              title: "Settings",
              arrow: true,
              placement: "bottom"
            },
              React.createElement(IconButton, {
                color: 'inherit',
                onClick: handleSettingsClick, // Uses updated handleSettingsClick
                sx: { mr: 1 }
              },
                React.createElement('span', { className: 'material-icons' }, 'settings')
              )
            ),
            
            // New chat button with tooltip
            React.createElement(Tooltip, {
              title: "New Chat",
              arrow: true,
              placement: "bottom"
            },
              React.createElement(IconButton, {
                color: 'inherit',
                onClick: messageHandlers.handleNewChat,
                sx: { ml: 1 }
              },
                React.createElement('span', { className: 'material-icons' }, 'add')
              )
            ),
            
            // Logout button with tooltip
            React.createElement(Tooltip, {
              title: "Logout",
              arrow: true,
              placement: "bottom"
            },
              React.createElement(IconButton, {
                color: 'inherit',
                href: '/logout',
                sx: { ml: 1 }
              },
                React.createElement('span', { className: 'material-icons' }, 'exit_to_app')
              )
            )
          )
        ),

        // Main Content Grid
        React.createElement(Box, {
          sx: {
            flexGrow: 1,
            display: 'grid',
            gridTemplateRows: 'minmax(0, 1fr) auto',
            pt: { xs: 8, sm: 9 }, // Adjust top padding to account for AppBar
            overflow: 'hidden',
            height: '100%'
          }
        },
          // Messages Container
          React.createElement(Box, {
            sx: { 
              overflow: 'auto',
              px: { xs: 1, sm: 2, md: 3 },
              py: 2
            }
          },
            React.createElement(MessageList, {
              messages: coreState.getFilteredMessages(),
              isLoading: coreState.isLoading,
              messagesEndRef: coreState.messagesEndRef
            })
          ),
          
          // Input Form Container
          React.createElement(Box, {
            sx: { 
              p: { xs: 1, sm: 2, md: 3 },
              backgroundColor: theme.palette.background.paper,
              borderTop: `1px solid ${theme.palette.divider}`
            }
          },
            React.createElement(InputForm, {
              userInput: coreState.userInput,
              setUserInput: coreState.setUserInput,
              isLoading: coreState.isLoading,
              handlers: messageHandlers,
              hasActiveTask: coreState.hasActiveTask,
              isSettingsOpen: coreState.showSettings
            })
          )
        )
      ),

      // Add SettingsPanel outside the main content flow
      React.createElement(window.Anges.SettingsPanel, {
        coreState: coreState,
        // onClose handler removed - drawer should only close via settings button
      }),

      // Edit Dialog
      React.createElement(EditDialog, {
        open: historyState.editDialogOpen,
        title: historyState.editingTitle,
        setTitle: historyState.setEditingTitle,
        onClose: () => historyState.setEditDialogOpen(false),
        onSubmit: historyState.handleEditSubmit
      })
    )
  );
}

try {
// Wrap the app with ThemeWrapper to provide theme context
ReactDOM.render(
  React.createElement(
    ThemeWrapper, 
    null, 
    React.createElement(ChatApp)
  ),
  document.getElementById('root')
);
} catch (error) {
  console.log('ReactDOM.render failed:', error);
  console.error('Full error details:', error);
}

