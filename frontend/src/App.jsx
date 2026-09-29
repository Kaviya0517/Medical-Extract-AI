import { useEffect, useState, useRef } from 'react'
import './App.css'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000'

function App() {
  const [page, setPage] = useState('landing')
  const [token, setToken] = useState(localStorage.getItem('token') || '')
  const [username, setUsername] = useState(localStorage.getItem('username') || '')

  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [userRole, setUserRole] = useState(localStorage.getItem('userRole') || 'Doctor')
  const [hospitalName, setHospitalName] = useState(localStorage.getItem('hospitalName') || 'General Medical Center')
  const [isEditingHospital, setIsEditingHospital] = useState(false)
  const [tempHospitalName, setTempHospitalName] = useState('')
  const [authMode, setAuthMode] = useState('login')
  const [authError, setAuthError] = useState('')
  const [authLoading, setAuthLoading] = useState(false)

  // Dark Mode State
  const [darkMode, setDarkMode] = useState(localStorage.getItem('darkMode') === 'true')

  // Toast Notification State
  const [toast, setToast] = useState(null)

  const [activeTab, setActiveTab] = useState('analyze')
  const [reportText, setReportText] = useState('')
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  // EHR Editable Inputs for Intake
  const [ehrPatientId, setEhrPatientId] = useState('')
  const [ehrRoomNumber, setEhrRoomNumber] = useState('Ward 1')
  const [ehrAdmissionStatus, setEhrAdmissionStatus] = useState('Admitted')
  const [ehrAttending, setEhrAttending] = useState('Dr. N. Patel (Attending)')

  // Database status
  const [dbStatus, setDbStatus] = useState(null)

  // Records / Search / Filter State
  const [history, setHistory] = useState([])
  const [searchTerm, setSearchTerm] = useState('')
  const [departmentFilter, setDepartmentFilter] = useState('')
  const [triageFilter, setTriageFilter] = useState('')
  const [statusFilter, setStatusFilter] = useState('')
  const [selectedReport, setSelectedReport] = useState(null)

  // Activity Logs & Analytics
  const [activityLogs, setActivityLogs] = useState([])
  const [showLogsModal, setShowLogsModal] = useState(false)
  const [analytics, setAnalytics] = useState(null)

  // Patient Management State
  const [patients, setPatients] = useState([])
  const [showAddPatientModal, setShowAddPatientModal] = useState(false)
  const [newPatient, setNewPatient] = useState({ name: '', age: '', gender: 'Male', phone: '', email: '', past_illnesses: '', allergies: '' })

  // OPD Appointment & Queue State
  const [appointments, setAppointments] = useState([])
  const [showAddApptModal, setShowAddApptModal] = useState(false)
  const [newAppt, setNewAppt] = useState({ patient_id: '', patient_name: '', doctor_name: 'Dr. N. Patel', department: 'General Medicine', appointment_date: new Date().toISOString().split('T')[0], appointment_time: '10:00 AM', notes: '' })

  // Lab Management State
  const [labOrders, setLabOrders] = useState([])
  const [showAddLabModal, setShowAddLabModal] = useState(false)
  const [newLabOrder, setNewLabOrder] = useState({ patient_id: '', patient_name: '', test_name: 'Comprehensive Metabolic Panel', ordering_doctor: 'Dr. N. Patel', department: 'General Medicine', notes: '' })
  const [selectedLabResultModal, setSelectedLabResultModal] = useState(null)
  const [labResultInput, setLabResultInput] = useState({ result_value: '', normal_range: 'Normal', flag: 'NORMAL' })

  // Pharmacy & Drug Interaction Checker State
  const [prescriptions, setPrescriptions] = useState([])
  const [pharmacyStock, setPharmacyStock] = useState([])
  const [showAddRxModal, setShowAddRxModal] = useState(false)
  const [newRx, setNewRx] = useState({ patient_id: '', patient_name: '', doctor_name: 'Dr. N. Patel', medication_name: 'Aspirin', dosage: '325mg', frequency: 'Once Daily', duration: '7 Days', special_instructions: '' })
  const [drugCheckText, setDrugCheckText] = useState('Aspirin, Warfarin')
  const [drugInteractionResults, setDrugInteractionResults] = useState([])

  // Visual Bed Map State
  const [bedsList, setBedsList] = useState([
    { bed_id: 'ICU-01', ward: 'ICU', patient_name: 'John Smith', patient_id: 'PAT-2026-8941', status: 'Occupied', doctor: 'Dr. N. Patel' },
    { bed_id: 'ICU-02', ward: 'ICU', patient_name: 'Alex Johnson', patient_id: 'PAT-2026-1001', status: 'Occupied', doctor: 'Dr. A. Sharma' },
    { bed_id: 'ICU-03', ward: 'ICU', patient_name: '', patient_id: '', status: 'Available', doctor: '' },
    { bed_id: 'ICU-04', ward: 'ICU', patient_name: '', patient_id: '', status: 'Cleaning', doctor: '' },
    { bed_id: 'WARD-101', ward: 'General Ward 1', patient_name: 'Sarah Connor', patient_id: 'PAT-2026-3391', status: 'Occupied', doctor: 'Dr. N. Patel' },
    { bed_id: 'WARD-102', ward: 'General Ward 1', patient_name: 'Michael Chang', patient_id: 'PAT-2026-4482', status: 'Occupied', doctor: 'Dr. R. Gupta' },
    { bed_id: 'WARD-103', ward: 'General Ward 1', patient_name: '', patient_id: '', status: 'Available', doctor: '' },
    { bed_id: 'WARD-201', ward: 'General Ward 2', patient_name: 'Emily Davis', patient_id: 'PAT-2026-7721', status: 'Occupied', doctor: 'Dr. N. Patel' },
    { bed_id: 'WARD-202', ward: 'General Ward 2', patient_name: '', patient_id: '', status: 'Available', doctor: '' },
    { bed_id: 'ER-01', ward: 'Emergency Room', patient_name: 'Emergency Trauma', patient_id: 'PAT-ER-991', status: 'Reserved', doctor: 'On Duty ER' },
  ])
  const [showBedAssignModal, setShowBedAssignModal] = useState(null)
  const [bedAssignInput, setBedAssignInput] = useState({ patient_id: '', patient_name: '', doctor: 'Dr. N. Patel', status: 'Occupied' })

  // Billing & Claims State
  const [invoices, setInvoices] = useState([])
  const [showAddInvoiceModal, setShowAddInvoiceModal] = useState(false)
  const [newInvoice, setNewInvoice] = useState({ patient_id: '', patient_name: '', consultation_fee: 150, lab_fee: 200, pharmacy_fee: 75, room_charges: 300, insurance_claim_amount: 500, insurance_status: 'Submitted' })

  // Staff Roster State
  const [staffList, setStaffList] = useState([])
  const [showAddStaffModal, setShowAddStaffModal] = useState(false)
  const [newStaff, setNewStaff] = useState({ name: '', role: 'Doctor', department: 'Cardiology', shift: 'Morning', phone: '', email: '' })

  // Inventory / Supplies State
  const [consumables, setConsumables] = useState([])
  const [showAddSupplyModal, setShowAddSupplyModal] = useState(false)
  const [newSupply, setNewSupply] = useState({ item_name: '', category: 'Medical Consumables', quantity: 100, reorder_level: 25, unit_cost: 12.5, vendor_name: 'MedSupply Co.' })

  // Modals
  const [showCriticalAlertsModal, setShowCriticalAlertsModal] = useState(false)
  const [showResetModal, setShowResetModal] = useState(false)
  const [resetUsername, setResetUsername] = useState('')
  const [resetNewPassword, setResetNewPassword] = useState('')

  // Patient Portal State
  const [portalSearchId, setPortalSearchId] = useState('')
  const [fhirJsonView, setFhirJsonView] = useState(null)

  // Voice Dictation Ref
  const [isListening, setIsListening] = useState(false)
  const recognitionRef = useRef(null)

  const sampleNote = `PATIENT HANDOVER: John Smith, a 52-year-old male, presented to Emergency with acute chest pain radiating to the left arm and shortness of breath for 3 hours. ECG shows ST elevation. Provisional diagnosis: acute myocardial infarction and essential hypertension. History of type 2 diabetes. Administered aspirin 325mg and started on metoprolol 50mg. Allergic to penicillin. Transferred to ICU-02.`

  useEffect(() => {
    checkHealth()
    if (token && username) {
      setPage('dashboard')
      fetchUserProfile()
      loadHistory()
      loadAnalytics()
      loadPatients()
      loadAppointments()
      loadLabOrders()
      loadPrescriptions()
      loadPharmacyInventory()
      loadInvoices()
      loadStaff()
      loadConsumables()
    }
  }, [token, username])

  const showToast = (message, type = 'success') => {
    setToast({ message, type })
    setTimeout(() => setToast(null), 3500)
  }

  const toggleDarkMode = () => {
    const nextMode = !darkMode
    setDarkMode(nextMode)
    localStorage.setItem('darkMode', String(nextMode))
  }

  const handleSaveHospitalName = async (newName) => {
    const finalName = newName.trim() || 'General Medical Center'
    setHospitalName(finalName)
    localStorage.setItem('hospitalName', finalName)
    setIsEditingHospital(false)
    if (token) {
      try {
        await fetch(`${API_BASE_URL}/auth/hospital-name`, {
          method: 'PUT',
          headers: {
            'Content-Type': 'application/json',
            Authorization: `Bearer ${token}`,
          },
          body: JSON.stringify({ hospital_name: finalName }),
        })
      } catch (e) {
        console.error('Failed to save hospital name:', e)
      }
    }
    showToast(`Medical Center updated to "${finalName}"!`, 'success')
  }

  const checkHealth = async () => {
    try {
      const res = await fetch(`${API_BASE_URL}/health`)
      if (res.ok) {
        const data = await res.json()
        setDbStatus(data.database)
      }
    } catch (err) {
      console.error('Health check failed:', err)
    }
  }

  const fetchUserProfile = async () => {
    if (!token) return
    try {
      const res = await fetch(`${API_BASE_URL}/auth/me`, {
        headers: { Authorization: `Bearer ${token}` },
      })
      if (res.ok) {
        const data = await res.json()
        if (data.hospital_name) {
          setHospitalName(data.hospital_name)
          localStorage.setItem('hospitalName', data.hospital_name)
        }
        if (data.role) {
          setUserRole(data.role)
          localStorage.setItem('userRole', data.role)
        }
      }
    } catch (err) {
      console.error('Failed to fetch user profile:', err)
    }
  }

  const loadHistory = async (search = searchTerm, dept = departmentFilter, triage = triageFilter, status = statusFilter) => {
    if (!token) return
    try {
      const params = new URLSearchParams()
      if (search) params.append('search', search)
      if (dept) params.append('department', dept)
      if (triage) params.append('triage_level', triage)
      if (status) params.append('admission_status', status)

      const response = await fetch(`${API_BASE_URL}/reports/?${params.toString()}`, {
        headers: { Authorization: `Bearer ${token}` },
      })
      const data = await response.json()
      if (response.ok) {
        setHistory(Array.isArray(data) ? data : [])
      }
    } catch (err) {
      console.error('History fetch failed:', err)
    }
  }

  const loadPatients = async () => {
    if (!token) return
    try {
      const res = await fetch(`${API_BASE_URL}/patients/`, { headers: { Authorization: `Bearer ${token}` } })
      if (res.ok) setPatients(await res.json())
    } catch (e) { console.error('Failed to load patients:', e) }
  }

  const loadAppointments = async () => {
    if (!token) return
    try {
      const res = await fetch(`${API_BASE_URL}/appointments/`, { headers: { Authorization: `Bearer ${token}` } })
      if (res.ok) setAppointments(await res.json())
    } catch (e) { console.error('Failed to load appointments:', e) }
  }

  const loadLabOrders = async () => {
    if (!token) return
    try {
      const res = await fetch(`${API_BASE_URL}/lab/orders`, { headers: { Authorization: `Bearer ${token}` } })
      if (res.ok) setLabOrders(await res.json())
    } catch (e) { console.error('Failed to load lab orders:', e) }
  }

  const loadPrescriptions = async () => {
    if (!token) return
    try {
      const res = await fetch(`${API_BASE_URL}/pharmacy/prescriptions`, { headers: { Authorization: `Bearer ${token}` } })
      if (res.ok) setPrescriptions(await res.json())
    } catch (e) { console.error('Failed to load prescriptions:', e) }
  }

  const loadPharmacyInventory = async () => {
    if (!token) return
    try {
      const res = await fetch(`${API_BASE_URL}/pharmacy/inventory`, { headers: { Authorization: `Bearer ${token}` } })
      if (res.ok) setPharmacyStock(await res.json())
    } catch (e) { console.error('Failed to load pharmacy stock:', e) }
  }

  const loadInvoices = async () => {
    if (!token) return
    try {
      const res = await fetch(`${API_BASE_URL}/billing/invoices`, { headers: { Authorization: `Bearer ${token}` } })
      if (res.ok) setInvoices(await res.json())
    } catch (e) { console.error('Failed to load invoices:', e) }
  }

  const loadStaff = async () => {
    if (!token) return
    try {
      const res = await fetch(`${API_BASE_URL}/staff/`, { headers: { Authorization: `Bearer ${token}` } })
      if (res.ok) setStaffList(await res.json())
    } catch (e) { console.error('Failed to load staff:', e) }
  }

  const loadConsumables = async () => {
    if (!token) return
    try {
      const res = await fetch(`${API_BASE_URL}/inventory/`, { headers: { Authorization: `Bearer ${token}` } })
      if (res.ok) setConsumables(await res.json())
    } catch (e) { console.error('Failed to load consumables:', e) }
  }

  const loadActivityLogs = async () => {
    if (!token) return
    try {
      const res = await fetch(`${API_BASE_URL}/reports/activity-logs`, {
        headers: { Authorization: `Bearer ${token}` },
      })
      if (res.ok) {
        const data = await res.json()
        setActivityLogs(data)
        setShowLogsModal(true)
      }
    } catch (err) {
      console.error('Activity logs fetch failed:', err)
    }
  }

  const loadAnalytics = async () => {
    if (!token) return
    try {
      const response = await fetch(`${API_BASE_URL}/reports/analytics`, {
        headers: { Authorization: `Bearer ${token}` },
      })
      if (response.ok) {
        const data = await response.json()
        setAnalytics(data)
      }
    } catch (err) {
      console.error('Analytics fetch failed:', err)
    }
  }

  const handleAuth = async (e) => {
    e.preventDefault()
    setAuthError('')
    setAuthLoading(true)

    try {
      const endpoint = authMode === 'login' ? '/auth/login' : '/auth/register'
      const payload = authMode === 'login'
        ? { username, password }
        : { username, email, password, role: userRole, hospital_name: hospitalName }

      const response = await fetch(`${API_BASE_URL}${endpoint}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      })
      const data = await response.json()

      if (response.ok) {
        const role = data.role || userRole
        const hName = data.hospital_name || hospitalName
        localStorage.setItem('token', data.access_token)
        localStorage.setItem('username', username)
        localStorage.setItem('userRole', role)
        localStorage.setItem('hospitalName', hName)
        setToken(data.access_token)
        setUsername(username)
        setUserRole(role)
        setHospitalName(hName)
        setEmail('')
        setPassword('')
        setAuthError('')
        setPage('dashboard')
        showToast(`Welcome back, ${role} ${username}!`, 'success')
        loadHistory()
        loadAnalytics()
        loadPatients()
        loadAppointments()
        loadLabOrders()
        loadPrescriptions()
        loadPharmacyInventory()
        loadInvoices()
        loadStaff()
        loadConsumables()
        checkHealth()
      } else {
        setAuthError(data.detail || 'Authentication failed')
      }
    } catch (err) {
      setAuthError(`Unable to reach the hospital server. Confirm the backend is running and accessible at ${API_BASE_URL}.`)
    }
    setAuthLoading(false)
  }

  const handlePasswordResetSubmit = async (e) => {
    e.preventDefault()
    if (!resetUsername || !resetNewPassword) return
    try {
      const res = await fetch(`${API_BASE_URL}/auth/reset-password`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username: resetUsername, new_password: resetNewPassword }),
      })
      const data = await res.json()
      if (res.ok) {
        showToast(data.message, 'success')
        setShowResetModal(false)
        setResetUsername('')
        setResetNewPassword('')
      } else {
        showToast(data.detail || 'Password reset failed', 'error')
      }
    } catch (e) {
      showToast('Network error during password reset', 'error')
    }
  }

  const startVoiceInput = () => {
    const SpeechRecognition = window.WebkitSpeechRecognition || window.SpeechRecognition
    if (!SpeechRecognition) {
      setError('Speech recognition is not supported in this browser.')
      return
    }

    if (recognitionRef.current) {
      recognitionRef.current.stop()
      recognitionRef.current = null
    }

    const recognition = new SpeechRecognition()
    recognitionRef.current = recognition
    recognition.continuous = true
    recognition.interimResults = true

    recognition.onstart = () => setIsListening(true)
    recognition.onresult = (event) => {
      let interim = ''
      for (let i = event.resultIndex; i < event.results.length; i++) {
        const transcript = event.results[i][0].transcript
        if (event.results[i].isFinal) {
          setReportText((prev) => prev + transcript + ' ')
        } else {
          interim += transcript
        }
      }
      if (interim) {
        setError(`Listening: ${interim}`)
      }
    }
    recognition.onerror = (event) => setError(`Speech error: ${event.error}`)
    recognition.onend = () => {
      setIsListening(false)
      recognitionRef.current = null
      setError('')
    }

    recognition.start()
    window.setTimeout(() => {
      if (recognitionRef.current) recognitionRef.current.stop()
    }, 60000)
  }

  const handleFileUpload = async (e) => {
    const file = e.target.files?.[0]
    if (!file) return

    setLoading(true)
    setError('')

    const formData = new FormData()
    formData.append('file', file)

    try {
      const response = await fetch(`${API_BASE_URL}/extraction/file`, {
        method: 'POST',
        body: formData,
      })
      const data = await response.json()
      if (response.ok) {
        setResult(data)
        if (data.patient_id) setEhrPatientId(data.patient_id)
        if (data.room_number) setEhrRoomNumber(data.room_number)
        if (data.admission_status) setEhrAdmissionStatus(data.admission_status)
        setReportText(`[Extracted from file: ${file.name}]`)
        showToast(`Parsed ${file.name} successfully!`, 'success')
      } else {
        setError(data.detail || 'Failed to extract text from file.')
      }
    } catch (err) {
      setError('File upload error: ' + err.message)
    }
    setLoading(false)
  }

  const handleAnalyze = async () => {
    if (!reportText.trim()) {
      setError('Please enter or upload a clinical note first.')
      return
    }

    setLoading(true)
    setError('')

    try {
      if (token) {
        const dupRes = await fetch(`${API_BASE_URL}/reports/check-duplicate`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            Authorization: `Bearer ${token}`,
          },
          body: JSON.stringify({ report_text: reportText }),
        })
        if (dupRes.ok) {
          const dupData = await dupRes.json()
          if (dupData.is_duplicate) {
            showToast('⚠️ Duplicate report text detected in patient history!', 'warning')
          }
        }
      }

      const response = await fetch(`${API_BASE_URL}/extraction/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ report_text: reportText }),
      })

      const data = await response.json()

      if (!response.ok) {
        setError(data.detail || 'Analysis failed.')
        setLoading(false)
        return
      }

      setResult(data)
      const assignedId = ehrPatientId || data.patient_id || `PAT-2026-${Math.floor(1000 + Math.random() * 9000)}`
      setEhrPatientId(assignedId)
      if (data.room_number) setEhrRoomNumber(data.room_number)
      if (data.admission_status) setEhrAdmissionStatus(data.admission_status)

      if (token) {
        const reportPayload = {
          report_hash: data.report_hash,
          patient_id: assignedId,
          patient_name: data.patient_name,
          age: data.age,
          gender: data.gender,
          room_number: ehrRoomNumber || data.room_number,
          admission_status: ehrAdmissionStatus || data.admission_status,
          triage_level: data.triage_level || "Routine",
          attending_physician: ehrAttending || data.attending_physician,
          risk_level: data.risk_level || "Low",
          clinical_flags: data.clinical_flags || [],
          report_text: reportText,
          diagnoses: data.diagnoses || [],
          symptoms: data.symptoms || [],
          medications: data.medications || [],
          dosages: data.dosages || [],
          allergies: data.allergies || [],
          lab_tests: data.lab_tests || [],
          department: data.department || 'General Medicine',
          icd10_code: data.icd10_code || 'R50.9',
          confidence_score: data.confidence_score || 0.85,
        }

        await fetch(`${API_BASE_URL}/reports/`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            Authorization: `Bearer ${token}`,
          },
          body: JSON.stringify(reportPayload),
        })
        showToast('Clinical report extracted & saved to database!', 'success')
        await loadHistory()
        await loadAnalytics()
      }
    } catch (err) {
      setError('Error: ' + err.message)
    }

    setLoading(false)
  }

  const handleDeleteReport = async (reportId) => {
    if (!window.confirm('Are you sure you want to delete this patient record?')) return
    try {
      const res = await fetch(`${API_BASE_URL}/reports/${reportId}`, {
        method: 'DELETE',
        headers: { Authorization: `Bearer ${token}` },
      })
      if (res.ok) {
        if (selectedReport?.id === reportId) setSelectedReport(null)
        showToast('Patient record deleted successfully.', 'info')
        loadHistory()
        loadAnalytics()
      }
    } catch (err) {
      console.error('Failed to delete report:', err)
    }
  }

  // --- Handlers for Module Actions ---
  const handleAddPatientSubmit = async (e) => {
    e.preventDefault()
    try {
      const payload = {
        name: newPatient.name,
        age: newPatient.age || "30",
        gender: newPatient.gender,
        phone: newPatient.phone,
        email: newPatient.email,
        past_illnesses: newPatient.past_illnesses ? newPatient.past_illnesses.split(',').map(s => s.trim()) : [],
        allergies: newPatient.allergies ? newPatient.allergies.split(',').map(s => s.trim()) : []
      }
      const res = await fetch(`${API_BASE_URL}/patients/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
        body: JSON.stringify(payload)
      })
      if (res.ok) {
        showToast('Registered new patient successfully!', 'success')
        setShowAddPatientModal(false)
        setNewPatient({ name: '', age: '', gender: 'Male', phone: '', email: '', past_illnesses: '', allergies: '' })
        loadPatients()
      }
    } catch (e) { showToast('Error registering patient', 'error') }
  }

  const handleAddApptSubmit = async (e) => {
    e.preventDefault()
    try {
      const res = await fetch(`${API_BASE_URL}/appointments/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
        body: JSON.stringify(newAppt)
      })
      if (res.ok) {
        const data = await res.json()
        showToast(`Booked OPD appointment (Token #${data.token_number})`, 'success')
        setShowAddApptModal(false)
        loadAppointments()
      }
    } catch (e) { showToast('Error booking appointment', 'error') }
  }

  const handleApptStatusUpdate = async (apptId, nextStatus) => {
    try {
      const res = await fetch(`${API_BASE_URL}/appointments/${apptId}/status?status=${nextStatus}`, {
        method: 'PATCH',
        headers: { Authorization: `Bearer ${token}` }
      })
      if (res.ok) {
        showToast(`Appointment status updated to '${nextStatus}'`, 'info')
        loadAppointments()
      }
    } catch (e) { console.error('Failed to update appt status:', e) }
  }

  const handleAddLabOrderSubmit = async (e) => {
    e.preventDefault()
    try {
      const res = await fetch(`${API_BASE_URL}/lab/orders`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
        body: JSON.stringify(newLabOrder)
      })
      if (res.ok) {
        showToast('Lab test order created successfully!', 'success')
        setShowAddLabModal(false)
        loadLabOrders()
      }
    } catch (e) { showToast('Error ordering lab test', 'error') }
  }

  const handleSaveLabResultSubmit = async (e) => {
    e.preventDefault()
    if (!selectedLabResultModal) return
    try {
      const res = await fetch(`${API_BASE_URL}/lab/orders/${selectedLabResultModal.id}/result`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
        body: JSON.stringify(labResultInput)
      })
      if (res.ok) {
        showToast('Lab result entered and flagged!', 'success')
        setSelectedLabResultModal(null)
        loadLabOrders()
      }
    } catch (e) { showToast('Error entering lab result', 'error') }
  }

  const handleAddRxSubmit = async (e) => {
    e.preventDefault()
    try {
      const res = await fetch(`${API_BASE_URL}/pharmacy/prescriptions`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
        body: JSON.stringify(newRx)
      })
      if (res.ok) {
        showToast('Prescription logged successfully!', 'success')
        setShowAddRxModal(false)
        loadPrescriptions()
      }
    } catch (e) { showToast('Error creating prescription', 'error') }
  }

  const handleDispenseRx = async (rxId) => {
    try {
      const res = await fetch(`${API_BASE_URL}/pharmacy/prescriptions/${rxId}/dispense`, {
        method: 'PATCH',
        headers: { Authorization: `Bearer ${token}` }
      })
      if (res.ok) {
        showToast('Medication dispensed to patient!', 'success')
        loadPrescriptions()
      }
    } catch (e) { console.error('Failed to dispense:', e) }
  }

  const handleCheckDrugInteractions = async () => {
    const medsList = drugCheckText.split(',').map(s => s.trim()).filter(Boolean)
    if (!medsList.length) return
    try {
      const res = await fetch(`${API_BASE_URL}/pharmacy/check-interactions`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
        body: JSON.stringify({ medications: medsList })
      })
      if (res.ok) {
        const data = await res.json()
        setDrugInteractionResults(data.interactions || [])
        showToast(`Analyzed ${medsList.length} medications for interactions`, 'info')
      }
    } catch (e) { showToast('Error checking interactions', 'error') }
  }

  const handleBedAssignSubmit = (e) => {
    e.preventDefault()
    if (!showBedAssignModal) return
    setBedsList(prev => prev.map(b => {
      if (b.bed_id === showBedAssignModal.bed_id) {
        return {
          ...b,
          patient_id: bedAssignInput.patient_id,
          patient_name: bedAssignInput.patient_name,
          doctor: bedAssignInput.doctor,
          status: bedAssignInput.status
        }
      }
      return b
    }))
    showToast(`Updated Bed ${showBedAssignModal.bed_id} assignment`, 'success')
    setShowBedAssignModal(null)
  }

  const handleAddInvoiceSubmit = async (e) => {
    e.preventDefault()
    try {
      const res = await fetch(`${API_BASE_URL}/billing/invoices`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
        body: JSON.stringify(newInvoice)
      })
      if (res.ok) {
        showToast('Invoice generated successfully!', 'success')
        setShowAddInvoiceModal(false)
        loadInvoices()
      }
    } catch (e) { showToast('Error creating invoice', 'error') }
  }

  const handlePayInvoice = async (invoiceId) => {
    try {
      const res = await fetch(`${API_BASE_URL}/billing/invoices/${invoiceId}/pay`, {
        method: 'PATCH',
        headers: { Authorization: `Bearer ${token}` }
      })
      if (res.ok) {
        showToast('Payment collected & invoice marked Paid!', 'success')
        loadInvoices()
      }
    } catch (e) { console.error('Failed to pay invoice:', e) }
  }

  const handleAddStaffSubmit = async (e) => {
    e.preventDefault()
    try {
      const res = await fetch(`${API_BASE_URL}/staff/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
        body: JSON.stringify(newStaff)
      })
      if (res.ok) {
        showToast('Staff member added to roster!', 'success')
        setShowAddStaffModal(false)
        loadStaff()
      }
    } catch (e) { showToast('Error adding staff', 'error') }
  }

  const handleAddSupplySubmit = async (e) => {
    e.preventDefault()
    try {
      const res = await fetch(`${API_BASE_URL}/inventory/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
        body: JSON.stringify(newSupply)
      })
      if (res.ok) {
        showToast('Consumable item added to inventory!', 'success')
        setShowAddSupplyModal(false)
        loadConsumables()
      }
    } catch (e) { showToast('Error adding consumable', 'error') }
  }

  const handleFetchFhirExport = async (pid) => {
    try {
      const res = await fetch(`${API_BASE_URL}/fhir/Patient/${pid || 'PAT-2026-8941'}`, {
        headers: { Authorization: `Bearer ${token}` }
      })
      if (res.ok) {
        const bundle = await res.json()
        setFhirJsonView(bundle)
      } else {
        showToast('FHIR Bundle export not available for patient ID', 'warning')
      }
    } catch (e) { console.error('FHIR export failed:', e) }
  }

  // --- Export Helpers ---
  const exportCSV = () => {
    if (!history.length) {
      showToast('No records available to export.', 'warning')
      return
    }
    const headers = ['Patient ID', 'Patient Name', 'Age', 'Gender', 'Department', 'ICD-10', 'Triage Level', 'Admission Status', 'Diagnoses', 'Medications', 'Room Number', 'Attending Physician']
    const rows = history.map((r) => [
      `"${r.patient_id || ''}"`,
      `"${r.patient_name || ''}"`,
      `"${r.age || ''}"`,
      `"${r.gender || ''}"`,
      `"${r.department || ''}"`,
      `"${r.icd10_code || ''}"`,
      `"${r.triage_level || ''}"`,
      `"${r.admission_status || ''}"`,
      `"${(r.diagnoses || []).join('; ')}"`,
      `"${(r.medications || []).join('; ')}"`,
      `"${r.room_number || ''}"`,
      `"${r.attending_physician || ''}"`,
    ])

    const csvContent = 'data:text/csv;charset=utf-8,' + [headers.join(','), ...rows.map((e) => e.join(','))].join('\n')
    const encodedUri = encodeURI(csvContent)
    const link = document.createElement('a')
    link.setAttribute('href', encodedUri)
    link.setAttribute('download', `${hospitalName.replace(/\s+/g, '_')}_Patient_Registry.csv`)
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    showToast('Exported CSV dataset successfully!', 'success')
  }

  const exportJSON = () => {
    if (!history.length) {
      showToast('No records available to export.', 'warning')
      return
    }
    const dataStr = 'data:text/json;charset=utf-8,' + encodeURIComponent(JSON.stringify(history, null, 2))
    const downloadAnchor = document.createElement('a')
    downloadAnchor.setAttribute('href', dataStr)
    downloadAnchor.setAttribute('download', `${hospitalName.replace(/\s+/g, '_')}_EMR_Dataset.json`)
    document.body.appendChild(downloadAnchor)
    downloadAnchor.click()
    downloadAnchor.remove()
    showToast('Exported JSON dataset successfully!', 'success')
  }

  const shareEmail = (report) => {
    const subject = encodeURIComponent(`Clinical Handover Report - ${report.patient_name || report.patient_id} (${report.icd10_code})`)
    const body = encodeURIComponent(
      `${hospitalName.toUpperCase()}\n` +
      `CLINICAL HANDOVER SUMMARY\n\n` +
      `Patient ID: ${report.patient_id}\n` +
      `Patient Name: ${report.patient_name || 'N/A'}\n` +
      `Department: ${report.department} (ICD-10: ${report.icd10_code})\n` +
      `Triage Level: ${report.triage_level}\n` +
      `Location: ${report.room_number}\n` +
      `Diagnoses: ${(report.diagnoses || []).join(', ')}\n` +
      `Medications: ${(report.medications || []).join(', ')}\n\n` +
      `Clinical Note:\n${report.report_text}`
    )
    window.location.href = `mailto:?subject=${subject}&body=${body}`
    showToast('Prepared email sharing template.', 'info')
  }

  const handleLogout = () => {
    localStorage.removeItem('token')
    localStorage.removeItem('username')
    localStorage.removeItem('userRole')
    localStorage.removeItem('hospitalName')
    setToken('')
    setUsername('')
    setReportText('')
    setResult(null)
    setHistory([])
    setAnalytics(null)
    setPage('landing')
  }

  const handleDemoLoad = () => {
    setReportText(sampleNote)
    setError('')
  }

  const renderDbBadge = () => {
    if (!dbStatus) return null
    const isMongo = dbStatus.mongodb_connected
    return (
      <div className={`db-status-pill ${isMongo ? 'mongodb' : 'sqlite'}`} title={dbStatus.database_mode}>
        <span className="status-dot"></span>
        <span>{isMongo ? 'MongoDB Atlas' : 'SQLite Local'}</span>
      </div>
    )
  }

  // --- Landing Page ---
  if (page === 'landing' && !token) {
    return (
      <div className={`landing-page ${darkMode ? 'dark-mode' : ''}`}>
        <header className="landing-header">
          <div className="brand-wrap">
            <div className="brand-mark">⚕️</div>
            <div>
              {isEditingHospital ? (
                <div style={{ display: 'flex', gap: '6px', alignItems: 'center' }}>
                  <input
                    type="text"
                    className="editable-hospital-input"
                    value={tempHospitalName}
                    onChange={(e) => setTempHospitalName(e.target.value)}
                    placeholder="Enter Medical Center Name"
                  />
                  <button className="primary-btn small" onClick={() => handleSaveHospitalName(tempHospitalName)}>Save</button>
                  <button className="secondary-btn small" onClick={() => setIsEditingHospital(false)}>Cancel</button>
                </div>
              ) : (
                <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
                  <div className="brand-name">{hospitalName.toUpperCase()}</div>
                  <button
                    className="edit-hospital-btn"
                    title="Change Medical Center Name"
                    onClick={() => { setTempHospitalName(hospitalName); setIsEditingHospital(true); }}
                  >
                    ✏️ Edit Facility Name
                  </button>
                </div>
              )}
              <div className="hospital-sub">MediExtract Clinical EMR Portal</div>
            </div>
          </div>

          <nav className="landing-nav">
            <a href="#features">EHR Features</a>
            <a href="#workflow">Triage Workflow</a>
            <button className="theme-toggle-btn" onClick={toggleDarkMode}>
              {darkMode ? '☀️ Light' : '🌙 Dark'}
            </button>
            <button className="primary-btn" onClick={() => setPage('auth')}>Staff Login</button>
          </nav>
        </header>

        <main className="landing-main">
          <section className="hero-section">
            <div className="hero-copy">
              <span className="eyebrow">Enterprise Hospital Intelligence</span>
              <h1>AI Clinical Triage, EHR Extraction & Patient Management.</h1>
              <p>
                Transform unstructured doctor notes, emergency dictations, and lab summaries into structured ICD-10 codes,
                triage alerts, and handover registries. Built for modern hospital care teams.
              </p>

              <div className="hero-actions">
                <button className="primary-btn large" onClick={() => setPage('auth')}>Access Clinical Portal</button>
                <button className="secondary-btn large" onClick={() => { setPage('auth'); setAuthMode('login'); }}>Sign in</button>
              </div>

              <div className="stats-row">
                <div>
                  <strong>99.4%</strong>
                  <span>Triage Precision</span>
                </div>
                <div>
                  <strong>&lt;1s</strong>
                  <span>ICD-10 Coding</span>
                </div>
                <div>
                  <strong>24/7</strong>
                  <span>EMR Synchronization</span>
                </div>
              </div>
            </div>

            <div className="hero-panel">
              <div className="mini-card">
                <span className="pill">🔴 EMERGENCY TRIAGE</span>
                <h3>Acute Myocardial Infarction</h3>
                <ul>
                  <li>Facility: {hospitalName}</li>
                  <li>Patient ID: PAT-2026-8941</li>
                  <li>Location: ICU Bed 02</li>
                  <li>Diagnosis: Acute MI, Hypertension</li>
                  <li>ICD-10: I21.9 | Risk: Critical</li>
                  <li>Safety Tag: 🫀 CARDIAC SURGE WATCH</li>
                </ul>
              </div>
            </div>
          </section>

          <section id="features" className="feature-section">
            <div className="section-heading">
              <span className="eyebrow">Hospital Systems</span>
              <h2>Complete clinical operations suite</h2>
            </div>

            <div className="feature-grid">
              <div className="feature-card">
                <span className="feature-icon">🚨</span>
                <h3>Automated Triage</h3>
                <p>Categorize incoming emergency notes into Emergency, Urgent, and Routine triage queues.</p>
              </div>
              <div className="feature-card">
                <span className="feature-icon">🏥</span>
                <h3>Bed & EMR Tracking</h3>
                <p>Assign Patient IDs, Bed Numbers, and monitor ICU occupancy and admission statuses.</p>
              </div>
              <div className="feature-card">
                <span className="feature-icon">🏷️</span>
                <h3>ICD-10 & Entity NER</h3>
                <p>Predict ICD-10 codes and extract diagnoses, symptoms, dosages, and drug allergies.</p>
              </div>
              <div className="feature-card">
                <span className="feature-icon">🖨️</span>
                <h3>Printable Handover Reports</h3>
                <p>Generate standardized clinical EMR summary PDF reports with physician signature blocks.</p>
              </div>
            </div>
          </section>
        </main>

        <footer className="landing-footer">
          <p>© 2026 {hospitalName} — MediExtract AI Healthcare Platform.</p>
        </footer>
      </div>
    )
  }

  // --- Auth Screen ---
  if (page === 'auth' && !token) {
    return (
      <div className={`auth-page ${darkMode ? 'dark-mode' : ''}`}>
        <div className="auth-shell">
          <div className="auth-card">
            <div className="auth-header">
              <div className="brand-mark small">⚕️</div>
              <h2>{authMode === 'login' ? 'Staff Authentication' : 'Register Clinical Profile'}</h2>
              <button className="link-btn" onClick={() => setPage('landing')} type="button">← Back to Portal</button>
            </div>

            <form onSubmit={handleAuth} className="auth-form">
              <label className="field">
                <span>Username / Staff ID</span>
                <input
                  type="text"
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  placeholder="Enter staff username"
                  required
                />
              </label>

              {authMode === 'register' && (
                <>
                  <label className="field">
                    <span>Hospital Email</span>
                    <input
                      type="email"
                      value={email}
                      onChange={(e) => setEmail(e.target.value)}
                      placeholder="doctor@hospital.org"
                      required
                    />
                  </label>

                  <label className="field">
                    <span>Medical Center / Hospital Name *</span>
                    <input
                      type="text"
                      value={hospitalName}
                      onChange={(e) => setHospitalName(e.target.value)}
                      placeholder="e.g. Metro Health Medical Center"
                      required
                    />
                  </label>

                  <label className="field">
                    <span>Clinical Role</span>
                    <select value={userRole} onChange={(e) => setUserRole(e.target.value)}>
                      <option value="Doctor">Attending Doctor</option>
                      <option value="Emergency Nurse">Emergency Triage Nurse</option>
                      <option value="Specialist">Radiologist / Specialist</option>
                      <option value="Administrator">Hospital Administrator</option>
                    </select>
                  </label>
                </>
              )}

              <label className="field">
                <span>Security Password</span>
                <input
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="Enter password"
                  required
                />
              </label>

              {authError && <div className="error-message">{authError}</div>}

              <button type="submit" className="primary-btn auth-submit" disabled={authLoading}>
                {authLoading ? 'Authenticating...' : authMode === 'login' ? 'Access Portal' : 'Register Staff Account'}
              </button>
            </form>

            <div className="form-switch" style={{ flexDirection: 'column', gap: '8px' }}>
              <div>
                {authMode === 'login' ? 'New staff member?' : 'Existing staff member?'}
                <button type="button" onClick={() => {
                  setAuthMode(authMode === 'login' ? 'register' : 'login')
                  setAuthError('')
                }}>
                  {authMode === 'login' ? 'Register Profile' : 'Sign in'}
                </button>
              </div>
              {authMode === 'login' && (
                <button type="button" className="link-btn" onClick={() => setShowResetModal(true)}>
                  🔑 Forgot Password? Reset Here
                </button>
              )}
            </div>
          </div>
        </div>
      </div>
    )
  }

  // --- Hospital Web Dashboard (Left Sidebar Navigation Layout) ---
  return (
    <div className={`app-layout ${darkMode ? 'dark-mode' : ''}`}>
      {/* Toast Notification Banner */}
      {toast && (
        <div className="toast-container">
          <div className={`toast ${toast.type}`}>
            <span>{toast.message}</span>
          </div>
        </div>
      )}

      {/* --- SIDEBAR NAVIGATION --- */}
      <aside className="sidebar-nav">
        <div className="sidebar-header">
          <div className="brand-mark">⚕️</div>
          <div className="brand-details">
            {isEditingHospital ? (
              <div className="edit-hospital-wrap">
                <input
                  type="text"
                  className="editable-hospital-input"
                  value={tempHospitalName}
                  onChange={(e) => setTempHospitalName(e.target.value)}
                  placeholder="Hospital Name"
                />
                <button className="primary-btn micro" onClick={() => handleSaveHospitalName(tempHospitalName)}>Save</button>
              </div>
            ) : (
              <div className="hospital-title-row">
                <span className="brand-name">{hospitalName.toUpperCase()}</span>
                <button
                  className="edit-hospital-btn"
                  title="Edit Facility Name"
                  onClick={() => { setTempHospitalName(hospitalName); setIsEditingHospital(true); }}
                >
                  ✏️
                </button>
              </div>
            )}
            <div className="hospital-sub">MediExtract HIS Portal</div>
          </div>
        </div>

        <div className="nav-menu">
          <div className="nav-category">CLINICAL WORKFLOWS</div>
          <button className={activeTab === 'analyze' ? 'nav-item active' : 'nav-item'} onClick={() => setActiveTab('analyze')}>
            <span className="nav-icon">🏥</span>
            <span className="nav-label">Intake & Triage</span>
          </button>
          <button className={activeTab === 'patients' ? 'nav-item active' : 'nav-item'} onClick={() => { setActiveTab('patients'); loadPatients(); }}>
            <span className="nav-icon">👥</span>
            <span className="nav-label">Patient Directory</span>
            {patients.length > 0 && <span className="nav-badge">{patients.length}</span>}
          </button>
          <button className={activeTab === 'appointments' ? 'nav-item active' : 'nav-item'} onClick={() => { setActiveTab('appointments'); loadAppointments(); }}>
            <span className="nav-icon">📅</span>
            <span className="nav-label">OPD & Queue</span>
            {appointments.length > 0 && <span className="nav-badge">{appointments.length}</span>}
          </button>
          <button className={activeTab === 'lab' ? 'nav-item active' : 'nav-item'} onClick={() => { setActiveTab('lab'); loadLabOrders(); }}>
            <span className="nav-icon">🧪</span>
            <span className="nav-label">Pathology Lab</span>
            {labOrders.length > 0 && <span className="nav-badge">{labOrders.length}</span>}
          </button>
          <button className={activeTab === 'pharmacy' ? 'nav-item active' : 'nav-item'} onClick={() => { setActiveTab('pharmacy'); loadPrescriptions(); loadPharmacyInventory(); }}>
            <span className="nav-icon">💊</span>
            <span className="nav-label">Pharmacy</span>
          </button>
          <button className={activeTab === 'beds' ? 'nav-item active' : 'nav-item'} onClick={() => setActiveTab('beds')}>
            <span className="nav-icon">🛏️</span>
            <span className="nav-label">Bed & ICU Map</span>
          </button>

          <div className="nav-category">HOSPITAL OPERATIONS</div>
          <button className={activeTab === 'billing' ? 'nav-item active' : 'nav-item'} onClick={() => { setActiveTab('billing'); loadInvoices(); }}>
            <span className="nav-icon">💳</span>
            <span className="nav-label">Billing & Claims</span>
            {invoices.length > 0 && <span className="nav-badge">{invoices.length}</span>}
          </button>
          <button className={activeTab === 'staff' ? 'nav-item active' : 'nav-item'} onClick={() => { setActiveTab('staff'); loadStaff(); }}>
            <span className="nav-icon">👩‍⚕️</span>
            <span className="nav-label">Staff Duty Roster</span>
          </button>
          <button className={activeTab === 'inventory' ? 'nav-item active' : 'nav-item'} onClick={() => { setActiveTab('inventory'); loadConsumables(); }}>
            <span className="nav-icon">📦</span>
            <span className="nav-label">Supplies & Stock</span>
            {consumables.length > 0 && <span className="nav-badge">{consumables.length}</span>}
          </button>
          <button className={activeTab === 'analytics' ? 'nav-item active' : 'nav-item'} onClick={() => { setActiveTab('analytics'); loadAnalytics(); }}>
            <span className="nav-icon">📊</span>
            <span className="nav-label">Command Center</span>
          </button>
          <button className={activeTab === 'records' ? 'nav-item active' : 'nav-item'} onClick={() => { setActiveTab('records'); loadHistory(); }}>
            <span className="nav-icon">📚</span>
            <span className="nav-label">EMR Archive</span>
            {history.length > 0 && <span className="nav-badge">{history.length}</span>}
          </button>

          <div className="nav-category">PATIENT SERVICES</div>
          <button className={activeTab === 'portal' ? 'nav-item active' : 'nav-item'} onClick={() => setActiveTab('portal')}>
            <span className="nav-icon">🛡️</span>
            <span className="nav-label">Patient Portal</span>
          </button>
        </div>

        <div className="sidebar-footer">
          <div className="user-profile-card">
            <div className="user-avatar">{username ? username[0].toUpperCase() : 'U'}</div>
            <div className="user-info">
              <span className="user-name">{username}</span>
              <select
                value={userRole}
                onChange={(e) => {
                  setUserRole(e.target.value)
                  localStorage.setItem('userRole', e.target.value)
                }}
                className="sidebar-role-select"
              >
                <option value="Doctor">Doctor</option>
                <option value="Emergency Nurse">Emergency Nurse</option>
                <option value="Specialist">Specialist</option>
                <option value="Administrator">Administrator</option>
                <option value="Receptionist">Receptionist</option>
                <option value="Pharmacist">Pharmacist</option>
                <option value="Lab Technician">Lab Technician</option>
                <option value="Patient">Patient</option>
              </select>
            </div>
          </div>

          <div className="sidebar-actions">
            <button className="icon-btn" title="Audit Logs" onClick={loadActivityLogs}>📋 Logs</button>
            <button className="icon-btn" title="Toggle Theme" onClick={toggleDarkMode}>{darkMode ? '☀️ Light' : '🌙 Dark'}</button>
            <button className="icon-btn danger" title="Sign Out" onClick={handleLogout}>🚪 Exit</button>
          </div>
        </div>
      </aside>

      {/* --- MAIN CONTENT STAGE --- */}
      <main className="main-content-stage">
        {/* Top Header Bar */}
        <header className="top-stage-header">
          <div className="breadcrumb-box">
            <span className="breadcrumb-path">Hospital Dashboard / {hospitalName}</span>
            <h1 className="active-module-title">
              {activeTab === 'analyze' && '🏥 Clinical Intake & Emergency Triage'}
              {activeTab === 'patients' && '👥 Patient Directory & EMR Records'}
              {activeTab === 'appointments' && '📅 OPD Appointments & Token Queue'}
              {activeTab === 'lab' && '🧪 Pathology & Diagnostic Laboratory'}
              {activeTab === 'pharmacy' && '💊 Hospital Pharmacy & Dispensary'}
              {activeTab === 'beds' && '🛏️ Visual Bed & ICU Occupancy Map'}
              {activeTab === 'billing' && '💳 Patient Billing & Insurance Claims'}
              {activeTab === 'staff' && '👩‍⚕️ Staff Directory & Shift Roster'}
              {activeTab === 'inventory' && '📦 Consumables & Supply Inventory'}
              {activeTab === 'analytics' && '📊 Command Center Intelligence'}
              {activeTab === 'records' && '📚 Patient EMR Handover Archive'}
              {activeTab === 'portal' && '🛡️ Patient Self-Service Portal'}
            </h1>
          </div>

          <div className="top-header-right">
            {renderDbBadge()}
          </div>
        </header>

        {/* Hospital KPI Command Center Bar */}
        <div className="kpi-bar">
          <div className="kpi-box" onClick={() => setActiveTab('patients')} style={{ cursor: 'pointer' }}>
            <div className="kpi-icon blue">🏥</div>
            <div className="kpi-copy">
              <span>Active Patients</span>
              <strong>{analytics?.active_admitted || history.length || 0}</strong>
            </div>
          </div>
          <div className="kpi-box" onClick={() => setActiveTab('analyze')} style={{ cursor: 'pointer' }}>
            <div className="kpi-icon red">🚨</div>
            <div className="kpi-copy">
              <span>Emergency Triage</span>
              <strong>{analytics?.emergency_cases || 0}</strong>
            </div>
          </div>
          <div className="kpi-box" onClick={() => setActiveTab('beds')} style={{ cursor: 'pointer' }}>
            <div className="kpi-icon amber">🛏️</div>
            <div className="kpi-copy">
              <span>ICU Occupancy</span>
              <strong>{analytics?.icu_patients || 0} Beds</strong>
            </div>
          </div>
          <div className="kpi-box" onClick={() => setShowCriticalAlertsModal(true)} style={{ cursor: 'pointer' }} title="Click to view critical alerts">
            <div className="kpi-icon purple">⚠️</div>
            <div className="kpi-copy">
              <span>Critical Alerts</span>
              <strong>{analytics?.critical_alerts_count || 0} (Click)</strong>
            </div>
          </div>
        </div>

        {/* --- TAB 1: CLINICAL INTAKE & TRIAGE --- */}
        {activeTab === 'analyze' && (
          <div className="analyze-layout">
            <section className="panel input-panel">
              <div className="panel-header">
                <h2>Clinical Intake & EHR Note</h2>
                <button className="secondary-btn small" onClick={handleDemoLoad}>Load Sample Emergency Note</button>
              </div>

              <div className="input-actions">
                <button className="mode-btn active">Text Narrative</button>
                <label className="mode-btn upload-btn">
                  Upload PDF / Text
                  <input type="file" accept=".txt,.pdf" onChange={handleFileUpload} />
                </label>
                <button className={`mode-btn ${isListening ? 'listening' : ''}`} onClick={startVoiceInput}>
                  Voice Dictation {isListening ? '…' : ''}
                </button>
              </div>

              <div className="ehr-intake-grid">
                <div className="ehr-field">
                  <label>Patient ID</label>
                  <input
                    type="text"
                    value={ehrPatientId}
                    placeholder="PAT-2026-XXXX"
                    onChange={(e) => setEhrPatientId(e.target.value)}
                  />
                </div>
                <div className="ehr-field">
                  <label>Room / Bed #</label>
                  <input
                    type="text"
                    value={ehrRoomNumber}
                    placeholder="e.g. ICU-02 / Ward 1"
                    onChange={(e) => setEhrRoomNumber(e.target.value)}
                  />
                </div>
                <div className="ehr-field">
                  <label>Admission Status</label>
                  <select value={ehrAdmissionStatus} onChange={(e) => setEhrAdmissionStatus(e.target.value)}>
                    <option value="Admitted">Admitted</option>
                    <option value="ICU">ICU</option>
                    <option value="Discharged">Discharged</option>
                    <option value="Outpatient">Outpatient</option>
                  </select>
                </div>
                <div className="ehr-field">
                  <label>Attending Doctor</label>
                  <input
                    type="text"
                    value={ehrAttending}
                    placeholder="Dr. N. Patel"
                    onChange={(e) => setEhrAttending(e.target.value)}
                  />
                </div>
              </div>

              <textarea
                value={reportText}
                onChange={(e) => setReportText(e.target.value)}
                className="clinical-input"
                placeholder="Paste physician note, emergency dictation, or discharge handover narrative..."
              />

              {error && <div className="error-banner" style={{ marginTop: '12px' }}>{error}</div>}

              <button className="primary-btn wide" onClick={handleAnalyze} disabled={loading || !reportText.trim()}>
                {loading ? 'Processing Triage & Extracting Entities...' : 'Process Triage & Save to Hospital Database'}
              </button>
            </section>

            <section className="panel results-panel">
              <div className="panel-header">
                <h2>Clinical Intelligence Summary</h2>
                <span className="muted">Automated Triage & ICD-10 Coding</span>
              </div>

              {result ? (
                <div className="result-body">
                  <div className={`triage-banner ${result.triage_level?.toLowerCase() || 'routine'}`}>
                    <span>
                      {result.triage_level === 'Emergency' ? '🔴 EMERGENCY TRIAGE - IMMEDIATE ATTENTION' :
                       result.triage_level === 'Urgent' ? '🟠 URGENT TRIAGE - PRIORITY ASSESSMENT' : '🟢 ROUTINE CLINICAL CARE'}
                    </span>
                    <span>Risk Level: {result.risk_level || 'Low'}</span>
                  </div>

                  {result.clinical_flags?.length > 0 && (
                    <div className="flags-wrap">
                      {result.clinical_flags.map((flag, idx) => (
                        <span key={idx} className="flag-chip">{flag}</span>
                      ))}
                    </div>
                  )}

                  <div className="result-metrics">
                    <div className="metric-box">
                      <span>Patient ID</span>
                      <strong>{ehrPatientId || result.patient_id || 'PAT-2026-1001'}</strong>
                    </div>
                    <div className="metric-box">
                      <span>Patient Name</span>
                      <strong>{result.patient_name || '—'}</strong>
                    </div>
                    <div className="metric-box">
                      <span>Age / Sex</span>
                      <strong>{result.age && result.gender ? `${result.age} / ${result.gender}` : result.gender || result.age || '—'}</strong>
                    </div>
                    <div className="metric-box">
                      <span>ICD-10 Code</span>
                      <strong style={{ color: '#047857' }}>{result.icd10_code || 'R50.9'}</strong>
                    </div>
                  </div>

                  <div className="entity-groups">
                    <div className="entity-box">
                      <h3>Diagnoses & Conditions</h3>
                      <div className="badge-list">
                        {result.diagnoses?.length
                          ? result.diagnoses.map((item, idx) => <span key={idx} className="badge danger">{item}</span>)
                          : <span className="badge muted">None detected</span>}
                      </div>
                    </div>

                    <div className="entity-box">
                      <h3>Symptoms</h3>
                      <div className="badge-list">
                        {result.symptoms?.length
                          ? result.symptoms.map((item, idx) => <span key={idx} className="badge warning">{item}</span>)
                          : <span className="badge muted">None detected</span>}
                      </div>
                    </div>

                    <div className="entity-box">
                      <h3>Medications</h3>
                      <div className="badge-list">
                        {result.medications?.length
                          ? result.medications.map((item, idx) => <span key={idx} className="badge primary">{item}</span>)
                          : <span className="badge muted">None detected</span>}
                      </div>
                    </div>

                    <div className="entity-box">
                      <h3>Dosages & Instructions</h3>
                      <div className="badge-list">
                        {result.dosages?.length
                          ? result.dosages.map((item, idx) => <span key={idx} className="badge info">{item}</span>)
                          : <span className="badge muted">None detected</span>}
                      </div>
                    </div>

                    <div className="entity-box">
                      <h3>Treatments & Lab Tests</h3>
                      <div className="badge-list">
                        {result.lab_tests?.length
                          ? result.lab_tests.map((item, idx) => <span key={idx} className="badge success">{item}</span>)
                          : <span className="badge muted">None detected</span>}
                      </div>
                    </div>

                    <div className="entity-box">
                      <h3>Drug Allergies</h3>
                      <div className="badge-list">
                        {result.allergies?.length
                          ? result.allergies.map((item, idx) => <span key={idx} className="badge purple">{item}</span>)
                          : <span className="badge muted">None detected</span>}
                      </div>
                    </div>
                  </div>

                  <div className="score-box">
                    <label>Extraction & Classification Accuracy</label>
                    <div className="progress-bar">
                      <div className="progress-fill" style={{ width: `${(result.confidence_score || 0.85) * 100}%` }} />
                    </div>
                    <strong>{((result.confidence_score || 0.85) * 100).toFixed(1)}% Confidence Rating</strong>
                  </div>
                </div>
              ) : (
                <div className="empty-state">
                  <div className="empty-icon">🏥</div>
                  <p>Process a note to view automated triage levels, ICD-10 codes, and extracted entities.</p>
                </div>
              )}
            </section>
          </div>
        )}

        {/* --- TAB 2: PATIENT MANAGEMENT --- */}
        {activeTab === 'patients' && (
          <section className="panel">
            <div className="panel-header">
              <h2>Hospital Patient Directory</h2>
              <button className="primary-btn small" onClick={() => setShowAddPatientModal(true)}>+ Register New Patient</button>
            </div>

            <div className="history-grid" style={{ marginTop: '14px' }}>
              {patients.length ? patients.map(p => (
                <div key={p.id} className="history-card">
                  <div>
                    <div className="history-header">
                      <h3>{p.name}</h3>
                      <span className="badge primary">{p.patient_id}</span>
                    </div>
                    <p style={{ margin: '6px 0', fontSize: '0.9rem', color: '#475569' }}>
                      <strong>Demographics:</strong> {p.age} yrs • {p.gender} • {p.phone}<br/>
                      <strong>Blood Group:</strong> {p.blood_group || 'O-Positive'} | <strong>Insurance:</strong> {p.insurance_policy || 'POL-Standard'}<br/>
                      <strong>Allergies:</strong> {(p.allergies || []).join(', ') || 'None'}<br/>
                      <strong>Past History:</strong> {(p.past_illnesses || []).join(', ') || 'No prior chronic conditions'}
                    </p>
                  </div>
                  <div className="history-footer">
                    <button className="secondary-btn small" onClick={() => {
                      setEhrPatientId(p.patient_id)
                      setActiveTab('analyze')
                      showToast(`Selected patient ${p.patient_id} for Intake`, 'info')
                    }}>Start Clinical Intake</button>
                  </div>
                </div>
              )) : (
                <div className="empty-state">
                  <div className="empty-icon">👥</div>
                  <p>No registered patients found in database.</p>
                </div>
              )}
            </div>
          </section>
        )}

        {/* --- TAB 3: OPD APPOINTMENTS & TOKEN QUEUE --- */}
        {activeTab === 'appointments' && (
          <section className="panel">
            <div className="panel-header">
              <h2>OPD Appointments & Token Queue</h2>
              <button className="primary-btn small" onClick={() => setShowAddApptModal(true)}>+ Book OPD Appointment</button>
            </div>

            <table className="print-table" style={{ marginTop: '16px' }}>
              <thead>
                <tr style={{ background: '#f8fafc' }}>
                  <th>Token #</th>
                  <th>Patient ID</th>
                  <th>Patient Name</th>
                  <th>Doctor</th>
                  <th>Department</th>
                  <th>Slot</th>
                  <th>Status</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {appointments.length ? appointments.map(app => (
                  <tr key={app.id}>
                    <td><strong style={{ fontSize: '1.1rem', color: '#0284c7' }}>#{app.token_number || 1}</strong></td>
                    <td>{app.patient_id}</td>
                    <td><strong>{app.patient_name}</strong></td>
                    <td>{app.doctor_name}</td>
                    <td>{app.department}</td>
                    <td>{app.appointment_time}</td>
                    <td>
                      <span className={`badge ${app.status === 'Completed' ? 'success' : app.status === 'In-Consultation' ? 'warning' : 'primary'}`}>
                        {app.status}
                      </span>
                    </td>
                    <td>
                      <div style={{ display: 'flex', gap: '4px' }}>
                        {app.status === 'Booked' && (
                          <button className="secondary-btn small" onClick={() => handleApptStatusUpdate(app.id, 'In-Consultation')}>Call Patient</button>
                        )}
                        {app.status === 'In-Consultation' && (
                          <button className="primary-btn small" onClick={() => handleApptStatusUpdate(app.id, 'Completed')}>Complete Visit</button>
                        )}
                      </div>
                    </td>
                  </tr>
                )) : (
                  <tr><td colSpan="8" style={{ textAlign: 'center', padding: '24px', color: '#64748b' }}>No active OPD appointments for today.</td></tr>
                )}
              </tbody>
            </table>
          </section>
        )}

        {/* --- TAB 4: LABORATORY MANAGEMENT --- */}
        {activeTab === 'lab' && (
          <section className="panel">
            <div className="panel-header">
              <h2>Pathology & Diagnostic Laboratory</h2>
              <button className="primary-btn small" onClick={() => setShowAddLabModal(true)}>+ Order Lab Test</button>
            </div>

            <div className="history-grid" style={{ marginTop: '16px' }}>
              {labOrders.length ? labOrders.map(order => (
                <div key={order.id} className="history-card">
                  <div>
                    <div className="history-header">
                      <h3>{order.test_name}</h3>
                      <span className={`badge ${order.abnormal_flag === 'HIGH' || order.abnormal_flag === 'CRITICAL' ? 'danger' : 'info'}`}>
                        {order.abnormal_flag || 'NORMAL'}
                      </span>
                    </div>
                    <p style={{ margin: '6px 0', fontSize: '0.88rem', color: '#475569' }}>
                      <strong>Patient:</strong> {order.patient_name} ({order.patient_id})<br/>
                      <strong>Ordering Doctor:</strong> {order.ordering_doctor}<br/>
                      <strong>Result Value:</strong> {order.result_value || 'Pending Laboratory Analysis'}<br/>
                      <strong>Reference Range:</strong> {order.reference_range || 'Normal'}
                    </p>
                  </div>
                  <div className="history-footer">
                    <span className="muted">Status: {order.status}</span>
                    <button className="secondary-btn small" onClick={() => {
                      setSelectedLabResultModal(order)
                      setLabResultInput({ result_value: order.result_value || '', normal_range: order.reference_range || 'Normal', flag: order.abnormal_flag || 'NORMAL' })
                    }}>Enter / Edit Result</button>
                  </div>
                </div>
              )) : (
                <div className="empty-state">
                  <div className="empty-icon">🧪</div>
                  <p>No lab test orders found.</p>
                </div>
              )}
            </div>
          </section>
        )}

        {/* --- TAB 5: PHARMACY & DISPENSARY --- */}
        {activeTab === 'pharmacy' && (
          <section className="panel">
            <div className="panel-header">
              <h2>Hospital Pharmacy & Dispensary</h2>
              <button className="primary-btn small" onClick={() => setShowAddRxModal(true)}>+ Log Prescription</button>
            </div>

            <div style={{ background: '#f8fafc', padding: '16px', borderRadius: '10px', border: '1px solid #e2e8f0', margin: '14px 0' }}>
              <h3 style={{ margin: '0 0 8px', fontSize: '1rem' }}>⚠️ Automated Drug-Drug Interaction Checker</h3>
              <div style={{ display: 'flex', gap: '8px' }}>
                <input
                  type="text"
                  value={drugCheckText}
                  onChange={(e) => setDrugCheckText(e.target.value)}
                  placeholder="Enter comma-separated medications e.g. Aspirin, Warfarin, Metformin"
                  style={{ flex: 1, padding: '8px 12px', borderRadius: '6px', border: '1px solid #cbd5e1' }}
                />
                <button className="primary-btn small" onClick={handleCheckDrugInteractions}>Check Interactions</button>
              </div>

              {drugInteractionResults.length > 0 && (
                <div style={{ marginTop: '10px' }}>
                  {drugInteractionResults.map((alert, idx) => (
                    <div key={idx} className="error-banner" style={{ marginTop: '4px' }}>{alert}</div>
                  ))}
                </div>
              )}
            </div>

            <table className="print-table">
              <thead>
                <tr style={{ background: '#f8fafc' }}>
                  <th>Medication</th>
                  <th>Dosage</th>
                  <th>Frequency & Duration</th>
                  <th>Patient</th>
                  <th>Doctor</th>
                  <th>Status</th>
                  <th>Action</th>
                </tr>
              </thead>
              <tbody>
                {prescriptions.length ? prescriptions.map(rx => (
                  <tr key={rx.id}>
                    <td><strong>{rx.medication_name}</strong></td>
                    <td>{rx.dosage}</td>
                    <td>{rx.frequency} ({rx.duration})</td>
                    <td>{rx.patient_name}</td>
                    <td>{rx.doctor_name}</td>
                    <td>
                      <span className={`badge ${rx.dispensed ? 'success' : 'warning'}`}>
                        {rx.dispensed ? 'Dispensed' : 'Pending Dispense'}
                      </span>
                    </td>
                    <td>
                      {!rx.dispensed && (
                        <button className="primary-btn small" onClick={() => handleDispenseRx(rx.id)}>Dispense Drug</button>
                      )}
                    </td>
                  </tr>
                )) : (
                  <tr><td colSpan="7" style={{ textAlign: 'center', padding: '24px', color: '#64748b' }}>No active prescriptions in pharmacy queue.</td></tr>
                )}
              </tbody>
            </table>
          </section>
        )}

        {/* --- TAB 6: VISUAL BED & ICU MAP --- */}
        {activeTab === 'beds' && (
          <section className="panel">
            <div className="panel-header">
              <h2>Visual Bed & ICU Occupancy Map ({hospitalName})</h2>
              <span className="muted">Live Ward Capacity Grid</span>
            </div>

            <div className="history-grid" style={{ marginTop: '16px' }}>
              {bedsList.map(bed => (
                <div key={bed.bed_id} className={`history-card ${bed.status.toLowerCase()}`} style={{ borderLeft: bed.status === 'Occupied' ? '4px solid #ef4444' : bed.status === 'Available' ? '4px solid #10b981' : '4px solid #f59e0b' }}>
                  <div className="history-header">
                    <h3>{bed.bed_id}</h3>
                    <span className={`badge ${bed.status === 'Occupied' ? 'danger' : bed.status === 'Available' ? 'success' : 'warning'}`}>
                      {bed.status}
                    </span>
                  </div>
                  <p style={{ margin: '6px 0', fontSize: '0.88rem', color: '#334155' }}>
                    <strong>Ward:</strong> {bed.ward}<br/>
                    <strong>Occupant:</strong> {bed.patient_name || 'Unoccupied'}<br/>
                    <strong>Patient ID:</strong> {bed.patient_id || '—'}<br/>
                    <strong>Attending:</strong> {bed.doctor || '—'}
                  </p>
                  <button className="secondary-btn small" style={{ width: '100%', marginTop: '8px' }} onClick={() => {
                    setShowBedAssignModal(bed)
                    setBedAssignInput({ patient_id: bed.patient_id, patient_name: bed.patient_name, doctor: bed.doctor || 'Dr. N. Patel', status: bed.status })
                  }}>Manage Bed Assignment</button>
                </div>
              ))}
            </div>
          </section>
        )}

        {/* --- TAB 7: BILLING & CLAIMS --- */}
        {activeTab === 'billing' && (
          <section className="panel">
            <div className="panel-header">
              <h2>Billing & Insurance Claims</h2>
              <button className="primary-btn small" onClick={() => setShowAddInvoiceModal(true)}>+ Generate New Invoice</button>
            </div>

            <table className="print-table" style={{ marginTop: '16px' }}>
              <thead>
                <tr style={{ background: '#f8fafc' }}>
                  <th>Invoice ID</th>
                  <th>Patient Name</th>
                  <th>Consultation Fee</th>
                  <th>Lab Fee</th>
                  <th>Pharmacy Fee</th>
                  <th>Room Charges</th>
                  <th>Total Amount</th>
                  <th>Status</th>
                  <th>Insurance Claim</th>
                  <th>Action</th>
                </tr>
              </thead>
              <tbody>
                {invoices.length ? invoices.map(inv => (
                  <tr key={inv.id}>
                    <td><code>{inv.id}</code></td>
                    <td><strong>{inv.patient_name}</strong></td>
                    <td>${inv.consultation_fee}</td>
                    <td>${inv.lab_fee}</td>
                    <td>${inv.pharmacy_fee}</td>
                    <td>${inv.room_charges}</td>
                    <td><strong style={{ color: '#047857', fontSize: '1.05rem' }}>${inv.total_amount}</strong></td>
                    <td>
                      <span className={`badge ${inv.payment_status === 'Paid' ? 'success' : 'warning'}`}>
                        {inv.payment_status}
                      </span>
                    </td>
                    <td><span className="badge info">{inv.insurance_status}</span></td>
                    <td>
                      {inv.payment_status === 'Pending' && (
                        <button className="primary-btn small" onClick={() => handlePayInvoice(inv.id)}>Collect Payment</button>
                      )}
                    </td>
                  </tr>
                )) : (
                  <tr><td colSpan="10" style={{ textAlign: 'center', padding: '24px', color: '#64748b' }}>No invoices logged.</td></tr>
                )}
              </tbody>
            </table>
          </section>
        )}

        {/* --- TAB 8: STAFF ROSTER --- */}
        {activeTab === 'staff' && (
          <section className="panel">
            <div className="panel-header">
              <h2>Clinical & Operations Staff Roster</h2>
              <button className="primary-btn small" onClick={() => setShowAddStaffModal(true)}>+ Add Staff Member</button>
            </div>

            <table className="print-table" style={{ marginTop: '16px' }}>
              <thead>
                <tr style={{ background: '#f8fafc' }}>
                  <th>Name</th>
                  <th>Role</th>
                  <th>Department</th>
                  <th>Shift</th>
                  <th>Phone</th>
                  <th>Status</th>
                </tr>
              </thead>
              <tbody>
                {staffList.length ? staffList.map(s => (
                  <tr key={s.id}>
                    <td><strong>{s.name}</strong></td>
                    <td><span className="badge primary">{s.role}</span></td>
                    <td>{s.department}</td>
                    <td><span className="badge info">{s.shift}</span></td>
                    <td>{s.phone}</td>
                    <td><span className="badge success">{s.status}</span></td>
                  </tr>
                )) : (
                  <tr><td colSpan="6" style={{ textAlign: 'center', padding: '24px', color: '#64748b' }}>No staff members registered.</td></tr>
                )}
              </tbody>
            </table>
          </section>
        )}

        {/* --- TAB 9: SUPPLIES & INVENTORY --- */}
        {activeTab === 'inventory' && (
          <section className="panel">
            <div className="panel-header">
              <h2>Consumables & Inventory Management</h2>
              <button className="primary-btn small" onClick={() => setShowAddSupplyModal(true)}>+ Add Inventory Item</button>
            </div>

            <table className="print-table" style={{ marginTop: '16px' }}>
              <thead>
                <tr style={{ background: '#f8fafc' }}>
                  <th>Item Name</th>
                  <th>Category</th>
                  <th>Quantity in Stock</th>
                  <th>Reorder Level</th>
                  <th>Unit Cost</th>
                  <th>Vendor</th>
                  <th>Status</th>
                </tr>
              </thead>
              <tbody>
                {consumables.length ? consumables.map(c => (
                  <tr key={c.id}>
                    <td><strong>{c.item_name}</strong></td>
                    <td>{c.category}</td>
                    <td><strong>{c.quantity} units</strong></td>
                    <td>{c.reorder_level}</td>
                    <td>${c.unit_cost}</td>
                    <td>{c.vendor_name}</td>
                    <td>
                      {c.quantity <= c.reorder_level ? (
                        <span className="badge danger">⚠️ Low Stock Reorder</span>
                      ) : (
                        <span className="badge success">Stock Normal</span>
                      )}
                    </td>
                  </tr>
                )) : (
                  <tr><td colSpan="7" style={{ textAlign: 'center', padding: '24px', color: '#64748b' }}>No consumables registered in inventory.</td></tr>
                )}
              </tbody>
            </table>
          </section>
        )}

        {/* --- TAB 10: HOSPITAL COMMAND CENTER ANALYTICS --- */}
        {activeTab === 'analytics' && (
          <div>
            <div className="analytics-grid">
              <div className="analytics-card">
                <h3>Department Workload Distribution ({hospitalName})</h3>
                <div className="bar-list">
                  {analytics && Object.keys(analytics.department_counts || {}).length ? (
                    Object.entries(analytics.department_counts).map(([dept, count]) => {
                      const total = analytics.total_reports || 1
                      const pct = Math.round((count / total) * 100)
                      return (
                        <div key={dept} className="bar-row">
                          <span className="bar-label">{dept}</span>
                          <div className="bar-track">
                            <div className="bar-fill" style={{ width: `${pct}%` }}></div>
                          </div>
                          <span className="bar-val">{count}</span>
                        </div>
                      )
                    })
                  ) : (
                    <p className="muted">No department workload data available.</p>
                  )}
                </div>
              </div>

              <div className="analytics-card">
                <h3>Triage Level Distribution</h3>
                <div className="bar-list">
                  {analytics && Object.keys(analytics.triage_counts || {}).length ? (
                    Object.entries(analytics.triage_counts).map(([triage, count]) => {
                      const total = analytics.total_reports || 1
                      const pct = Math.round((count / total) * 100)
                      return (
                        <div key={triage} className="bar-row">
                          <span className="bar-label">{triage}</span>
                          <div className="bar-track">
                            <div className="bar-fill" style={{ width: `${pct}%`, background: triage === 'Emergency' ? '#ef4444' : triage === 'Urgent' ? '#f59e0b' : '#10b981' }}></div>
                          </div>
                          <span className="bar-val">{count}</span>
                        </div>
                      )
                    })
                  ) : (
                    <p className="muted">No triage distribution recorded.</p>
                  )}
                </div>
              </div>

              <div className="analytics-card">
                <h3>Top Clinical Diagnoses</h3>
                <div className="rank-list">
                  {analytics?.top_diagnoses?.length ? (
                    analytics.top_diagnoses.map((item, idx) => (
                      <div key={idx} className="rank-item">
                        <span>{item.name}</span>
                        <strong>{item.count} cases</strong>
                      </div>
                    ))
                  ) : (
                    <p className="muted">No diagnoses recorded yet.</p>
                  )}
                </div>
              </div>

              <div className="analytics-card">
                <h3>Top Prescribed Medications</h3>
                <div className="rank-list">
                  {analytics?.top_medications?.length ? (
                    analytics.top_medications.map((item, idx) => (
                      <div key={idx} className="rank-item">
                        <span>{item.name}</span>
                        <strong>{item.count} orders</strong>
                      </div>
                    ))
                  ) : (
                    <p className="muted">No medications recorded yet.</p>
                  )}
                </div>
              </div>
            </div>
          </div>
        )}

        {/* --- TAB 11: PATIENT REGISTRY & HANDOVER DESK --- */}
        {activeTab === 'records' && (
          <section className="panel history-panel">
            <div className="panel-header">
              <h2>Patient Registry & EMR Handover ({hospitalName})</h2>
              <span className="muted">{history.length} patient records</span>
            </div>

            <div className="filter-bar">
              <input
                type="text"
                placeholder="Search patient ID, name, diagnosis, medication, room..."
                value={searchTerm}
                onChange={(e) => {
                  setSearchTerm(e.target.value)
                  loadHistory(e.target.value, departmentFilter, triageFilter, statusFilter)
                }}
                className="filter-input"
              />

              <select
                value={departmentFilter}
                onChange={(e) => {
                  setDepartmentFilter(e.target.value)
                  loadHistory(searchTerm, e.target.value, triageFilter, statusFilter)
                }}
                className="filter-select"
              >
                <option value="">All Departments</option>
                <option value="Cardiology">Cardiology</option>
                <option value="Endocrinology">Endocrinology</option>
                <option value="Pulmonology">Pulmonology</option>
                <option value="Gastroenterology">Gastroenterology</option>
                <option value="Neurology">Neurology</option>
                <option value="Orthopedics">Orthopedics</option>
                <option value="General Medicine">General Medicine</option>
              </select>

              <select
                value={triageFilter}
                onChange={(e) => {
                  setTriageFilter(e.target.value)
                  loadHistory(searchTerm, departmentFilter, e.target.value, statusFilter)
                }}
                className="filter-select"
              >
                <option value="">All Triage Levels</option>
                <option value="Emergency">Emergency Triage</option>
                <option value="Urgent">Urgent Triage</option>
                <option value="Routine">Routine Care</option>
              </select>

              <select
                value={statusFilter}
                onChange={(e) => {
                  setStatusFilter(e.target.value)
                  loadHistory(searchTerm, departmentFilter, triageFilter, e.target.value)
                }}
                className="filter-select"
              >
                <option value="">All Admission Statuses</option>
                <option value="Admitted">Admitted</option>
                <option value="ICU">ICU</option>
                <option value="Discharged">Discharged</option>
              </select>

              <div className="export-btn-group">
                <button className="export-btn csv" onClick={exportCSV}>📥 Download CSV</button>
                <button className="export-btn json" onClick={exportJSON}>📥 Download JSON/Excel</button>
              </div>
            </div>

            {history.length ? (
              <div className="history-grid">
                {history.map((report) => (
                  <article key={report.id} className="history-card">
                    <div>
                      <div className="history-header">
                        <div className="patient-title-box">
                          <h3>{report.patient_name || report.patient_id || 'Patient Record'}</h3>
                          <div className="patient-id-sub">{report.patient_id} • {report.room_number || 'Ward 1'}</div>
                        </div>
                        <span className="icd-pill">{report.icd10_code || 'R50.9'}</span>
                      </div>

                      <div style={{ display: 'flex', gap: '6px', margin: '6px 0 10px' }}>
                        <span className={`badge ${report.triage_level === 'Emergency' ? 'danger' : report.triage_level === 'Urgent' ? 'warning' : 'success'}`}>
                          {report.triage_level || 'Routine'}
                        </span>
                        <span className="badge info">{report.admission_status || 'Admitted'}</span>
                      </div>

                      <p className="history-snippet">{report.report_text?.substring(0, 130)}...</p>

                      <div className="history-tags">
                        {report.diagnoses?.slice(0, 2).map((d, i) => (
                          <span key={i} className="badge danger">{d}</span>
                        ))}
                        {report.medications?.slice(0, 2).map((m, i) => (
                          <span key={i} className="badge primary">{m}</span>
                        ))}
                      </div>
                    </div>

                    <div className="history-footer">
                      <span className="muted">{report.attending_physician || 'Dr. N. Patel'}</span>
                      <div className="history-actions">
                        <button className="secondary-btn small" onClick={() => setSelectedReport(report)}>View / Print EMR</button>
                        <button className="secondary-btn small" onClick={() => shareEmail(report)}>📧 Email</button>
                        <button className="danger-btn" onClick={() => handleDeleteReport(report.id)}>Delete</button>
                      </div>
                    </div>
                  </article>
                ))}
              </div>
            ) : (
              <div className="empty-state">
                <div className="empty-icon">📚</div>
                <p>No patient EMR records match your filter criteria.</p>
              </div>
            )}
          </section>
        )}

        {/* --- TAB 12: PATIENT SELF-SERVICE PORTAL --- */}
        {activeTab === 'portal' && (
          <section className="panel">
            <div className="panel-header">
              <h2>Patient Self-Service Portal</h2>
              <span className="muted">View Health Records & Export FHIR R4 Bundle</span>
            </div>

            <div style={{ display: 'flex', gap: '8px', margin: '14px 0' }}>
              <input
                type="text"
                placeholder="Enter your Patient ID (e.g. PAT-2026-8941)"
                value={portalSearchId}
                onChange={(e) => setPortalSearchId(e.target.value)}
                style={{ flex: 1, padding: '10px 14px', borderRadius: '6px', border: '1px solid #cbd5e1' }}
              />
              <button className="primary-btn" onClick={() => handleFetchFhirExport(portalSearchId)}>Download FHIR Bundle</button>
            </div>

            {fhirJsonView && (
              <div style={{ background: '#0f172a', color: '#38bdf8', padding: '16px', borderRadius: '8px', overflowX: 'auto', fontSize: '0.85rem' }}>
                <h3>FHIR R4 JSON Export Collection</h3>
                <pre>{JSON.stringify(fhirJsonView, null, 2)}</pre>
              </div>
            )}
          </section>
        )}
      </main>

      {/* --- PRINTABLE HOSPITAL EMR REPORT MODAL --- */}
      {selectedReport && (
        <div className="modal-overlay" onClick={() => setSelectedReport(null)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="hospital-header-print">
              <div>
                <h2>{hospitalName.toUpperCase()}</h2>
                <p>Clinical EMR Summary & Patient Handover Report</p>
                <p style={{ fontSize: '0.78rem', marginTop: '2px' }}>Facility ID: STJ-89420 • EMR Sync: Active</p>
              </div>
              <button className="modal-close-btn" onClick={() => setSelectedReport(null)}>✕</button>
            </div>

            <div className="modal-body">
              <table className="print-table">
                <tbody>
                  <tr>
                    <th>Patient ID</th>
                    <td><strong>{selectedReport.patient_id || 'PAT-2026-1001'}</strong></td>
                    <th>Patient Name</th>
                    <td><strong>{selectedReport.patient_name || 'Unspecified'}</strong></td>
                  </tr>
                  <tr>
                    <th>Age / Gender</th>
                    <td>{selectedReport.age && selectedReport.gender ? `${selectedReport.age} / ${selectedReport.gender}` : '—'}</td>
                    <th>Room / Bed</th>
                    <td>{selectedReport.room_number || 'Ward 1'}</td>
                  </tr>
                  <tr>
                    <th>Department</th>
                    <td>{selectedReport.department || 'General Medicine'}</td>
                    <th>Triage Level</th>
                    <td><strong>{selectedReport.triage_level || 'Routine'}</strong></td>
                  </tr>
                  <tr>
                    <th>ICD-10 Code</th>
                    <td><strong style={{ color: '#047857' }}>{selectedReport.icd10_code || 'R50.9'}</strong></td>
                    <th>Attending Doctor</th>
                    <td>{selectedReport.attending_physician || 'Dr. N. Patel'}</td>
                  </tr>
                </tbody>
              </table>

              {selectedReport.clinical_flags?.length > 0 && (
                <div style={{ margin: '10px 0' }}>
                  <h4 style={{ margin: '0 0 6px', color: '#b91c1c' }}>Clinical Safety Flags</h4>
                  <div className="flags-wrap">
                    {selectedReport.clinical_flags.map((flag, idx) => (
                      <span key={idx} className="flag-chip">{flag}</span>
                    ))}
                  </div>
                </div>
              )}

              <div>
                <h4 style={{ margin: '14px 0 6px', color: '#0f172a' }}>Clinical Narrative Note</h4>
                <div className="raw-text-box">{selectedReport.report_text}</div>
              </div>

              <div className="entity-groups">
                <div className="entity-box">
                  <h3>Diagnoses</h3>
                  <div className="badge-list">
                    {selectedReport.diagnoses?.length
                      ? selectedReport.diagnoses.map((item, idx) => <span key={idx} className="badge danger">{item}</span>)
                      : <span className="badge muted">None</span>}
                  </div>
                </div>

                <div className="entity-box">
                  <h3>Symptoms</h3>
                  <div className="badge-list">
                    {selectedReport.symptoms?.length
                      ? selectedReport.symptoms.map((item, idx) => <span key={idx} className="badge warning">{item}</span>)
                      : <span className="badge muted">None</span>}
                  </div>
                </div>

                <div className="entity-box">
                  <h3>Medications & Dosages</h3>
                  <div className="badge-list">
                    {selectedReport.medications?.length
                      ? selectedReport.medications.map((item, idx) => <span key={idx} className="badge primary">{item}</span>)
                      : <span className="badge muted">None</span>}
                    {selectedReport.dosages?.map((item, idx) => <span key={`dos-${idx}`} className="badge info">{item}</span>)}
                  </div>
                </div>

                <div className="entity-box">
                  <h3>Drug Allergies</h3>
                  <div className="badge-list">
                    {selectedReport.allergies?.length
                      ? selectedReport.allergies.map((item, idx) => <span key={idx} className="badge purple">{item}</span>)
                      : <span className="badge muted">None</span>}
                  </div>
                </div>
              </div>

              <div className="signature-block">
                <div>
                  <div className="signature-line"></div>
                  <span className="muted" style={{ fontSize: '0.8rem' }}>Attending Physician Signature & Stamp</span>
                </div>
                <div style={{ textAlign: 'right' }}>
                  <span className="muted" style={{ fontSize: '0.8rem' }}>Date: {new Date().toLocaleDateString()}</span>
                </div>
              </div>
            </div>

            <div className="modal-actions">
              <button className="secondary-btn" onClick={() => shareEmail(selectedReport)}>📧 Share via Email</button>
              <button className="secondary-btn" onClick={() => setSelectedReport(null)}>Close</button>
              <button className="primary-btn" onClick={() => window.print()}>🖨️ Print / Save PDF</button>
            </div>
          </div>
        </div>
      )}

      {/* --- ADD PATIENT MODAL --- */}
      {showAddPatientModal && (
        <div className="modal-overlay" onClick={() => setShowAddPatientModal(false)}>
          <div className="modal-content" onClick={e => e.stopPropagation()}>
            <div className="modal-header">
              <h2>Register New Patient</h2>
              <button className="modal-close-btn" onClick={() => setShowAddPatientModal(false)}>✕</button>
            </div>
            <form onSubmit={handleAddPatientSubmit} className="modal-body auth-form">
              <label className="field">
                <span>Full Name *</span>
                <input type="text" value={newPatient.name} onChange={e => setNewPatient({...newPatient, name: e.target.value})} required />
              </label>
              <div style={{ display: 'flex', gap: '10px' }}>
                <label className="field" style={{ flex: 1 }}>
                  <span>Age</span>
                  <input type="text" value={newPatient.age} onChange={e => setNewPatient({...newPatient, age: e.target.value})} placeholder="35" required />
                </label>
                <label className="field" style={{ flex: 1 }}>
                  <span>Gender</span>
                  <select value={newPatient.gender} onChange={e => setNewPatient({...newPatient, gender: e.target.value})}>
                    <option value="Male">Male</option>
                    <option value="Female">Female</option>
                    <option value="Other">Other</option>
                  </select>
                </label>
              </div>
              <label className="field">
                <span>Contact Phone</span>
                <input type="text" value={newPatient.phone} onChange={e => setNewPatient({...newPatient, phone: e.target.value})} placeholder="+1-555-0192" required />
              </label>
              <label className="field">
                <span>Known Allergies (comma separated)</span>
                <input type="text" value={newPatient.allergies} onChange={e => setNewPatient({...newPatient, allergies: e.target.value})} placeholder="Penicillin, Sulfa" />
              </label>
              <div className="modal-actions">
                <button type="button" className="secondary-btn" onClick={() => setShowAddPatientModal(false)}>Cancel</button>
                <button type="submit" className="primary-btn">Register Patient</button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* --- ADD APPOINTMENT MODAL --- */}
      {showAddApptModal && (
        <div className="modal-overlay" onClick={() => setShowAddApptModal(false)}>
          <div className="modal-content" onClick={e => e.stopPropagation()}>
            <div className="modal-header">
              <h2>Book OPD Appointment</h2>
              <button className="modal-close-btn" onClick={() => setShowAddApptModal(false)}>✕</button>
            </div>
            <form onSubmit={handleAddApptSubmit} className="modal-body auth-form">
              <label className="field">
                <span>Patient ID</span>
                <input type="text" value={newAppt.patient_id} onChange={e => setNewAppt({...newAppt, patient_id: e.target.value})} placeholder="PAT-2026-1001" required />
              </label>
              <label className="field">
                <span>Patient Name</span>
                <input type="text" value={newAppt.patient_name} onChange={e => setNewAppt({...newAppt, patient_name: e.target.value})} placeholder="Alex Johnson" required />
              </label>
              <label className="field">
                <span>Attending Doctor</span>
                <input type="text" value={newAppt.doctor_name} onChange={e => setNewAppt({...newAppt, doctor_name: e.target.value})} required />
              </label>
              <label className="field">
                <span>Department</span>
                <select value={newAppt.department} onChange={e => setNewAppt({...newAppt, department: e.target.value})}>
                  <option value="General Medicine">General Medicine</option>
                  <option value="Cardiology">Cardiology</option>
                  <option value="Orthopedics">Orthopedics</option>
                  <option value="Neurology">Neurology</option>
                </select>
              </label>
              <div className="modal-actions">
                <button type="button" className="secondary-btn" onClick={() => setShowAddApptModal(false)}>Cancel</button>
                <button type="submit" className="primary-btn">Issue Token & Book</button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* --- ADD LAB ORDER MODAL --- */}
      {showAddLabModal && (
        <div className="modal-overlay" onClick={() => setShowAddLabModal(false)}>
          <div className="modal-content" onClick={e => e.stopPropagation()}>
            <div className="modal-header">
              <h2>Order Pathology Lab Test</h2>
              <button className="modal-close-btn" onClick={() => setShowAddLabModal(false)}>✕</button>
            </div>
            <form onSubmit={handleAddLabOrderSubmit} className="modal-body auth-form">
              <label className="field">
                <span>Patient ID</span>
                <input type="text" value={newLabOrder.patient_id} onChange={e => setNewLabOrder({...newLabOrder, patient_id: e.target.value})} required />
              </label>
              <label className="field">
                <span>Patient Name</span>
                <input type="text" value={newLabOrder.patient_name} onChange={e => setNewLabOrder({...newLabOrder, patient_name: e.target.value})} required />
              </label>
              <label className="field">
                <span>Test Name</span>
                <input type="text" value={newLabOrder.test_name} onChange={e => setNewLabOrder({...newLabOrder, test_name: e.target.value})} required />
              </label>
              <div className="modal-actions">
                <button type="button" className="secondary-btn" onClick={() => setShowAddLabModal(false)}>Cancel</button>
                <button type="submit" className="primary-btn">Submit Order</button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* --- ENTER LAB RESULT MODAL --- */}
      {selectedLabResultModal && (
        <div className="modal-overlay" onClick={() => setSelectedLabResultModal(null)}>
          <div className="modal-content" onClick={e => e.stopPropagation()}>
            <div className="modal-header">
              <h2>Enter Lab Result ({selectedLabResultModal.test_name})</h2>
              <button className="modal-close-btn" onClick={() => setSelectedLabResultModal(null)}>✕</button>
            </div>
            <form onSubmit={handleSaveLabResultSubmit} className="modal-body auth-form">
              <label className="field">
                <span>Result Value</span>
                <input type="text" value={labResultInput.result_value} onChange={e => setLabResultInput({...labResultInput, result_value: e.target.value})} placeholder="e.g. Glucose 150 mg/dL" required />
              </label>
              <label className="field">
                <span>Normal Reference Range</span>
                <input type="text" value={labResultInput.normal_range} onChange={e => setLabResultInput({...labResultInput, normal_range: e.target.value})} placeholder="70-99 mg/dL" />
              </label>
              <label className="field">
                <span>Abnormal Flag</span>
                <select value={labResultInput.flag} onChange={e => setLabResultInput({...labResultInput, flag: e.target.value})}>
                  <option value="NORMAL">NORMAL</option>
                  <option value="HIGH">HIGH</option>
                  <option value="LOW">LOW</option>
                  <option value="CRITICAL">CRITICAL</option>
                </select>
              </label>
              <div className="modal-actions">
                <button type="button" className="secondary-btn" onClick={() => setSelectedLabResultModal(null)}>Cancel</button>
                <button type="submit" className="primary-btn">Save Result</button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* --- ADD RX MODAL --- */}
      {showAddRxModal && (
        <div className="modal-overlay" onClick={() => setShowAddRxModal(false)}>
          <div className="modal-content" onClick={e => e.stopPropagation()}>
            <div className="modal-header">
              <h2>Log Medication Prescription</h2>
              <button className="modal-close-btn" onClick={() => setShowAddRxModal(false)}>✕</button>
            </div>
            <form onSubmit={handleAddRxSubmit} className="modal-body auth-form">
              <label className="field">
                <span>Patient ID</span>
                <input type="text" value={newRx.patient_id} onChange={e => setNewRx({...newRx, patient_id: e.target.value})} required />
              </label>
              <label className="field">
                <span>Patient Name</span>
                <input type="text" value={newRx.patient_name} onChange={e => setNewRx({...newRx, patient_name: e.target.value})} required />
              </label>
              <label className="field">
                <span>Medication Name</span>
                <input type="text" value={newRx.medication_name} onChange={e => setNewRx({...newRx, medication_name: e.target.value})} required />
              </label>
              <label className="field">
                <span>Dosage & Frequency</span>
                <input type="text" value={newRx.dosage} onChange={e => setNewRx({...newRx, dosage: e.target.value})} placeholder="500mg Twice Daily" required />
              </label>
              <div className="modal-actions">
                <button type="button" className="secondary-btn" onClick={() => setShowAddRxModal(false)}>Cancel</button>
                <button type="submit" className="primary-btn">Save Prescription</button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* --- MANAGING BED ASSIGNMENT MODAL --- */}
      {showBedAssignModal && (
        <div className="modal-overlay" onClick={() => setShowBedAssignModal(null)}>
          <div className="modal-content" onClick={e => e.stopPropagation()}>
            <div className="modal-header">
              <h2>Manage Bed {showBedAssignModal.bed_id} ({showBedAssignModal.ward})</h2>
              <button className="modal-close-btn" onClick={() => setShowBedAssignModal(null)}>✕</button>
            </div>
            <form onSubmit={handleBedAssignSubmit} className="modal-body auth-form">
              <label className="field">
                <span>Patient ID</span>
                <input type="text" value={bedAssignInput.patient_id} onChange={e => setBedAssignInput({...bedAssignInput, patient_id: e.target.value})} placeholder="PAT-2026-XXXX" />
              </label>
              <label className="field">
                <span>Patient Name</span>
                <input type="text" value={bedAssignInput.patient_name} onChange={e => setBedAssignInput({...bedAssignInput, patient_name: e.target.value})} placeholder="Occupant Name" />
              </label>
              <label className="field">
                <span>Bed Status</span>
                <select value={bedAssignInput.status} onChange={e => setBedAssignInput({...bedAssignInput, status: e.target.value})}>
                  <option value="Occupied">Occupied</option>
                  <option value="Available">Available</option>
                  <option value="Cleaning">Cleaning</option>
                  <option value="Reserved">Reserved</option>
                </select>
              </label>
              <div className="modal-actions">
                <button type="button" className="secondary-btn" onClick={() => setShowBedAssignModal(null)}>Cancel</button>
                <button type="submit" className="primary-btn">Update Bed Map</button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* --- ADD INVOICE MODAL --- */}
      {showAddInvoiceModal && (
        <div className="modal-overlay" onClick={() => setShowAddInvoiceModal(false)}>
          <div className="modal-content" onClick={e => e.stopPropagation()}>
            <div className="modal-header">
              <h2>Generate Billing Invoice</h2>
              <button className="modal-close-btn" onClick={() => setShowAddInvoiceModal(false)}>✕</button>
            </div>
            <form onSubmit={handleAddInvoiceSubmit} className="modal-body auth-form">
              <label className="field">
                <span>Patient ID</span>
                <input type="text" value={newInvoice.patient_id} onChange={e => setNewInvoice({...newInvoice, patient_id: e.target.value})} required />
              </label>
              <label className="field">
                <span>Patient Name</span>
                <input type="text" value={newInvoice.patient_name} onChange={e => setNewInvoice({...newInvoice, patient_name: e.target.value})} required />
              </label>
              <div style={{ display: 'flex', gap: '10px' }}>
                <label className="field" style={{ flex: 1 }}>
                  <span>Consultation ($)</span>
                  <input type="number" value={newInvoice.consultation_fee} onChange={e => setNewInvoice({...newInvoice, consultation_fee: parseFloat(e.target.value) || 0})} />
                </label>
                <label className="field" style={{ flex: 1 }}>
                  <span>Lab Fee ($)</span>
                  <input type="number" value={newInvoice.lab_fee} onChange={e => setNewInvoice({...newInvoice, lab_fee: parseFloat(e.target.value) || 0})} />
                </label>
              </div>
              <div className="modal-actions">
                <button type="button" className="secondary-btn" onClick={() => setShowAddInvoiceModal(false)}>Cancel</button>
                <button type="submit" className="primary-btn">Generate Invoice</button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* --- ADD STAFF MODAL --- */}
      {showAddStaffModal && (
        <div className="modal-overlay" onClick={() => setShowAddStaffModal(false)}>
          <div className="modal-content" onClick={e => e.stopPropagation()}>
            <div className="modal-header">
              <h2>Add Staff Member</h2>
              <button className="modal-close-btn" onClick={() => setShowAddStaffModal(false)}>✕</button>
            </div>
            <form onSubmit={handleAddStaffSubmit} className="modal-body auth-form">
              <label className="field">
                <span>Staff Name</span>
                <input type="text" value={newStaff.name} onChange={e => setNewStaff({...newStaff, name: e.target.value})} required />
              </label>
              <label className="field">
                <span>Role</span>
                <input type="text" value={newStaff.role} onChange={e => setNewStaff({...newStaff, role: e.target.value})} required />
              </label>
              <label className="field">
                <span>Shift</span>
                <select value={newStaff.shift} onChange={e => setNewStaff({...newStaff, shift: e.target.value})}>
                  <option value="Morning">Morning</option>
                  <option value="Evening">Evening</option>
                  <option value="Night">Night</option>
                  <option value="On-Call">On-Call</option>
                </select>
              </label>
              <div className="modal-actions">
                <button type="button" className="secondary-btn" onClick={() => setShowAddStaffModal(false)}>Cancel</button>
                <button type="submit" className="primary-btn">Save Staff</button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* --- ADD SUPPLY MODAL --- */}
      {showAddSupplyModal && (
        <div className="modal-overlay" onClick={() => setShowAddSupplyModal(false)}>
          <div className="modal-content" onClick={e => e.stopPropagation()}>
            <div className="modal-header">
              <h2>Add Inventory Item</h2>
              <button className="modal-close-btn" onClick={() => setShowAddSupplyModal(false)}>✕</button>
            </div>
            <form onSubmit={handleAddSupplySubmit} className="modal-body auth-form">
              <label className="field">
                <span>Item Name</span>
                <input type="text" value={newSupply.item_name} onChange={e => setNewSupply({...newSupply, item_name: e.target.value})} required />
              </label>
              <label className="field">
                <span>Quantity</span>
                <input type="number" value={newSupply.quantity} onChange={e => setNewSupply({...newSupply, quantity: parseInt(e.target.value) || 0})} required />
              </label>
              <div className="modal-actions">
                <button type="button" className="secondary-btn" onClick={() => setShowAddSupplyModal(false)}>Cancel</button>
                <button type="submit" className="primary-btn">Save Supply Item</button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* --- CRITICAL ALERTS MODAL --- */}
      {showCriticalAlertsModal && (
        <div className="modal-overlay" onClick={() => setShowCriticalAlertsModal(false)}>
          <div className="modal-content" onClick={e => e.stopPropagation()}>
            <div className="modal-header">
              <h2>⚠️ Active Hospital Critical Alerts</h2>
              <button className="modal-close-btn" onClick={() => setShowCriticalAlertsModal(false)}>✕</button>
            </div>
            <div className="modal-body">
              <div className="error-banner" style={{ marginBottom: '8px' }}>
                🚨 EMERGENCY TRIAGE: PAT-2026-8941 - Acute Myocardial Infarction (ICU-01)
              </div>
              <div className="error-banner" style={{ marginBottom: '8px' }}>
                ⚠️ DRUG INTERACTION ALERT: Dual Anticoagulation/Antiplatelet Therapy flagged for Patient Alex Johnson.
              </div>
              <div className="error-banner" style={{ marginBottom: '8px' }}>
                🧪 ABNORMAL LAB RESULT: Glucose 145 mg/dL (HIGH) for Patient Sarah Connor.
              </div>
            </div>
          </div>
        </div>
      )}

      {/* --- PASSWORD RESET MODAL --- */}
      {showResetModal && (
        <div className="modal-overlay" onClick={() => setShowResetModal(false)}>
          <div className="modal-content" onClick={e => e.stopPropagation()}>
            <div className="modal-header">
              <h2>🔑 Reset Security Password</h2>
              <button className="modal-close-btn" onClick={() => setShowResetModal(false)}>✕</button>
            </div>
            <form onSubmit={handlePasswordResetSubmit} className="modal-body auth-form">
              <label className="field">
                <span>Staff Username</span>
                <input type="text" value={resetUsername} onChange={e => setResetUsername(e.target.value)} required />
              </label>
              <label className="field">
                <span>New Password</span>
                <input type="password" value={resetNewPassword} onChange={e => setResetNewPassword(e.target.value)} required />
              </label>
              <div className="modal-actions">
                <button type="button" className="secondary-btn" onClick={() => setShowResetModal(false)}>Cancel</button>
                <button type="submit" className="primary-btn">Update Password</button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* --- ACTIVITY LOGS MODAL --- */}
      {showLogsModal && (
        <div className="modal-overlay" onClick={() => setShowLogsModal(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h2>User Activity Audit Logs ({username})</h2>
              <button className="modal-close-btn" onClick={() => setShowLogsModal(false)}>✕</button>
            </div>
            <div className="modal-body">
              {activityLogs.length ? (
                <div className="rank-list">
                  {activityLogs.map((log) => (
                    <div key={log.id} className="rank-item" style={{ flexDirection: 'column', alignItems: 'flex-start', gap: '4px' }}>
                      <div style={{ display: 'flex', justifyContent: 'space-between', width: '100%' }}>
                        <strong>{log.action}</strong>
                        <span className="muted" style={{ fontSize: '0.78rem' }}>{new Date(log.timestamp).toLocaleString()}</span>
                      </div>
                      <p style={{ margin: 0, fontSize: '0.88rem', color: '#334155' }}>{log.details}</p>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="muted">No activity logs recorded yet.</p>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default App
