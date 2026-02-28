"""
Onboarding Routes for SymptoTrack
Multi-step onboarding process for doctors and patients.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional
from datetime import datetime, date, timedelta
from uuid import UUID

from app.core.database import get_db
from app.core.security import hash_password, create_access_token, create_refresh_token
from app.models.user import User, UserRole, RefreshToken
from app.models.patient import Patient
from app.models.doctor import Doctor
from app.schemas.auth import TokenResponse, UserResponse
from pydantic import BaseModel, Field, EmailStr, validator

router = APIRouter(prefix="/onboarding", tags=["Onboarding"])


# ================================
# Patient Onboarding Schemas
# ================================

class PatientStep1(BaseModel):
    """Step 1: Phone verification (OTP already verified via /auth/verify-otp)"""
    phone: str = Field(..., description="Phone number in E.164 format")


class PatientStep2(BaseModel):
    """Step 2: Basic information"""
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    date_of_birth: date = Field(..., description="Date of birth")
    gender: str  # Accept string instead of Gender enum
    
    @validator('date_of_birth')
    def validate_dob(cls, v):
        if v > date.today():
            raise ValueError('Date of birth cannot be in the future')
        age = (date.today() - v).days / 365.25
        if age < 0 or age > 150:
            raise ValueError('Invalid age')
        return v


class PatientStep3(BaseModel):
    """Step 3: Contact & address"""
    alternate_phone: Optional[str] = None
    address: str = Field(..., min_length=10)
    city: str = Field(..., min_length=2, max_length=100)
    state: str = Field(..., min_length=2, max_length=100)
    zip_code: str = Field(..., min_length=5, max_length=10)
    country: str = Field(default="India", max_length=100)


class PatientStep4(BaseModel):
    """Step 4: Emergency contact & health basics"""
    emergency_contact_name: str = Field(..., min_length=2, max_length=200)
    emergency_contact_phone: str = Field(..., min_length=10, max_length=20)
    blood_group: Optional[str] = Field(None, max_length=10)


class PatientStep5(BaseModel):
    """Step 5: Health profile (optional)"""
    known_allergies: Optional[str] = None
    chronic_conditions: Optional[str] = None
    caregiver_name: Optional[str] = None
    caregiver_phone: Optional[str] = None
    profile_picture: Optional[str] = None


# ================================
# Doctor Onboarding Schemas
# ================================

class DoctorStep1(BaseModel):
    """Step 1: Phone verification (OTP already verified via /auth/verify-otp)"""
    phone: str = Field(..., description="Phone number in E.164 format")


class DoctorStep2(BaseModel):
    """Step 2: Personal & professional info"""
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    gender: str = Field(..., max_length=10)
    registration_number: str = Field(..., description="Medical council registration number")
    state_medical_council: str = Field(..., description="State medical council")
    qualification: str = Field(..., min_length=5, max_length=500)
    experience_years: int = Field(..., ge=0, le=70)


class DoctorStep3(BaseModel):
    """Step 3: Specialization & consultation details"""
    specialization_ids: list[UUID] = Field(..., description="List of specialization IDs")
    consultation_fee: float = Field(..., ge=0, description="Consultation fee in INR")
    about: Optional[str] = Field(None, max_length=2000)


class DoctorStep4(BaseModel):
    """Step 4: Clinic information"""
    clinic_name: str = Field(..., min_length=2, max_length=200)
    clinic_address: str = Field(..., min_length=10)
    clinic_city: str = Field(..., min_length=2, max_length=100)
    clinic_state: str = Field(..., min_length=2, max_length=100)
    clinic_zip_code: Optional[str] = Field(None, max_length=20)
    clinic_phone: Optional[str] = Field(None, max_length=20)


class DoctorStep5(BaseModel):
    """Step 5: Profile & verification (optional)"""
    profile_picture: Optional[str] = None
    clinic_logo: Optional[str] = None
    hfr_id: Optional[str] = Field(None, description="Health Facility Registry ID")


# ================================
# Patient Onboarding Endpoints
# ================================

@router.post("/patient/step/1", response_model=dict)
async def patient_onboarding_step1(
    data: PatientStep1,
    db: AsyncSession = Depends(get_db)
):
    """
    Patient Onboarding - Step 1: Create user account.
    
    This assumes OTP verification was already done via /auth/verify-otp.
    Creates a User record with PATIENT role.
    """
    # Check if phone already exists
    result = await db.execute(
        select(User).where(User.phone == data.phone, User.is_deleted == False)
    )
    existing_user = result.scalar_one_or_none()
    
    if existing_user:
        # Check if patient profile already exists
        result = await db.execute(
            select(Patient).where(Patient.user_id == existing_user.id, Patient.is_deleted == False)
        )
        existing_patient = result.scalar_one_or_none()
        
        if existing_patient:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Patient profile already exists"
            )
        
        return {
            "success": True,
            "message": "User account found. Proceed to step 2.",
            "user_id": str(existing_user.id)
        }
    
    # Create new user
    user = User(
        phone=data.phone,
        role=UserRole.PATIENT,
        is_active=True,
        is_verified=True  # Phone verified via OTP
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    
    return {
        "success": True,
        "message": "User account created. Proceed to step 2.",
        "user_id": str(user.id)
    }


@router.post("/patient/step/2", response_model=dict)
async def patient_onboarding_step2(
    data: PatientStep2,
    phone: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Patient Onboarding - Step 2: Basic information.
    """
    # Get user by phone
    result = await db.execute(
        select(User).where(User.phone == phone, User.is_deleted == False)
    )
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found. Complete step 1 first."
        )
    
    # Create or update patient profile
    result = await db.execute(
        select(Patient).where(Patient.user_id == user.id, Patient.is_deleted == False)
    )
    patient = result.scalar_one_or_none()
    
    if patient:
        # Update existing
        patient.first_name = data.first_name
        patient.last_name = data.last_name
        patient.date_of_birth = data.date_of_birth
        patient.gender = data.gender
        patient.phone = phone
    else:
        # Create new
        patient = Patient(
            user_id=user.id,
            first_name=data.first_name,
            last_name=data.last_name,
            date_of_birth=data.date_of_birth,
            gender=data.gender,
            phone=phone
        )
        db.add(patient)
    
    await db.commit()
    
    return {
        "success": True,
        "message": "Basic information saved. Proceed to step 3.",
        "patient_id": str(patient.id)
    }


@router.post("/patient/step/3", response_model=dict)
async def patient_onboarding_step3(
    data: PatientStep3,
    phone: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Patient Onboarding - Step 3: Contact & address.
    """
    # Get patient
    result = await db.execute(
        select(User).where(User.phone == phone, User.is_deleted == False)
    )
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    result = await db.execute(
        select(Patient).where(Patient.user_id == user.id, Patient.is_deleted == False)
    )
    patient = result.scalar_one_or_none()
    
    if not patient:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Complete step 2 first")
    
    # Update patient
    patient.alternate_phone = data.alternate_phone
    patient.address = data.address
    patient.city = data.city
    patient.state = data.state
    patient.zip_code = data.zip_code
    patient.country = data.country
    
    await db.commit()
    
    return {
        "success": True,
        "message": "Contact information saved. Proceed to step 4."
    }


@router.post("/patient/step/4", response_model=dict)
async def patient_onboarding_step4(
    data: PatientStep4,
    phone: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Patient Onboarding - Step 4: Emergency contact & health basics.
    """
    # Get patient
    result = await db.execute(
        select(User).where(User.phone == phone, User.is_deleted == False)
    )
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    result = await db.execute(
        select(Patient).where(Patient.user_id == user.id, Patient.is_deleted == False)
    )
    patient = result.scalar_one_or_none()
    
    if not patient:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Complete previous steps first")
    
    # Update patient
    patient.emergency_contact_name = data.emergency_contact_name
    patient.emergency_contact_phone = data.emergency_contact_phone
    patient.blood_group = data.blood_group
    
    await db.commit()
    
    return {
        "success": True,
        "message": "Emergency contact saved. Proceed to step 5 or complete onboarding."
    }


@router.post("/patient/step/5", response_model=TokenResponse)
async def patient_onboarding_step5(
    data: PatientStep5,
    phone: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Patient Onboarding - Step 5: Health profile (optional) & complete onboarding.
    
    Returns JWT tokens on completion.
    """
    # Get patient
    result = await db.execute(
        select(User).where(User.phone == phone, User.is_deleted == False)
    )
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    result = await db.execute(
        select(Patient).where(Patient.user_id == user.id, Patient.is_deleted == False)
    )
    patient = result.scalar_one_or_none()
    
    if not patient:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Complete previous steps first")
    
    # Update optional fields
    if data.known_allergies:
        patient.known_allergies = data.known_allergies
    if data.chronic_conditions:
        patient.chronic_conditions = data.chronic_conditions
    if data.caregiver_name:
        patient.caregiver_name = data.caregiver_name
    if data.caregiver_phone:
        patient.caregiver_phone = data.caregiver_phone
    if data.profile_picture:
        patient.profile_picture = data.profile_picture
    
    # Mark onboarding complete
    user.is_verified = True
    user.last_login = datetime.utcnow()
    
    await db.commit()
    await db.refresh(user)
    
    # Generate tokens
    access_token = create_access_token({"sub": str(user.id), "role": user.role.value})
    refresh_token_str = create_refresh_token({"sub": str(user.id)})
    
    # Store refresh token
    refresh_token = RefreshToken(
        user_id=user.id,
        token=refresh_token_str,
        expires_at=datetime.utcnow() + timedelta(days=7)
    )
    db.add(refresh_token)
    await db.commit()
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token_str,
        user=UserResponse.from_orm(user)
    )


# ================================
# Doctor Onboarding Endpoints
# ================================

@router.post("/doctor/step/1", response_model=dict)
async def doctor_onboarding_step1(
    data: DoctorStep1,
    db: AsyncSession = Depends(get_db)
):
    """
    Doctor Onboarding - Step 1: Create user account.
    
    This assumes OTP verification was already done via /auth/verify-otp.
    Creates a User record with DOCTOR role.
    """
    # Check if phone already exists
    result = await db.execute(
        select(User).where(User.phone == data.phone, User.is_deleted == False)
    )
    existing_user = result.scalar_one_or_none()
    
    if existing_user:
        # Check if doctor profile already exists
        result = await db.execute(
            select(Doctor).where(Doctor.user_id == existing_user.id, Doctor.is_deleted == False)
        )
        existing_doctor = result.scalar_one_or_none()
        
        if existing_doctor:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Doctor profile already exists"
            )
        
        return {
            "success": True,
            "message": "User account found. Proceed to step 2.",
            "user_id": str(existing_user.id)
        }
    
    # Create new user
    user = User(
        phone=data.phone,
        role=UserRole.DOCTOR,
        is_active=True,
        is_verified=False  # Will be verified after NMC check
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    
    return {
        "success": True,
        "message": "User account created. Proceed to step 2.",
        "user_id": str(user.id)
    }


@router.post("/doctor/step/2", response_model=dict)
async def doctor_onboarding_step2(
    data: DoctorStep2,
    phone: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Doctor Onboarding - Step 2: Personal & professional info.
    """
    # Get user by phone
    result = await db.execute(
        select(User).where(User.phone == phone, User.is_deleted == False)
    )
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found. Complete step 1 first."
        )
    
    # Check if registration number already exists
    result = await db.execute(
        select(Doctor).where(
            Doctor.registration_number == data.registration_number,
            Doctor.is_deleted == False
        )
    )
    existing_doctor = result.scalar_one_or_none()
    
    if existing_doctor:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Registration number already exists"
        )
    
    # Create or update doctor profile
    result = await db.execute(
        select(Doctor).where(Doctor.user_id == user.id, Doctor.is_deleted == False)
    )
    doctor = result.scalar_one_or_none()
    
    if doctor:
        # Update existing
        doctor.first_name = data.first_name
        doctor.last_name = data.last_name
        doctor.gender = data.gender
        doctor.phone = phone
        doctor.registration_number = data.registration_number
        doctor.state_medical_council = data.state_medical_council
        doctor.qualification = data.qualification
        doctor.experience_years = data.experience_years
    else:
        # Create new
        doctor = Doctor(
            user_id=user.id,
            first_name=data.first_name,
            last_name=data.last_name,
            gender=data.gender,
            phone=phone,
            registration_number=data.registration_number,
            state_medical_council=data.state_medical_council,
            qualification=data.qualification,
            experience_years=data.experience_years,
            consultation_fee=0  # Will be set in step 3
        )
        db.add(doctor)
    
    await db.commit()
    
    return {
        "success": True,
        "message": "Professional information saved. Proceed to step 3.",
        "doctor_id": str(doctor.id)
    }


@router.post("/doctor/step/3", response_model=dict)
async def doctor_onboarding_step3(
    data: DoctorStep3,
    phone: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Doctor Onboarding - Step 3: Specialization & consultation details.
    """
    # Get doctor
    result = await db.execute(
        select(User).where(User.phone == phone, User.is_deleted == False)
    )
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    result = await db.execute(
        select(Doctor).where(Doctor.user_id == user.id, Doctor.is_deleted == False)
    )
    doctor = result.scalar_one_or_none()
    
    if not doctor:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Complete step 2 first")
    
    # Update doctor
    doctor.consultation_fee = data.consultation_fee
    if data.about:
        doctor.about = data.about
    
    # TODO: Handle specialization_ids by creating DoctorSpecialization records
    # For now, we'll skip this as it requires the DoctorSpecialization model
    
    await db.commit()
    
    return {
        "success": True,
        "message": "Consultation details saved. Proceed to step 4."
    }


@router.post("/doctor/step/4", response_model=dict)
async def doctor_onboarding_step4(
    data: DoctorStep4,
    phone: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Doctor Onboarding - Step 4: Clinic information.
    """
    # Get doctor
    result = await db.execute(
        select(User).where(User.phone == phone, User.is_deleted == False)
    )
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    result = await db.execute(
        select(Doctor).where(Doctor.user_id == user.id, Doctor.is_deleted == False)
    )
    doctor = result.scalar_one_or_none()
    
    if not doctor:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Complete previous steps first")
    
    # Update doctor with clinic info
    doctor.clinic_name = data.clinic_name
    doctor.clinic_address = data.clinic_address
    
    # TODO: Create Clinic record
    # For now, store in doctor record
    
    await db.commit()
    
    return {
        "success": True,
        "message": "Clinic information saved. Proceed to step 5 or complete onboarding."
    }


@router.post("/doctor/step/5", response_model=TokenResponse)
async def doctor_onboarding_step5(
    data: DoctorStep5,
    phone: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Doctor Onboarding - Step 5: Profile & verification (optional) & complete onboarding.
    
    Returns JWT tokens on completion.
    """
    # Get doctor
    result = await db.execute(
        select(User).where(User.phone == phone, User.is_deleted == False)
    )
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    result = await db.execute(
        select(Doctor).where(Doctor.user_id == user.id, Doctor.is_deleted == False)
    )
    doctor = result.scalar_one_or_none()
    
    if not doctor:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Complete previous steps first")
    
    # Update optional fields
    if data.profile_picture:
        doctor.profile_picture = data.profile_picture
    if data.clinic_logo:
        doctor.clinic_logo = data.clinic_logo
    if data.hfr_id:
        doctor.hfr_id = data.hfr_id
    
    # Mark onboarding complete (pending verification)
    user.last_login = datetime.utcnow()
    
    await db.commit()
    await db.refresh(user)
    
    # Generate tokens
    access_token = create_access_token({"sub": str(user.id), "role": user.role.value})
    refresh_token_str = create_refresh_token({"sub": str(user.id)})
    
    # Store refresh token
    refresh_token = RefreshToken(
        user_id=user.id,
        token=refresh_token_str,
        expires_at=datetime.utcnow() + timedelta(days=7)
    )
    db.add(refresh_token)
    await db.commit()
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token_str,
        user=UserResponse.from_orm(user)
    )
