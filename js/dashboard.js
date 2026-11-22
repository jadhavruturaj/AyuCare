/**
 * आयुCare (AyuCare) - Patient Dashboard Controller
 */

document.addEventListener("DOMContentLoaded", () => {
  // Authentication Guard
  if (!AyuAPI.isAuthenticated()) {
    window.location.href = "login.html";
    return;
  }

  const user = AyuAPI.getUser();
  if (user && user.role !== "patient") {
    window.location.href = "doctor-dashboard.html";
    return;
  }

  // DOM Elements
  const patientNameEl = document.getElementById("patient-display-name");
  const patientEmailEl = document.getElementById("patient-email");
  const patientMobileEl = document.getElementById("patient-mobile");
  const patientAgeEl = document.getElementById("patient-age");
  const patientGenderEl = document.getElementById("patient-gender");

  // Metrics
  const statChecksEl = document.getElementById("stat-total-checks");
  const statConsultsEl = document.getElementById("stat-total-consults");
  const statPendingEl = document.getElementById("stat-pending-consults");

  // Tables / Lists
  const symptomsTableBody = document.getElementById("symptoms-history-tbody");
  const consultsTableBody = document.getElementById("consultations-tbody");

  // Modals & Forms
  const editProfileForm = document.getElementById("patient-edit-profile-form");

  // Sidebar navigation panel switcher
  setupDashboardNav();

  // Load dashboard data
  loadDashboardData();

  async function loadDashboardData() {
    try {
      const data = await AyuAPI.getPatientDashboard();
      if (data.success) {
        populateProfile(data.profile);
        populateMetrics(data.stats);
        populateRecentSymptoms(data.recent_symptoms);
        populateConsultations(data.recent_consultations);
      }
    } catch (err) {
      console.error("Dashboard load failed:", err);
      showToast("Failed to load dashboard data. Please try again.", "error");
    }
  }

  function populateProfile(profile) {
    if (!profile) return;
    if (patientNameEl) patientNameEl.textContent = profile.full_name;
    if (patientEmailEl) patientEmailEl.textContent = profile.email;
    if (patientMobileEl) patientMobileEl.textContent = profile.mobile || "Not specified";
    if (patientAgeEl) patientAgeEl.textContent = profile.age ? `${profile.age} yrs` : "N/A";
    if (patientGenderEl) patientGenderEl.textContent = profile.gender || "Not specified";

    // Pre-populate edit form
    const nameInput = document.getElementById("edit-name");
    const mobileInput = document.getElementById("edit-mobile");
    const ageInput = document.getElementById("edit-age");
    const genderInput = document.getElementById("edit-gender");

    if (nameInput) nameInput.value = profile.full_name;
    if (mobileInput) mobileInput.value = profile.mobile;
    if (ageInput) ageInput.value = profile.age;
    if (genderInput) genderInput.value = profile.gender || "Not Specified";
  }

  function populateMetrics(stats) {
    if (!stats) return;
    if (statChecksEl) statChecksEl.textContent = stats.total_symptom_checks || 0;
    if (statConsultsEl) statConsultsEl.textContent = stats.total_consultations || 0;
    if (statPendingEl) statPendingEl.textContent = stats.pending_consultations || 0;
  }

  function populateRecentSymptoms(symptoms) {
    if (!symptomsTableBody) return;

    if (!symptoms || symptoms.length === 0) {
      symptomsTableBody.innerHTML = `
        <tr>
          <td colspan="5" class="empty-state">
            <i class="fa-solid fa-notes-medical"></i>
            <h4>No Symptom Checks Yet</h4>
            <p>You haven't submitted any symptoms for review yet.</p>
            <a href="symptom-checker.html" class="btn btn-primary btn-sm" style="margin-top:0.5rem;">
              <i class="fa-solid fa-stethoscope"></i> Check Symptoms Now
            </a>
          </td>
        </tr>
      `;
      return;
    }

    symptomsTableBody.innerHTML = symptoms.map(s => {
      const date = new Date(s.created_at).toLocaleDateString("en-IN", {
        day: "numeric", month: "short", year: "numeric"
      });
      const severityClass = s.severity.toLowerCase() === "severe" ? "status-danger" : (s.severity.toLowerCase() === "moderate" ? "status-warning" : "status-success");

      return `
        <tr>
          <td><strong>${s.symptom_name}</strong></td>
          <td>${s.duration}</td>
          <td><span class="status-pill ${s.severity.toLowerCase()}">${s.severity}</span></td>
          <td><i class="fa-solid fa-user-doctor" style="color:var(--primary-blue); margin-right:4px;"></i> ${s.recommended_specialist}</td>
          <td>${date}</td>
        </tr>
      `;
    }).join("");
  }

  function populateConsultations(consultations) {
    if (!consultsTableBody) return;

    if (!consultations || consultations.length === 0) {
      consultsTableBody.innerHTML = `
        <tr>
          <td colspan="5" class="empty-state">
            <i class="fa-solid fa-calendar-xmark"></i>
            <h4>No Consultations Requested</h4>
            <p>You have not requested a consultation with a specialist yet.</p>
            <a href="specialists.html" class="btn btn-secondary btn-sm" style="margin-top:0.5rem;">
              <i class="fa-solid fa-user-doctor"></i> Explore Doctors
            </a>
          </td>
        </tr>
      `;
      return;
    }

    consultsTableBody.innerHTML = consultations.map(c => {
      const statusClass = c.status.toLowerCase();
      const prefDate = c.preferred_date ? c.preferred_date : "Flexible";
      const prefTime = c.preferred_time ? ` (${c.preferred_time})` : "";

      return `
        <tr>
          <td><strong>${c.doctor_name}</strong><br><small style="color:var(--text-secondary);">${c.doctor_specialization}</small></td>
          <td>${prefDate}${prefTime}</td>
          <td><span class="status-pill ${statusClass}">${c.status}</span></td>
          <td>${c.doctor_notes || '<span style="color:var(--text-muted);">Awaiting response</span>'}</td>
          <td>
            <a href="specialists.html" class="btn btn-outline btn-sm">
              <i class="fa-solid fa-eye"></i> View Doctor
            </a>
          </td>
        </tr>
      `;
    }).join("");
  }

  function setupDashboardNav() {
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
      const fullName = document.getElementById("edit-name")?.value.trim();
      const mobile = document.getElementById("edit-mobile")?.value.trim();
      const age = document.getElementById("edit-age")?.value;
      const gender = document.getElementById("edit-gender")?.value;

      try {
        const res = await AyuAPI.updatePatientProfile({
          full_name: fullName,
          mobile: mobile,
          age: age,
          gender: gender
        });

        if (res.success) {
          showToast("Profile updated successfully!", "success");
          // Refresh user in local storage
          const u = AyuAPI.getUser();
          u.full_name = fullName;
          u.mobile = mobile;
          AyuAPI.setUser(u);
          loadDashboardData();
        }
      } catch (err) {
        showToast(err.message || "Failed to update profile.", "error");
      }
    });
  }
});
