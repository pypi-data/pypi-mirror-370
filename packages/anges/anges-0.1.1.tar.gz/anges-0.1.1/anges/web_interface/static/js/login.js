// This function will be initialized with template variables from the HTML
function initializeLogin(errorMessage, loginUrl) {
    console.log("initializeLogin called with:", { errorMessage, loginUrl });
    
    const {
        AppBar, Toolbar, Typography, Button, TextField,
        Paper, Container, Box, Card, CardContent,
        IconButton, InputAdornment
    } = MaterialUI;
    
    // Check if ThemeWrapper exists
    console.log("ThemeWrapper exists:", typeof ThemeWrapper !== 'undefined');
    
    function LoginApp() {
        console.log("LoginApp component rendering");
        const [showPassword, setShowPassword] = React.useState(false);
        const [password, setPassword] = React.useState('');

        // Use theme context if available
        const colorModeContext = React.useContext(ColorModeContext || React.createContext({}));
        const { toggleColorMode, mode } = colorModeContext;

        const handleSubmit = (e) => {
            e.preventDefault();
            e.target.submit();
        };

        const handlePasswordChange = (e) => {
            setPassword(e.target.value);
        };

        const handleTogglePasswordVisibility = () => {
            setShowPassword(!showPassword);
        };

        const handleThemeToggle = () => {
            if (toggleColorMode) {
                toggleColorMode();
            }
        };

        return (
            <Box sx={{ flexGrow: 1 }}>
                <AppBar position="static" elevation={4}>
                    <Toolbar>
                        <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
                            Anges AI
                        </Typography>
                        <IconButton 
                            color="inherit" 
                            sx={{ ml: 1 }}
                            title="Toggle light/dark theme"
                            onClick={handleThemeToggle}
                        >
                            <span className="material-icons">
                                {mode === 'dark' ? 'light_mode' : 'dark_mode'}
                            </span>
                        </IconButton>
                    </Toolbar>
                </AppBar>

                <Container maxWidth="sm" sx={{ mt: 8 }}>
                    <Card elevation={4}>
                        <CardContent sx={{ p: 4 }}>
                            <Typography variant="h4" component="h1" gutterBottom align="center">
                                Welcome
                            </Typography>

                            {errorMessage && (
                                <Box className="error-message">
                                    <span className="material-icons">error</span>
                                    {errorMessage}
                                </Box>
                            )}

                            <form method="POST" action={loginUrl} onSubmit={handleSubmit}>
                                <TextField
                                    fullWidth
                                    type={showPassword ? 'text' : 'password'}
                                    name="password"
                                    label="Enter password"
                                    variant="outlined"
                                    value={password}
                                    onChange={handlePasswordChange}
                                    sx={{ mb: 3 }}
                                    InputProps={{
                                        endAdornment: (
                                            <InputAdornment position="end">
                                                <IconButton
                                                    onClick={handleTogglePasswordVisibility}
                                                    edge="end"
                                                >
                                                    <span className="material-icons">
                                                        {showPassword ? 'visibility_off' : 'visibility'}
                                                    </span>
                                                </IconButton>
                                            </InputAdornment>
                                        ),
                                    }}
                                />

                                <Button
                                    type="submit"
                                    fullWidth
                                    variant="contained"
                                    size="large"
                                    startIcon={<span className="material-icons">login</span>}
                                >
                                    Login
                                </Button>
                            </form>
                        </CardContent>
                    </Card>
                </Container>
            </Box>
        );
    }

    function AppWrapper() {
        try {
            if (typeof ThemeWrapper === 'undefined') {
                console.warn("ThemeWrapper is not defined, using default styling");
                return <LoginApp />;
            }
            
            return (
                <ThemeWrapper>
                    <LoginApp />
                </ThemeWrapper>
            );
        } catch (error) {
            console.error("Error rendering AppWrapper:", error);
            return (
                <Box sx={{ p: 4, color: 'error.main' }}>
                    <Typography variant="h5">Error Rendering Login</Typography>
                    <pre>{error.toString()}</pre>
                    <pre>{error.stack}</pre>
                </Box>
            );
        }
    }

    try {
        console.log("Attempting to render AppWrapper");
        ReactDOM.render(<AppWrapper />, document.getElementById('root'));
        console.log("AppWrapper rendered successfully");
    } catch (error) {
        console.error("Error during ReactDOM.render:", error);
        // Display error on the page for debugging
        document.getElementById('root').innerHTML = `
            <div style="color: red; padding: 20px;">
                <h2>Error Rendering Login Page</h2>
                <p>${error.toString()}</p>
                <pre>${error.stack}</pre>
            </div>
        `;
    }
}
