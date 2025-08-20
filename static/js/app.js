// Telegram Archive Browser - Main JavaScript

// Global variables
let searchTimeout;
const SEARCH_DELAY = 300; // ms

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
});

function initializeApp() {
    // Initialize tooltips
    initializeTooltips();
    
    // Setup keyboard shortcuts
    setupKeyboardShortcuts();
    
    // Setup search functionality
    setupSearch();
    
    // Setup theme toggle
    setupThemeToggle();
    
    // Setup auto-refresh
    setupAutoRefresh();
    
    console.log('📱 Telegram Archive Browser initialized');
}

// Tooltip initialization
function initializeTooltips() {
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

// Keyboard shortcuts
function setupKeyboardShortcuts() {
    document.addEventListener('keydown', function(e) {
        // Ctrl/Cmd + K: Focus search
        if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
            e.preventDefault();
            const searchInput = document.querySelector('input[name="q"]');
            if (searchInput) {
                searchInput.focus();
                searchInput.select();
            }
        }
        
        // Ctrl/Cmd + R: Refresh page
        if ((e.ctrlKey || e.metaKey) && e.key === 'r') {
            e.preventDefault();
            window.location.reload();
        }
        
        // Escape: Clear search or close modals
        if (e.key === 'Escape') {
            const searchInput = document.querySelector('input[name="q"]');
            if (searchInput && searchInput === document.activeElement) {
                searchInput.value = '';
                searchInput.blur();
            }
        }
    });
}

// Search functionality
function setupSearch() {
    const searchInputs = document.querySelectorAll('input[name="q"]');
    
    searchInputs.forEach(input => {
        // Auto-complete and suggestions
        input.addEventListener('input', function() {
            clearTimeout(searchTimeout);
            searchTimeout = setTimeout(() => {
                handleSearchInput(this);
            }, SEARCH_DELAY);
        });
        
        // Search on Enter
        input.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                clearTimeout(searchTimeout);
                handleSearchSubmit(this);
            }
        });
    });
}

function handleSearchInput(input) {
    const query = input.value.trim();
    
    if (query.length >= 2) {
        // Show search suggestions (if implemented)
        showSearchSuggestions(input, query);
    } else {
        hideSearchSuggestions(input);
    }
}

function handleSearchSubmit(input) {
    const form = input.closest('form');
    if (form) {
        form.submit();
    }
}

function showSearchSuggestions(input, query) {
    // Placeholder for search suggestions
    // Could implement autocomplete with popular search terms
}

function hideSearchSuggestions(input) {
    // Hide suggestions dropdown
}

// Theme toggle functionality
function setupThemeToggle() {
    // Check for saved theme preference or default to 'light'
    const currentTheme = localStorage.getItem('theme') || 'light';
    document.documentElement.setAttribute('data-theme', currentTheme);
    
    // Create theme toggle button if it doesn't exist
    const navbar = document.querySelector('.navbar-nav');
    if (navbar && !document.getElementById('themeToggle')) {
        const themeToggle = document.createElement('li');
        themeToggle.className = 'nav-item';
        themeToggle.innerHTML = `
            <button class="nav-link btn btn-link" id="themeToggle" title="Toggle theme">
                <i class="bi bi-${currentTheme === 'dark' ? 'sun' : 'moon'}"></i>
            </button>
        `;
        navbar.appendChild(themeToggle);
        
        themeToggle.addEventListener('click', toggleTheme);
    }
}

function toggleTheme() {
    const currentTheme = document.documentElement.getAttribute('data-theme');
    const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
    
    document.documentElement.setAttribute('data-theme', newTheme);
    localStorage.setItem('theme', newTheme);
    
    // Update toggle button icon
    const toggleBtn = document.querySelector('#themeToggle i');
    if (toggleBtn) {
        toggleBtn.className = `bi bi-${newTheme === 'dark' ? 'sun' : 'moon'}`;
    }
}

// Auto-refresh functionality
function setupAutoRefresh() {
    // Auto-refresh dashboard every 5 minutes if on dashboard page
    if (window.location.pathname === '/') {
        setInterval(() => {
            refreshDashboardStats();
        }, 5 * 60 * 1000); // 5 minutes
    }
}

function refreshDashboardStats() {
    fetch('/api/stats')
        .then(response => response.json())
        .then(data => {
            updateStatsCards(data);
        })
        .catch(error => {
            console.error('Error refreshing stats:', error);
        });
}

function updateStatsCards(stats) {
    // Update statistics cards with new data
    const statsElements = {
        'total_channels': document.querySelector('[data-stat="channels"]'),
        'total_messages': document.querySelector('[data-stat="messages"]'),
        'total_files': document.querySelector('[data-stat="files"]'),
        'total_media': document.querySelector('[data-stat="media"]')
    };
    
    Object.entries(statsElements).forEach(([key, element]) => {
        if (element && stats[key] !== undefined) {
            element.textContent = formatNumber(stats[key]);
        }
    });
}

// Utility functions
function formatNumber(num) {
    return new Intl.NumberFormat().format(num);
}

function formatFileSize(bytes) {
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    if (bytes === 0) return '0 Bytes';
    const i = Math.floor(Math.log(bytes) / Math.log(1024));
    return Math.round(bytes / Math.pow(1024, i) * 100) / 100 + ' ' + sizes[i];
}

function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString() + ' ' + date.toLocaleTimeString();
}

function showNotification(message, type = 'info') {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
    notification.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
    notification.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    document.body.appendChild(notification);
    
    // Auto-remove after 5 seconds
    setTimeout(() => {
        if (notification.parentNode) {
            notification.remove();
        }
    }, 5000);
}

// Search API functions
async function searchMessages(query, channel = '', limit = 20) {
    try {
        const params = new URLSearchParams({
            q: query,
            limit: limit
        });
        
        if (channel) {
            params.append('channel', channel);
        }
        
        const response = await fetch(`/api/search?${params}`);
        const data = await response.json();
        
        if (response.ok) {
            return data;
        } else {
            throw new Error(data.error || 'Search failed');
        }
    } catch (error) {
        console.error('Search error:', error);
        showNotification('Search failed: ' + error.message, 'danger');
        return { results: [], count: 0 };
    }
}

// Media handling
function preloadImages() {
    const images = document.querySelectorAll('img[data-src]');
    
    const imageObserver = new IntersectionObserver((entries, observer) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const img = entry.target;
                img.src = img.dataset.src;
                img.removeAttribute('data-src');
                observer.unobserve(img);
            }
        });
    });
    
    images.forEach(img => imageObserver.observe(img));
}

// Copy to clipboard functionality
async function copyToClipboard(text) {
    try {
        await navigator.clipboard.writeText(text);
        showNotification('Copied to clipboard!', 'success');
        return true;
    } catch (err) {
        // Fallback for older browsers
        const textArea = document.createElement('textarea');
        textArea.value = text;
        textArea.style.position = 'fixed';
        textArea.style.left = '-999999px';
        textArea.style.top = '-999999px';
        document.body.appendChild(textArea);
        textArea.focus();
        textArea.select();
        
        try {
            document.execCommand('copy');
            showNotification('Copied to clipboard!', 'success');
            return true;
        } catch (err) {
            showNotification('Failed to copy to clipboard', 'danger');
            return false;
        } finally {
            document.body.removeChild(textArea);
        }
    }
}

// Download functionality
function downloadFile(content, filename, contentType = 'text/plain') {
    const blob = new Blob([content], { type: contentType });
    const url = window.URL.createObjectURL(blob);
    
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    
    window.URL.revokeObjectURL(url);
    showNotification(`Downloaded ${filename}`, 'success');
}

// Performance monitoring
function measurePerformance(name, fn) {
    const start = performance.now();
    const result = fn();
    const end = performance.now();
    console.log(`${name} took ${end - start} milliseconds`);
    return result;
}

// Error handling
window.addEventListener('error', function(e) {
    console.error('Global error:', e.error);
    showNotification('An error occurred. Please refresh the page.', 'danger');
});

// Service worker registration (for offline support)
if ('serviceWorker' in navigator) {
    window.addEventListener('load', function() {
        navigator.serviceWorker.register('/static/js/sw.js')
            .then(function(registration) {
                console.log('ServiceWorker registration successful');
            })
            .catch(function(err) {
                console.log('ServiceWorker registration failed');
            });
    });
}

// Export functions for use in other scripts
window.TelegramArchive = {
    searchMessages,
    copyToClipboard,
    downloadFile,
    showNotification,
    formatNumber,
    formatFileSize,
    formatDate
};