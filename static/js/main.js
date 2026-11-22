/**
 * आयुCare (AyuCare) - Main App & Navigation Controller
 */

document.addEventListener("DOMContentLoaded", () => {
  // 1. Hide Loader
  const loader = document.querySelector(".page-loader");
  if (loader) {
    window.addEventListener("load", () => {
      setTimeout(() => loader.classList.add("hidden"), 300);
    });
    // Fallback in case load already fired
    setTimeout(() => loader.classList.add("hidden"), 1200);
  }

  // 2. Sticky Navbar Shadow
  const header = document.querySelector(".site-header");
  if (header) {
    window.addEventListener("scroll", () => {
      if (window.scrollY > 20) {
        header.classList.add("scrolled");
      } else {
        header.classList.remove("scrolled");
      }
    });
  }

  // 3. Mobile Navigation Menu Toggle
  const menuToggle = document.querySelector(".menu-toggle");
  const navMenu = document.querySelector(".nav-menu");
  if (menuToggle && navMenu) {
    menuToggle.addEventListener("click", () => {
      navMenu.classList.toggle("open");
      const icon = menuToggle.querySelector("i");
      if (icon) {
        icon.classList.toggle("fa-bars");
        icon.classList.toggle("fa-xmark");
      }
    });

    // Close on link click
    navMenu.querySelectorAll(".nav-link").forEach(link => {
      link.addEventListener("click", () => {
        navMenu.classList.remove("open");
        const icon = menuToggle.querySelector("i");
        if (icon) {
          icon.classList.add("fa-bars");
          icon.classList.remove("fa-xmark");
        }
      });
    });
  }

  // 4. Update Navigation Based on Authentication State
  updateNavbarAuth();

  // 5. Statistics Counters (IntersectionObserver)
  initStatCounters();
});

function updateNavbarAuth() {
  const navActions = document.querySelector(".nav-actions");
  if (!navActions) return;

  const user = AyuAPI.getUser();
  const token = AyuAPI.getToken();

  if (user && token) {
    const isDoctor = user.role === "doctor";
    const dashboardUrl = isDoctor ? "doctor-dashboard.html" : "dashboard.html";
    const displayName = user.full_name || (isDoctor ? "Doctor" : "Patient");

    navActions.innerHTML = `
      <a href="${dashboardUrl}" class="btn btn-outline btn-sm">
        <i class="fa-solid fa-user-circle"></i>
        <span>${displayName.split(" ")[0]}</span>
      </a>
      <button id="nav-logout-btn" class="btn btn-primary btn-sm">
        <i class="fa-solid fa-arrow-right-from-bracket"></i>
        <span>Logout</span>
      </button>
    `;

    document.getElementById("nav-logout-btn")?.addEventListener("click", () => {
      AyuAPI.logout();
    });
  }
}

function initStatCounters() {
  const statNumbers = document.querySelectorAll(".stat-number[data-target]");
  if (!statNumbers.length) return;

  const observer = new IntersectionObserver((entries, obs) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        const target = parseInt(entry.target.getAttribute("data-target"), 10);
        const suffix = entry.target.getAttribute("data-suffix") || "";
        animateNumber(entry.target, 0, target, 1600, suffix);
        obs.unobserve(entry.target);
      }
    });
  }, { threshold: 0.5 });

  statNumbers.forEach(stat => observer.observe(stat));
}

function animateNumber(element, start, end, duration, suffix = "") {
  let startTimestamp = null;
  const step = (timestamp) => {
    if (!startTimestamp) startTimestamp = timestamp;
    const progress = Math.min((timestamp - startTimestamp) / duration, 1);
    const easeOutQuad = 1 - (1 - progress) * (1 - progress);
    const current = Math.floor(easeOutQuad * (end - start) + start);
    element.textContent = current.toLocaleString() + suffix;
    if (progress < 1) {
      window.requestAnimationFrame(step);
    }
  };
  window.requestAnimationFrame(step);
}
