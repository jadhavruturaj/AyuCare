/**
 * आयुCare (AyuCare) - Symptom Checker Module
 */

document.addEventListener("DOMContentLoaded", () => {
  const symptomSelect = document.getElementById("symptom-select");
  const symptomForm = document.getElementById("symptom-check-form");
  const reportContainer = document.getElementById("symptom-report-container");
  const categoryFilters = document.getElementById("category-filter-chips");

  let allSymptoms = [];

  // Load all 50 symptoms from API
  loadSymptomsList();

  async function loadSymptomsList() {
    try {
      const data = await AyuAPI.getSymptoms();
      if (data.success && data.symptoms) {
        allSymptoms = data.symptoms;
        populateSymptomDropdown(allSymptoms);
        buildCategoryChips(allSymptoms);
      }
    } catch (err) {
      console.error("Failed to load symptoms:", err);
      showToast("Unable to load symptoms dataset from server.", "error");
    }
  }

  function populateSymptomDropdown(symptoms) {
    if (!symptomSelect) return;
    symptomSelect.innerHTML = `<option value="">-- Choose or search a symptom (${symptoms.length} available) --</option>`;
    symptoms.forEach(s => {
      const opt = document.createElement("option");
      opt.value = s.name;
      opt.textContent = `${s.name} (${s.category})`;
      symptomSelect.appendChild(opt);
    });
  }

  function buildCategoryChips(symptoms) {
    if (!categoryFilters) return;
    const categories = ["All", ...new Set(symptoms.map(s => s.category))];
    categoryFilters.innerHTML = "";

    categories.forEach(cat => {
      const btn = document.createElement("button");
      btn.type = "button";
      btn.className = `chip-btn ${cat === "All" ? "active" : ""}`;
      btn.textContent = cat;
      btn.addEventListener("click", () => {
        categoryFilters.querySelectorAll(".chip-btn").forEach(b => b.classList.remove("active"));
        btn.classList.add("active");
        if (cat === "All") {
          populateSymptomDropdown(allSymptoms);
        } else {
          const filtered = allSymptoms.filter(s => s.category === cat);
          populateSymptomDropdown(filtered);
        }
      });
      categoryFilters.appendChild(btn);
    });
  }

  // Handle Form Submission
  if (symptomForm) {
    symptomForm.addEventListener("submit", async (e) => {
      e.preventDefault();

      const symptomName = symptomSelect ? symptomSelect.value : "";
      const duration = document.getElementById("duration-input")?.value.trim();
      const severity = document.querySelector('input[name="severity"]:checked')?.value || "Mild";
      const description = document.getElementById("description-input")?.value.trim();
      const additional = document.getElementById("additional-input")?.value.trim();
      const submitBtn = document.getElementById("submit-symptom-btn");

      if (!symptomName) {
        showToast("Please select your primary symptom from the list.", "warning");
        return;
      }

      if (!duration) {
        showToast("Please enter how long you have experienced this symptom.", "warning");
        return;
      }

      // UI Loading state
      const originalText = submitBtn.innerHTML;
      submitBtn.disabled = true;
      submitBtn.innerHTML = `<i class="fa-solid fa-spinner fa-spin"></i> Analyzing Clinical Guidance...`;

      try {
        const res = await AyuAPI.checkSymptoms({
          symptom_name: symptomName,
          duration: duration,
          severity: severity,
          description: description,
          additional_details: additional
        });

        if (res.success && res.report) {
          renderReport(res.report);
          showToast("Guidance report generated successfully.", "success");
          // Smooth scroll to report
          reportContainer.scrollIntoView({ behavior: "smooth", block: "start" });
        } else {
          showToast(res.message || "Failed to analyze symptoms.", "error");
        }
      } catch (err) {
        showToast(err.message || "An error occurred during symptom triage.", "error");
      } finally {
        submitBtn.disabled = false;
        submitBtn.innerHTML = originalText;
      }
    });
  }

  // Render Full Clinical Guidance Report
  function renderReport(report) {
    if (!reportContainer) return;

    const sub = report.submitted;
    const isEmerg = report.is_emergency;
    const spec = report.recommended_specialist;

    let emergencyAlertHtml = "";
    if (isEmerg) {
      emergencyAlertHtml = `
        <div class="emergency-alert-box">
          <i class="fa-solid fa-triangle-exclamation"></i>
          <div>
            <h3>EMERGENCY MEDICAL WARNING</h3>
            <p>${report.emergency_details?.emergency_prompt || "Your reported symptoms show critical red-flag signs. Please contact emergency services (112 / 108 / 911) or visit the nearest hospital emergency room immediately."}</p>
          </div>
        </div>
      `;
    }

    let homeCareHtml = "";
    if (report.general_home_care) {
      homeCareHtml = `
        <div class="report-card">
          <div class="report-card-title green">
            <i class="fa-solid fa-leaf"></i>
            <span>General Home-Care Guidance (For Mild Symptoms)</span>
          </div>
          <p>${report.general_home_care}</p>
        </div>
      `;
    } else {
      homeCareHtml = `
        <div class="report-card">
          <div class="report-card-title orange">
            <i class="fa-solid fa-stethoscope"></i>
            <span>Professional Evaluation Recommended</span>
          </div>
          <p>Routine home remedies are not clinically advised for this symptom or severity level. Please consult the recommended medical specialist below for an accurate assessment.</p>
        </div>
      `;
    }

    reportContainer.innerHTML = `
      <div class="report-container">
        <div class="report-header">
          <div class="report-title-group">
            <h2>Guidance Report: ${sub.symptom_name}</h2>
            <p>Duration: <strong>${sub.duration}</strong> | Severity: <strong>${sub.severity}</strong></p>
          </div>
          <div class="urgency-badge" style="background:${report.urgency_color}; color:#FFFFFF;">
            <i class="fa-solid fa-bell"></i>
            <span>${report.urgency_badge}</span>
          </div>
        </div>

        <div class="report-body">
          ${emergencyAlertHtml}

          <div class="report-card">
            <div class="report-card-title">
              <i class="fa-solid fa-clipboard-check"></i>
              <span>Preliminary Clinical Guidance</span>
            </div>
            <p>${report.preliminary_guidance}</p>
          </div>

          ${homeCareHtml}

          <div class="report-card">
            <div class="report-card-title orange">
              <i class="fa-solid fa-circle-exclamation"></i>
              <span>Warning Signs & When to Seek Urgent Care</span>
            </div>
            <p>${report.warning_signs}</p>
          </div>

          <div class="specialist-rec-box">
            <div class="specialist-info">
              <div class="specialist-avatar">
                <i class="fa-solid ${spec.icon || 'fa-user-doctor'}"></i>
              </div>
              <div class="specialist-details">
                <h3>Recommended: ${spec.name}</h3>
                <p>${spec.description}</p>
              </div>
            </div>
            <a href="specialists.html?specialty=${encodeURIComponent(spec.name)}" class="btn btn-secondary btn-sm">
              <i class="fa-solid fa-calendar-check"></i>
              <span>Find ${spec.name}</span>
            </a>
          </div>

          <div class="disclaimer-banner">
            <i class="fa-solid fa-shield-halved disclaimer-icon"></i>
            <div class="disclaimer-content">
              <h4>Safety & Limitations Notice</h4>
              <p>${report.disclaimer}</p>
              <p style="margin-top:0.35rem; font-size:0.75rem; color:#8C5300;">Source: ${report.reference_source || 'Evidence-based healthcare guidelines'}</p>
            </div>
          </div>

          <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:1rem; margin-top:0.5rem;">
            <button type="button" class="btn btn-outline btn-sm" onclick="window.print()">
              <i class="fa-solid fa-print"></i> Print / Save Report
            </button>
            <button type="button" class="btn btn-primary btn-sm" onclick="document.getElementById('symptom-check-form').reset(); window.scrollTo({top: 0, behavior: 'smooth'});">
              <i class="fa-solid fa-rotate-left"></i> Check Another Symptom
            </button>
          </div>
        </div>
      </div>
    `;

    reportContainer.style.display = "block";
  }
});
