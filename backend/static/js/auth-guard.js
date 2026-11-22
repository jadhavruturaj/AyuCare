/**
 * AyuCare Auth Guard
 * Enforces mandatory login for protected pages.
 * Runs synchronously in <head> to prevent unauthenticated access or content flashing.
 */
(function() {
  const token = localStorage.getItem('ayucare_token');
  const user = localStorage.getItem('ayucare_user');

  if (!token || !user) {
    // User is unauthenticated. Clear any corrupted state.
    localStorage.removeItem('ayucare_token');
    localStorage.removeItem('ayucare_user');

    const currentFile = window.location.pathname.split('/').pop() || 'index.html';
    // If accessing doctor dashboard without auth, redirect to doctor-login
    const targetLogin = currentFile.includes('doctor') ? 'doctor-login.html' : 'login.html';
    const redirectParam = encodeURIComponent(window.location.pathname + window.location.search);
    
    window.location.replace(`${targetLogin}?redirect=${redirectParam}`);
  }
})();
