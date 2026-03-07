import React, { useState } from 'react';
import {
  Box,
  Container,
  Typography,
  TextField,
  Button,
  Paper,
  Tabs,
  Tab,
  Card,
  CardContent,
  Chip,
  CircularProgress,
  Alert,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  InputAdornment,
  Divider,
  List,
  ListItem,
  ListItemText,
  Badge,
} from '@mui/material';
import {
  Search,
  ExpandMore,
  Medication,
  Warning,
  Info,
  LocalPharmacy,
  HealthAndSafety,
  Description,
} from '@mui/icons-material';
import axios from 'axios';

const FDA_API_BASE = 'https://api.fda.gov';

const DrugSearch = () => {
  const [searchTerm, setSearchTerm] = useState('');
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState(0);
  const [drugInfo, setDrugInfo] = useState(null);
  const [adverseEvents, setAdverseEvents] = useState(null);
  const [recalls, setRecalls] = useState(null);
  const [error, setError] = useState('');

  // Search drug information
  const searchDrug = async () => {
    if (!searchTerm || searchTerm.trim().length < 2) {
      setError('Please enter at least 2 characters');
      return;
    }

    setLoading(true);
    setError('');
    setDrugInfo(null);
    setAdverseEvents(null);
    setRecalls(null);

    try {
      // Search drug labels
      const labelResponse = await axios.get(
        `${FDA_API_BASE}/drug/label.json`,
        {
          params: {
            search: `openfda.brand_name:"${searchTerm}" OR openfda.generic_name:"${searchTerm}"`,
            limit: 5,
          },
        }
      );

      setDrugInfo(labelResponse.data);

      // Search adverse events
      try {
        const eventsResponse = await axios.get(
          `${FDA_API_BASE}/drug/event.json`,
          {
            params: {
              search: `patient.drug.medicinalproduct:"${searchTerm}"`,
              limit: 10,
            },
          }
        );
        setAdverseEvents(eventsResponse.data);
      } catch (eventErr) {
        console.log('No adverse events found');
        setAdverseEvents({ results: [] });
      }

      // Search recalls
      try {
        const recallsResponse = await axios.get(
          `${FDA_API_BASE}/drug/enforcement.json`,
          {
            params: {
              search: `product_description:"${searchTerm}"`,
              limit: 10,
            },
          }
        );
        setRecalls(recallsResponse.data);
      } catch (recallErr) {
        console.log('No recalls found');
        setRecalls({ results: [] });
      }
    } catch (err) {
      console.error('Error searching drug:', err);
      if (err.response?.status === 404) {
        setError('No drug information found. Try a different drug name.');
      } else {
        setError('Failed to fetch drug information. Please try again.');
      }
    } finally {
      setLoading(false);
    }
  };

  // Handle Enter key press
  const handleKeyPress = (e) => {
    if (e.key === 'Enter') {
      searchDrug();
    }
  };

  // Render drug information tab
  const renderDrugInfo = () => {
    if (!drugInfo?.results?.[0]) {
      return (
        <Alert severity="info" sx={{ mt: 2 }}>
          No drug information available
        </Alert>
      );
    }

    const drug = drugInfo.results[0];
    const brandNames = drug.openfda?.brand_name || [];
    const genericNames = drug.openfda?.generic_name || [];
    const manufacturer = drug.openfda?.manufacturer_name?.[0] || 'N/A';
    const purpose = drug.purpose?.[0] || 'N/A';
    const indications = drug.indications_and_usage?.[0] || 'N/A';
    const warnings = drug.warnings?.[0] || 'N/A';
    const dosage = drug.dosage_and_administration?.[0] || 'N/A';
    const activeIngredients = drug.active_ingredient?.[0] || 'N/A';

    return (
      <Box sx={{ mt: 3 }}>
        {/* Brand and Generic Names */}
        <Card sx={{ mb: 2 }}>
          <CardContent>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
              <LocalPharmacy sx={{ color: '#10b981', fontSize: 28 }} />
              <Typography variant="h6" sx={{ fontWeight: 600 }}>
                Drug Names
              </Typography>
            </Box>
            <Box sx={{ mb: 2 }}>
              <Typography variant="body2" color="text.secondary" gutterBottom>
                Brand Names:
              </Typography>
              <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                {brandNames.map((name, idx) => (
                  <Chip key={idx} label={name} color="primary" size="small" />
                ))}
              </Box>
            </Box>
            <Box>
              <Typography variant="body2" color="text.secondary" gutterBottom>
                Generic Names:
              </Typography>
              <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                {genericNames.map((name, idx) => (
                  <Chip key={idx} label={name} variant="outlined" size="small" />
                ))}
              </Box>
            </Box>
            <Divider sx={{ my: 2 }} />
            <Typography variant="body2" color="text.secondary">
              Manufacturer: <strong>{manufacturer}</strong>
            </Typography>
          </CardContent>
        </Card>

        {/* Purpose */}
        <Accordion defaultExpanded>
          <AccordionSummary expandIcon={<ExpandMore />}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <Info sx={{ color: '#3b82f6' }} />
              <Typography fontWeight={600}>Purpose</Typography>
            </Box>
          </AccordionSummary>
          <AccordionDetails>
            <Typography variant="body2" sx={{ whiteSpace: 'pre-wrap' }}>
              {purpose}
            </Typography>
          </AccordionDetails>
        </Accordion>

        {/* Indications and Usage */}
        <Accordion>
          <AccordionSummary expandIcon={<ExpandMore />}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <HealthAndSafety sx={{ color: '#10b981' }} />
              <Typography fontWeight={600}>Indications and Usage</Typography>
            </Box>
          </AccordionSummary>
          <AccordionDetails>
            <Typography variant="body2" sx={{ whiteSpace: 'pre-wrap' }}>
              {indications}
            </Typography>
          </AccordionDetails>
        </Accordion>

        {/* Active Ingredients */}
        <Accordion>
          <AccordionSummary expandIcon={<ExpandMore />}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <Medication sx={{ color: '#8b5cf6' }} />
              <Typography fontWeight={600}>Active Ingredients</Typography>
            </Box>
          </AccordionSummary>
          <AccordionDetails>
            <Typography variant="body2" sx={{ whiteSpace: 'pre-wrap' }}>
              {activeIngredients}
            </Typography>
          </AccordionDetails>
        </Accordion>

        {/* Dosage */}
        <Accordion>
          <AccordionSummary expandIcon={<ExpandMore />}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <Description sx={{ color: '#f59e0b' }} />
              <Typography fontWeight={600}>Dosage and Administration</Typography>
            </Box>
          </AccordionSummary>
          <AccordionDetails>
            <Typography variant="body2" sx={{ whiteSpace: 'pre-wrap' }}>
              {dosage}
            </Typography>
          </AccordionDetails>
        </Accordion>

        {/* Warnings */}
        <Accordion>
          <AccordionSummary expandIcon={<ExpandMore />}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <Warning sx={{ color: '#ef4444' }} />
              <Typography fontWeight={600}>Warnings</Typography>
            </Box>
          </AccordionSummary>
          <AccordionDetails>
            <Alert severity="warning" sx={{ mb: 2 }}>
              Always consult healthcare professionals before taking any medication
            </Alert>
            <Typography variant="body2" sx={{ whiteSpace: 'pre-wrap' }}>
              {warnings}
            </Typography>
          </AccordionDetails>
        </Accordion>
      </Box>
    );
  };

  // Render adverse events tab
  const renderAdverseEvents = () => {
    if (!adverseEvents?.results || adverseEvents.results.length === 0) {
      return (
        <Alert severity="success" sx={{ mt: 2 }}>
          No adverse events reported for this drug
        </Alert>
      );
    }

    // Aggregate reaction counts
    const reactionCounts = {};
    adverseEvents.results.forEach((event) => {
      event.patient?.reaction?.forEach((reaction) => {
        const name = reaction.reactionmeddrapt;
        reactionCounts[name] = (reactionCounts[name] || 0) + 1;
      });
    });

    const topReactions = Object.entries(reactionCounts)
      .sort((a, b) => b[1] - a[1])
      .slice(0, 10);

    return (
      <Box sx={{ mt: 3 }}>
        <Alert severity="info" sx={{ mb: 2 }}>
          Showing reported adverse events from FDA database. Total reports: {adverseEvents.results.length}
        </Alert>

        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Most Common Reported Reactions
            </Typography>
            <List>
              {topReactions.map(([reaction, count], idx) => (
                <ListItem key={idx} divider>
                  <ListItemText
                    primary={reaction}
                    secondary={`Reported ${count} time(s) in this dataset`}
                  />
                  <Chip label={count} color="warning" size="small" />
                </ListItem>
              ))}
            </List>
          </CardContent>
        </Card>

        <Alert severity="warning" sx={{ mt: 2 }}>
          These are reported adverse events and do not establish causation. Consult healthcare professionals for medical advice.
        </Alert>
      </Box>
    );
  };

  // Render recalls tab
  const renderRecalls = () => {
    if (!recalls?.results || recalls.results.length === 0) {
      return (
        <Alert severity="success" sx={{ mt: 2 }}>
          No recalls found for this drug
        </Alert>
      );
    }

    return (
      <Box sx={{ mt: 3 }}>
        <Alert severity="error" sx={{ mb: 2 }}>
          {recalls.results.length} recall(s) found for this drug
        </Alert>

        {recalls.results.map((recall, idx) => (
          <Accordion key={idx}>
            <AccordionSummary expandIcon={<ExpandMore />}>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, width: '100%' }}>
                <Warning sx={{ color: '#ef4444' }} />
                <Box sx={{ flexGrow: 1 }}>
                  <Typography fontWeight={600}>
                    {recall.product_description?.substring(0, 100)}...
                  </Typography>
                  <Typography variant="caption" color="text.secondary">
                    {new Date(recall.recall_initiation_date).toLocaleDateString()}
                  </Typography>
                </Box>
                <Chip
                  label={recall.classification || 'N/A'}
                  color={recall.classification === 'Class I' ? 'error' : 'warning'}
                  size="small"
                />
              </Box>
            </AccordionSummary>
            <AccordionDetails>
              <Box>
                <Typography variant="body2" paragraph>
                  <strong>Reason:</strong> {recall.reason_for_recall}
                </Typography>
                <Typography variant="body2" paragraph>
                  <strong>Status:</strong> {recall.status}
                </Typography>
                <Typography variant="body2" paragraph>
                  <strong>Company:</strong> {recall.recalling_firm}
                </Typography>
                <Typography variant="body2">
                  <strong>Distribution:</strong> {recall.distribution_pattern || 'N/A'}
                </Typography>
              </Box>
            </AccordionDetails>
          </Accordion>
        ))}
      </Box>
    );
  };

  return (
    <Box
      id="drug-search"
      sx={{
        py: 8,
        background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
      }}
    >
      <Container maxWidth="lg">
        <Box sx={{ textAlign: 'center', mb: 4 }}>
          <Box sx={{ display: 'flex', justifyContent: 'center', mb: 2 }}>
            <Box
              sx={{
                width: 70,
                height: 70,
                background: 'white',
                borderRadius: '50%',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
              }}
            >
              <LocalPharmacy sx={{ fontSize: 40, color: '#667eea' }} />
            </Box>
          </Box>
          <Typography
            variant="h3"
            sx={{
              fontWeight: 700,
              color: 'white',
              mb: 2,
              fontSize: { xs: '2rem', md: '3rem' },
            }}
          >
            FDA Drug Information
          </Typography>
          <Typography
            variant="h6"
            sx={{
              color: 'rgba(255,255,255,0.9)',
              maxWidth: 700,
              mx: 'auto',
            }}
          >
            Search official FDA database for drug information, adverse events, and recalls
          </Typography>
        </Box>

        <Paper
          elevation={8}
          sx={{
            p: 4,
            borderRadius: 4,
            maxWidth: 900,
            mx: 'auto',
          }}
        >
          {/* Search Bar */}
          <TextField
            fullWidth
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Enter drug name (e.g., Aspirin, Ibuprofen, Metformin)"
            InputProps={{
              startAdornment: (
                <InputAdornment position="start">
                  <Search />
                </InputAdornment>
              ),
              endAdornment: loading && (
                <InputAdornment position="end">
                  <CircularProgress size={24} />
                </InputAdornment>
              ),
            }}
            sx={{ mb: 2 }}
          />

          <Button
            fullWidth
            variant="contained"
            size="large"
            onClick={searchDrug}
            disabled={loading}
            sx={{
              background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
              py: 1.5,
              fontSize: '1.1rem',
            }}
          >
            {loading ? 'Searching...' : 'Search Drug Information'}
          </Button>

          {/* Error Message */}
          {error && (
            <Alert severity="error" sx={{ mt: 2 }}>
              {error}
            </Alert>
          )}

          {/* Results Tabs */}
          {(drugInfo || adverseEvents || recalls) && !loading && (
            <Box sx={{ mt: 4 }}>
              <Tabs
                value={activeTab}
                onChange={(e, newValue) => setActiveTab(newValue)}
                variant="fullWidth"
              >
                <Tab
                  label={
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                      <Info />
                      <span>Drug Info</span>
                    </Box>
                  }
                />
                <Tab
                  label={
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                      <Warning />
                      <span>Adverse Events</span>
                      {adverseEvents?.results?.length > 0 && (
                        <Badge badgeContent={adverseEvents.results.length} color="error" />
                      )}
                    </Box>
                  }
                />
                <Tab
                  label={
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                      <HealthAndSafety />
                      <span>Recalls</span>
                      {recalls?.results?.length > 0 && (
                        <Badge badgeContent={recalls.results.length} color="error" />
                      )}
                    </Box>
                  }
                />
              </Tabs>

              {activeTab === 0 && renderDrugInfo()}
              {activeTab === 1 && renderAdverseEvents()}
              {activeTab === 2 && renderRecalls()}
            </Box>
          )}

          {/* Info Box */}
          {!drugInfo && !loading && (
            <Alert severity="info" sx={{ mt: 3 }}>
              <Typography variant="body2" fontWeight={600} gutterBottom>
                About openFDA Drug Database:
              </Typography>
              <Typography variant="body2">
                • Search by brand name or generic name
                <br />
                • View official FDA drug labels and information
                <br />
                • Check reported adverse events
                <br />
                • See drug recalls and safety alerts
                <br />• All data is from official FDA sources
              </Typography>
            </Alert>
          )}
        </Paper>

        {/* Medical Disclaimer */}
        <Alert severity="warning" sx={{ mt: 3, maxWidth: 900, mx: 'auto' }}>
          <Typography variant="body2">
            <strong>Medical Disclaimer:</strong> This information is sourced from the FDA and is for
            educational purposes only. It does not constitute medical advice. Always consult with
            qualified healthcare professionals before taking any medication or making health decisions.
          </Typography>
        </Alert>
      </Container>
    </Box>
  );
};

export default DrugSearch;
