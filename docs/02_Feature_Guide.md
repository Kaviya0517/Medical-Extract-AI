# MediExtract AI Feature Guide

## Purpose

MediExtract AI is a hospital operations and clinical-note support application. Staff can capture clinical notes, review extracted information, manage operational queues, and retrieve reports from the dashboard.

This guide describes the features currently present in the application. It is not a substitute for local clinical, privacy, billing, or records-management policy.

## Getting Started

1. Open the MediExtract portal and sign in with a staff account, or register an account if registration is enabled for your deployment.
2. After sign-in, use the left navigation to open a work area. The summary indicators across the top link to patient, triage, bed, and alert views.
3. Use the facility-name control to set the hospital name shown in the workspace and reports. Use the theme control to switch between light and dark display.
4. The database indicator shows which configured storage mode is active, such as MongoDB Atlas or local SQLite.

The application requires its API service to be running. If sign-in or registration reports that the hospital server cannot be reached, check that the backend is available at the configured API address.

## Clinical Workflows

### 1. Clinical Intake and Emergency Triage

Use this area to analyze a physician note, handover, or emergency narrative.

1. Enter the patient ID, room or bed, admission status, and attending clinician where known.
2. Add a note by typing or pasting text, loading the sample note, uploading a `.txt` or `.pdf` file, or using browser voice dictation where supported.
3. Select **Process Triage & Save to Hospital Database**.
4. Review the returned triage level, risk, clinical flags, patient details, department, ICD-10 code, diagnoses, symptoms, medications, dosages, tests, and allergies.

For a signed-in user, successfully processed reports are saved to the EMR archive and included in analytics. A duplicate-note warning may appear if similar report text already exists. The confidence score describes the extraction/classification result; it is not a measure of clinical certainty.

Voice dictation depends on browser speech-recognition support and stops automatically after approximately one minute. File parsing and extraction can fail if the service cannot read the file.

### 2. Patient Directory

Use the directory to register patients and review their listed demographics and history.

- Select **Register New Patient** and enter the requested name, age, gender, contact details, and known allergies.
- Select **Start Clinical Intake** on a patient record to carry that patient's ID into the intake workflow.

Patient records are saved through the backend. Verify identity and clinical details against the hospital's approved source before use.

### 3. OPD Appointments and Queue

Use this area to book outpatient visits and track their queue status.

- Select **Book OPD Appointment**, enter the patient ID and name, clinician, and department, then issue the booking.
- The system assigns a queue token.
- For a booked visit, select **Call Patient** to move it to **In-Consultation**. Select **Complete Visit** when the consultation is finished.

Appointments are stored through the backend. The current booking form uses the application's configured appointment date and time defaults.

### 4. Pathology and Diagnostic Laboratory

Use this area to create test orders and record results.

- Select **Order Lab Test** and provide the patient ID, patient name, and test name.
- When results are available, open **Enter / Edit Result** and enter the result, reference range, and flag.
- Result flags include **NORMAL**, **HIGH**, **LOW**, and **CRITICAL**.

Orders and results are saved through the backend. The application displays the entered flag and result; staff remain responsible for interpreting and escalating results under hospital policy.

### 5. Pharmacy and Dispensary

Use this area to record prescriptions and track dispensing.

- Select **Log Prescription** and enter the patient, medication, dosage, and schedule details.
- A prescription begins as pending dispense. Select **Dispense Drug** after dispensing to update its status.
- In the interaction checker, enter medication names separated by commas and select **Check Interactions**. Review any returned alerts before proceeding.

Interaction results are decision support only and should be checked against an authoritative clinical reference and the patient's complete medication history.

### 6. Bed and ICU Map

Use the map to view and change the displayed bed assignment. Each bed shows its ward, occupant, patient ID, attending clinician, and status. Available statuses include **Occupied**, **Available**, **Cleaning**, and **Reserved**.

Select **Manage Bed Assignment** to edit the occupant and status. Important: the current bed list is sample data stored in browser memory. Changes are not persisted by the backend and are lost when the page is reloaded. Do not use this map as an authoritative live bed-management system.

## Hospital Operations

### 7. Billing and Insurance Claims

Use this area to create invoices and review payment and insurance statuses.

- Select **Generate New Invoice**, provide patient details and charge amounts, then create the invoice.
- Review consultation, lab, pharmacy, and room charges, total amount, payment status, and insurance claim status in the invoice list.
- Select **Collect Payment** on a pending invoice to mark the payment as collected.

Invoices and status changes are stored through the backend. The current payment action records a status update; it is not a payment-gateway transaction. Verify amounts and claim information using the hospital's billing process.

### 8. Staff Duty Roster

Use the roster to add and review staff members, roles, departments, shifts, and contact details.

- Select **Add Staff Member**, enter the staff details, and save the roster entry.
- Shift options include morning, evening, night, and on-call.

Roster records are stored through the backend. The roster is an information list and does not itself schedule, authorize, or verify staff coverage.

### 9. Supplies and Stock

Use inventory to record supply quantities and identify items at or below their reorder level.

- Select **Add Inventory Item** and enter the item name and quantity; the form also carries category, reorder level, unit cost, and vendor details.
- Items at or below the reorder level are marked **Low Stock Reorder**; other items are marked **Stock Normal**.

Inventory records are stored through the backend. Confirm counts against physical stock before ordering.

### 10. Command Center Analytics

Use the analytics view for an aggregate picture of recorded activity, including:

- Department workload distribution.
- Triage-level distribution.
- Frequently recorded diagnoses.
- Frequently recorded medications.

Analytics depend on data already recorded in the system. They are operational summaries, not forecasts or clinical recommendations.

### 11. EMR Archive and Handover

Use the archive to find and review saved clinical reports.

- Search by patient-related text and filter by department, triage level, or admission status.
- Select **View / Print EMR** to review the report and print it or save it as a PDF.
- Select **Email** to prepare a handover message in the device's configured email application.
- Download the displayed results as CSV or JSON.
- Select **Delete** to remove a report after confirming the prompt.

The archive is populated by reports saved from clinical intake. Email sharing opens a prefilled email draft; it does not send the message automatically. Follow local policy before printing, exporting, emailing, or deleting patient information.

### 12. Patient Portal and FHIR Export

This staff-dashboard utility looks up a patient record by patient ID and requests a FHIR R4 bundle. When available, the returned JSON is displayed on screen for review and download/inspection.

This is not a separate authenticated patient login experience. A bundle may be unavailable when the patient ID has no matching record.

## Account, Facility, and Audit Controls

- **Staff sign-in and registration:** authenticate a staff account to use the dashboard. The role selector records the displayed clinical role; follow your organization's account-provisioning and access-control policy.
- **Password reset:** the current reset form asks for a staff username and a new password, without an additional verification step. Restrict access to this function and use an approved identity-verification process in any real deployment.
- **Facility name:** update the hospital name shown in the application. Signed-in changes are sent to the backend.
- **Activity logs:** select **Logs** in the sidebar to review recorded user actions and timestamps when logs are available.
- **Database status:** the indicator reports the active storage mode. Local SQLite mode is useful for development; configure and secure an approved database for real patient information.
- **Sign out:** use **Exit** to end the current browser session and return to the portal.

## Clinical and Data-Handling Notes

- AI extraction, triage labels, risk indicators, and ICD-10 suggestions must be reviewed by qualified staff before being used in care or entered as a final clinical decision.
- The critical-alert dialog currently contains demonstration examples; it is not a live alert feed.
- The bed map is currently in-memory sample data and is not a live census.
- Before using real patient information, configure production-grade identity verification, access controls, audit procedures, encryption, backups, and privacy safeguards appropriate to your organization and jurisdiction.