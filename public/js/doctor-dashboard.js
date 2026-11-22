/**
 * आयुCare (AyuCare) - Doctor Dashboard Controller
 */

document.addEventListener("DOMContentLoaded", () => {
  // Authentication Guard
  if (!AyuAPI.isAuthenticated()) {
    window.location.href = "doctor-login.html";
    return;
  }

  const user = AyuAPI.getUser();
  if (user && user.role !== "doctor") {
    window.location.href = "dashboard.html";
    return;
  }

  // Profile DOM
  const docNameEl = document.getElementById("doctor-display-name");
  const docSpecEl = document.getElementById("doctor-specialization");
  const docRegEl = document.getElementById("doctor-registration-no");
  const docClinicEl = document.getElementById("doctor-clinic");
  const docStatusBadge = document.getElementById("doctor-status-badge");

  // Metrics DOM
  const statTotalRequests = document.getElementById("stat-doctor-total");
  const statPendingRequests = document.getElementById("stat-doctor-pending");
  const statAcceptedRequests = document.getElementById("stat-doctor-accepted");
  const statCompletedRequests = document.getElementById("stat-doctor-completed");

  // Requests Table
  const requestsTableBody = document.getElementById("doctor-requests-tbody");

  // Modal elements for updating consultation status
  const statusModal = document.getElementById("status-update-modal");
  const statusForm = document.getElementById("status-update-form");
  const modalCloseBtn = document.getElementById("modal-close-btn");
  const modalCancelBtn = document.getElementById("modal-cancel-btn");
  let activeConsultationId = null;

  // Edit profile form
  const editProfileForm = document.getElementById("doctor-edit-profile-form");

  setupDoctorNav();
  loadDoctorData();

  async function loadDoctorData() {
    try {
      const data = await AyuAPI.getDoctorDashboard();
      if (data.success) {
        populateDoctorProfile(data.profile);
        populateDoctorMetrics(data.stats);
        populateConsultationRequests(data.consultations);
      }
    } catch (err) {
      console.error("Doctor dashboard error:", err);
      showToast("Unable to fetch doctor portal data.", "error");
    }
  }

  function populateDoctorProfile(profile) {
    if (!profile) return;
    if (docNameEl) docNameEl.textContent = profile.full_name;
    if (docSpecEl) docSpecEl.textContent = profile.specialization;
    if (docRegEl) docRegEl.textContent = profile.registration_number;
    if (docClinicEl) docClinicEl.textContent = profile.hospital_clinic || "Private Practice";

    if (docStatusBadge) {
      const status = (profile.verification_status || "pending").toLowerCase();
      docStatusBadge.className = `verification-badge ${status}`;
      docStatusBadge.innerHTML = `
        <i class="fa-solid ${status === 'verified' ? 'fa-circle-check' : (status === 'rejected' ? 'fa-circle-xmark' : 'fa-clock')}"></i>
        <span>${status.toUpperCase()}</span>
      `;
    }

    // Populate edit form
    const nameIn = document.getElementById("doc-edit-name");
    const mobileIn = document.getElementById("doc-edit-mobile");
    const bioIn = document.getElementById("doc-edit-bio");
    const expIn = document.getElementById("doc-edit-exp");
    const clinicIn = document.getElementById("doc-edit-clinic");

    if (nameIn) nameIn.value = profile.full_name;
    if (mobileIn) mobileIn.value = profile.mobile;
    if (bioIn) bioIn.value = profile.bio || "";
    if (expIn) expIn.value = profile.experience_years || 0;
    if (clinicIn) clinicIn.value = profile.hospital_clinic || "";
  }

  function populateDoctorMetrics(stats) {
    if (!stats) return;
    if (statTotalRequests) statTotalRequests.textContent = stats.total_requests || 0;
    if (statPendingRequests) statPendingRequests.textContent = stats.pending_requests || 0;
    if (statAcceptedRequests) statAcceptedRequests.textContent = stats.accepted_requests || 0;
    if (statCompletedRequests) statCompletedRequests.textContent = stats.completed_requests || 0;
  }

  function populateConsultationRequests(consultations) {
    if (!requestsTableBody) return;

    if (!consultations || consultations.length === 0) {
      requestsTableBody.innerHTML = `
        <tr>
          <td colspan="6" class="empty-state">
            <i class="fa-solid fa-inbox"></i>
            <h4>No Consultation Requests Yet</h4>
            <p>You do not have any patient appointment or guidance requests at this moment.</p>
          </td>
        </tr>
      `;
      return;
    }

    requestsTableBody.innerHTML = consultations.map(c => {
      const statusClass = c.status.toLowerCase();
      const patientSummary = `
        <strong>${c.patient_name}</strong>
        <div style="font-size:0.78rem; color:var(--text-secondary);">
          ${c.patient_age} yrs, ${c.patient_gender} | ${c.patient_mobile}
        </div>
      `;

      return `
        <tr>
          <td>${patientSummary}</td>
          <td><strong>${c.symptom_summary || 'General health guidance'}</strong><br><small style="color:var(--text-secondary);">${c.notes || 'No extra notes'}</small></td>
          <td>${c.preferred_date || 'Flexible'}<br><small>${c.preferred_time || ''}</small></td>
          <td><span class="status-pill ${statusClass}">${c.status}</span></td>
          <td>${c.doctor_notes || '<span style="color:var(--text-muted);">None provided</span>'}</td>
          <td>
            <button class="btn btn-primary btn-sm action-update-btn" data-id="${c.id}" data-status="${c.status}" data-notes="${escapeHtml(c.doctor_notes || '')}">
              <i class="fa-solid fa-pen-to-square"></i> Manage
            </button>
          </td>
        </tr>
      `;
    }).join("");

    // Attach click events to Manage buttons
    requestsTableBody.querySelectorAll(".action-update-btn").forEach(btn => {
      btn.addEventListener("click", () => {
        activeConsultationId = btn.getAttribute("data-id");
        const currentStatus = btn.getAttribute("data-status");
        const currentNotes = btn.getAttribute("data-notes");

        const statusSelect = document.getElementById("update-status-select");
        const notesInput = document.getElementById("update-notes-input");

        if (statusSelect) statusSelect.value = currentStatus;
        if (notesInput) notesInput.value = currentNotes;

        if (statusModal) statusModal.classList.add("active");
      });
    });
  }

  // Handle Status Update Submission
  if (statusForm) {
    statusForm.addEventListener("submit", async (e) => {
      e.preventDefault();
      if (!activeConsultationId) return;

      const newStatus = document.getElementById("update-status-select")?.value;
      const notes = document.getElementById("update-notes-input")?.value.trim();

      try {
        const res = await AyuAPI.updateConsultationStatus(activeConsultationId, {
          status: newStatus,
          doctor_notes: notes
        });

        if (res.success) {
          showToast(res.message, "success");
          closeModal();
          loadDoctorData();
        }
      } catch (err) {
        showToast(err.message || "Failed to update consultation.", "error");
      }
    });
  }

  // Modal close handlers
  if (modalCloseBtn) modalCloseBtn.addEventListener("click", closeModal);
  if (modalCancelBtn) modalCancelBtn.addEventListener("click", closeModal);
  if (statusModal) {
    statusModal.addEventListener("click", (e) => {
      if (e.target === statusModal) closeModal();
    });
  }

  function closeModal() {
    if (statusModal) statusModal.classList.remove("active");
    activeConsultationId = null;
  }

  function setupDoctorNav() {
    const navButtons = document.querySelectorAll(".dash-nav-btn[data-target]");
    const panels = document.querySelectorAll(".dash-panel");

    navButtons.forEach(btn => {
      btn.addEventListener("click", () => {
        const targetId = btn.getAttribute("data-target");
        navButtons.forEach(b => b.classList.remove("active"));
        panels.forEach(p => p.classList.remove("active"));

        btn.classList.add("active");
        const targetPanel = document.getElementById(targetId);
        if (targetPanel) targetPanel.classList.add("active");
      });
    });
  }

  // Profile Edit Submission
  if (editProfileForm) {
    editProfileForm.addEventListener("submit", async (e) => {
      e.preventDefault();
      const fullName = document.getElementById("doc-edit-name")?.value.trim();
      const mobile = document.getElementById("doc-edit-mobile")?.value.trim();
      const bio = document.getElementById("doc-edit-bio")?.value.trim();
      const exp = document.getElementById("doc-edit-exp")?.value;
      const clinic = document.getElementById("doc-edit-clinic")?.value.trim();

      try {
        const res = await AyuAPI.updateDoctorProfile({
          full_name: fullName,
          mobile: mobile,
          bio: bio,
          experience_years: exp,
          hospital_clinic: clinic
        });

        if (res.success) {
          showToast("Doctor profile updated successfully!", "success");
          loadDoctorData();
        }
      } catch (err) {
        showToast(err.message || "Failed to update profile.", "error");
      }
    });
  }

  function escapeHtml(text) {
    return text.replace(/"/g, "&quot;").replace(/'/g, "&#039;");
  }
});
