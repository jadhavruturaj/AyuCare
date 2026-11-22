/**
 * AyuCare Guest Guard
 * For public auth pages (login.html, register.html, etc.).
 * If the user is already authenticated, redirect them to the main website or dashboard.
 */
(function() {
  const token = localStorage.getItem('ayucare_token');
  const rawUser = localStorage.getItem('ayucare_user');

  if (token && rawUser) {
    try {
      const user = JSON.parse(rawUser);
      const urlParams = new URLSearchParams(window.location.search);
      const redirect = urlParams.get('redirect');

      if (redirect) {
        window.location.replace(decodeURIComponent(redirect));
      } else if (user.role === 'doctor') {
        window.location.replace('doctor-dashboard.html');
      } else {
        window.location.replace('index.html');
      }
    } catch (e) {
      localStorage.removeItem('ayucare_token');
      localStorage.removeItem('ayucare_user');
    }
  }
})();
