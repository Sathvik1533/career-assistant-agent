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

// Make sure event listener triggers properly
if (fileUpload) {
    fileUpload.addEventListener('change', function(e) {
        if (e.target.files && e.target.files.length > 0) {
            const fileName = e.target.files[0].name;
            
            // Update the filename display
            if (fileNameDisplay) {
                fileNameDisplay.textContent = fileName;
            }
            
            // Hide upload UI, show success UI
            if (uploadUI) {
                uploadUI.classList.add('hidden');
                uploadUI.classList.remove('flex');
            }
            if (successUI) {
                successUI.classList.remove('hidden');
                successUI.classList.add('flex');
            }
            
            // Update dropzone styling
            if (dropZone) {
                dropZone.classList.add('border-[#3b82f6]', 'bg-[#f1f5f9]');
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
    if (dropZone) {
        dropZone.classList.remove('border-[#3b82f6]', 'bg-[#f1f5f9]');
    }
}

function clearAllResults() {
    const defaultMessage = '<div class="h-full flex items-center justify-center text-outline-variant italic font-body-technical">Awaiting computation...</div>';
    
    const outJobSearch = document.getElementById('outJobSearch');
    const outSkillGaps = document.getElementById('outSkillGaps');
    const outProjects = document.getElementById('outProjects');
    const outGithub = document.getElementById('outGithub');
    
    if (outJobSearch) outJobSearch.innerHTML = defaultMessage;
    if (outSkillGaps) outSkillGaps.innerHTML = defaultMessage;
    if (outProjects) outProjects.innerHTML = defaultMessage;
    if (outGithub) outGithub.innerHTML = defaultMessage;
}

// Dark mode toggle
const themeToggle = document.getElementById('themeToggle');
if (themeToggle) {
    // Check for saved theme preference or default to light
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

// Clock Update
setInterval(() => {
    const now = new Date();
    const timestampEl = document.getElementById('timestamp');
    if (timestampEl) {
        timestampEl.textContent = now.toLocaleTimeString('en-US', { hour12: false });
    }
}, 1000);

// Store analysis data globally for PDF generation
let lastAnalysisData = null;

// Download PDF Roadmap
function downloadRoadmap() {
    if (!lastAnalysisData) {
        alert('Please run an analysis first before downloading the roadmap');
        return;
    }
    
    // Create markdown content
    let markdown = `# Career Development Roadmap\n\n`;
    markdown += `**Generated on:** ${new Date().toLocaleString()}\n\n`;
    markdown += `---\n\n`;
    markdown += `## 📊 Market Alignment Strategy\n\n${lastAnalysisData.job_search}\n\n`;
    markdown += `---\n\n`;
    markdown += `## 🎯 Skill Matrix Gaps\n\n${lastAnalysisData.skill_gaps}\n\n`;
    markdown += `---\n\n`;
    markdown += `## 💡 Portfolio Roadmap\n\n${lastAnalysisData.project_ideas}\n\n`;
    markdown += `---\n\n`;
    markdown += `## 🔧 GitHub Analysis\n\n${lastAnalysisData.github_summary}\n\n`;
    
    // Create and download file
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

// Attach download handler to button
const downloadBtn = document.getElementById('downloadBtn');
if (downloadBtn) {
    downloadBtn.addEventListener('click', downloadRoadmap);
}

// Form Submit & Real API Pipeline Logic
const form = document.getElementById('analyzeForm');
const analyzeBtn = document.getElementById('analyzeBtn');
const statusText = document.getElementById('statusText');
const statusIndicator = document.getElementById('statusIndicator');

if (form) {
    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        // Clear previous results when starting new analysis
        clearAllResults();
        lastAnalysisData = null;
        
        // Check if file is selected
        if (!fileUpload.files || fileUpload.files.length === 0) {
            alert('Please select a resume file first');
            return;
        }
        
        // 1. Establish active processing telemetry state
        if (analyzeBtn) {
            analyzeBtn.disabled = true;
            analyzeBtn.innerHTML = '<span class="material-symbols-outlined text-[16px] animate-spin">sync</span><span>PROCESSING</span>';
            analyzeBtn.classList.add('bg-secondary', 'cursor-not-allowed');
            analyzeBtn.classList.remove('bg-primary', 'hover:bg-[#1e293b]');
        }
        
        if (statusText) {
            statusText.textContent = "SYSTEM STATUS: COMPUTING // MULTI-TOOL AGENT RUNTIME ACTIVE";
        }
        
        if (statusIndicator) {
            statusIndicator.classList.remove('bg-outline', 'bg-error');
            statusIndicator.classList.add('bg-[#3b82f6]', 'animate-pulse');
        }
        
        // 2. Extract files and text properties into multi-part payload package
        const formData = new FormData();
        formData.append('resume', fileUpload.files[0]);
        formData.append('target_role', document.getElementById('targetRole').value);
        formData.append('github_username', document.getElementById('githubUsername').value);
        
        try {
            // 4. Fire network packet directly to our real API POST endpoint
            const response = await fetch('/analyze', {
                method: 'POST',
                body: formData
            });
            const data = await response.json();
            
            if (data.status === 'success') {
                // Store data for PDF download
                lastAnalysisData = {
                    job_search: data.job_search || '',
                    skill_gaps: data.skill_gaps || '',
                    project_ideas: data.project_ideas || '',
                    github_summary: data.github_summary || ''
                };
                
                if (statusText) {
                    statusText.textContent = "SYSTEM_STATUS: SUCCESS // PAYLOAD_COMPILED";
                }
                if (statusIndicator) {
                    statusIndicator.classList.remove('bg-[#3b82f6]', 'animate-pulse');
                    statusIndicator.classList.add('bg-[#10b981]');
                }
                
                // 5. Safely map keys explicitly using the marked library parser
                const outJobSearch = document.getElementById('outJobSearch');
                const outSkillGaps = document.getElementById('outSkillGaps');
                const outProjects = document.getElementById('outProjects');
                const outGithub = document.getElementById('outGithub');
                
                if (outJobSearch) outJobSearch.innerHTML = marked.parse(data.job_search || "Data null.");
                if (outSkillGaps) outSkillGaps.innerHTML = marked.parse(data.skill_gaps || "Data null.");
                if (outProjects) outProjects.innerHTML = marked.parse(data.project_ideas || "Data null.");
                if (outGithub) outGithub.innerHTML = marked.parse(data.github_summary || "Data null.");
            } else {
                if (statusIndicator) {
                    statusIndicator.classList.remove('bg-[#3b82f6]', 'animate-pulse');
                    statusIndicator.classList.add('bg-error');
                }
                if (statusText) {
                    statusText.textContent = `SYSTEM_ERROR: ${data.error || 'Execution aborted'}`;
                }
            }
        } catch (err) {
            console.error('Network error:', err);
            if (statusIndicator) {
                statusIndicator.classList.remove('bg-[#3b82f6]', 'animate-pulse');
                statusIndicator.classList.add('bg-error');
            }
            if (statusText) {
                statusText.textContent = `NETWORK_PIPELINE_ERROR: ${err.message}`;
            }
        } finally {
            // 3. Reset input selectors AFTER API call completes
            form.reset();
            resetFileInput();
            
            // 6. Restore action button state parameters safely
            if (analyzeBtn) {
                analyzeBtn.disabled = false;
                analyzeBtn.innerHTML = '<span>Analyze Profile</span><span class="material-symbols-outlined text-[16px]">memory</span>';
                analyzeBtn.classList.remove('bg-secondary', 'cursor-not-allowed');
                analyzeBtn.classList.add('bg-primary', 'hover:bg-[#1e293b]');
            }
            
            setTimeout(() => {
                if (statusIndicator) {
                    statusIndicator.classList.remove('bg-[#10b981]', 'bg-error');
                    statusIndicator.classList.add('bg-outline');
                }
                if (statusText) {
                    statusText.textContent = "SYSTEM_STATUS: IDLE // AWAITING_PAYLOAD";
                }
            }, 4000);
        }
    });
}
