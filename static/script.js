// Clear previous analysis results on page load
window.addEventListener('DOMContentLoaded', function() {
    clearAllResults();
});

// File Upload UI Logic
const fileUpload = document.getElementById('fileUpload');
const uploadUI = document.getElementById('uploadUI');
const successUI = document.getElementById('successUI');
const fileNameDisplay = document.getElementById('fileNameDisplay');
const dropZone = document.getElementById('dropZone');

// File upload event handler
if (fileUpload) {
    fileUpload.addEventListener('change', function(e) {
        if (e.target.files && e.target.files.length > 0) {
            const fileName = e.target.files[0].name;
            
            if (fileNameDisplay) {
                fileNameDisplay.textContent = fileName;
            }
            
            if (uploadUI) {
                uploadUI.classList.add('hidden');
                uploadUI.classList.remove('flex');
            }
            if (successUI) {
                successUI.classList.remove('hidden');
                successUI.classList.add('flex');
            }
        }
    });
}

function resetFileInput() {
    if (fileUpload) {
        fileUpload.value = '';
    }
    if (uploadUI) {
        uploadUI.classList.remove('hidden');
        uploadUI.classList.add('flex');
    }
    if (successUI) {
        successUI.classList.add('hidden');
        successUI.classList.remove('flex');
    }
}

function clearAllResults() {
    const defaultMessage = '<div class="h-full flex items-center justify-center text-text-muted dark:text-slate-500 italic text-sm">Waiting for analysis...</div>';
    
    const outJobSearch = document.getElementById('outJobSearch');
    const outSkillGaps = document.getElementById('outSkillGaps');
    const outProjects = document.getElementById('outProjects');
    const outGithub = document.getElementById('outGithub');
    
    if (outJobSearch) outJobSearch.innerHTML = defaultMessage;
    if (outSkillGaps) outSkillGaps.innerHTML = defaultMessage;
    if (outProjects) outProjects.innerHTML = defaultMessage;
    if (outGithub) outGithub.innerHTML = defaultMessage;
}

// Dynamic status updater with user-friendly messages
function updateStatus(message, type = 'idle') {
    const statusText = document.getElementById('statusText');
    const statusIndicator = document.getElementById('statusIndicator');
    
    if (statusText) {
        statusText.textContent = message;
    }
    
    if (statusIndicator) {
        // Remove all possible classes
        statusIndicator.classList.remove(
            'bg-slate-300', 'dark:bg-slate-600',
            'bg-blue-500', 'animate-pulse',
            'bg-green-500',
            'bg-red-500'
        );
        
        // Add appropriate classes based on type
        switch(type) {
            case 'processing':
                statusIndicator.classList.add('bg-blue-500', 'animate-pulse');
                break;
            case 'success':
                statusIndicator.classList.add('bg-green-500');
                break;
            case 'error':
                statusIndicator.classList.add('bg-red-500');
                break;
            default: // idle
                statusIndicator.classList.add('bg-slate-300', 'dark:bg-slate-600');
        }
    }
}

// Dark mode toggle
const themeToggle = document.getElementById('themeToggle');
if (themeToggle) {
    const savedTheme = localStorage.getItem('theme') || 'light';
    if (savedTheme === 'dark') {
        document.documentElement.classList.add('dark');
    }
    
    themeToggle.addEventListener('click', () => {
        document.documentElement.classList.toggle('dark');
        const isDark = document.documentElement.classList.contains('dark');
        localStorage.setItem('theme', isDark ? 'dark' : 'light');
    });
}

// Store analysis data globally for download
let lastAnalysisData = null;

// Download roadmap function
function downloadRoadmap() {
    if (!lastAnalysisData) {
        alert('Please complete an analysis first before downloading');
        return;
    }
    
    let markdown = `# Career Development Roadmap\n\n`;
    markdown += `**Generated on:** ${new Date().toLocaleString()}\n\n`;
    markdown += `---\n\n`;
    markdown += `## 💼 Job Market Insights\n\n${lastAnalysisData.job_search}\n\n`;
    markdown += `---\n\n`;
    markdown += `## 📈 Skills to Develop\n\n${lastAnalysisData.skill_gaps}\n\n`;
    markdown += `---\n\n`;
    markdown += `## 💡 Project Ideas\n\n${lastAnalysisData.project_ideas}\n\n`;
    markdown += `---\n\n`;
    markdown += `## 🔧 GitHub Analysis\n\n${lastAnalysisData.github_summary}\n\n`;
    
    const blob = new Blob([markdown], { type: 'text/markdown' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `career-roadmap-${Date.now()}.md`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
}

const downloadBtn = document.getElementById('downloadBtn');
if (downloadBtn) {
    downloadBtn.addEventListener('click', downloadRoadmap);
}

// Form submission with dynamic status updates
const form = document.getElementById('analyzeForm');
const analyzeBtn = document.getElementById('analyzeBtn');

if (form) {
    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        // Clear previous results
        clearAllResults();
        lastAnalysisData = null;
        
        // Check file selection
        if (!fileUpload.files || fileUpload.files.length === 0) {
            alert('Please upload your resume first');
            return;
        }
        
        // Disable button and update UI
        if (analyzeBtn) {
            analyzeBtn.disabled = true;
            analyzeBtn.innerHTML = '<span class="material-symbols-outlined text-[18px] animate-spin">progress_activity</span><span>Analyzing...</span>';
            analyzeBtn.classList.add('opacity-75', 'cursor-not-allowed');
        }
        
        // Dynamic status updates
        updateStatus('Uploading your resume...', 'processing');
        
        const formData = new FormData();
        formData.append('resume', fileUpload.files[0]);
        formData.append('target_role', document.getElementById('targetRole').value);
        formData.append('github_username', document.getElementById('githubUsername').value);
        
        // Simulated progress updates
        const statusUpdates = [
            { delay: 1000, message: 'Reading your resume...', type: 'processing' },
            { delay: 3000, message: 'Analyzing your experience...', type: 'processing' },
            { delay: 6000, message: 'Researching job market trends...', type: 'processing' },
            { delay: 9000, message: 'Identifying skill gaps...', type: 'processing' },
            { delay: 12000, message: 'Generating project recommendations...', type: 'processing' },
            { delay: 15000, message: 'Analyzing your GitHub profile...', type: 'processing' },
            { delay: 18000, message: 'Finalizing your career roadmap...', type: 'processing' }
        ];
        
        const timeouts = [];
        statusUpdates.forEach(update => {
            const timeout = setTimeout(() => {
                updateStatus(update.message, update.type);
            }, update.delay);
            timeouts.push(timeout);
        });
        
        try {
            const response = await fetch('/analyze', {
                method: 'POST',
                body: formData
            });
            const data = await response.json();
            
            // Clear all status update timeouts
            timeouts.forEach(timeout => clearTimeout(timeout));
            
            if (data.status === 'success') {
                // Store data for download
                lastAnalysisData = {
                    job_search: data.job_search || '',
                    skill_gaps: data.skill_gaps || '',
                    project_ideas: data.project_ideas || '',
                    github_summary: data.github_summary || ''
                };
                
                updateStatus('Analysis complete! Review your results below', 'success');
                
                // Render results
                const outJobSearch = document.getElementById('outJobSearch');
                const outSkillGaps = document.getElementById('outSkillGaps');
                const outProjects = document.getElementById('outProjects');
                const outGithub = document.getElementById('outGithub');
                
                if (outJobSearch) outJobSearch.innerHTML = marked.parse(data.job_search || "No data available.");
                if (outSkillGaps) outSkillGaps.innerHTML = marked.parse(data.skill_gaps || "No data available.");
                if (outProjects) outProjects.innerHTML = marked.parse(data.project_ideas || "No data available.");
                if (outGithub) outGithub.innerHTML = marked.parse(data.github_summary || "No data available.");
                
            } else {
                updateStatus('Analysis failed. Please try again.', 'error');
            }
        } catch (err) {
            console.error('Network error:', err);
            timeouts.forEach(timeout => clearTimeout(timeout));
            updateStatus('Connection error. Please check your internet.', 'error');
        } finally {
            // Reset form and button
            form.reset();
            resetFileInput();
            
            if (analyzeBtn) {
                analyzeBtn.disabled = false;
                analyzeBtn.innerHTML = '<span>Analyze My Profile</span><span class="material-symbols-outlined text-[18px]">arrow_forward</span>';
                analyzeBtn.classList.remove('opacity-75', 'cursor-not-allowed');
            }
            
            // Reset status after 5 seconds
            setTimeout(() => {
                if (lastAnalysisData) {
                    updateStatus('Ready to analyze', 'idle');
                }
            }, 5000);
        }
    });
}
