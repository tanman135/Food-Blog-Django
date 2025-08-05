document.querySelectorAll('a[href^="#"]').forEach(anchor => {
  anchor.addEventListener('click', function (e) {
    e.preventDefault();
    const target = document.querySelector(this.getAttribute('href'));
    if (target) {
      target.scrollIntoView({
        behavior: 'smooth'
      });
    }
  });
});

// Navbar toggle
const navbarToggler = document.querySelector('.navbar-toggler');
const navbarMenu = document.querySelector('.navbar-collapse');

if (navbarToggler && navbarMenu) {
  navbarToggler.addEventListener('click', () => {
    navbarMenu.classList.toggle('show');
  });
}


window.addEventListener('scroll', () => {
  const sections = document.querySelectorAll('section');
  const scrollPos = window.scrollY || window.pageYOffset;

  sections.forEach(section => {
    const top = section.offsetTop - 80;
    const bottom = top + section.offsetHeight;

    const id = section.getAttribute('id');
    const navLink = document.querySelector(`.nav-link[href="#${id}"]`);

    if (navLink) {
      if (scrollPos >= top && scrollPos < bottom) {
        navLink.classList.add('active');
      } else {
        navLink.classList.remove('active');
      }
    }
  });
});
