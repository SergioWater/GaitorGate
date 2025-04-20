document.addEventListener('DOMContentLoaded', function() {
    const ratingElements = document.querySelectorAll('.result-info li:last-child');
  
    ratingElements.forEach(function(ratingElement) {
      const ratingTextElement = ratingElement.querySelector('.average-rating-value');
  
      if (ratingTextElement) {
        const ratingValue = parseFloat(ratingTextElement.textContent);
        let stars = '';
        const fullStars = Math.floor(ratingValue);
        const fraction = ratingValue - fullStars;
  
        for (let i = 0; i < fullStars; i++) {
          stars += '★';
        }
  
        if (fraction >= 0.5) {
          stars += '½';
        }
  
        ratingTextElement.insertAdjacentHTML('afterend', ' ' + stars);
      }
    });
  });