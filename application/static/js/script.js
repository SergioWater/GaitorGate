document.addEventListener('DOMContentLoaded', () => {
    const sidebarLeft = document.getElementById('sidebarLeft');
    const sidebarRight = document.getElementById('sidebarRight');
    const toggleLeftBtn = document.getElementById('toggleLeftBtn');
    const toggleRightBtn = document.getElementById('toggleRightBtn');
  
    // Toggle for left sidebar
    toggleLeftBtn.addEventListener('click', () => {
      sidebarLeft.classList.toggle('expanded');
      sidebarLeft.classList.toggle('collapsed');
    });
  
    // Toggle for right sidebar
    toggleRightBtn.addEventListener('click', () => {
      sidebarRight.classList.toggle('expanded');
      sidebarRight.classList.toggle('collapsed');
    });
  });
  
