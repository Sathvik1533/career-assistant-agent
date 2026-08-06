// API Configuration
const API_BASE_URL = 'https://career-assistant-agent-bet6.onrender.com';

// DOM Elements
const form = document.getElementById('careerForm');
const fileInput = document.getElementById('resume');
const fileName = document.getElementById('fileName');
const submitBtn = document.getElementById('submitBtn');
const submitText = document.getElementById('submitText');
const submitLoader = document.getElementById('submitLoader');
const resultsSection = document.getElementById('results');
const analyzerForm = document.getElementById('analyzer-form');

// File input change handler
fileInput.addEventListener('change', (e) => {
    const file = e.target.files[0];
    if (file) {
        fileName.textContent = file.name;
        fileName.style.color = 'var(--primary)';
    } else {
        fileName.textContent = 'No file chosen';
        fileName.style.color = 'var(--text-secondary)';
    }
});

// Smooth scroll to form
function scrollToForm() {
    analyzerForm.scrollIntoView({ behavior: 'smooth' });
}

// Form submission handler
form.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    // Get form data
    const formData = new FormData();
    const resume = fileInput.files[0];
    const targetRole = document.getElementById('targetRole').value;
    const githubUsername = document.getElementById('githubUsername').value;
    
    // Validation
    if (!resume) {
        showError('Please upload your resume');
        return;
    }
    
    if (resume.type !== 'application/pdf') {
        showError('Please upload a PDF file');
        return;
    }
    
    if (resume.size > 10 * 1024 * 1024) { // 10MB limit
        showError('File size must be less than 10MB');
        return;
    }
    
    // Prepare form data
    formData.append('resume', resume);
    formData.append('target_role', targetRole);
    formData.append('github_username', githubUsername);
    
    // Show loading state
    setLoadingState(true);
    
    try {
        // Make API request
        const response = await fetch(`${API_BASE_URL}/analyze`, {
            method: 'POST',
            body: formData
        });
        
        if (!response.ok) {
            const errorData = await response.json().catch(() => ({}));
            throw new Error(errorData.detail || `Server error: ${response.status}`);
        }
        
        const data = await response.json();
        
        // Display results
        displayResults(data);
        
        // Scroll to results
        setTimeout(() => {
            resultsSection.scrollIntoView({ behavior: 'smooth' });
        }, 300);
        
    } catch (error) {
        console.error('Error:', error);
        showError(error.message || 'Failed to analyze. Please try again.');
    } finally {
        setLoadingState(false);
    }
});

// Set loading state
function setLoadingState(isLoading) {
    submitBtn.disabled = isLoading;
    
    if (isLoading) {
        submitText.classList.add('hidden');
        submitLoader.classList.remove('hidden');
    } else {
        submitText.classList.remove('hidden');
        submitLoader.classList.add('hidden');
    }
}

// Display results
function displayResults(data) {
    // Show results section
    resultsSection.classList.remove('hidden');
    
    // Populate result cards
    const results = {
        jobSearchResult: data.job_search || data.output?.job_search || 'No job search data available',
        skillGapResult: data.skill_gaps || data.output?.skill_gaps || 'No skill gap data available',
        projectIdeasResult: data.project_ideas || data.output?.project_ideas || 'No project ideas available',
        githubReviewResult: data.github_summary || data.output?.github_summary || 'No GitHub review available'
    };
    
    // Animate results in
    Object.keys(results).forEach((key, index) => {
        setTimeout(() => {
            const element = document.getElementById(key);
            element.innerHTML = formatText(results[key]);
            element.style.opacity = '0';
            element.style.transform = 'translateY(20px)';
            
            setTimeout(() => {
                element.style.transition = 'all 0.5s ease';
                element.style.opacity = '1';
                element.style.transform = 'translateY(0)';
            }, 50);
        }, index * 100);
    });
}

// Format text for better readability
function formatText(text) {
    if (!text || typeof text !== 'string') return 'No data available';
    
    // Replace numbered lists
    text = text.replace(/(\d+)\.\s/g, '<strong>$1.</strong> ');
    
    // Replace bullet points
    text = text.replace(/•/g, '•');
    
    // Replace double newlines with paragraph breaks
    text = text.replace(/\n\n/g, '<br><br>');
    
    // Replace single newlines with line breaks
    text = text.replace(/\n/g, '<br>');
    
    // Highlight important sections
    text = text.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
    
    return text;
}

// Show error message
function showError(message) {
    // Create error notification
    const errorDiv = document.createElement('div');
    errorDiv.className = 'error-notification';
    errorDiv.style.cssText = `
        position: fixed;
        top: 24px;
        right: 24px;
        background: var(--error);
        color: white;
        padding: 16px 24px;
        border-radius: 12px;
        box-shadow: 0 8px 30px rgba(244, 67, 54, 0.3);
        z-index: 2000;
        animation: slideIn 0.3s ease;
        max-width: 400px;
    `;
    errorDiv.textContent = message;
    
    document.body.appendChild(errorDiv);
    
    // Remove after 5 seconds
    setTimeout(() => {
        errorDiv.style.animation = 'slideOut 0.3s ease';
        setTimeout(() => errorDiv.remove(), 300);
    }, 5000);
}

// Reset form
function resetForm() {
    form.reset();
    fileName.textContent = 'No file chosen';
    fileName.style.color = 'var(--text-secondary)';
    resultsSection.classList.add('hidden');
    
    // Scroll to form
    analyzerForm.scrollIntoView({ behavior: 'smooth' });
}

// Add CSS animations
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from {
            transform: translateX(400px);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
    
    @keyframes slideOut {
        from {
            transform: translateX(0);
            opacity: 1;
        }
        to {
            transform: translateX(400px);
            opacity: 0;
        }
    }
`;
document.head.appendChild(style);

// Handle smooth scrolling for navigation links
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            target.scrollIntoView({ behavior: 'smooth' });
        }
    });
});

// Add scroll-based header shadow
let lastScroll = 0;
const header = document.querySelector('.header');

window.addEventListener('scroll', () => {
    const currentScroll = window.pageYOffset;
    
    if (currentScroll > 50) {
        header.style.boxShadow = '0 4px 20px rgba(0, 0, 0, 0.3)';
    } else {
        header.style.boxShadow = 'none';
    }
    
    lastScroll = currentScroll;
});

// Add loading animation to result cards
function showLoadingSkeleton() {
    const resultCards = document.querySelectorAll('.result-content');
    resultCards.forEach(card => {
        card.innerHTML = '<div class="skeleton"></div>';
    });
}

// Log initialization
console.log('Career Assistant Agent - Frontend Initialized');
console.log('API Base URL:', API_BASE_URL);
