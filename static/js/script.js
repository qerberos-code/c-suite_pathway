// JavaScript for C-Suite Pathway Program

document.addEventListener('DOMContentLoaded', function() {
    // Add fade-in animation to cards
    const cards = document.querySelectorAll('.card, .message-item, .event-card');
    cards.forEach((card, index) => {
        card.style.animationDelay = `${index * 0.1}s`;
        card.classList.add('fade-in');
    });

    // Form validation for registration
    const registerForm = document.querySelector('form[action*="register"]');
    if (registerForm) {
        registerForm.addEventListener('submit', function(e) {
            const password = document.getElementById('password');
            const confirmPassword = document.getElementById('confirm_password');
            
            if (password.value !== confirmPassword.value) {
                e.preventDefault();
                alert('Passwords do not match!');
                return false;
            }
            
            if (password.value.length < 8) {
                e.preventDefault();
                alert('Password must be at least 8 characters long!');
                return false;
            }
        });
    }

    // Auto-hide alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            alert.classList.add('fade');
            setTimeout(() => {
                alert.remove();
            }, 300);
        }, 5000);
    });

    // Smooth scrolling for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });

    // Add loading state to buttons on form submission
    document.querySelectorAll('form').forEach(form => {
        form.addEventListener('submit', function() {
            const submitBtn = this.querySelector('button[type="submit"]');
            if (submitBtn) {
                submitBtn.classList.add('loading');
                submitBtn.disabled = true;
                submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Processing...';
            }
        });
    });

    // Interactive tooltips for feature cards
    const featureCards = document.querySelectorAll('.feature-card');
    featureCards.forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-5px) scale(1.02)';
        });
        
        card.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0) scale(1)';
        });
    });

    // Message character counter
    const messageTextarea = document.getElementById('content');
    if (messageTextarea) {
        const counter = document.createElement('div');
        counter.className = 'form-text text-end';
        counter.id = 'char-counter';
        messageTextarea.parentNode.appendChild(counter);
        
        function updateCounter() {
            const remaining = 1000 - messageTextarea.value.length;
            counter.textContent = `${remaining} characters remaining`;
            counter.style.color = remaining < 100 ? '#dc3545' : '#6c757d';
        }
        
        messageTextarea.addEventListener('input', updateCounter);
        updateCounter();
    }

    // FAQ search functionality
    const faqSearch = document.createElement('input');
    faqSearch.type = 'text';
    faqSearch.className = 'form-control mb-3';
    faqSearch.placeholder = 'Search FAQs...';
    
    const faqContainer = document.querySelector('#faqAccordion');
    if (faqContainer) {
        faqContainer.parentNode.insertBefore(faqSearch, faqContainer);
        
        faqSearch.addEventListener('input', function() {
            const searchTerm = this.value.toLowerCase();
            const faqItems = faqContainer.querySelectorAll('.accordion-item');
            
            faqItems.forEach(item => {
                const question = item.querySelector('.accordion-button').textContent.toLowerCase();
                const answer = item.querySelector('.accordion-body').textContent.toLowerCase();
                
                if (question.includes(searchTerm) || answer.includes(searchTerm)) {
                    item.style.display = 'block';
                } else {
                    item.style.display = 'none';
                }
            });
        });
    }

    // Event date validation
    const eventDateInput = document.getElementById('date');
    if (eventDateInput) {
        eventDateInput.addEventListener('change', function() {
            const selectedDate = new Date(this.value);
            const now = new Date();
            
            if (selectedDate < now) {
                alert('Please select a future date and time.');
                this.value = '';
            }
        });
    }

    // Responsive navigation toggle
    const navbarToggler = document.querySelector('.navbar-toggler');
    const navbarCollapse = document.querySelector('.navbar-collapse');
    
    if (navbarToggler && navbarCollapse) {
        navbarToggler.addEventListener('click', function() {
            navbarCollapse.classList.toggle('show');
        });
        
        // Close mobile menu when clicking outside
        document.addEventListener('click', function(e) {
            if (!navbarToggler.contains(e.target) && !navbarCollapse.contains(e.target)) {
                navbarCollapse.classList.remove('show');
            }
        });
    }

    // Add confirmation for logout
    const logoutLink = document.querySelector('a[href*="logout"]');
    if (logoutLink) {
        logoutLink.addEventListener('click', function(e) {
            if (!confirm('Are you sure you want to logout?')) {
                e.preventDefault();
            }
        });
    }

    // Real-time message preview
    const messageTitle = document.getElementById('title');
    const messageContent = document.getElementById('content');
    const previewContainer = document.createElement('div');
    previewContainer.className = 'mt-3 p-3 border rounded bg-light';
    previewContainer.style.display = 'none';
    
    if (messageTitle && messageContent) {
        messageTitle.parentNode.appendChild(previewContainer);
        
        function updatePreview() {
            if (messageTitle.value || messageContent.value) {
                previewContainer.style.display = 'block';
                previewContainer.innerHTML = `
                    <h6>Preview:</h6>
                    <strong>${messageTitle.value || 'Untitled'}</strong>
                    <p class="mb-0 mt-2">${messageContent.value || 'No content yet...'}</p>
                `;
            } else {
                previewContainer.style.display = 'none';
            }
        }
        
        messageTitle.addEventListener('input', updatePreview);
        messageContent.addEventListener('input', updatePreview);
    }

    // Add keyboard shortcuts
    document.addEventListener('keydown', function(e) {
        // Ctrl/Cmd + Enter to submit forms
        if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
            const activeForm = document.querySelector('form:focus-within');
            if (activeForm) {
                const submitBtn = activeForm.querySelector('button[type="submit"]');
                if (submitBtn) {
                    submitBtn.click();
                }
            }
        }
        
        // Escape key to close modals/alerts
        if (e.key === 'Escape') {
            const alerts = document.querySelectorAll('.alert');
            alerts.forEach(alert => alert.remove());
        }
    });

    // Add success animations
    function addSuccessAnimation(element) {
        element.classList.add('success-animation');
        setTimeout(() => {
            element.classList.remove('success-animation');
        }, 1000);
    }

    // Monitor for successful form submissions
    const observer = new MutationObserver(function(mutations) {
        mutations.forEach(function(mutation) {
            if (mutation.type === 'childList') {
                mutation.addedNodes.forEach(function(node) {
                    if (node.nodeType === 1 && node.classList && node.classList.contains('alert-success')) {
                        addSuccessAnimation(node);
                    }
                });
            }
        });
    });

    observer.observe(document.body, {
        childList: true,
        subtree: true
    });
});

// Add CSS for animations
const style = document.createElement('style');
style.textContent = `
    .success-animation {
        animation: successPulse 1s ease-in-out;
    }
    
    @keyframes successPulse {
        0% { transform: scale(1); }
        50% { transform: scale(1.05); }
        100% { transform: scale(1); }
    }
    
    .fade {
        opacity: 0;
        transition: opacity 0.3s ease;
    }
`;
document.head.appendChild(style);
