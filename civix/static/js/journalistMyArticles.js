
// Filter articles
function filterArticles() {
    const statusFilter = document.getElementById('statusFilter').value;
    const categoryFilter = document.getElementById('categoryFilter').value;
    const searchInput = document.getElementById('searchInput').value.toLowerCase();
    const articles = document.querySelectorAll('.article-item');

    let visibleCount = 0;

    articles.forEach(article => {
        const status = article.dataset.status;
        const category = article.dataset.category;
        const title = article.dataset.title.toLowerCase();

        let show = true;

        if (statusFilter !== 'all' && status !== statusFilter) show = false;
        if (categoryFilter !== 'all' && category !== categoryFilter) show = false;
        if (searchInput && !title.includes(searchInput)) show = false;

        if (show) {
            article.style.display = 'grid';
            visibleCount++;
        } else {
            article.style.display = 'none';
        }
    });

    // Show empty state if no results
    const articlesList = document.getElementById('articlesList');
    const existingEmpty = articlesList.querySelector('.empty-state');

    if (visibleCount === 0 && !existingEmpty) {
        const emptyState = document.createElement('div');
        emptyState.className = 'empty-state';
        emptyState.innerHTML = `
      <div class="empty-icon">🔍</div>
      <h3 class="empty-title">No articles found</h3>
      <p class="empty-text">Try adjusting your filters or search query</p>
      <button class="btn btn-secondary" onclick="resetFilters()">Reset Filters</button>
    `;
        articlesList.appendChild(emptyState);
    } else if (visibleCount > 0 && existingEmpty) {
        existingEmpty.remove();
    }
}

// Reset filters
function resetFilters() {
    document.getElementById('statusFilter').value = 'all';
    document.getElementById('categoryFilter').value = 'all';
    document.getElementById('sortFilter').value = 'newest';
    document.getElementById('searchInput').value = '';
    filterArticles();
}

// Filter by status (from sidebar)
function filterByStatus(status) {
    document.getElementById('statusFilter').value = status;
    filterArticles();
}

// Preview article in popup window
function previewArticle(url) {
    const width = 1000;
    const height = 700;
    const left = (screen.width - width) / 2;
    const top = (screen.height - height) / 2;
    window.open(
        url,
        'articlePreview',
        `width=${width},height=${height},top=${top},left=${left},scrollbars=yes,resizable=yes`
    );
}





