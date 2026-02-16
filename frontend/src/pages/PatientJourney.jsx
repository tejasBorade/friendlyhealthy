import React, { useEffect, useMemo, useState } from 'react';
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
  MenuItem,
} from '@mui/material';
import { useParams, useNavigate } from 'react-router-dom';
import { LocalizationProvider, DatePicker } from '@mui/x-date-pickers';
import { AdapterDateFns } from '@mui/x-date-pickers/AdapterDateFns';
import AddIcon from '@mui/icons-material/Add';
import UploadIcon from '@mui/icons-material/Upload';
import DownloadIcon from '@mui/icons-material/Download';
import ArrowBackIcon from '@mui/icons-material/ArrowBack';
import api from '../services/api';
import { toast } from 'react-toastify';
import { format } from 'date-fns';
import DoctorSidebar from '../components/DoctorSidebar';

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

  const [historyDialog, setHistoryDialog] = useState(false);
  const [prescriptionDialog, setPrescriptionDialog] = useState(false);
  const [reportDialog, setReportDialog] = useState(false);

  const [historyForm, setHistoryForm] = useState({
    appointmentId: '',
    diagnosis: '',
    symptoms: '',
    treatment: '',
    notes: '',
    visitDate: new Date(),
  });

  const [prescriptionForm, setPrescriptionForm] = useState({
    appointmentId: '',
    diagnosis: '',
    medicationName: '',
    dosage: '',
    frequency: '',
    duration: '',
    instructions: '',
  });

  const [reportForm, setReportForm] = useState({
    appointmentId: '',
    reportType: 'Lab Test',
    reportDate: new Date(),
    findings: '',
    file: null,
  });

  useEffect(() => {
    fetchPatientData();
  }, [patientId]);

  const appointmentOptions = useMemo(
    () =>
      appointments.map((apt) => ({
        id: apt.id,
        label: `${formatDate(apt.appointment_date)} ${apt.appointment_time || ''} - ${apt.reason || 'Consultation'}`,
      })),
    [appointments]
  );

  const fetchPatientData = async () => {
    try {
      setLoading(true);

      const [patientRes, appointmentsRes, recordsRes, prescriptionsRes] = await Promise.all([
        api.get(`/patients/${patientId}`),
        api.get('/appointments', { params: { patientId } }),
        api.get('/medical-records', { params: { patientId } }),
        api.get('/prescriptions', { params: { patientId } }),
      ]);

      const allAppointments = appointmentsRes.data.appointments || [];
      const allRecords = recordsRes.data.records || [];
      const allPrescriptions = prescriptionsRes.data.prescriptions || [];

      setPatient(patientRes.data.patient || null);
      setAppointments(allAppointments);
      setPrescriptions(allPrescriptions);

      const historyRecords = allRecords.filter(
        (record) => record.record_type === 'Clinical Note' || record.record_type === 'Medical History'
      );
      const reportRecords = allRecords.filter(
        (record) => record.record_type !== 'Clinical Note' && record.record_type !== 'Medical History'
      );
      setMedicalHistory(historyRecords);
      setReports(reportRecords);
    } catch (error) {
      console.error('Error fetching patient data:', error);
      toast.error('Failed to load patient data');
    } finally {
      setLoading(false);
    }
  };

  const handleAddHistory = async () => {
    if (!historyForm.appointmentId || !historyForm.diagnosis) {
      toast.error('Please select an appointment and add diagnosis');
      return;
    }

    try {
      await api.post('/medical-records', {
        patientId,
        appointmentId: historyForm.appointmentId,
        recordType: 'Clinical Note',
        title: historyForm.diagnosis,
        description: `Symptoms: ${historyForm.symptoms}\nTreatment: ${historyForm.treatment}`,
        resultSummary: historyForm.notes,
        testDate: historyForm.visitDate.toISOString().split('T')[0],
      });
      toast.success('Medical history added successfully');
      setHistoryDialog(false);
      setHistoryForm({
        appointmentId: '',
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
    if (!prescriptionForm.appointmentId || !prescriptionForm.medicationName) {
      toast.error('Please select an appointment and medication');
      return;
    }

    try {
      await api.post('/prescriptions', {
        patientId,
        appointmentId: prescriptionForm.appointmentId,
        diagnosis: prescriptionForm.diagnosis || 'Consultation',
        medicationName: prescriptionForm.medicationName,
        dosage: prescriptionForm.dosage,
        frequency: prescriptionForm.frequency,
        duration: prescriptionForm.duration,
        instructions: prescriptionForm.instructions,
      });
      toast.success('Prescription added successfully');
      setPrescriptionDialog(false);
      setPrescriptionForm({
        appointmentId: '',
        diagnosis: '',
        medicationName: '',
        dosage: '',
        frequency: '',
        duration: '',
        instructions: '',
      });
      fetchPatientData();
    } catch (error) {
      toast.error('Failed to add prescription');
    }
  };

  const handleUploadReport = async () => {
    if (!reportForm.appointmentId || !reportForm.findings) {
      toast.error('Please select an appointment and enter findings');
      return;
    }

    try {
      await api.post('/medical-records', {
        patientId,
        appointmentId: reportForm.appointmentId,
        recordType: reportForm.reportType || 'Lab Test',
        title: reportForm.reportType || 'Report',
        resultSummary: reportForm.findings,
        testDate: reportForm.reportDate.toISOString().split('T')[0],
        fileUrl: reportForm.file?.name || null,
      });
      toast.success('Report added successfully');
      setReportDialog(false);
      setReportForm({
        appointmentId: '',
        reportType: 'Lab Test',
        reportDate: new Date(),
        findings: '',
        file: null,
      });
      fetchPatientData();
    } catch (error) {
      toast.error('Failed to add report');
    }
  };

  function formatDate(date) {
    try {
      return format(new Date(date), 'MMM dd, yyyy');
    } catch {
      return date;
    }
  }

  const loadingContent = (
    <Container sx={{ mt: 4, textAlign: 'center' }}>
      <Typography>Loading patient data...</Typography>
    </Container>
  );

  if (loading) {
    return (
      <Box sx={{ display: 'flex', minHeight: '100vh', background: '#f9fafb' }}>
        <DoctorSidebar activeItem="My Patients" />
        <Box sx={{ ml: { xs: 0, md: '280px' }, flex: 1 }}>{loadingContent}</Box>
      </Box>
    );
  }

  const pageContent = (
    <Container maxWidth="xl" sx={{ mt: 4, mb: 4 }}>
      <Box sx={{ mb: 3, display: 'flex', alignItems: 'center', gap: 2 }}>
        <IconButton onClick={() => navigate(-1)}>
          <ArrowBackIcon />
        </IconButton>
        <Box sx={{ flexGrow: 1 }}>
          <Typography variant="h4">
            Patient Journey - {patient?.first_name} {patient?.last_name}
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Patient ID: {patientId} | DOB:{' '}
            {patient?.date_of_birth ? formatDate(patient.date_of_birth) : 'N/A'} | Blood Group:{' '}
            {patient?.blood_group || 'N/A'}
          </Typography>
        </Box>
      </Box>

      <Grid container spacing={2} sx={{ mb: 3 }}>
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Typography color="text.secondary" gutterBottom>
                Total Visits
              </Typography>
              <Typography variant="h4">{appointments.length}</Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Typography color="text.secondary" gutterBottom>
                Medical History
              </Typography>
              <Typography variant="h4">{medicalHistory.length}</Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Typography color="text.secondary" gutterBottom>
                Prescriptions
              </Typography>
              <Typography variant="h4">{prescriptions.length}</Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Typography color="text.secondary" gutterBottom>
                Reports
              </Typography>
              <Typography variant="h4">{reports.length}</Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      <Paper sx={{ mb: 3 }}>
        <Tabs value={tabValue} onChange={(e, v) => setTabValue(v)}>
          <Tab label="Appointments History" />
          <Tab label="Medical History" />
          <Tab label="Prescriptions" />
          <Tab label="Reports & Documents" />
        </Tabs>
      </Paper>

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
                    <Chip label={apt.status} size="small" />
                  </TableCell>
                </TableRow>
              ))}
              {appointments.length === 0 && (
                <TableRow>
                  <TableCell colSpan={4} align="center">
                    No appointments found
                  </TableCell>
                </TableRow>
              )}
            </TableBody>
          </Table>
        </TableContainer>
      </TabPanel>

      <TabPanel value={tabValue} index={1}>
        <Box sx={{ mb: 2 }}>
          <Button variant="contained" startIcon={<AddIcon />} onClick={() => setHistoryDialog(true)}>
            Add Medical History
          </Button>
        </Box>
        <Grid container spacing={2}>
          {medicalHistory.map((record) => (
            <Grid item xs={12} key={record.id}>
              <Card>
                <CardContent>
                  <Typography variant="h6">{record.title}</Typography>
                  <Typography variant="body2" color="text.secondary" gutterBottom>
                    Visit Date: {formatDate(record.test_date)}
                  </Typography>
                  <Typography variant="body2" sx={{ whiteSpace: 'pre-line' }}>
                    {record.description || '-'}
                  </Typography>
                  {record.result_summary && (
                    <Typography variant="body2" sx={{ mt: 1 }}>
                      <strong>Notes:</strong> {record.result_summary}
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
                <TableCell>Diagnosis</TableCell>
                <TableCell>Appointment</TableCell>
                <TableCell>Notes</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {prescriptions.map((rx) => (
                <TableRow key={rx.id}>
                  <TableCell>{formatDate(rx.created_at)}</TableCell>
                  <TableCell>{rx.diagnosis}</TableCell>
                  <TableCell>{formatDate(rx.appointment_date)}</TableCell>
                  <TableCell>{rx.notes || '-'}</TableCell>
                </TableRow>
              ))}
              {prescriptions.length === 0 && (
                <TableRow>
                  <TableCell colSpan={4} align="center">
                    No prescriptions found
                  </TableCell>
                </TableRow>
              )}
            </TableBody>
          </Table>
        </TableContainer>
      </TabPanel>

      <TabPanel value={tabValue} index={3}>
        <Box sx={{ mb: 2 }}>
          <Button variant="contained" startIcon={<UploadIcon />} onClick={() => setReportDialog(true)}>
            Add Report
          </Button>
        </Box>
        <Grid container spacing={2}>
          {reports.map((report) => (
            <Grid item xs={12} md={6} key={report.id}>
              <Card>
                <CardContent>
                  <Typography variant="h6">{report.record_type}</Typography>
                  <Typography variant="body2" color="text.secondary">
                    Date: {formatDate(report.test_date)}
                  </Typography>
                  <Typography variant="body2" sx={{ mt: 1 }}>
                    {report.result_summary || '-'}
                  </Typography>
                  {report.file_url && (
                    <Box sx={{ mt: 2 }}>
                      <Button size="small" startIcon={<DownloadIcon />}>
                        {report.file_url}
                      </Button>
                    </Box>
                  )}
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

      <Dialog open={historyDialog} onClose={() => setHistoryDialog(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Add Medical History</DialogTitle>
        <DialogContent>
          <Box sx={{ mt: 2, display: 'flex', flexDirection: 'column', gap: 2 }}>
            <TextField
              select
              fullWidth
              label="Appointment"
              value={historyForm.appointmentId}
              onChange={(e) => setHistoryForm({ ...historyForm, appointmentId: e.target.value })}
            >
              {appointmentOptions.map((option) => (
                <MenuItem key={option.id} value={option.id}>
                  {option.label}
                </MenuItem>
              ))}
            </TextField>
            <LocalizationProvider dateAdapter={AdapterDateFns}>
              <DatePicker
                label="Visit Date"
                value={historyForm.visitDate}
                onChange={(date) => setHistoryForm({ ...historyForm, visitDate: date || new Date() })}
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
          <Button onClick={handleAddHistory} variant="contained">
            Add History
          </Button>
        </DialogActions>
      </Dialog>

      <Dialog
        open={prescriptionDialog}
        onClose={() => setPrescriptionDialog(false)}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>Add Prescription</DialogTitle>
        <DialogContent>
          <Box sx={{ mt: 2, display: 'flex', flexDirection: 'column', gap: 2 }}>
            <TextField
              select
              fullWidth
              label="Appointment"
              value={prescriptionForm.appointmentId}
              onChange={(e) =>
                setPrescriptionForm({ ...prescriptionForm, appointmentId: e.target.value })
              }
            >
              {appointmentOptions.map((option) => (
                <MenuItem key={option.id} value={option.id}>
                  {option.label}
                </MenuItem>
              ))}
            </TextField>
            <TextField
              fullWidth
              label="Diagnosis"
              value={prescriptionForm.diagnosis}
              onChange={(e) => setPrescriptionForm({ ...prescriptionForm, diagnosis: e.target.value })}
            />
            <TextField
              fullWidth
              label="Medication Name"
              value={prescriptionForm.medicationName}
              onChange={(e) =>
                setPrescriptionForm({ ...prescriptionForm, medicationName: e.target.value })
              }
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
              onChange={(e) =>
                setPrescriptionForm({ ...prescriptionForm, frequency: e.target.value })
              }
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
              onChange={(e) =>
                setPrescriptionForm({ ...prescriptionForm, instructions: e.target.value })
              }
            />
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setPrescriptionDialog(false)}>Cancel</Button>
          <Button onClick={handleAddPrescription} variant="contained">
            Add Prescription
          </Button>
        </DialogActions>
      </Dialog>

      <Dialog open={reportDialog} onClose={() => setReportDialog(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Add Report</DialogTitle>
        <DialogContent>
          <Box sx={{ mt: 2, display: 'flex', flexDirection: 'column', gap: 2 }}>
            <TextField
              select
              fullWidth
              label="Appointment"
              value={reportForm.appointmentId}
              onChange={(e) => setReportForm({ ...reportForm, appointmentId: e.target.value })}
            >
              {appointmentOptions.map((option) => (
                <MenuItem key={option.id} value={option.id}>
                  {option.label}
                </MenuItem>
              ))}
            </TextField>
            <TextField
              select
              fullWidth
              label="Report Type"
              value={reportForm.reportType}
              onChange={(e) => setReportForm({ ...reportForm, reportType: e.target.value })}
            >
              <MenuItem value="Lab Test">Lab Test</MenuItem>
              <MenuItem value="Diagnostic">Diagnostic</MenuItem>
              <MenuItem value="Clinical Report">Clinical Report</MenuItem>
            </TextField>
            <LocalizationProvider dateAdapter={AdapterDateFns}>
              <DatePicker
                label="Report Date"
                value={reportForm.reportDate}
                onChange={(date) => setReportForm({ ...reportForm, reportDate: date || new Date() })}
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
            <Button variant="outlined" component="label" startIcon={<UploadIcon />}>
              Choose File (Optional)
              <input
                type="file"
                hidden
                onChange={(e) => setReportForm({ ...reportForm, file: e.target.files?.[0] || null })}
              />
            </Button>
            {reportForm.file && (
              <Typography variant="body2">Selected: {reportForm.file.name}</Typography>
            )}
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setReportDialog(false)}>Cancel</Button>
          <Button onClick={handleUploadReport} variant="contained">
            Add Report
          </Button>
        </DialogActions>
      </Dialog>
    </Container>
  );

  return (
    <Box sx={{ display: 'flex', minHeight: '100vh', background: '#f9fafb' }}>
      <DoctorSidebar activeItem="My Patients" />
      <Box sx={{ ml: { xs: 0, md: '280px' }, flex: 1 }}>{pageContent}</Box>
    </Box>
  );
};

export default PatientJourney;
