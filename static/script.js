// API Configuration
const API_BASE_URL = window.location.origin;

// DOM Elements
const form = document.getElementById('careerForm');
const fileConsoleBar = document.getElementById('file-console-bar');
const fileInput = document.getElementById('resume');
const fileStatusText = document.getElementById('file-status-text');
const analyzeBtn = document.getElementById('analyze-btn');
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

// File console bar interactivity
fileConsoleBar.addEventListener('click', () => {
    fileInput.click();
});

fileInput.addEventListener('change', () => {
    if (fileInput.files.length) {
        const name = fileInput.files[0].name;
        fileStatusText.innerText = `FS_LOADED // LOCAL_PATH: /src/${name}`;
        fileStatusText.style.color = '#34d399';
        fileConsoleBar.style.borderColor = '#10b981';
        fileConsoleBar.style.borderLeftColor = '#10b981';
    }
});

// Form submission handler with SSE streaming
form.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    // Get form data
    const resume = fileInput.files[0];
    const targetRole = document.getElementById('targetRole').value;
    const githubUsername = document.getElementById('githubUsername').value;
    
    // Validation
    if (!resume) {
        alert('⚠️ ERROR: No payload mounted. Please select a resume file.');
        return;
    }
    
    if (resume.type !== 'application/pdf') {
        alert('⚠️ ERROR: Invalid payload format. Please upload a PDF file.');
        return;
    }
    
    if (resume.size > 10 * 1024 * 1024) {
        alert('⚠️ ERROR: Payload exceeds size limit (10MB)');
        return;
    }
    
    // Prepare form data
    const formData = new FormData();
    formData.append('resume', resume);
    formData.append('target_role', targetRole);
    formData.append('github_username', githubUsername);
    
    // Show terminal and hide results
    terminalContainer.style.display = 'block';
    terminalLogs.innerHTML = '';
    terminalStatus.innerText = 'PROCESSING...';
    terminalStatus.style.color = '#34d399';
    resultsSection.classList.add('hidden');
    
    // Reset file input
    fileInput.value = '';
    fileStatusText.innerText = 'PATH: (no_payload_allocated)';
    fileStatusText.style.color = '#475569';
    fileConsoleBar.style.borderColor = '#1e293b';
    fileConsoleBar.style.borderLeftColor = '#3b82f6';
    
    // Disable button
    analyzeBtn.disabled = true;
    analyzeBtn.innerText = 'EXECUTING...';
    
    try {
        // Create EventSource for SSE
        const eventSource = new EventSource(
            `${API_BASE_URL}/analyze-stream?` + 
            `target_role=${encodeURIComponent(targetRole)}&` +
            `github_username=${encodeURIComponent(githubUsername)}`
        );
        
        // Use fetch to upload file first
        const response = await fetch(`${API_BASE_URL}/analyze-stream`, {
            method: 'POST',
            body: formData
        });
        
        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        
        while (true) {
            const { done, value } = await reader.read();
            if (done) break;
            
            const chunk = decoder.decode(value);
            const lines = chunk.split('\n');
            
            for (const line of lines) {
                if (line.startsWith('data: ')) {
                    try {
                        const data = JSON.parse(line.slice(6));
                        
                        if (data.status === 'done') {
                            // Analysis complete - show results
                            terminalStatus.innerText = 'COMPLETE';
                            terminalStatus.style.color = '#60a5fa';
                            
                            // Add completion log
                            const completionLog = document.createElement('div');
                            completionLog.className = 'log-line';
                            completionLog.style.color = '#34d399';
                            completionLog.innerHTML = '✅ [Complete] Structured response verified and transmitted';
                            terminalLogs.appendChild(completionLog);
                            
                            // Display results
                            displayResults(data.data);
                            
                        } else if (data.status === 'error') {
                            // Error occurred
                            terminalStatus.innerText = 'ERROR';
                            terminalStatus.style.color = '#ef4444';
                            
                            const errorLog = document.createElement('div');
                            errorLog.className = 'log-line';
                            errorLog.style.color = '#ef4444';
                            errorLog.innerHTML = `❌ ${data.message || 'Analysis failed'}`;
                            terminalLogs.appendChild(errorLog);
                            
                        } else {
                            // Status update
                            const logLine = document.createElement('div');
                            logLine.className = 'log-line';
                            
                            if (data.status === 'success') {
                                logLine.style.color = '#34d399';
                            } else if (data.status === 'tool') {
                                logLine.style.color = '#60a5fa';
                            } else {
                                logLine.style.color = '#94a3b8';
                            }
                            
                            logLine.innerHTML = data.message;
                            terminalLogs.appendChild(logLine);
                            terminalLogs.scrollTop = terminalLogs.scrollHeight;
                        }
                    } catch (err) {
                        console.error('Parse error:', err);
                    }
                }
            }
        }
        
    } catch (error) {
        console.error('Analysis error:', error);
        terminalStatus.innerText = 'ERROR';
        terminalStatus.style.color = '#ef4444';
        
        const errorLog = document.createElement('div');
        errorLog.className = 'log-line';
        errorLog.style.color = '#ef4444';
        errorLog.innerHTML = `❌ ${error.message}`;
        terminalLogs.appendChild(errorLog);
    } finally {
        // Re-enable button
        analyzeBtn.disabled = false;
        analyzeBtn.innerText = 'RUN EXECUTION_PIPELINE() ➔';
    }
});

function displayResults(data) {
    // Show results section
    resultsSection.classList.remove('hidden');
    resultsSection.style.display = 'grid';
    
    // Render markdown content
    document.getElementById('job-search-content').innerHTML = marked.parse(data.job_search || 'No data available');
    document.getElementById('skill-gaps-content').innerHTML = marked.parse(data.skill_gaps || 'No data available');
    document.getElementById('project-ideas-content').innerHTML = marked.parse(data.project_ideas || 'No data available');
    document.getElementById('github-summary-content').innerHTML = marked.parse(data.github_summary || 'No data available');
}
