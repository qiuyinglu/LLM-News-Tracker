/**
 * JavaScript for LLM News Thread Viewer
 * Handles pagination, filtering, and dynamic content loading
 */

// Global variables
let currentPage = 1;
let currentStatusFilter = '';
let currentSortBy = 'created_at';
let currentSortOrder = 'desc';

/**
 * Initialize the application when DOM is loaded
 */
document.addEventListener('DOMContentLoaded', function() {
    // Get current parameters from URL
    const urlParams = new URLSearchParams(window.location.search);
    currentPage = parseInt(urlParams.get('page')) || 1;
    currentStatusFilter = urlParams.get('status') || '';
    currentSortBy = urlParams.get('sort_by') || 'created_at';
    currentSortOrder = urlParams.get('sort_order') || 'desc';
    
    // Set form values
    document.getElementById('status-filter').value = currentStatusFilter;
    document.getElementById('sort-by').value = currentSortBy;
    document.getElementById('sort-order').value = currentSortOrder;
    
    // Add event listeners for responsive behavior
    window.addEventListener('resize', handleResize);
    
    // Initialize tooltips for news links
    initializeTooltips();
});

/**
 * Apply filters and reload content
 */
function applyFilters() {
    // Get current filter values
    currentStatusFilter = document.getElementById('status-filter').value;
    currentSortBy = document.getElementById('sort-by').value;
    currentSortOrder = document.getElementById('sort-order').value;
    currentPage = 1; // Reset to first page when applying filters
    
    // Update URL and reload content
    updateURL();
    loadThreads();
}

/**
 * Navigate to a specific page
 * @param {number} page - Page number to navigate to
 */
function goToPage(page) {
    currentPage = page;
    updateURL();
    loadThreads();
}

/**
 * Update the browser URL with current parameters
 */
function updateURL() {
    const params = new URLSearchParams();
    
    if (currentPage > 1) params.set('page', currentPage);
    if (currentStatusFilter) params.set('status', currentStatusFilter);
    if (currentSortBy !== 'created_at') params.set('sort_by', currentSortBy);
    if (currentSortOrder !== 'desc') params.set('sort_order', currentSortOrder);
    
    const newURL = window.location.pathname + (params.toString() ? '?' + params.toString() : '');
    window.history.pushState({}, '', newURL);
}

/**
 * Load threads data via API and update the page
 */
function loadThreads() {
    const container = document.getElementById('threads-container');
    const pagination = document.getElementById('pagination');
    
    // Show loading state
    container.classList.add('loading');
    
    // Build API URL
    const params = new URLSearchParams();
    params.set('page', currentPage);
    if (currentStatusFilter) params.set('status', currentStatusFilter);
    params.set('sort_by', currentSortBy);
    params.set('sort_order', currentSortOrder);
    
    const apiURL = '/api/threads?' + params.toString();
    
    // Fetch data
    fetch(apiURL)
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            updateThreadsDisplay(data.threads);
            updatePaginationDisplay(data.pagination);
            container.classList.remove('loading');
            
            // Scroll to top after loading new content
            window.scrollTo({ top: 0, behavior: 'smooth' });
            
            // Reinitialize tooltips for new content
            initializeTooltips();
        })
        .catch(error => {
            console.error('Error loading threads:', error);
            container.innerHTML = `
                <div class="no-threads">
                    <i class="fas fa-exclamation-triangle"></i>
                    <p>Error loading threads. Please try again.</p>
                </div>
            `;
            container.classList.remove('loading');
        });
}

/**
 * Update the threads display with new data
 * @param {Array} threads - Array of thread objects
 */
function updateThreadsDisplay(threads) {
    const container = document.getElementById('threads-container');
    
    if (!threads || threads.length === 0) {
        container.innerHTML = `
            <div class="no-threads">
                <i class="fas fa-search"></i>
                <p>No threads found matching your criteria.</p>
            </div>
        `;
        return;
    }
    
    const threadsHTML = threads.map(thread => createThreadHTML(thread)).join('');
    container.innerHTML = threadsHTML;
}

/**
 * Create HTML for a single thread
 * @param {Object} thread - Thread object
 * @returns {string} HTML string
 */
function createThreadHTML(thread) {
    const statusClass = thread.status.replace(/\s+/g, '-').toLowerCase();
    const newsLinks = thread.news.map((news, index) => 
        `<a href="${news.url}" 
           target="_blank" 
           class="news-link"
           title="${escapeHTML(news.title)}"
           data-similarity="${news.llm_similarity_score}">
            ${index + 1}
        </a>`
    ).join('');
    
    return `
        <div class="thread-card">
            <div class="thread-header">
                <h2 class="thread-title">${escapeHTML(thread.llm_title)}</h2>
                <div class="thread-meta">
                    <span class="status status-${statusClass}">
                        ${capitalizeFirst(thread.status)}
                    </span>
                    <span class="category">${capitalizeFirst(thread.category)}</span>
                    <span class="location">${thread.country.toUpperCase()} | ${thread.language.toUpperCase()}</span>
                </div>
            </div>

            <div class="thread-summary">
                <p>${escapeHTML(thread.llm_summary)}</p>
            </div>

            <div class="thread-news">
                <h4>Related News Articles (${thread.news.length}):</h4>
                <div class="news-links">
                    ${newsLinks}
                </div>
            </div>

            <div class="thread-dates">
                <span class="created">Created: ${formatDate(thread.created_at)}</span>
                <span class="updated">Updated: ${formatDate(thread.updated_at)}</span>
            </div>
        </div>
    `;
}

/**
 * Update pagination display
 * @param {Object} pagination - Pagination object
 */
function updatePaginationDisplay(pagination) {
    const container = document.getElementById('pagination');
    
    if (pagination.total_pages <= 1) {
        container.innerHTML = '';
        return;
    }
    
    let paginationHTML = `
        <div class="pagination-info">
            Showing page ${pagination.current_page} of ${pagination.total_pages} 
            (${pagination.total_threads} total threads)
        </div>
        <div class="pagination-controls">
    `;
    
    // First and Previous buttons
    if (pagination.has_prev) {
        paginationHTML += `
            <a href="#" onclick="goToPage(1)" class="page-link">First</a>
            <a href="#" onclick="goToPage(${pagination.prev_page})" class="page-link">Previous</a>
        `;
    }
    
    // Page numbers
    const startPage = Math.max(1, pagination.current_page - 2);
    const endPage = Math.min(pagination.total_pages, pagination.current_page + 2);
    
    for (let i = startPage; i <= endPage; i++) {
        if (i === pagination.current_page) {
            paginationHTML += `<span class="page-link current">${i}</span>`;
        } else {
            paginationHTML += `<a href="#" onclick="goToPage(${i})" class="page-link">${i}</a>`;
        }
    }
    
    // Next and Last buttons
    if (pagination.has_next) {
        paginationHTML += `
            <a href="#" onclick="goToPage(${pagination.next_page})" class="page-link">Next</a>
            <a href="#" onclick="goToPage(${pagination.total_pages})" class="page-link">Last</a>
        `;
    }
    
    paginationHTML += '</div>';
    container.innerHTML = paginationHTML;
}

/**
 * Initialize tooltips for news links
 */
function initializeTooltips() {
    // Remove existing tooltips
    const existingTooltips = document.querySelectorAll('.tooltip');
    existingTooltips.forEach(tooltip => tooltip.remove());
    
    // Add hover events for news links
    const newsLinks = document.querySelectorAll('.news-link');
    newsLinks.forEach(link => {
        link.addEventListener('mouseenter', showTooltip);
        link.addEventListener('mouseleave', hideTooltip);
    });
}

/**
 * Show tooltip for news link
 * @param {Event} event - Mouse event
 */
function showTooltip(event) {
    const link = event.target;
    const title = link.getAttribute('title');
    const similarity = link.getAttribute('data-similarity');
    
    if (!title) return;
    
    const tooltip = document.createElement('div');
    tooltip.className = 'tooltip';
    tooltip.innerHTML = `
        <div><strong>${escapeHTML(title)}</strong></div>
        <div>Similarity Score: ${similarity}%</div>
    `;
    tooltip.style.cssText = `
        position: absolute;
        background: #333;
        color: white;
        padding: 8px 12px;
        border-radius: 5px;
        font-size: 12px;
        z-index: 1000;
        max-width: 300px;
        word-wrap: break-word;
        pointer-events: none;
        white-space: normal;
        line-height: 1.4;
    `;
    
    document.body.appendChild(tooltip);
    
    // Position tooltip
    const rect = link.getBoundingClientRect();
    const tooltipRect = tooltip.getBoundingClientRect();
    
    let left = rect.left + (rect.width / 2) - (tooltipRect.width / 2);
    let top = rect.top - tooltipRect.height - 8;
    
    // Adjust if tooltip goes off screen
    if (left < 10) left = 10;
    if (left + tooltipRect.width > window.innerWidth - 10) {
        left = window.innerWidth - tooltipRect.width - 10;
    }
    if (top < 10) {
        top = rect.bottom + 8;
    }
    
    tooltip.style.left = left + window.scrollX + 'px';
    tooltip.style.top = top + window.scrollY + 'px';
    
    // Remove title attribute to prevent default tooltip
    link.removeAttribute('title');
    link._originalTitle = title;
}

/**
 * Hide tooltip
 * @param {Event} event - Mouse event
 */
function hideTooltip(event) {
    const link = event.target;
    const tooltip = document.querySelector('.tooltip');
    
    if (tooltip) {
        tooltip.remove();
    }
    
    // Restore title attribute
    if (link._originalTitle) {
        link.setAttribute('title', link._originalTitle);
        delete link._originalTitle;
    }
}

/**
 * Handle window resize for responsive behavior
 */
function handleResize() {
    // Hide any open tooltips on resize
    const tooltips = document.querySelectorAll('.tooltip');
    tooltips.forEach(tooltip => tooltip.remove());
}

/**
 * Utility function to escape HTML
 * @param {string} text - Text to escape
 * @returns {string} Escaped text
 */
function escapeHTML(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

/**
 * Utility function to capitalize first letter
 * @param {string} str - String to capitalize
 * @returns {string} Capitalized string
 */
function capitalizeFirst(str) {
    return str.charAt(0).toUpperCase() + str.slice(1);
}

/**
 * Utility function to format date
 * @param {string} dateString - Date string to format
 * @returns {string} Formatted date
 */
function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleString('en-US', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit',
        hour12: false
    });
}

/**
 * Handle keyboard navigation
 */
document.addEventListener('keydown', function(event) {
    // Only handle keyboard navigation if no input is focused
    if (document.activeElement.tagName === 'INPUT' || 
        document.activeElement.tagName === 'SELECT' ||
        document.activeElement.tagName === 'TEXTAREA') {
        return;
    }
    
    const pagination = document.querySelector('.pagination-controls');
    if (!pagination) return;
    
    switch (event.key) {
        case 'ArrowLeft':
            // Previous page
            const prevLink = pagination.querySelector('a[onclick*="goToPage"][onclick*="' + (currentPage - 1) + '"]');
            if (prevLink) {
                event.preventDefault();
                goToPage(currentPage - 1);
            }
            break;
        case 'ArrowRight':
            // Next page
            const nextLink = pagination.querySelector('a[onclick*="goToPage"][onclick*="' + (currentPage + 1) + '"]');
            if (nextLink) {
                event.preventDefault();
                goToPage(currentPage + 1);
            }
            break;
        case 'Home':
            // First page
            event.preventDefault();
            goToPage(1);
            break;
        case 'End':
            // Last page
            const lastPageLink = pagination.querySelector('a[onclick*="Last"]');
            if (lastPageLink) {
                event.preventDefault();
                const lastPage = parseInt(lastPageLink.getAttribute('onclick').match(/\d+/)[0]);
                goToPage(lastPage);
            }
            break;
    }
});
