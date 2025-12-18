/**
 * JavaScript for category filtering on role selection page
 */

document.addEventListener('DOMContentLoaded', function() {
    const categoryTabs = document.querySelectorAll('.category-tab');
    const roleCards = document.querySelectorAll('.role-card-wrapper');
    const noResults = document.getElementById('no-results');
    
    // Initialize all cards as visible
    roleCards.forEach(card => {
        card.style.display = 'block';
        card.style.opacity = '1';
        card.style.transform = 'translateY(0)';
    });
    
    // Initialize - ensure "All" tab is active and all cards are visible
    if (categoryTabs.length > 0) {
        const allTab = Array.from(categoryTabs).find(tab => tab.getAttribute('data-category') === 'All');
        if (allTab) {
            allTab.classList.add('active');
        }
    }
    
    // Add click handlers to category tabs
    categoryTabs.forEach(tab => {
        tab.addEventListener('click', function() {
            const category = this.getAttribute('data-category');
            
            // Update active tab
            categoryTabs.forEach(t => t.classList.remove('active'));
            this.classList.add('active');
            
            // Filter cards
            filterByCategory(category);
        });
    });
    
    function filterByCategory(category) {
        let visibleCount = 0;
        
        roleCards.forEach(card => {
            const cardCategory = card.getAttribute('data-category');
            
            if (category === 'All' || cardCategory === category) {
                // Show card with fade-in animation
                card.style.display = 'block';
                card.style.opacity = '0';
                card.style.transform = 'translateY(20px)';
                
                // Trigger animation
                setTimeout(() => {
                    card.style.transition = 'opacity 0.3s ease, transform 0.3s ease';
                    card.style.opacity = '1';
                    card.style.transform = 'translateY(0)';
                }, 10);
                
                visibleCount++;
            } else {
                // Hide card with fade-out animation
                card.style.transition = 'opacity 0.2s ease, transform 0.2s ease';
                card.style.opacity = '0';
                card.style.transform = 'translateY(-10px)';
                
                setTimeout(() => {
                    card.style.display = 'none';
                }, 200);
            }
        });
        
        // Show/hide "no results" message
        if (visibleCount === 0) {
            noResults.style.display = 'block';
            noResults.style.opacity = '0';
            setTimeout(() => {
                noResults.style.transition = 'opacity 0.3s ease';
                noResults.style.opacity = '1';
            }, 10);
        } else {
            noResults.style.opacity = '0';
            setTimeout(() => {
                noResults.style.display = 'none';
            }, 200);
        }
    }
});

