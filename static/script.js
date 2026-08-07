// File Upload UI Logic
const fileUpload = document.getElementById('fileUpload');
const uploadUI = document.getElementById('uploadUI');
const successUI = document.getElementById('successUI');
const fileNameDisplay = document.getElementById('fileNameDisplay');
const dropZone = document.getElementById('dropZone');

fileUpload.addEventListener('change', (e) => {
    if (e.target.files.length > 0) {
        const fileName = e.target.files[0].name;
        fileNameDisplay.textContent = fileName;
        uploadUI.classList.add('hidden');
        uploadUI.classList.remove('flex');
        successUI.classList.remove('hidden');
        successUI.classList.add('flex');
        dropZone.classList.add('border-[#3b82f6]', 'bg-[#f1f5f9]');
    } else {
        resetFileInput();
    }
});

function resetFileInput() {
    fileUpload.value = '';
    uploadUI.classList.remove('hidden');
    uploadUI.classList.add('flex');
    successUI.classList.add('hidden');
    successUI.classList.remove('flex');
    dropZone.classList.remove('border-[#3b82f6]', 'bg-[#f1f5f9]');
}

// Clock Update
setInterval(() => {
    const now = new Date();
    document.getElementById('timestamp').textContent = now.toLocaleTimeString('en-US', { hour12: false });
}, 1000);

// Form Submit & Real API Pipeline Logic
const form = document.getElementById('analyzeForm');
const analyzeBtn = document.getElementById('analyzeBtn');
const statusText = document.getElementById('statusText');
const statusIndicator = document.getElementById('statusIndicator');

form.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    // 1. Establish active processing telemetry state
    analyzeBtn.disabled = true;
    analyzeBtn.innerHTML = '<span class="material-symbols-outlined text-[16px] animate-spin">sync</span><span>PROCESSING</span>';
    analyzeBtn.classList.add('bg-secondary', 'cursor-not-allowed');
    analyzeBtn.classList.remove('bg-primary', 'hover:bg-[#1e293b]');
    statusText.textContent = "SYSTEM STATUS: COMPUTING // MULTI-TOOL AGENT RUNTIME ACTIVE";
    statusIndicator.classList.remove('bg-outline', 'bg-error');
    statusIndicator.classList.add('bg-[#3b82f6]', 'animate-pulse');
    
    // 2. Extract files and text properties into multi-part payload package
    const formData = new FormData();
    formData.append('resume', document.getElementById('fileUpload').files[0]);
    formData.append('target_role', document.getElementById('targetRole').value);
    formData.append('github_username', document.getElementById('githubUsername').value);
    
    // 3. Instantly reset input selectors on click for sharp user experience
    form.reset();
    resetFileInput();
    
    try {
        // 4. Fire network packet directly to our real API POST endpoint
        const response = await fetch('/analyze', {
            method: 'POST',
            body: formData
        });
        const data = await response.json();
        
        if (data.status === 'success') {
            statusText.textContent = "SYSTEM_STATUS: SUCCESS // PAYLOAD_COMPILED";
            statusIndicator.classList.remove('bg-[#3b82f6]', 'animate-pulse');
            statusIndicator.classList.add('bg-[#10b981]'); // Clean success node indicator
            
            // 5. Safely map keys explicitly using the marked library parser
            document.getElementById('outJobSearch').innerHTML = marked.parse(data.job_search || "Data null.");
            document.getElementById('outSkillGaps').innerHTML = marked.parse(data.skill_gaps || "Data null.");
            document.getElementById('outProjects').innerHTML = marked.parse(data.project_ideas || "Data null.");
            document.getElementById('outGithub').innerHTML = marked.parse(data.github_summary || "Data null.");
        } else {
            statusIndicator.classList.remove('bg-[#3b82f6]', 'animate-pulse');
            statusIndicator.classList.add('bg-error');
            statusText.textContent = `SYSTEM_ERROR: ${data.error || 'Execution aborted'}`;
        }
    } catch (err) {
        statusIndicator.classList.remove('bg-[#3b82f6]', 'animate-pulse');
        statusIndicator.classList.add('bg-error');
        statusText.textContent = `NETWORK_PIPELINE_ERROR: ${err.message}`;
    } finally {
        // 6. Restore action button state parameters safely
        analyzeBtn.disabled = false;
        analyzeBtn.innerHTML = '<span>Analyze Profile</span><span class="material-symbols-outlined text-[16px]">memory</span>';
        analyzeBtn.classList.remove('bg-secondary', 'cursor-not-allowed');
        analyzeBtn.classList.add('bg-primary', 'hover:bg-[#1e293b]');
        
        setTimeout(() => {
            statusIndicator.classList.remove('bg-[#10b981]', 'bg-error');
            statusIndicator.classList.add('bg-outline');
            statusText.textContent = "SYSTEM_STATUS: IDLE // AWAITING_PAYLOAD";
        }, 4000);
    }
});
