const dropzone = document.getElementById('dropzone');
const fileInput = document.getElementById('resume');
const uploadStatus = document.getElementById('upload-status');
const statusNode = document.getElementById('status-node');
const statusString = document.getElementById('status-string');

// Clean dropzone mechanics
dropzone.addEventListener('click', () => fileInput.click());
fileInput.addEventListener('change', () => {
    if (fileInput.files.length) {
        uploadStatus.innerHTML = `<span style="color: #10b981; font-weight: 500;">✓ ${fileInput.files[0].name}</span>`;
        dropzone.style.borderColor = "#10b981";
    }
});

document.getElementById('engine-form').addEventListener('submit', async function(e) {
    e.preventDefault();
    
    // Set active blinking state indicator
    statusNode.style.backgroundColor = "#f59e0b";
    statusNode.style.animation = "pulse 1.5s infinite";
    statusString.innerText = "INITIALIZING CORE DATA SYSTEM GATEWAY...";
    
    const logs = [
        "VALIDATING INCOMING FILE PAYLOAD VIA PYDANTIC...",
        "LAUNCHING INTEGRATED LANGCHAIN EXECUTOR CONTEXTS...",
        "GROQ HARDWARE ACCELERATION CLOUD CONNECTION SECURED...",
        "INVOKING LOCAL PYTHON GITHUB SCRAPER TOOL MODULE...",
        "ESTABLISHING AUTHENTICATED HEADERS SECURE CONNECT FOR API.GITHUB.COM...",
        "SCANNING PUBLIC REPOSITORIES // STRIPPING FORKS // COMPILING TOP 10...",
        "RUNNING SYSTEM INFERENCE TO SYNTHESIZE COMPLEX EVALUATION..."
    ];
    
    let logIndex = 0;
    const logTimer = setInterval(() => {
        if (logIndex < logs.length) {
            statusString.innerText = `EXECUTION_LOG: ${logs[logIndex]}`;
            logIndex++;
        }
    }, 700);
    
    const formData = new FormData();
    formData.append('resume', fileInput.files[0]);
    formData.append('target_role', document.getElementById('target_role').value);
    formData.append('github_username', document.getElementById('github_username').value);
    
    // Reset input fields right after collecting data payload
    fileInput.value = '';
    uploadStatus.innerHTML = "<strong>Click to select</strong> or drop PDF";
    dropzone.style.borderColor = "#334155";
    
    try {
        const response = await fetch('/analyze', { method: 'POST', body: formData });
        const data = await response.json();
        
        clearInterval(logTimer);
        
        if (data.status === 'success') {
            statusNode.style.backgroundColor = "#10b981";
            statusNode.style.animation = "none";
            statusString.innerText = "SYSTEM_STATUS: VERIFIED_SUCCESS // PAYLOAD_COMPILED";
            
            document.getElementById('res-job').innerHTML = marked.parse(data.job_search || "Data extraction null.");
            document.getElementById('res-skills').innerHTML = marked.parse(data.skill_gaps || "Data extraction null.");
            document.getElementById('res-projects').innerHTML = marked.parse(data.project_ideas || "Data extraction null.");
            document.getElementById('res-github').innerHTML = marked.parse(data.github_summary || "Data extraction null.");
        } else {
            statusNode.style.backgroundColor = "#ef4444";
            statusString.innerText = `SYSTEM_ERROR: ${data.error || 'Execution break'}`;
        }
    } catch (err) {
        clearInterval(logTimer);
        statusNode.style.backgroundColor = "#ef4444";
        statusString.innerText = `NETWORK_PIPELINE_ERROR: ${err.message}`;
    }
});
