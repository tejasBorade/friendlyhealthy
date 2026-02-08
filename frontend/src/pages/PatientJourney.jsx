import React, { useState, useEffect } from 'react';
import {
  Container,
  Typography,
  Paper,
  Tabs,
  Tab,
  Box,
  Grid,
  Card,
  CardContent,
  Button,
  TextField,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Chip,
  IconButton,
  Avatar,
} from '@mui/material';
import { useParams, useNavigate } from 'react-router-dom';
import { LocalizationProvider, DatePicker } from '@mui/x-date-pickers';
import { AdapterDateFns } from '@mui/x-date-pickers/AdapterDateFns';
import AddIcon from '@mui/icons-material/Add';
import UploadIcon from '@mui/icons-material/Upload';
import DownloadIcon from '@mui/icons-material/Download';
import DeleteIcon from '@mui/icons-material/Delete';
import ArrowBackIcon from '@mui/icons-material/ArrowBack';
import api from '../services/api';
import { toast } from 'react-toastify';
import { format } from 'date-fns';

function TabPanel({ children, value, index }) {
  return (
    <div hidden={value !== index} style={{ paddingTop: 24 }}>
      {value === index && children}
    </div>
  );
}

const PatientJourney = () => {
  const { patientId } = useParams();
  const navigate = useNavigate();
  const [tabValue, setTabValue] = useState(0);
  const [patient, setPatient] = useState(null);
  const [appointments, setAppointments] = useState([]);
  const [medicalHistory, setMedicalHistory] = useState([]);
  const [prescriptions, setPrescriptions] = useState([]);
  const [reports, setReports] = useState([]);
  const [loading, setLoading] = useState(true);

  // Dialogs
  const [historyDialog, setHistoryDialog] = useState(false);
  const [prescriptionDialog, setPrescriptionDialog] = useState(false);
  const [reportDialog, setReportDialog] = useState(false);

  // Form states
  const [historyForm, setHistoryForm] = useState({
    diagnosis: '',
    symptoms: '',
    treatment: '',
    notes: '',
    visitDate: new Date(),
  });

  const [prescriptionForm, setPrescriptionForm] = useState({
    medicationName: '',
    dosage: '',
    frequency: '',
    duration: '',
    instructions: '',
    prescribedDate: new Date(),
  });

  const [reportForm, setReportForm] = useState({
    reportType: '',
    reportDate: new Date(),
    findings: '',
    file: null,
  });

  useEffect(() => {
    fetchPatientData();
  }, [patientId]);

  const fetchPatientData = async () => {
    try {
      setLoading(true);
      // Fetch patient details
      const patientRes = await api.get(`/patients/${patientId}`);
      setPatient(patientRes.data.patient || null);

      // Fetch appointments
      const appointmentsRes = await api.get('/appointments', {
        params: { patientId }
      });
      setAppointments(appointmentsRes.data.appointments || []);

      // Fetch medical history
      const historyRes = await api.get(`/medical-records/${patientId}`);
      setMedicalHistory(historyRes.data.records || []);

      // Fetch prescriptions
      const prescriptionsRes = await api.get(`/prescriptions/${patientId}`);
      setPrescriptions(prescriptionsRes.data.prescriptions || []);

      // Fetch reports
      const reportsRes = await api.get(`/reports/${patientId}`);
      setReports(reportsRes.data.reports || []);
    } catch (error) {
      console.error('Error fetching patient data:', error);
      toast.error('Failed to load patient data');
    } finally {
      setLoading(false);
    }
  };

  const handleAddHistory = async () => {
    try {
      await api.post('/medical-records', {
        patientId,
        ...historyForm,
        visitDate: historyForm.visitDate.toISOString().split('T')[0],
      });
      toast.success('Medical history added successfully');
      setHistoryDialog(false);
      setHistoryForm({
        diagnosis: '',
        symptoms: '',
        treatment: '',
        notes: '',
        visitDate: new Date(),
      });
      fetchPatientData();
    } catch (error) {
      toast.error('Failed to add medical history');
    }
  };

  const handleAddPrescription = async () => {
    try {
      await api.post('/prescriptions', {
        patientId,
        ...prescriptionForm,
        prescribedDate: prescriptionForm.prescribedDate.toISOString().split('T')[0],
      });
      toast.success('Prescription added successfully');
      setPrescriptionDialog(false);
      setPrescriptionForm({
        medicationName: '',
        dosage: '',
        frequency: '',
        duration: '',
        instructions: '',
        prescribedDate: new Date(),
      });
      fetchPatientData();
    } catch (error) {
      toast.error('Failed to add prescription');
    }
  };

  const handleUploadReport = async () => {
    try {
      const formData = new FormData();
      formData.append('patientId', patientId);
      formData.append('reportType', reportForm.reportType);
      formData.append('reportDate', reportForm.reportDate.toISOString().split('T')[0]);
      formData.append('findings', reportForm.findings);
      if (reportForm.file) {
        formData.append('file', reportForm.file);
      }

      await api.post('/reports', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      toast.success('Report uploaded successfully');
      setReportDialog(false);
      setReportForm({
        reportType: '',
        reportDate: new Date(),
        findings: '',
        file: null,
      });
      fetchPatientData();
    } catch (error) {
      toast.error('Failed to upload report');
    }
  };

  const formatDate = (date) => {
    try {
      return format(new Date(date), 'MMM dd, yyyy');
    } catch {
      return date;
    }
  };

  if (loading) {
    return (
      <Container sx={{ mt: 4, textAlign: 'center' }}>
        <Typography>Loading patient data...</Typography>
      </Container>
    );
  }

  return (
    <Container maxWidth="xl" sx={{ mt: 4, mb: 4 }}>
      {/* Header */}
      <Box sx={{ mb: 3, display: 'flex', alignItems: 'center', gap: 2 }}>
        <IconButton onClick={() => navigate(-1)}>
          <ArrowBackIcon />
        </IconButton>
        <Box sx={{ flexGrow: 1 }}>
          <Typography variant="h4">
            Patient Journey - {patient?.first_name} {patient?.last_name}
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Patient ID: {patientId} | DOB: {patient?.date_of_birth ? formatDate(patient.date_of_birth) : 'N/A'} | 
            Blood Group: {patient?.blood_group || 'N/A'}
          </Typography>
        </Box>
      </Box>

      {/* Patient Info Cards */}
      <Grid container spacing={2} sx={{ mb: 3 }}>
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Typography color="text.secondary" gutterBottom>Total Visits</Typography>
              <Typography variant="h4">{appointments.length}</Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Typography color="text.secondary" gutterBottom>Medical Records</Typography>
              <Typography variant="h4">{medicalHistory.length}</Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Typography color="text.secondary" gutterBottom>Prescriptions</Typography>
              <Typography variant="h4">{prescriptions.length}</Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Typography color="text.secondary" gutterBottom>Reports</Typography>
              <Typography variant="h4">{reports.length}</Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Tabs */}
      <Paper sx={{ mb: 3 }}>
        <Tabs value={tabValue} onChange={(e, v) => setTabValue(v)}>
          <Tab label="Appointments History" />
          <Tab label="Medical History" />
          <Tab label="Prescriptions" />
          <Tab label="Reports & Documents" />
        </Tabs>
      </Paper>

      {/* Appointments Tab */}
      <TabPanel value={tabValue} index={0}>
        <TableContainer component={Paper}>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Date</TableCell>
                <TableCell>Time</TableCell>
                <TableCell>Reason</TableCell>
                <TableCell>Status</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {appointments.map((apt) => (
                <TableRow key={apt.id}>
                  <TableCell>{formatDate(apt.appointment_date)}</TableCell>
                  <TableCell>{apt.appointment_time}</TableCell>
                  <TableCell>{apt.reason}</TableCell>
                  <TableCell>
                    <Chip label={apt.status} color="primary" size="small" />
                  </TableCell>
                </TableRow>
              ))}
              {appointments.length === 0 && (
                <TableRow>
                  <TableCell colSpan={4} align="center">No appointments found</TableCell>
                </TableRow>
              )}
            </TableBody>
          </Table>
        </TableContainer>
      </TabPanel>

      {/* Medical History Tab */}
      <TabPanel value={tabValue} index={1}>
        <Box sx={{ mb: 2 }}>
          <Button
            variant="contained"
            startIcon={<AddIcon />}
            onClick={() => setHistoryDialog(true)}
          >
            Add Medical History
          </Button>
        </Box>
        <Grid container spacing={2}>
          {medicalHistory.map((record) => (
            <Grid item xs={12} key={record.id}>
              <Card>
                <CardContent>
                  <Typography variant="h6">{record.diagnosis}</Typography>
                  <Typography variant="body2" color="text.secondary" gutterBottom>
                    Visit Date: {formatDate(record.visit_date)}
                  </Typography>
                  <Typography variant="body2" sx={{ mt: 1 }}>
                    <strong>Symptoms:</strong> {record.symptoms}
                  </Typography>
                  <Typography variant="body2">
                    <strong>Treatment:</strong> {record.treatment}
                  </Typography>
                  {record.notes && (
                    <Typography variant="body2">
                      <strong>Notes:</strong> {record.notes}
                    </Typography>
                  )}
                </CardContent>
              </Card>
            </Grid>
          ))}
          {medicalHistory.length === 0 && (
            <Grid item xs={12}>
              <Typography align="center" color="text.secondary">
                No medical history recorded yet
              </Typography>
            </Grid>
          )}
        </Grid>
      </TabPanel>

      {/* Prescriptions Tab */}
      <TabPanel value={tabValue} index={2}>
        <Box sx={{ mb: 2 }}>
          <Button
            variant="contained"
            startIcon={<AddIcon />}
            onClick={() => setPrescriptionDialog(true)}
          >
            Add Prescription
          </Button>
        </Box>
        <TableContainer component={Paper}>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Date</TableCell>
                <TableCell>Medication</TableCell>
                <TableCell>Dosage</TableCell>
                <TableCell>Frequency</TableCell>
                <TableCell>Duration</TableCell>
                <TableCell>Instructions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {prescriptions.map((rx) => (
                <TableRow key={rx.id}>
                  <TableCell>{formatDate(rx.prescribed_date)}</TableCell>
                  <TableCell>{rx.medication_name}</TableCell>
                  <TableCell>{rx.dosage}</TableCell>
                  <TableCell>{rx.frequency}</TableCell>
                  <TableCell>{rx.duration}</TableCell>
                  <TableCell>{rx.instructions}</TableCell>
                </TableRow>
              ))}
              {prescriptions.length === 0 && (
                <TableRow>
                  <TableCell colSpan={6} align="center">No prescriptions found</TableCell>
                </TableRow>
              )}
            </TableBody>
          </Table>
        </TableContainer>
      </TabPanel>

      {/* Reports Tab */}
      <TabPanel value={tabValue} index={3}>
        <Box sx={{ mb: 2 }}>
          <Button
            variant="contained"
            startIcon={<UploadIcon />}
            onClick={() => setReportDialog(true)}
          >
            Upload Report
          </Button>
        </Box>
        <Grid container spacing={2}>
          {reports.map((report) => (
            <Grid item xs={12} md={6} key={report.id}>
              <Card>
                <CardContent>
                  <Typography variant="h6">{report.report_type}</Typography>
                  <Typography variant="body2" color="text.secondary">
                    Date: {formatDate(report.report_date)}
                  </Typography>
                  <Typography variant="body2" sx={{ mt: 1 }}>
                    {report.findings}
                  </Typography>
                  <Box sx={{ mt: 2 }}>
                    <Button
                      size="small"
                      startIcon={<DownloadIcon />}
                      onClick={() => window.open(report.file_url, '_blank')}
                    >
                      Download
                    </Button>
                  </Box>
                </CardContent>
              </Card>
            </Grid>
          ))}
          {reports.length === 0 && (
            <Grid item xs={12}>
              <Typography align="center" color="text.secondary">
                No reports uploaded yet
              </Typography>
            </Grid>
          )}
        </Grid>
      </TabPanel>

      {/* Add Medical History Dialog */}
      <Dialog open={historyDialog} onClose={() => setHistoryDialog(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Add Medical History</DialogTitle>
        <DialogContent>
          <Box sx={{ mt: 2, display: 'flex', flexDirection: 'column', gap: 2 }}>
            <LocalizationProvider dateAdapter={AdapterDateFns}>
              <DatePicker
                label="Visit Date"
                value={historyForm.visitDate}
                onChange={(date) => setHistoryForm({ ...historyForm, visitDate: date })}
                slotProps={{ textField: { fullWidth: true } }}
              />
            </LocalizationProvider>
            <TextField
              fullWidth
              label="Diagnosis"
              value={historyForm.diagnosis}
              onChange={(e) => setHistoryForm({ ...historyForm, diagnosis: e.target.value })}
            />
            <TextField
              fullWidth
              multiline
              rows={2}
              label="Symptoms"
              value={historyForm.symptoms}
              onChange={(e) => setHistoryForm({ ...historyForm, symptoms: e.target.value })}
            />
            <TextField
              fullWidth
              multiline
              rows={2}
              label="Treatment"
              value={historyForm.treatment}
              onChange={(e) => setHistoryForm({ ...historyForm, treatment: e.target.value })}
            />
            <TextField
              fullWidth
              multiline
              rows={2}
              label="Additional Notes"
              value={historyForm.notes}
              onChange={(e) => setHistoryForm({ ...historyForm, notes: e.target.value })}
            />
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setHistoryDialog(false)}>Cancel</Button>
          <Button onClick={handleAddHistory} variant="contained">Add History</Button>
        </DialogActions>
      </Dialog>

      {/* Add Prescription Dialog */}
      <Dialog open={prescriptionDialog} onClose={() => setPrescriptionDialog(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Add Prescription</DialogTitle>
        <DialogContent>
          <Box sx={{ mt: 2, display: 'flex', flexDirection: 'column', gap: 2 }}>
            <LocalizationProvider dateAdapter={AdapterDateFns}>
              <DatePicker
                label="Prescribed Date"
                value={prescriptionForm.prescribedDate}
                onChange={(date) => setPrescriptionForm({ ...prescriptionForm, prescribedDate: date })}
                slotProps={{ textField: { fullWidth: true } }}
              />
            </LocalizationProvider>
            <TextField
              fullWidth
              label="Medication Name"
              value={prescriptionForm.medicationName}
              onChange={(e) => setPrescriptionForm({ ...prescriptionForm, medicationName: e.target.value })}
            />
            <TextField
              fullWidth
              label="Dosage"
              placeholder="e.g., 500mg"
              value={prescriptionForm.dosage}
              onChange={(e) => setPrescriptionForm({ ...prescriptionForm, dosage: e.target.value })}
            />
            <TextField
              fullWidth
              label="Frequency"
              placeholder="e.g., Twice daily"
              value={prescriptionForm.frequency}
              onChange={(e) => setPrescriptionForm({ ...prescriptionForm, frequency: e.target.value })}
            />
            <TextField
              fullWidth
              label="Duration"
              placeholder="e.g., 7 days"
              value={prescriptionForm.duration}
              onChange={(e) => setPrescriptionForm({ ...prescriptionForm, duration: e.target.value })}
            />
            <TextField
              fullWidth
              multiline
              rows={2}
              label="Instructions"
              value={prescriptionForm.instructions}
              onChange={(e) => setPrescriptionForm({ ...prescriptionForm, instructions: e.target.value })}
            />
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setPrescriptionDialog(false)}>Cancel</Button>
          <Button onClick={handleAddPrescription} variant="contained">Add Prescription</Button>
        </DialogActions>
      </Dialog>

      {/* Upload Report Dialog */}
      <Dialog open={reportDialog} onClose={() => setReportDialog(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Upload Report</DialogTitle>
        <DialogContent>
          <Box sx={{ mt: 2, display: 'flex', flexDirection: 'column', gap: 2 }}>
            <TextField
              fullWidth
              label="Report Type"
              placeholder="e.g., Blood Test, X-Ray, MRI"
              value={reportForm.reportType}
              onChange={(e) => setReportForm({ ...reportForm, reportType: e.target.value })}
            />
            <LocalizationProvider dateAdapter={AdapterDateFns}>
              <DatePicker
                label="Report Date"
                value={reportForm.reportDate}
                onChange={(date) => setReportForm({ ...reportForm, reportDate: date })}
                slotProps={{ textField: { fullWidth: true } }}
              />
            </LocalizationProvider>
            <TextField
              fullWidth
              multiline
              rows={3}
              label="Findings"
              value={reportForm.findings}
              onChange={(e) => setReportForm({ ...reportForm, findings: e.target.value })}
            />
            <Button
              variant="outlined"
              component="label"
              startIcon={<UploadIcon />}
            >
              Choose File
              <input
                type="file"
                hidden
                onChange={(e) => setReportForm({ ...reportForm, file: e.target.files[0] })}
              />
            </Button>
            {reportForm.file && (
              <Typography variant="body2">
                Selected: {reportForm.file.name}
              </Typography>
            )}
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setReportDialog(false)}>Cancel</Button>
          <Button onClick={handleUploadReport} variant="contained">Upload Report</Button>
        </DialogActions>
      </Dialog>
    </Container>
  );
};

export default PatientJourney;
