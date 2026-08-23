// HTMX normally injects its indicator CSS via an inline <style> tag, which the
// CSP's style-src 'self' blocks. The equivalent rules are compiled into
// tailwind.css instead (see assets/css/input.css).
if (window.htmx) {
  htmx.config.includeIndicatorStyles = false;
}

document.addEventListener("DOMContentLoaded", () => {
  const contactButton = document.getElementById("nav-contact-btn");
  if (contactButton) {
    contactButton.addEventListener("click", () => {
      document.getElementById("contact").scrollIntoView({ behavior: "smooth" });
    });
  }
});
