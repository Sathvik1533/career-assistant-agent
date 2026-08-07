// File Upload UI Logic
const fileUpload = document.getElementById('fileUpload');
const uploadUI = document.getElementById('uploadUI');
const successUI = document.getElementById('successUI');
const fileNameDisplay = document.getElementById('fileNameDisplay');
const dropZone = document.getElementById('dropZone');

// Make sure event listener triggers properly
if (fileUpload) {
    fileUpload.addEventListener('change', function(e) {
        console.log('File selected:', e.target.files); // Debug log
        if (e.target.files && e.target.files.length > 0) {
            const fileName = e.target.files[0].name;
            console.log('Updating UI with filename:', fileName); // Debug log
            
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

// Clock Update
setInterval(() => {
    const now = new Date();
    const timestampEl = document.getElementById('timestamp');
    if (timestampEl) {
        timestampEl.textContent = now.toLocaleTimeString('en-US', { hour12: false });
    }
}, 1000);

// Form Submit & Real API Pipeline Logic
const form = document.getElementById('analyzeForm');
const analyzeBtn = document.getElementById('analyzeBtn');
const statusText = document.getElementById('statusText');
const statusIndicator = document.getElementById('statusIndicator');

if (form) {
    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        
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
