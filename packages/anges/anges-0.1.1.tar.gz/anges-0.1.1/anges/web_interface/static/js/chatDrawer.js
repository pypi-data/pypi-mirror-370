// Minimal-comment version
// Required MaterialUI components
const {
  Drawer, List, ListItem, ListItemText, IconButton,
  Tooltip, CircularProgress, Menu, MenuItem, Dialog,
  DialogTitle, DialogContent, DialogActions, Button
} = MaterialUI;

const extractIdPath = (title) => {
  const match = title.match(/^([\w-]+)\s+Child Agent/);
  if (!match) return null;
  return match[1].split('-');
};

const buildChatTree = (chatList) => {
  const chatMap = new Map();
  const rootNodes = [];

  // 1) Create a map of stream_id -> node
  chatList.forEach((chat) => {
    chatMap.set(chat.stream_id, {
      ...chat,
      children: [],
      idPath: extractIdPath(chat.title),
    });
  });

  // 2) Build the tree
  chatList.forEach((chat) => {
    const node = chatMap.get(chat.stream_id);
    const { idPath } = node;

    // If no path => root node
    if (!idPath || idPath.length === 0) {
      rootNodes.push(node);
      return;
    }

    // Parent path is everything except the last segment, joined by '-'
    const parentPath = idPath.slice(0, -1).join('-');

    const parentNode = Array.from(chatMap.values()).find((p) => {
      if (node.idPath.length === 1) {
        return node.idPath[0] === p.stream_id;
      }
      if (!p.idPath) return false;

      return p.idPath.join('-') === parentPath;
    });

    if (parentNode) {
      parentNode.children.push(node);
    } else {
      rootNodes.push(node);
    }
  });

  return rootNodes;
};

function RecursiveChatItem({
  chat,
  level = 0,
  selectedChat,
  handlers,
  isLoading,
  expandedChats,
  onExpand,
  showTimestamp = true
}) {
  const isExpanded = expandedChats.has(chat.stream_id);
  const [infoModalOpen, setInfoModalOpen] = React.useState(false);
  const [tokenData, setTokenData] = React.useState(null);
  const [tokenLoading, setTokenLoading] = React.useState(false);
  const [menuAnchorEl, setMenuAnchorEl] = React.useState(null);
  const [isHovering, setIsHovering] = React.useState(false);
  const open = Boolean(menuAnchorEl);

  const handleExpandClick = (e) => {
    e.stopPropagation();
    onExpand(chat.stream_id);
  };

  const handleChatClick = async (chatId) => {
    if (isLoading) return;
    const success = await handlers.handleChatSelect(chatId);
    if (success) {
      window.dispatchEvent(new CustomEvent('loadChat', { detail: { chatId } }));
    }
  };
  const fetchTokenData = async (chatId) => {
    setTokenLoading(true);
    try {
      const response = await fetch(`/load-chat/${chatId}`);
      const data = await response.json();
      if (data.status === 'success') {
        return {
          inputTokens: data.est_input_token || 0,
          outputTokens: data.est_output_token || 0,
          totalEvents: data.events ? data.events.length : 0
        };
      }
      return null;
    } catch (error) {
      console.error('Error fetching token data:', error);
      return null;
    } finally {
      setTokenLoading(false);
    }
  };

  const formatNumber = (num) => {
    if (num >= 1000000) {
      return (num / 1000000).toFixed(1) + 'M';
    } else if (num >= 1000) {
      return (num / 1000).toFixed(1) + 'K';
    }
    return num.toString();
  };

  const handleInfoClick = async (e) => {
    e.stopPropagation();
    setInfoModalOpen(true);
    setMenuAnchorEl(null);
    
    // Fetch token data when info modal opens
    const data = await fetchTokenData(chat.stream_id);
    setTokenData(data);
  };

  const handleMenuOpen = (event) => {
    event.stopPropagation();
    setMenuAnchorEl(event.currentTarget);
  };

  const handleMenuClose = (event) => {
    if (event) event.stopPropagation();
    setMenuAnchorEl(null);
  };

  const handleEditClick = (event) => {
    event.stopPropagation();
    handlers.handleEditClick(chat.stream_id);
    handleMenuClose();
  };

  const handleDeleteClick = (event) => {
    event.stopPropagation();
    handlers.handleDeleteClick(chat.stream_id);
    handleMenuClose();
  };

  const handleExportClick = (event) => {
    event.stopPropagation();
    handlers.handleExportClick(chat.stream_id);
    handleMenuClose();
  };

  return React.createElement(
    React.Fragment,
    null,
    React.createElement(
      ListItem,
      {
        key: chat.stream_id,
        selected: selectedChat === chat.stream_id,
        onClick: () => handleChatClick(chat.stream_id),
        onMouseEnter: () => setIsHovering(true),
        onMouseLeave: () => setIsHovering(false),
        sx: {
          cursor: isLoading ? 'not-allowed' : 'pointer',
          paddingLeft: `${(level + 1) * 8}px`,
          paddingTop: '4px',
          paddingBottom: '4px',
          opacity: isLoading ? 0.6 : 1,
          '&:hover': {
            backgroundColor: isLoading ? 
              'inherit' : 
              (selectedChat === chat.stream_id ? 
                (theme) => `${theme.palette.primary.inherit}` : 
                (theme) => `${theme.palette.action.hover}`)
          },
          // Add a shadow effect for selected chat
          boxShadow: selectedChat === chat.stream_id ? 
            '0 2px 5px rgba(0, 0, 0, 0.2)' : 'none',
          // Add a transition for smooth opacity changes
          transition: 'all 0.3s ease',
        },
        disabled: isLoading,
      },
      // Expand/collapse button for chats with children
      chat.children.length > 0 &&
        React.createElement(
          IconButton,
          { size: 'small', onClick: handleExpandClick },
          React.createElement(
            'span',
            { className: 'material-icons' },
            isExpanded ? 'expand_more' : 'chevron_right'
          )
        ),
      React.createElement(ListItemText, {
        primary: chat.title,
        secondary: showTimestamp ? new Date(chat.created_at).toLocaleString() : null,
        primaryTypographyProps: {
          style: {
            fontSize: '0.875rem',
            overflow: 'hidden',
            textOverflow: 'ellipsis',
            whiteSpace: 'nowrap',
            maxWidth: '200px'
          }
        }
      }),
      // Show loading indicator when this chat is being loaded
      selectedChat === chat.stream_id && isLoading &&
        React.createElement(
          CircularProgress,
          {
            size: 20,
            sx: { marginRight: '8px' }
          }
        ),
      // Ellipsis menu button that appears on hover
      (isHovering || open) && React.createElement(
        Tooltip,
        {
          title: "Options",
          placement: "top",
          arrow: true
        },
        React.createElement(
          IconButton,
          {
            edge: 'end',
            onClick: handleMenuOpen,
            disabled: isLoading,
            size: 'small',
            'aria-label': 'chat options',
            'aria-controls': open ? 'chat-menu' : undefined,
            'aria-haspopup': 'true',
            'aria-expanded': open ? 'true' : undefined,
          },
          React.createElement('span', { className: 'material-icons' }, 'more_vert')
        )
      ),
      // Dropdown menu for edit and delete options
      React.createElement(
        Menu,
        {
          id: 'chat-menu',
          anchorEl: menuAnchorEl,
          open: open,
          onClose: handleMenuClose,
          MenuListProps: {
            'aria-labelledby': 'chat-options-button',
          },
        },
        React.createElement(
          MenuItem,
          {
            onClick: handleEditClick,
          },
          React.createElement('span', { 
            className: 'material-icons',
            style: { marginRight: '8px', fontSize: '16px' }
          }, 'edit'),
          "Edit"
        ),
        React.createElement(
          MenuItem,
          {
            onClick: handleDeleteClick,
          },
          React.createElement('span', { 
            className: 'material-icons',
            style: { marginRight: '8px', fontSize: '16px' }
          }, 'delete'),
          "Delete"
        ),
        React.createElement(
          MenuItem,
          {
            onClick: handleExportClick,
          },
          React.createElement('span', { 
            className: 'material-icons',
            style: { marginRight: '8px', fontSize: '16px' }
          }, 'download'),
          "Export"
        ),
        React.createElement(
          MenuItem,
          {
            onClick: handleInfoClick,
          },
          React.createElement('span', { 
            className: 'material-icons',
            style: { marginRight: '8px', fontSize: '16px' }
          }, 'info'),
          "Info"
        )
      )
    ),
    // Render children if expanded
    isExpanded &&
      chat.children.map((childChat) =>
        React.createElement(RecursiveChatItem, {
          key: childChat.stream_id,
          chat: childChat,
          level: level + 1,
          selectedChat,
          handlers,
          isLoading,
          expandedChats,
          onExpand,
          showTimestamp
        })
      ),
    // Info Modal
    React.createElement(
      Dialog,
      {
        open: infoModalOpen,
        onClose: () => setInfoModalOpen(false),
        maxWidth: 'sm',
        fullWidth: true,
        PaperProps: {
          style: {
            background: '#ffffff',
            color: '#424242',
            borderRadius: '12px',
            boxShadow: '0 8px 32px rgba(0,0,0,0.1)',
            border: '1px solid #e0e0e0'
          }
        }
      },
      React.createElement(
        DialogTitle,
        {
          style: {
            background: '#f5f5f5',
            borderBottom: '1px solid #e0e0e0',
            fontWeight: 'bold',
            color: '#424242'
          }
        },
        'Chat Information'
      ),
      React.createElement(
        DialogContent,
        {
          style: {
            padding: '20px',
            background: '#ffffff',
            color: '#424242'
          }
        },
        tokenLoading ? 
          React.createElement(
            'div',
            {
              style: {
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                padding: '20px'
              }
            },
            React.createElement(CircularProgress, { 
              style: { color: '#1976d2', marginRight: '10px' } 
            }),
            'Loading chat information...'
          ) :
          tokenData ? 
            React.createElement(
              'div',
              {
                style: {
                  background: '#f8f8f8',
                  padding: '15px',
                  borderRadius: '8px',
                  border: '1px solid #e0e0e0'
                }
              },
              React.createElement('h4', { 
                style: { margin: '0 0 10px 0', color: '#424242' } 
              }, 'Token Usage'),
              React.createElement('p', { 
                style: { margin: '5px 0', fontSize: '14px', color: '#666666' } 
              }, `Input Tokens: ${formatNumber(tokenData.inputTokens)}`),
              React.createElement('p', { 
                style: { margin: '5px 0', fontSize: '14px', color: '#666666' } 
              }, `Output Tokens: ${formatNumber(tokenData.outputTokens)}`),
              React.createElement('p', { 
                style: { margin: '5px 0', fontSize: '14px', fontWeight: 'bold', color: '#424242' } 
              }, `Total Events: ${formatNumber(tokenData.totalEvents)}`)
            ) :
            React.createElement(
              'div',
              {
                style: {
                  textAlign: 'center',
                  padding: '20px',
                  color: '#f44336'
                }
              },
              'Failed to load chat information'
            )
      ),
      React.createElement(
        DialogActions,
        {
          style: {
            background: '#f5f5f5',
            borderTop: '1px solid #e0e0e0',
            padding: '15px 20px'
          }
        },
        React.createElement(
          Button,
          {
            onClick: () => setInfoModalOpen(false),
            style: {
              background: '#1976d2',
              color: 'white',
              border: 'none',
              borderRadius: '6px',
              padding: '8px 16px',
              fontWeight: 'bold'
            }
          },
          'Close'
        )
      )
    )
  );
};

function ChatDrawer({
  showChatHistory,
  chatHistory,
  handlers,
  selectedChat,
  isLoading,
}) {
  const [expandedChats, setExpandedChats] = React.useState(new Set());
  const [searchTerm, setSearchTerm] = React.useState('');
  const [isExpanded, setIsExpanded] = React.useState(false);
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('sm'));

  const handleExpand = React.useCallback((chatId) => {
    setExpandedChats((prev) => {
      const next = new Set(prev);
      next.has(chatId) ? next.delete(chatId) : next.add(chatId);
      return next;
    });
  }, []);

  const handleSearchChange = (event) => {
    setSearchTerm(event.target.value);
  };

  // Group chats by time periods
  const groupChatsByDate = (chats) => {
    // Build the tree to preserve parent–child relationships
    const chatTrees = buildChatTree(chats);

    // Recursively compute the effective (newest) date for the node and its children
    const getEffectiveDate = (node) => {
      let date = new Date(node.created_at);
      node.children.forEach(child => {
        const childDate = getEffectiveDate(child);
        if (childDate > date) date = childDate;
      });
      return date;
    };

    const now = new Date();
    const today = new Date(now.getFullYear(), now.getMonth(), now.getDate());
    const yesterday = new Date(today);
    yesterday.setDate(yesterday.getDate() - 1);
    const lastWeek = new Date(today);
    lastWeek.setDate(lastWeek.getDate() - 7);
    const lastMonth = new Date(today);
    lastMonth.setDate(lastMonth.getDate() - 30);

    // Initialize groups
    const groups = {
      'Today': [],
      'Yesterday': [],
      'Last 7 Days': [],
      'Last 30 Days': [],
      'Older': []
    };

    // Sort chats into time-based groups
    chatTrees.forEach(chat => {
      const effectiveDate = getEffectiveDate(chat);
      // Store the effective date on the chat object for sorting later
      chat.effectiveDate = effectiveDate;
      
      if (effectiveDate >= today) {
        groups['Today'].push(chat);
      } else if (effectiveDate >= yesterday) {
        groups['Yesterday'].push(chat);
      } else if (effectiveDate >= lastWeek) {
        groups['Last 7 Days'].push(chat);
      } else if (effectiveDate >= lastMonth) {
        groups['Last 30 Days'].push(chat);
      } else {
        groups['Older'].push(chat);
      }
    });
    
    // Sort chats within each group by effective date (newest first)
    Object.keys(groups).forEach(groupKey => {
      groups[groupKey].sort((a, b) => b.effectiveDate - a.effectiveDate);
    });

    return groups;
  };

  // Process chat history into grouped format
  const chatGroups = React.useMemo(() => {
    return groupChatsByDate(chatHistory || []);
  }, [chatHistory]);

  // Filter chats based on search term
  const filteredChatGroups = React.useMemo(() => {
    if (!searchTerm.trim()) {
      return chatGroups;
    }

    const searchTermLower = searchTerm.toLowerCase();
    const filteredGroups = {};
    Object.entries(chatGroups).forEach(([groupName, chats]) => {
      const filteredChats = chats.filter(chat => 
        chat.title.toLowerCase().includes(searchTermLower)
      );
      
      if (filteredChats.length > 0) {
        filteredGroups[groupName] = filteredChats;
      }
    });

    return filteredGroups;
  }, [chatGroups, searchTerm]);

  return React.createElement(
    Drawer,
    {
      variant: 'persistent',
      anchor: 'left',
      open: showChatHistory,
      sx: {
        width: showChatHistory ? { xs: '100%', sm: 240 } : 0,
        flexShrink: 0,
        '& .MuiDrawer-paper': {
          width: { xs: '100%', sm: 240 },
          boxSizing: 'border-box',
          top: '64px',
          height: 'calc(100% - 64px)',
          borderRight: `1px solid ${theme.palette.divider}`,
          boxShadow: theme.shadows[3],
          transition: theme.transitions.create('width', {
            easing: theme.transitions.easing.sharp,
            duration: theme.transitions.duration.enteringScreen,
          }),
        },
      },
    },
    React.createElement(
      Box,
      { 
        sx: { 
          display: 'flex', 
          flexDirection: 'column',
          height: '100%',
          overflow: 'hidden'
        } 
      },
      // Search and header controls
      React.createElement(
        Box,
        {
          sx: {
            p: 1,
            display: 'flex',
            alignItems: 'center',
            borderBottom: `1px solid ${theme.palette.divider}`,
            backgroundColor: theme.palette.background.paper,
          }
        },
        // Search input
        React.createElement(
          TextField,
          {
            size: 'small',
            placeholder: 'Search chats...',
            value: searchTerm,
            onChange: handleSearchChange,
            variant: 'outlined',
            fullWidth: true,
            InputProps: {
              startAdornment: React.createElement(
                'span',
                { 
                  className: 'material-icons',
                  style: { 
                    fontSize: '1.2rem',
                    marginRight: '8px',
                    color: theme.palette.text.secondary
                  }
                },
                'search'
              ),
              sx: { borderRadius: 4 }
            }
          }
        ),
        // Expand/collapse button
        React.createElement(
          Box,
          {
            sx: { display: 'flex', gap: '8px', ml: 1 }
          },
          // Close button (mobile only)
          React.createElement(
            IconButton,
            {
              onClick: () => handlers.toggleChatHistory(),
              'aria-label': 'close drawer',
              size: 'small'
            },
            React.createElement('span', { className: 'material-icons' }, 'close')
          )
        )
      ),
      
      // Chat list with scroll
      React.createElement(
        Box,
        {
          sx: {
            overflow: 'auto',
            flexGrow: 1,
            backgroundColor: theme.palette.background.default,
          }
        },
        React.createElement(
          List,
          { 
            sx: { 
              padding: 0,
              '& .MuiListItem-root': {
                transition: 'all 0.2s ease',
              }
            } 
          },
          Object.entries(filteredChatGroups).map(([groupName, chats]) =>
            chats.length > 0 && React.createElement(
              React.Fragment,
              { key: groupName },
              // Group header
              React.createElement(
                ListItem,
                {
                  sx: {
                    backgroundColor: theme.palette.mode === 'dark' 
                      ? theme.palette.grey[900] 
                      : theme.palette.grey[100],
                    padding: '4px 16px',
                    position: 'sticky',
                    top: 0,
                    zIndex: 1,
                  }
                },
                React.createElement(
                  ListItemText,
                  {
                    primary: groupName,
                    primaryTypographyProps: {
                      variant: 'caption',
                      style: { 
                        fontWeight: 'bold', 
                        color: theme.palette.text.secondary,
                        fontSize: '0.75rem',
                        textTransform: 'uppercase',
                        letterSpacing: '0.5px'
                      }
                    }
                  }
                )
              ),
              // Chat items in this group
              chats.map((chat) =>
                React.createElement(
                  Box,
                  {
                    key: chat.stream_id,
                    sx: {
                      mb: 1,
                      mx: 1,
                      borderRadius: 1,
                      overflow: 'hidden',
                      boxShadow: selectedChat === chat.stream_id 
                        ? `0 0 0 2px ${theme.palette.primary.main}`
                        : 'none',
                      transition: 'all 0.2s ease',
                      '&:hover': {
                        boxShadow: `0 2px 8px ${theme.palette.mode === 'dark' 
                          ? 'rgba(0, 0, 0, 0.5)' 
                          : 'rgba(0, 0, 0, 0.1)'}`
                      }
                    }
                  },
                  React.createElement(RecursiveChatItem, {
                    chat,
                    selectedChat,
                    handlers: {
                      ...handlers,
                      forceUpdate: () => handlers.forceUpdate(),
                    },
                    isLoading,
                    expandedChats,
                    onExpand: handleExpand,
                    showTimestamp: false, // Hide individual timestamps
                  })
                )
              )
            )
          ),
          // Empty state when no chats match search
          Object.keys(filteredChatGroups).length === 0 && React.createElement(
            Box,
            {
              sx: {
                p: 2,
                textAlign: 'center',
                color: theme.palette.text.secondary
              }
            },
            searchTerm ? "No chats match your search" : "No chat history yet"
          )
        )
      ),
      
    )
  );
}
