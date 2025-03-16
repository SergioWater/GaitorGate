document.addEventListener('DOMContentLoaded', () => {
  const sidebarLeft = document.getElementById('sidebarLeft');
  const sidebarRight = document.getElementById('sidebarRight');
  const toggleLeftBtn = document.getElementById('toggleLeft');
  const toggleRightBtn = document.getElementById('toggleRight');
  const mainContent = document.querySelector('.main-content');

  console.log("DOM Content Loaded");

  if (toggleLeftBtn) {
      toggleLeftBtn.addEventListener('click', () => {
          console.log("Left Toggle Clicked");
          sidebarLeft.classList.toggle('expanded');
          sidebarLeft.classList.toggle('collapsed');
      });
  }

  if (toggleRightBtn) {
      toggleRightBtn.addEventListener('click', () => {
          console.log("Right Toggle Clicked");
          sidebarRight.classList.toggle('expanded');
          sidebarRight.classList.toggle('collapsed');
      });
  }
});