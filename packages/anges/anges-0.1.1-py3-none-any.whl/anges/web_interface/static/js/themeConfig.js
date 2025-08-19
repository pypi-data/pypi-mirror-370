// themeConfig.js - Material-UI Theme Configuration
// This file defines the theme settings for the chat application

const { createTheme, ThemeProvider, CssBaseline } = MaterialUI;

// Create a context for color mode toggling
const ColorModeContext = React.createContext({ toggleColorMode: () => {}, mode: 'light' });

// Define color palette
const lightPalette = {
  primary: {
    main: '#0D47A1',  // Deep blue (main color)
    light: '#5472D3',
    dark: '#002171',
    contrastText: '#FFFFFF',
  },
  secondary: {
    main: '#7B1FA2',  // Purple (secondary color)
    light: '#AE52D4',
    dark: '#4A0072',
    contrastText: '#FFFFFF',
  },
  accent: {
    main: '#26A69A',  // Light green (accent color)
    light: '#64D8CB',
    dark: '#00766C',
    contrastText: '#FFFFFF',
  },
  background: {
    default: '#F5F7FA',
    paper: '#FFFFFF',
  },
  text: {
    primary: '#212121',
    secondary: '#616161',
  },
};

// Define dark mode palette
const darkPalette = {
  primary: {
    main: '#5472D3',  // Lighter version of deep blue for dark mode
    light: '#84A0FF',
    dark: '#0D47A1',
    contrastText: '#FFFFFF',
  },
  secondary: {
    main: '#AE52D4',  // Lighter version of purple for dark mode
    light: '#E180FF',
    dark: '#7B1FA2',
    contrastText: '#FFFFFF',
  },
  accent: {
    main: '#64D8CB',  // Lighter version of green for dark mode
    light: '#9EFFFF',
    dark: '#26A69A',
    contrastText: '#212121',
  },
  background: {
    default: '#121212',
    paper: '#1E1E1E',
  },
  text: {
    primary: '#FFFFFF',
    secondary: '#B0B0B0',
  },
};

// Typography settings
const typography = {
  fontFamily: '"Inter", "Roboto", "Helvetica", "Arial", sans-serif',
  h1: {
    fontWeight: 500,
    fontSize: '2.5rem',
  },
  h2: {
    fontWeight: 500,
    fontSize: '2rem',
  },
  h3: {
    fontWeight: 500,
    fontSize: '1.75rem',
  },
  h4: {
    fontWeight: 500,
    fontSize: '1.5rem',
  },
  h5: {
    fontWeight: 500,
    fontSize: '1.25rem',
  },
  h6: {
    fontWeight: 500,
    fontSize: '1rem',
  },
  body1: {
    fontSize: '1rem',
  },
  body2: {
    fontSize: '0.875rem',
  },
  button: {
    textTransform: 'none',
    fontWeight: 500,
  },
  code: {
    fontFamily: '"JetBrains Mono", monospace',
    fontSize: '0.875rem',
  },
};

// Create theme hook
function useAppTheme() {
  // Initialize with saved theme from localStorage
  const savedMode = localStorage.getItem('themeMode');
  const [mode, setMode] = React.useState(
    savedMode && (savedMode === 'light' || savedMode === 'dark') 
      ? savedMode 
      : 'light'
  );
  
  const toggleColorMode = () => {
    setMode((prevMode) => {
      const newMode = prevMode === 'light' ? 'dark' : 'light';
      localStorage.setItem('themeMode', newMode);
      return newMode;
    });
  };

  const theme = React.useMemo(() => {
    const palette = mode === 'light' ? lightPalette : darkPalette;
    
    return createTheme({
      palette: {
        mode,
        primary: palette.primary,
        secondary: palette.secondary,
        background: palette.background,
        text: palette.text,
      },
      typography,
      components: {
        MuiButton: {
          styleOverrides: {
            root: {
              borderRadius: 8,
              padding: '8px 16px',
            },
            contained: {
              boxShadow: 'none',
              '&:hover': {
                boxShadow: '0px 2px 4px rgba(0, 0, 0, 0.2)',
              },
            },
          },
        },
        MuiPaper: {
          styleOverrides: {
            root: {
              borderRadius: 12,
              boxShadow: mode === 'light' 
                ? '0px 2px 8px rgba(0, 0, 0, 0.05)' 
                : '0px 2px 8px rgba(0, 0, 0, 0.2)',
            },
          },
        },
        MuiAppBar: {
          styleOverrides: {
            root: {
              boxShadow: '0px 1px 3px rgba(0, 0, 0, 0.1)',
            },
          },
        },
        MuiTextField: {
          styleOverrides: {
            root: {
              '& .MuiOutlinedInput-root': {
                borderRadius: 8,
              },
            },
          },
        },
      },
    });
  }, [mode]);

  return { theme, mode, toggleColorMode };
}

// Theme Provider Component
function ThemeWrapper({ children }) {
  const { theme, mode, toggleColorMode } = useAppTheme();
  
  // Create the context value to be provided
  const colorModeContextValue = React.useMemo(
    () => ({
      toggleColorMode,
      mode
    }),
    [toggleColorMode, mode]
  );
  
  return (
    <ColorModeContext.Provider value={colorModeContextValue}>
      <ThemeProvider theme={theme}>
        <CssBaseline />
        {children}
      </ThemeProvider>
    </ColorModeContext.Provider>
  );
}
