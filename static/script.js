// API Configuration
const API_BASE_URL = window.location.origin; // Use same origin in production

// DOM Elements
const form = document.getElementById('careerForm');
const fileInput = document.getElementById('resume');
const fileName = document.getElementById('fileName');
const submitBtn = document.getElementById('submitBtn');
const submitText = document.getElementById('submitText');
const submitLoader = document.getElementById('submitLoader');
const terminalContainer = document.getElementById('terminal-container');
const terminalLogs = document.getElementById('terminal-logs');
const terminalStatus = document.getElementById('terminal-status');
const resultsSection = document.getElementById('results');

// Configure marked.js for secure markdown rendering
if (typeof marked !== 'undefined') {
    marked.setOptions({
        breaks: true,
        gfm: true,
        headerIds: false,
        mangle: false
    });
}

// File input change handler
fileInput.addEventListener('change', (e) => {
    const file = e.target.files[0];
    if (file) {
        fileName.textContent = file.name;
        fileName.style.color = '#FF6F00';
    } else {
        fileName.textContent = 'No file chosen';
        fileName.style.color = '#666';
    }
});

// Form submission handler with SSE streaming
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
    
    // Show and initialize terminal
    terminalContainer.style.display = 'block';
    terminalLogs.innerHTML = '';
    terminalStatus.innerText = 'PROCESSING...';
    terminalStatus.style.color = '#34d399';
    resultsSection.classList.add('hidden');
    
    // Reset file input to clear the filename display
    fileInput.value = '';
    fileName.textContent = 'No file chosen';
    fileName.style.color = '#666';
    
    // Reset file input to blank state
    fileInput.value = '';
    fileName.textContent = 'No file chosen';
    fileName.style.color = '#666';
    
    // Scroll to terminal
    setTimeout(() => {
        terminalContainer.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }, 100);
    
    try {
        // Use SSE endpoint for live streaming
        await streamAnalysis(formData);
        
    } catch (error) {
        console.error('Error:', error);
        addTerminalLog(`❌ Error: ${error.message}`, '#e06c75');
        terminalStatus.innerText = 'ERROR';
        terminalStatus.style.color = '#e06c75';
        showError(error.message || 'Failed to analyze. Please try again.');
        setLoadingState(false);
    }
});

// Stream analysis with Server-Sent Events
async function streamAnalysis(formData) {
    return new Promise((resolve, reject) => {
        // Create SSE connection
        const url = `${API_BASE_URL}/analyze-stream`;
        
        fetch(url, {
            method: 'POST',
            body: formData
        })
        .then(async response => {
            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                throw new Error(errorData.detail || `Server error: ${response.status}`);
            }
            
            const reader = response.body.getReader();
            const decoder = new TextDecoder();
            let buffer = '';
            
            // Read stream
            while (true) {
                const { done, value } = await reader.read();
                
                if (done) break;
                
                // Decode chunk
                buffer += decoder.decode(value, { stream: true });
                
                // Process complete messages
                const lines = buffer.split('\n\n');
                buffer = lines.pop(); // Keep incomplete message in buffer
                
                for (const line of lines) {
                    if (line.startsWith('data: ')) {
                        const data = JSON.parse(line.slice(6));
                        handleStreamMessage(data);
                        
                        // Check if done
                        if (data.status === 'done') {
                            setLoadingState(false);
                            
                            if (data.error) {
                                reject(new Error(data.error));
                            } else if (data.data) {
                                // Mark as complete
                                terminalStatus.innerText = 'COMPLETE';
                                terminalStatus.style.color = '#60a5fa';
                                
                                const successLine = document.createElement('div');
                                successLine.innerText = "✅ [Complete] Structured response verified. Displaying report below.";
                                successLine.style.color = "#60a5fa";
                                successLine.style.marginTop = "8px";
                                terminalLogs.appendChild(successLine);
                                
                                // Scroll to show success line
                                terminalLogs.scrollTop = terminalLogs.scrollHeight;
                                
                                // Display results after short delay
                                setTimeout(() => {
                                    displayResults(data.data);
                                }, 500);
                                
                                resolve();
                            }
                            return;
                        }
                    }
                }
            }
        })
        .catch(error => {
            setLoadingState(false);
            reject(error);
        });
    });
}

// Handle SSE stream messages
function handleStreamMessage(data) {
    if (data.message) {
        // Map status types to colors
        const colorMap = {
            'info': '#61afef',      // Blue
            'success': '#98c379',   // Green
            'tool': '#e5c07b',      // Yellow
            'error': '#e06c75',     // Red
            'done': '#56b6c2'       // Cyan
        };
        
        const color = colorMap[data.status] || '#34d399'; // Default green
        addTerminalLog(data.message, color);
    }
}

// Add log to terminal
function addTerminalLog(message, color = '#34d399') {
    const logLine = document.createElement('div');
    logLine.innerText = message;
    logLine.style.color = color;
    logLine.style.marginBottom = '4px';
    
    terminalLogs.appendChild(logLine);
    
    // Auto-scroll to bottom
    terminalLogs.scrollTop = terminalLogs.scrollHeight;
}

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

// Display results with markdown rendering
function displayResults(data) {
    // Show results section
    resultsSection.classList.remove('hidden');
    
    // Scroll to results
    setTimeout(() => {
        resultsSection.scrollIntoView({ behavior: 'smooth' });
    }, 300);
    
    // Populate result cards with markdown rendering
    const results = {
        jobSearchResult: data.job_search || 'No job search data available',
        skillGapResult: data.skill_gaps || 'No skill gap data available',
        projectIdeasResult: data.project_ideas || 'No project ideas available',
        githubReviewResult: data.github_summary || 'No GitHub review available'
    };
    
    // Animate results in with markdown
    Object.keys(results).forEach((key, index) => {
        setTimeout(() => {
            const element = document.getElementById(key);
            
            // Render markdown to HTML
            const markdownText = results[key];
            const htmlContent = typeof marked !== 'undefined' 
                ? marked.parse(markdownText) 
                : formatTextFallback(markdownText);
            
            element.innerHTML = htmlContent;
            element.style.opacity = '0';
            element.style.transform = 'translateY(20px)';
            
            setTimeout(() => {
                element.style.transition = 'all 0.5s ease';
                element.style.opacity = '1';
                element.style.transform = 'translateY(0)';
            }, 50);
        }, index * 150);
    });
}

// Fallback text formatting if marked.js fails to load
function formatTextFallback(text) {
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
    
    // Convert ## headers
    text = text.replace(/^##\s+(.+)$/gm, '<h4>$1</h4>');
    
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
        background: #f44336;
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
    fileName.style.color = '#666';
    resultsSection.classList.add('hidden');
    terminalContainer.style.display = 'none';
    terminalLogs.innerHTML = '';
    
    // Scroll to form
    form.scrollIntoView({ behavior: 'smooth' });
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

// Log initialization
console.log('Career Assistant Agent - Frontend Initialized with SSE');
console.log('API Base URL:', API_BASE_URL);
console.log('Marked.js loaded:', typeof marked !== 'undefined');
console.log('Terminal-style console ready');
