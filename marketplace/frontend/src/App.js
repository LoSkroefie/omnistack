import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import { Web3Provider } from '@ethersproject/providers';
import { Web3ReactProvider } from '@web3-react/core';

import Navigation from './components/Navigation';
import Marketplace from './components/Marketplace';
import ModuleDetails from './components/ModuleDetails';
import CreateModule from './components/CreateModule';
import Dashboard from './components/Dashboard';

const theme = createTheme({
    palette: {
        mode: 'dark',
        primary: {
            main: '#3f51b5',
        },
        secondary: {
            main: '#f50057',
        },
    },
});

function getLibrary(provider) {
    return new Web3Provider(provider);
}

function App() {
    return (
        <Web3ReactProvider getLibrary={getLibrary}>
            <ThemeProvider theme={theme}>
                <CssBaseline />
                <Router>
                    <Navigation />
                    <Routes>
                        <Route path="/" element={<Marketplace />} />
                        <Route path="/module/:id" element={<ModuleDetails />} />
                        <Route path="/create" element={<CreateModule />} />
                        <Route path="/dashboard" element={<Dashboard />} />
                    </Routes>
                </Router>
            </ThemeProvider>
        </Web3ReactProvider>
    );
}

export default App;
