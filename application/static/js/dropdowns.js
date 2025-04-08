const searchForm = document.querySelector('.search-form');
const addFilterButton = document.querySelector('.add-filter-button');
const filterContainer = document.querySelector('.filter-container');
const optionsData = {
    categories: ['Healthcare', 'Environment', 'Technology'],
    publishing: ['2025', '2024', '2023'],
    type: ['Picture', 'Video', 'Article'],
};
let filterCount = 1; // Start with one filter dropdown

function createFilterDropdowns() {
    const newFilterContainer = document.createElement('div');
    newFilterContainer.classList.add('filter-container');

    const filterSelect = document.createElement('select');
    filterSelect.name = 'filter[]';
    filterSelect.classList.add('filter-dropdown');
    filterSelect.innerHTML = `
        <option class="dropdown-option" value="">Filter</option>
        <option class="dropdown-option" value="categories">Categories</option>
        <option class="dropdown-option" value="publishing">Publishing</option>
        <option class="dropdown-option" value="type">Type</option>
    `;

    const optionsSelect = document.createElement('select');
    optionsSelect.name = 'filter-options[]';
    optionsSelect.classList.add('filter-dropdown');
    optionsSelect.innerHTML = '<option class="dropdown-option" value="">Option</option>';

    filterSelect.addEventListener('change', function() {
        updateOptions(this, optionsSelect);
    });

    newFilterContainer.appendChild(filterSelect);
    newFilterContainer.appendChild(optionsSelect);
    return newFilterContainer;
}

function updateOptions(filterDropdown, optionsDropdown) {
    const selectedFilter = filterDropdown.value;
    optionsDropdown.innerHTML = '<option class="dropdown-option" value="">Option</option>'; // Reset options

    if (optionsData[selectedFilter]) {
        optionsData[selectedFilter].forEach(option => {
            const optionElement = document.createElement('option');
            optionElement.classList.add('dropdown-option');
            optionElement.textContent = option;
            optionsDropdown.appendChild(optionElement);
        });
    }
}

// Initialize the first dropdown
const initialFilterSelect = filterContainer.querySelector('select[name="filter[]"]');
const initialOptionsSelect = filterContainer.querySelector('select[name="filter-options[]"]');
initialFilterSelect.addEventListener('change', function() {
    updateOptions(this, initialOptionsSelect);
});

addFilterButton.addEventListener('click', function() {
    if (filterCount < 3) {
        const newDropdowns = createFilterDropdowns();
        searchForm.insertBefore(newDropdowns, searchForm.querySelector('.search-bar'));
        filterCount++;
    }
    if (filterCount >= 3) {
        addFilterButton.style.display = 'none'; // Hide the button after 3 dropdowns
    }
});
