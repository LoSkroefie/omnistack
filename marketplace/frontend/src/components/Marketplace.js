import React, { useState, useEffect } from 'react';
import { useWeb3React } from '@web3-react/core';
import { Link } from 'react-router-dom';
import {
    Container,
    Grid,
    Card,
    CardContent,
    CardActions,
    Typography,
    Button,
    TextField,
    Box,
    Rating,
    Chip,
    CircularProgress
} from '@mui/material';
import { ethers } from 'ethers';

import { useMarketplaceContract } from '../hooks/useContract';
import { formatEther } from '../utils/format';

const Marketplace = () => {
    const { account, active } = useWeb3React();
    const marketplaceContract = useMarketplaceContract();
    
    const [modules, setModules] = useState([]);
    const [loading, setLoading] = useState(true);
    const [searchTerm, setSearchTerm] = useState('');
    const [filter, setFilter] = useState('all');
    
    useEffect(() => {
        loadModules();
    }, [marketplaceContract]);
    
    const loadModules = async () => {
        try {
            if (!marketplaceContract) return;
            
            const totalModules = await marketplaceContract.nextModuleId();
            const modulePromises = [];
            
            for (let i = 1; i < totalModules; i++) {
                modulePromises.push(marketplaceContract.modules(i));
            }
            
            const moduleData = await Promise.all(modulePromises);
            const formattedModules = moduleData
                .map((module, index) => ({
                    id: index + 1,
                    creator: module.creator,
                    metadata: JSON.parse(module.metadata),
                    price: formatEther(module.price),
                    isActive: module.isActive,
                    rating: module.rating.toNumber() / 100,
                    numRatings: module.numRatings.toNumber()
                }))
                .filter(module => module.isActive);
            
            setModules(formattedModules);
        } catch (error) {
            console.error('Error loading modules:', error);
        } finally {
            setLoading(false);
        }
    };
    
    const filteredModules = modules
        .filter(module => {
            const matchesSearch = module.metadata.name
                .toLowerCase()
                .includes(searchTerm.toLowerCase());
            
            if (filter === 'all') return matchesSearch;
            if (filter === 'owned') return matchesSearch && module.creator === account;
            if (filter === 'top-rated') return matchesSearch && module.rating >= 4;
            
            return matchesSearch;
        });
    
    if (loading) {
        return (
            <Box
                display="flex"
                justifyContent="center"
                alignItems="center"
                minHeight="80vh"
            >
                <CircularProgress />
            </Box>
        );
    }
    
    return (
        <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
            <Box sx={{ mb: 4 }}>
                <Typography variant="h4" component="h1" gutterBottom>
                    AI Module Marketplace
                </Typography>
                
                <Grid container spacing={2} sx={{ mb: 3 }}>
                    <Grid item xs={12} md={6}>
                        <TextField
                            fullWidth
                            label="Search Modules"
                            variant="outlined"
                            value={searchTerm}
                            onChange={(e) => setSearchTerm(e.target.value)}
                        />
                    </Grid>
                    <Grid item xs={12} md={6}>
                        <Box sx={{ display: 'flex', gap: 1 }}>
                            <Chip
                                label="All"
                                onClick={() => setFilter('all')}
                                color={filter === 'all' ? 'primary' : 'default'}
                            />
                            <Chip
                                label="My Modules"
                                onClick={() => setFilter('owned')}
                                color={filter === 'owned' ? 'primary' : 'default'}
                            />
                            <Chip
                                label="Top Rated"
                                onClick={() => setFilter('top-rated')}
                                color={filter === 'top-rated' ? 'primary' : 'default'}
                            />
                        </Box>
                    </Grid>
                </Grid>
            </Box>
            
            <Grid container spacing={3}>
                {filteredModules.map((module) => (
                    <Grid item xs={12} sm={6} md={4} key={module.id}>
                        <Card>
                            <CardContent>
                                <Typography variant="h6" component="h2">
                                    {module.metadata.name}
                                </Typography>
                                
                                <Typography
                                    color="textSecondary"
                                    gutterBottom
                                    noWrap
                                    sx={{ mb: 2 }}
                                >
                                    {module.metadata.description}
                                </Typography>
                                
                                <Box
                                    sx={{
                                        display: 'flex',
                                        alignItems: 'center',
                                        mb: 1
                                    }}
                                >
                                    <Rating
                                        value={module.rating}
                                        readOnly
                                        precision={0.5}
                                    />
                                    <Typography
                                        variant="body2"
                                        color="textSecondary"
                                        sx={{ ml: 1 }}
                                    >
                                        ({module.numRatings})
                                    </Typography>
                                </Box>
                                
                                <Typography variant="h6" color="primary">
                                    {module.price} ETH
                                </Typography>
                            </CardContent>
                            
                            <CardActions>
                                <Button
                                    component={Link}
                                    to={`/module/${module.id}`}
                                    size="small"
                                    color="primary"
                                >
                                    View Details
                                </Button>
                                
                                {active && module.creator === account && (
                                    <Button
                                        size="small"
                                        color="secondary"
                                        component={Link}
                                        to={`/module/${module.id}/edit`}
                                    >
                                        Edit
                                    </Button>
                                )}
                            </CardActions>
                        </Card>
                    </Grid>
                ))}
            </Grid>
            
            {active && (
                <Box sx={{ mt: 4, display: 'flex', justifyContent: 'center' }}>
                    <Button
                        component={Link}
                        to="/create"
                        variant="contained"
                        color="primary"
                        size="large"
                    >
                        Create New Module
                    </Button>
                </Box>
            )}
        </Container>
    );
};

export default Marketplace;
