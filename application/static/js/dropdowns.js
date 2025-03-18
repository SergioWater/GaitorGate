const filterSelect = document.getElementById('filterSelect');
const filterOptionsSelect = document.getElementById('filterOptionsSelect');

const options = {
    categories: ['Healthcare', 'Environment', 'Technology'],
    publishing: ['2025', '2024', '2023'],
    type: ['Picture', 'Video', 'Article'],
};

filterSelect.addEventListener('change', function() {
    const selectedFilter = this.value;
    filterOptionsSelect.innerHTML = '<option class="dropdown-option">Option</option>'; // Reset options

    if (options[selectedFilter]) {
        options[selectedFilter].forEach(option => {
            const optionElement = document.createElement('option');
            optionElement.classList.add('dropdown-option');
            optionElement.textContent = option;
            filterOptionsSelect.appendChild(optionElement);
        });
    }
});