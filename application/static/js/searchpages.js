const allData = {{ all_data|tojson }};
const resultsPerPage = {{ results_per_page }};
let currentPage = {{ current_page }};
const totalResults = allData.length;
const totalPages = Math.ceil(totalResults / resultsPerPage);

function displayResults(pageNumber) {
    const startIndex = (pageNumber - 1) * resultsPerPage;
    const endIndex = startIndex + resultsPerPage;
    const currentPageData = allData.slice(startIndex, endIndex);

    const resultsContent = document.getElementById('results-content');
    resultsContent.innerHTML = '';

    if (currentPageData.length > 0) {
        currentPageData.forEach(item => {
            const resultItem = document.createElement('div');
            resultItem.classList.add('result-item');
            resultItem.innerHTML = `
                <br>
                <div class="result-info">
                    ${item.title}, ${item.author}, <a href="${item.url}" target="_blank">View</a>, ${item.category || ''}, ${item.published_date || ''}
                </div>
                <div><img src="${item.thumbnail_url || ''}" height="25%" width="25%"></div>
                </br>
            `;

            const ratingFormContainer = document.createElement('div');
            // Assuming you have a way to generate this HTML based on item.docID
            ratingFormContainer.innerHTML = ``;

            const reviewFormContainer = document.createElement('div');
            // Assuming you have a way to generate this HTML based on item.docID
            reviewFormContainer.innerHTML = ``;

            resultItem.appendChild(ratingFormContainer);
            resultItem.appendChild(reviewFormContainer);

            resultsContent.appendChild(resultItem);
        });
    } else if (totalResults > 0) {
        resultsContent.innerHTML = '<p>No results on this page.</p>';
    } else {
        resultsContent.innerHTML = '<p>No results found.</p>';
    }
}

function generatePaginationLinks() {
    const paginationLinksContainer = document.getElementById('pagination-links');
    paginationLinksContainer.innerHTML = '';

    if (totalPages > 1) {
        if (currentPage > 1) {
            const prevLink = document.createElement('a');
            prevLink.href = '#';
            prevLink.textContent = 'Previous';
            prevLink.addEventListener('click', () => {
                currentPage--;
                displayResults(currentPage);
                updatePaginationLinks();
            });
            paginationLinksContainer.appendChild(prevLink);
        }

        for (let i = 1; i <= totalPages; i++) {
            const pageLink = document.createElement('a');
            pageLink.href = '#';
            pageLink.textContent = i;
            if (i === currentPage) {
                pageLink.classList.add('current-page');
            } else {
                pageLink.addEventListener('click', () => {
                    currentPage = i;
                    displayResults(currentPage);
                    updatePaginationLinks();
                });
            }
            paginationLinksContainer.appendChild(pageLink);
        }

        if (currentPage < totalPages) {
            const nextLink = document.createElement('a');
            nextLink.href = '#';
            nextLink.textContent = 'Next';
            nextLink.addEventListener('click', () => {
                currentPage++;
                displayResults(currentPage);
                updatePaginationLinks();
            });
            paginationLinksContainer.appendChild(nextLink);
        }
    }
}

function updatePaginationLinks() {
    const paginationLinksContainer = document.getElementById('pagination-links');
    paginationLinksContainer.innerHTML = '';
    generatePaginationLinks();
}

// Initial display
displayResults(currentPage);
generatePaginationLinks();
