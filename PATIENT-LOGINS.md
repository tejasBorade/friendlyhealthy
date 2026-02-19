# Patient Login Credentials

All patients have the password: **Patient@123**

## Complete Patient List (Total: 15 Patients)

### Existing Patients (1-5)
1. **Email:** patient@healthcare.com  
   **Name:** Rahul Verma  
   **DOB:** 1990-05-15  
   **Conditions:** Hypertension, Type 2 Diabetes  
   **Doctor:** Dr. John Smith (Cardiology)

2. **Email:** patient2@healthcare.com  
   **Name:** Priya Sharma  
   **DOB:** 1995-08-20  
   **Conditions:** Asthma, Allergic Rhinitis  
   **Doctor:** Dr. Priya Desai (Pediatrics)

3. **Email:** patient3@healthcare.com  
   **Name:** Amit Patel  
   **DOB:** 1988-03-10  
   **Conditions:** Migraine  
   **Doctor:** Dr. Anjali Gupta (Cardiology)

4. **Email:** patient4@healthcare.com  
   **Name:** Sneha Reddy  
   **DOB:** 1992-11-25  
   **Conditions:** PCOD, Hypothyroidism  
   **Doctor:** Dr. Anjali Gupta (Cardiology)

5. **Email:** patient5@healthcare.com  
   **Name:** Karan Singh  
   **DOB:** 1987-07-18  
   **Conditions:** Gastritis  
   **Doctor:** Dr. John Smith (Cardiology)

### Previous Addition (6-10)
6. **Email:** patient6@healthcare.com  
   **Name:** Rahul Sharma  
   **DOB:** 1992-05-10  
   **Conditions:** Allergic Rhinitis  
   **Doctor:** Dr. John Smith (Cardiology)

7. **Email:** patient7@healthcare.com  
   **Name:** Sneha Reddy  
   **DOB:** 1988-08-25  
   **Conditions:** Osteoarthritis  
   **Doctor:** Dr. Vikram Mehta (Dermatology)

8. **Email:** patient8@healthcare.com  
   **Name:** Amit Patel  
   **DOB:** 1995-03-12  
   **Conditions:** Myopia  
   **Doctor:** Dr. Anjali Gupta (Cardiology)

9. **Email:** patient9@healthcare.com  
   **Name:** Neha Kumar  
   **DOB:** 1990-11-30  
   **Conditions:** Lower Back Pain  
   **Doctor:** Dr. Vikram Mehta (Dermatology)

10. **Email:** patient10@healthcare.com  
    **Name:** Suresh Singh  
    **DOB:** 1985-01-20  
    **Conditions:** Prediabetes, Hypertension  
    **Doctor:** Dr. Anjali Gupta (Cardiology)

### New Patients (11-15)
11. **Email:** rajesh.kumar@gmail.com  
    **Name:** Rajesh Kumar  
    **DOB:** 1980-06-15  
    **City:** Bangalore  
    **Conditions:** Type 2 Diabetes, Hypertension  
    **Doctor:** Dr. John Smith (Cardiology)

12. **Email:** anita.sharma@gmail.com  
    **Name:** Anita Sharma  
    **DOB:** 1992-09-20  
    **City:** Jaipur  
    **Conditions:** Anxiety Disorder  
    **Doctor:** Dr. Anjali Gupta (Cardiology)

13. **Email:** vikram.singh@gmail.com  
    **Name:** Vikram Singh  
    **DOB:** 1975-03-10  
    **City:** Lucknow  
    **Conditions:** Chronic Kidney Disease Stage 2, Hypertension  
    **Doctor:** Dr. John Smith (Cardiology)

14. **Email:** priya.mehta@gmail.com  
    **Name:** Priya Mehta  
    **DOB:** 1998-12-25  
    **City:** Chennai  
    **Conditions:** Iron Deficiency Anemia  
    **Doctor:** Dr. Priya Desai (Pediatrics)

15. **Email:** arjun.patel@gmail.com  
    **Name:** Arjun Patel  
    **DOB:** 1987-04-30  
    **City:** Ahmedabad  
    **Conditions:** Psoriasis  
    **Doctor:** Dr. Vikram Mehta (Dermatology)

---

## Doctor Assignments Summary

### Dr. John Smith (Cardiology)
- Patients: 1, 5, 6, 11, 13
- Specialties: General Medicine, Diabetes, Hypertension, Kidney Disease

### Dr. Anjali Gupta (Cardiology)
- Patients: 3, 4, 8, 10, 12
- Specialties: Cardiology, PCOD, General Consultation

### Dr. Vikram Mehta (Dermatology)
- Patients: 7, 9, 15
- Specialties: Orthopedics, Back Pain, Dermatology

### Dr. Priya Desai (Pediatrics)
- Patients: 2, 14
- Specialties: Asthma, Anemia, Pediatric Care

---

## Medical Summary

### Total Data Points
- **Patients:** 15
- **Medical Conditions:** 21 different conditions
- **Appointments:** 25 total (15 completed, 10 scheduled/upcoming)
- **Prescriptions:** 20 prescriptions with 43 medications
- **Medical History Records:** 21 entries

### Common Conditions Treated
1. Hypertension (4 patients)
2. Type 2 Diabetes (3 patients)
3. Allergic Rhinitis (2 patients)
4. Asthma (1 patient)
5. PCOD (1 patient)
6. Migraine (1 patient)
7. Gastritis (1 patient)
8. Osteoarthritis (1 patient)
9. Myopia (1 patient)
10. Back Pain (1 patient)
11. Prediabetes (1 patient)
12. Anxiety Disorder (1 patient)
13. Chronic Kidney Disease (1 patient)
14. Iron Deficiency Anemia (1 patient)
15. Psoriasis (1 patient)

---

## Testing Notes

### Login Testing
```
Email: patient@healthcare.com
Password: Patient@123

Email: rajesh.kumar@gmail.com
Password: Patient@123
```

### Features to Test
1. **Dashboard** - View appointments, prescriptions, medical reports
2. **Appointments** - View past and upcoming appointments
3. **Medical History** - Review diagnosed conditions
4. **Prescriptions** - View prescribed medications with dosages
5. **Billing** - View bills for completed appointments

### API Endpoints
- GET /api/v1/appointments?patientId={id}
- GET /api/v1/prescriptions?patientId={id}
- GET /api/v1/medical-records?patientId={id}
- GET /api/v1/billing
