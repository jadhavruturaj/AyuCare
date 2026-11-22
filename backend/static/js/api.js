/**
 * आयुCare (AyuCare) - Central API & Auth Manager
 */

const API_PORT = 5001;
const API_BASE = window.location.port === "5500" || window.location.port === "3000" || window.location.port === "8080"
  ? `http://localhost:${API_PORT}/api`
  : "/api";

const AyuAPI = {
  // Authentication State
  getToken() {
    return localStorage.getItem("ayucare_token");
  },

  setToken(token) {
    if (token) localStorage.setItem("ayucare_token", token);
    else localStorage.removeItem("ayucare_token");
  },

  getUser() {
    const raw = localStorage.getItem("ayucare_user");
    try {
      return raw ? JSON.parse(raw) : null;
    } catch {
      return null;
    }
  },

  setUser(user) {
    if (user) localStorage.setItem("ayucare_user", JSON.stringify(user));
    else localStorage.removeItem("ayucare_user");
  },

  isAuthenticated() {
    return !!this.getToken() && !!this.getUser();
  },

  getRole() {
    const user = this.getUser();
    return user ? user.role : null;
  },

  logout() {
    this.setToken(null);
    this.setUser(null);
    window.location.href = "login.html";
  },

  // Base Request Method
  async request(endpoint, options = {}) {
    const url = endpoint.startsWith("http") ? endpoint : `${API_BASE}${endpoint}`;
    const headers = {
      "Content-Type": "application/json",
      ...(options.headers || {})
    };

    const token = this.getToken();
    if (token) {
      headers["Authorization"] = `Bearer ${token}`;
    }

    try {
      const response = await fetch(url, { ...options, headers });
      const data = await response.json().catch(() => ({}));

      if (!response.ok) {
        if (response.status === 401 && !endpoint.includes("/login")) {
          // Token expired or invalid
          this.setToken(null);
          this.setUser(null);
        }
        throw new Error(data.message || `Request failed with status ${response.status}`);
      }

      return data;
    } catch (err) {
      console.error(`API Error [${endpoint}]:`, err);
      throw err;
    }
  },

  // Auth Endpoints
  registerPatient(payload) {
    return this.request("/auth/patient/register", { method: "POST", body: JSON.stringify(payload) });
  },

  loginPatient(payload) {
    return this.request("/auth/patient/login", { method: "POST", body: JSON.stringify(payload) });
  },

  registerDoctor(payload) {
    return this.request("/auth/doctor/register", { method: "POST", body: JSON.stringify(payload) });
  },

  loginDoctor(payload) {
    return this.request("/auth/doctor/login", { method: "POST", body: JSON.stringify(payload) });
  },

  getCurrentUser() {
    return this.request("/auth/me");
  },

  forgotPassword(payload) {
    return this.request("/auth/forgot-password", { method: "POST", body: JSON.stringify(payload) });
  },

  // Symptoms Endpoints
  getSymptoms() {
    return this.request("/symptoms");
  },

  getSymptomDetail(id) {
    return this.request(`/symptoms/${id}`);
  },

  checkSymptoms(payload) {
    return this.request("/symptoms/check", { method: "POST", body: JSON.stringify(payload) });
  },

  getPatientHistory() {
    return this.request("/symptoms/history");
  },

  // Specialists Endpoints
  getSpecialists() {
    return this.request("/specialists");
  },

  getSpecialistDetail(id) {
    return this.request(`/specialists/${id}`);
  },

  getDoctors(params = "") {
    return this.request(`/doctors${params ? `?${params}` : ""}`);
  },

  getDoctorDetail(id) {
    return this.request(`/doctors/${id}`);
  },

  // Consultations Endpoints
  createConsultation(payload) {
    return this.request("/consultations", { method: "POST", body: JSON.stringify(payload) });
  },

  getPatientConsultations() {
    return this.request("/consultations/patient");
  },

  getDoctorConsultations() {
    return this.request("/consultations/doctor");
  },

  updateConsultationStatus(id, payload) {
    return this.request(`/consultations/${id}/status`, { method: "PATCH", body: JSON.stringify(payload) });
  },

  // Dashboards Endpoints
  getPatientDashboard() {
    return this.request("/patient/dashboard");
  },

  getDoctorDashboard() {
    return this.request("/doctor/dashboard");
  },

  updatePatientProfile(payload) {
    return this.request("/patient/profile", { method: "PUT", body: JSON.stringify(payload) });
  },

  updateDoctorProfile(payload) {
    return this.request("/doctor/profile", { method: "PUT", body: JSON.stringify(payload) });
  },

  // Chatbot Endpoints
  getChatbotFaqs() {
    return this.request("/chatbot/faqs");
  },

  sendChatbotMessage(message) {
    return this.request("/chatbot/message", { method: "POST", body: JSON.stringify({ message }) });
  },

  // Contact Endpoint
  submitContact(payload) {
    return this.request("/contact", { method: "POST", body: JSON.stringify(payload) });
  }
};

// UI Notification Toast
function showToast(message, type = "info") {
  let toast = document.querySelector(".notification-toast");
  if (!toast) {
    toast = document.createElement("div");
    toast.className = "notification-toast";
    document.body.appendChild(toast);
  }

  const icons = {
    success: "fa-circle-check",
    error: "fa-circle-exclamation",
    warning: "fa-triangle-exclamation",
    info: "fa-circle-info"
  };

  toast.className = `notification-toast ${type} show`;
  toast.innerHTML = `
    <i class="fa-solid ${icons[type] || icons.info}"></i>
    <span>${message}</span>
  `;

  setTimeout(() => {
    toast.classList.remove("show");
  }, 4000);
}
