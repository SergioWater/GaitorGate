document.addEventListener('DOMContentLoaded', function() {
    const recommendedContainer = document.querySelector('.recommended-container');
    const carousel = document.querySelector('.carousel');
    const rotateItem = document.querySelector('.rotate-item');
    const prevButton = rotateItem.querySelector('.carousel-button.prev');
    const nextButton = rotateItem.querySelector('.carousel-button.next');
    const items = carousel.querySelectorAll('.recommended-item');
    const currentPageDisplay = rotateItem.querySelector('.current-page');

    if (!recommendedContainer || !carousel || !rotateItem || !prevButton || !nextButton || items.length === 0) {
        return;
    }

    let currentIndex = 0;
    const itemWidth = items[0].offsetWidth + parseInt(window.getComputedStyle(items[0]).marginRight);

    function scrollToItem(index) {
        const translateX = -index * itemWidth;
        carousel.style.transform = `translateX(${translateX}px)`;
        currentIndex = index;
        updateButtonVisibility();
        updateCurrentPageDisplay();
    }

    function updateButtonVisibility() {
        prevButton.style.visibility = currentIndex > 0 ? 'visible' : 'hidden';
        nextButton.style.visibility = carousel.offsetWidth > recommendedContainer.offsetWidth && currentIndex < Math.floor((carousel.offsetWidth - recommendedContainer.offsetWidth) / itemWidth) ? 'visible' : 'hidden';
    }

    function updateCurrentPageDisplay() {
        if (currentPageDisplay) {
            currentPageDisplay.textContent = `${currentIndex + 1} / ${items.length}`;
        }
    }

    prevButton.addEventListener('click', () => {
        if (currentIndex > 0) {
            scrollToItem(currentIndex - 1);
        }
    });

    nextButton.addEventListener('click', () => {
        if (carousel.offsetWidth > recommendedContainer.offsetWidth && currentIndex < Math.floor((carousel.offsetWidth - recommendedContainer.offsetWidth) / itemWidth)) {
            scrollToItem(currentIndex + 1);
        }
    });

    updateButtonVisibility();
    updateCurrentPageDisplay();
});