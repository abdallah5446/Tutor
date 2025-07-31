// Main Application JavaScript
class TutoringLeadApp {
    constructor() {
        this.leads = [];
        this.filteredLeads = [];
        this.currentFilters = {
            search: '',
            source: '',
            subject: ''
        };
        
        this.init();
    }
    
    init() {
        this.bindEvents();
        this.loadLeads();
        this.loadStats();
    }
    
    bindEvents() {
        // Search functionality
        const searchInput = document.getElementById('searchInput');
        searchInput.addEventListener('input', (e) => {
            this.currentFilters.search = e.target.value;
            this.filterLeads();
        });
        
        // Filter functionality
        const sourceFilter = document.getElementById('sourceFilter');
        sourceFilter.addEventListener('change', (e) => {
            this.currentFilters.source = e.target.value;
            this.filterLeads();
        });
        
        const subjectFilter = document.getElementById('subjectFilter');
        subjectFilter.addEventListener('change', (e) => {
            this.currentFilters.subject = e.target.value;
            this.filterLeads();
        });
        
        // Clear filters
        const clearFiltersBtn = document.getElementById('clearFilters');
        clearFiltersBtn.addEventListener('click', () => {
            this.clearFilters();
        });
        
        // Scrape button
        const scrapeBtn = document.getElementById('scrapeBtn');
        scrapeBtn.addEventListener('click', () => {
            this.triggerScrape();
        });
        
        // Modal functionality
        const modal = document.getElementById('leadModal');
        const closeBtn = document.querySelector('.close');
        
        closeBtn.addEventListener('click', () => {
            modal.style.display = 'none';
        });
        
        window.addEventListener('click', (e) => {
            if (e.target === modal) {
                modal.style.display = 'none';
            }
        });
    }
    
    async loadLeads() {
        try {
            this.showLoading(true);
            const response = await fetch('/api/leads');
            const data = await response.json();
            
            this.leads = data.leads || [];
            this.filterLeads();
            this.updateResultsCount();
            
        } catch (error) {
            console.error('Error loading leads:', error);
            this.showError('Failed to load leads. Please try again.');
        } finally {
            this.showLoading(false);
        }
    }
    
    async loadStats() {
        try {
            const response = await fetch('/api/stats');
            const stats = await response.json();
            
            this.updateStats(stats);
            this.updateSourceBreakdown(stats.source_breakdown || {});
            
        } catch (error) {
            console.error('Error loading stats:', error);
        }
    }
    
    async triggerScrape() {
        const scrapeBtn = document.getElementById('scrapeBtn');
        const icon = scrapeBtn.querySelector('i');
        
        try {
            // Show loading state
            scrapeBtn.disabled = true;
            icon.classList.add('spin');
            scrapeBtn.innerHTML = '<i class="fas fa-sync-alt spin"></i> Scraping...';
            
            const response = await fetch('/api/scrape');
            const result = await response.json();
            
            if (result.status === 'success') {
                this.showSuccess('Scraping started! Results will update shortly.');
                
                // Refresh data after a short delay
                setTimeout(() => {
                    this.loadLeads();
                    this.loadStats();
                }, 3000);
            }
            
        } catch (error) {
            console.error('Error triggering scrape:', error);
            this.showError('Failed to start scraping. Please try again.');
        } finally {
            // Reset button state
            setTimeout(() => {
                scrapeBtn.disabled = false;
                icon.classList.remove('spin');
                scrapeBtn.innerHTML = '<i class="fas fa-sync-alt"></i> Refresh Leads';
            }, 2000);
        }
    }
    
    filterLeads() {
        this.filteredLeads = this.leads.filter(lead => {
            // Search filter
            if (this.currentFilters.search) {
                const searchTerm = this.currentFilters.search.toLowerCase();
                const searchableText = `${lead.title} ${lead.description} ${lead.subject}`.toLowerCase();
                if (!searchableText.includes(searchTerm)) {
                    return false;
                }
            }
            
            // Source filter
            if (this.currentFilters.source) {
                if (lead.source !== this.currentFilters.source) {
                    return false;
                }
            }
            
            // Subject filter
            if (this.currentFilters.subject) {
                if (!lead.subject || !lead.subject.toLowerCase().includes(this.currentFilters.subject.toLowerCase())) {
                    return false;
                }
            }
            
            return true;
        });
        
        this.renderLeads();
        this.updateResultsCount();
    }
    
    renderLeads() {
        const container = document.getElementById('leadsContainer');
        const noResults = document.getElementById('noResults');
        
        if (this.filteredLeads.length === 0) {
            container.innerHTML = '';
            noResults.style.display = 'block';
            return;
        }
        
        noResults.style.display = 'none';
        
        container.innerHTML = this.filteredLeads.map(lead => this.createLeadCard(lead)).join('');
        
        // Add click events to lead cards
        container.querySelectorAll('.lead-card').forEach((card, index) => {
            card.addEventListener('click', () => {
                this.showLeadDetails(this.filteredLeads[index]);
            });
        });
    }
    
    createLeadCard(lead) {
        const postedDate = this.formatDate(lead.posted_date || lead.scraped_at);
        const sourceClass = `source-${lead.source}`;
        
        return `
            <div class="lead-card fade-in">
                <div class="lead-header">
                    <h3 class="lead-title">${this.escapeHtml(lead.title)}</h3>
                </div>
                
                <div class="lead-meta">
                    <span class="lead-badge ${sourceClass}">${this.capitalizeFirst(lead.source)}</span>
                    ${lead.subreddit ? `<span class="lead-badge subreddit-badge">r/${this.escapeHtml(lead.subreddit)}</span>` : ''}
                    <span class="lead-badge subject-badge">${this.escapeHtml(lead.subject || 'General')}</span>
                    <span class="lead-badge budget-badge">${this.escapeHtml(lead.budget || 'Not specified')}</span>
                    ${lead.score !== undefined ? `<span class="lead-badge score-badge">↑${lead.score}</span>` : ''}
                </div>
                
                <div class="lead-description">
                    ${this.escapeHtml(lead.description || 'No description available')}
                </div>
                
                <div class="lead-footer">
                    <div class="lead-location">
                        <i class="fas fa-map-marker-alt"></i>
                        ${this.escapeHtml(lead.location || 'Location not specified')}
                    </div>
                    <div class="lead-date">
                        ${postedDate}
                    </div>
                </div>
            </div>
        `;
    }
    
    showLeadDetails(lead) {
        const modal = document.getElementById('leadModal');
        const modalContent = document.getElementById('modalContent');
        
        const postedDate = this.formatDate(lead.posted_date || lead.scraped_at);
        const sourceClass = `source-${lead.source}`;
        
        modalContent.innerHTML = `
            <div class="lead-detail">
                <h2 class="lead-title">${this.escapeHtml(lead.title)}</h2>
                
                <div class="lead-meta" style="margin: 20px 0;">
                    <span class="lead-badge ${sourceClass}">${this.capitalizeFirst(lead.source)}</span>
                    ${lead.subreddit ? `<span class="lead-badge subreddit-badge">r/${this.escapeHtml(lead.subreddit)}</span>` : ''}
                    <span class="lead-badge subject-badge">${this.escapeHtml(lead.subject || 'General')}</span>
                    <span class="lead-badge budget-badge">${this.escapeHtml(lead.budget || 'Not specified')}</span>
                    ${lead.score !== undefined ? `<span class="lead-badge score-badge">↑${lead.score}</span>` : ''}
                    ${lead.num_comments !== undefined ? `<span class="lead-badge comments-badge">${lead.num_comments} comments</span>` : ''}
                </div>
                
                <div style="margin: 20px 0;">
                    <h4>Description:</h4>
                    <p style="margin-top: 10px; line-height: 1.6;">${this.escapeHtml(lead.description || 'No description available')}</p>
                </div>
                
                <div style="margin: 20px 0;">
                    <h4>Details:</h4>
                    <ul style="margin-top: 10px; line-height: 1.8;">
                        <li><strong>Location:</strong> ${this.escapeHtml(lead.location || 'Not specified')}</li>
                        <li><strong>Contact:</strong> ${this.escapeHtml(lead.contact || 'See original post')}</li>
                        <li><strong>Posted:</strong> ${postedDate}</li>
                        ${lead.subreddit ? `<li><strong>Subreddit:</strong> r/${this.escapeHtml(lead.subreddit)}</li>` : ''}
                        ${lead.score !== undefined ? `<li><strong>Reddit Score:</strong> ${lead.score} upvotes</li>` : ''}
                        ${lead.num_comments !== undefined ? `<li><strong>Comments:</strong> ${lead.num_comments}</li>` : ''}
                    </ul>
                </div>
                
                <div style="margin: 20px 0;">
                    <a href="${this.escapeHtml(lead.url || '#')}" target="_blank" 
                       style="display: inline-block; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                              color: white; padding: 12px 24px; text-decoration: none; border-radius: 10px; 
                              font-weight: 600; transition: all 0.3s ease;">
                        <i class="fas fa-external-link-alt"></i> View Original Post
                    </a>
                </div>
            </div>
        `;
        
        modal.style.display = 'block';
    }
    
    updateStats(stats) {
        document.getElementById('totalLeads').textContent = stats.total_leads || 0;
        document.getElementById('recentLeads').textContent = stats.recent_leads || 0;
        document.getElementById('lastUpdated').textContent = stats.last_updated || 'Never';
    }
    
    updateSourceBreakdown(sourceBreakdown) {
        const container = document.getElementById('sourceStats');
        
        if (Object.keys(sourceBreakdown).length === 0) {
            container.innerHTML = '<span class="source-stat">No data available</span>';
            return;
        }
        
        container.innerHTML = Object.entries(sourceBreakdown)
            .map(([source, count]) => `
                <span class="source-stat">
                    ${this.capitalizeFirst(source)}: ${count}
                </span>
            `).join('');
    }
    
    updateResultsCount() {
        const count = this.filteredLeads.length;
        const total = this.leads.length;
        const resultsCount = document.getElementById('resultsCount');
        
        if (count === total) {
            resultsCount.textContent = `${count} lead${count !== 1 ? 's' : ''}`;
        } else {
            resultsCount.textContent = `${count} of ${total} lead${total !== 1 ? 's' : ''}`;
        }
    }
    
    clearFilters() {
        this.currentFilters = {
            search: '',
            source: '',
            subject: ''
        };
        
        document.getElementById('searchInput').value = '';
        document.getElementById('sourceFilter').value = '';
        document.getElementById('subjectFilter').value = '';
        
        this.filterLeads();
    }
    
    showLoading(show) {
        const loadingSpinner = document.getElementById('loadingSpinner');
        const leadsContainer = document.getElementById('leadsContainer');
        
        if (show) {
            loadingSpinner.style.display = 'block';
            leadsContainer.style.display = 'none';
        } else {
            loadingSpinner.style.display = 'none';
            leadsContainer.style.display = 'grid';
        }
    }
    
    showSuccess(message) {
        this.showNotification(message, 'success');
    }
    
    showError(message) {
        this.showNotification(message, 'error');
    }
    
    showNotification(message, type) {
        // Create notification element
        const notification = document.createElement('div');
        notification.className = `notification ${type}`;
        notification.innerHTML = `
            <i class="fas fa-${type === 'success' ? 'check-circle' : 'exclamation-circle'}"></i>
            ${message}
        `;
        
        // Add styles
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 15px 25px;
            border-radius: 10px;
            color: white;
            font-weight: 600;
            z-index: 1001;
            animation: slideIn 0.3s ease;
            background: ${type === 'success' ? '#48bb78' : '#e53e3e'};
            box-shadow: 0 5px 15px rgba(0,0,0,0.2);
        `;
        
        document.body.appendChild(notification);
        
        // Remove after 4 seconds
        setTimeout(() => {
            notification.style.animation = 'slideOut 0.3s ease';
            setTimeout(() => {
                document.body.removeChild(notification);
            }, 300);
        }, 4000);
    }
    
    // Utility functions
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
    
    capitalizeFirst(str) {
        return str.charAt(0).toUpperCase() + str.slice(1);
    }
    
    formatDate(dateString) {
        if (!dateString) return 'Unknown';
        
        try {
            const date = new Date(dateString);
            const now = new Date();
            const diffTime = Math.abs(now - date);
            const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
            
            if (diffDays === 1) {
                return 'Today';
            } else if (diffDays === 2) {
                return 'Yesterday';
            } else if (diffDays <= 7) {
                return `${diffDays - 1} days ago`;
            } else {
                return date.toLocaleDateString();
            }
        } catch (e) {
            return 'Unknown';
        }
    }
}

// Add CSS animations for notifications
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from { transform: translateX(100%); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }
    
    @keyframes slideOut {
        from { transform: translateX(0); opacity: 1; }
        to { transform: translateX(100%); opacity: 0; }
    }
`;
document.head.appendChild(style);

// Initialize the application when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new TutoringLeadApp();
});