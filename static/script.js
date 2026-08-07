// 1. Locate the file input and the upload container references
const uploadBar = document.getElementById('upload-bar');
const fileInput = document.getElementById('resume');
const uploadText = document.getElementById('upload-text') || (uploadBar ? uploadBar.querySelector('span') : null);
const telemetryNode = document.getElementById('telemetry-node');
const telemetryText = document.getElementById('telemetry-text');

// 2. Set up the click handler
if (uploadBar && fileInput) {
    uploadBar.addEventListener('click', () => fileInput.click());
}

// 3. Dynamic Text Update Handler (Major UX Improvement)
if (fileInput) {
    fileInput.addEventListener('change', () => {
        if (fileInput.files && fileInput.files.length > 0) {
            const fileName = fileInput.files[0].name;
            // Premium muted-success styling (No neon or bright blue slop)
            if (uploadText) {
                uploadText.innerHTML = `<span style="color: #f4f4f5; font-weight: 500; font-family: monospace;">✓ ${fileName}</span>`;
            }
            if (uploadBar) {
                uploadBar.style.borderColor = '#52525b';
                uploadBar.style.backgroundColor = '#141417';
            }
        }
    });
}

document.getElementById('pipeline-form').addEventListener('submit', async function(e) {
    e.preventDefault();
    
    // Set dynamic system loading telemetry string
    telemetryNode.style.backgroundColor = "#eab308";
    telemetryText.innerText = "STATUS: INTENT_GATEWAY_VALIDATION_ACTIVE...";
    
    const statusUpdates = [
        "STATUS: COMPILING_PYDANTIC_PAYLOAD_BLUEPRINT...",
        "STATUS: MOUNTING_INTEGRATED_LANGCHAIN_EXECUTOR...",
        "STATUS: ROUTING_CONTEXT_DATA_TO_GROQ_COMPUTE_GRID...",
        "STATUS: EXECUTING_LOCAL_GITHUB_PROFILE_SCRAPER...",
        "STATUS: FETCHING_API_DATA_FROM_LIVE_GITHUB_SERVERS...",
        "STATUS: CONSOLIDATING_ORIGINAL_REPOS_AND_STRIPPING_FORKS...",
        "STATUS: COMPILING_FINAL_INFERENCE_REPORT_PAYLOAD..."
    ];
    
    let logIndex = 0;
    const telemetryInterval = setInterval(() => {
        if (logIndex < statusUpdates.length) {
            telemetryText.innerText = statusUpdates[logIndex];
            logIndex++;
        }
    }, 700);
    
    const formData = new FormData();
    formData.append('resume', fileInput.files[0]);
    formData.append('target_role', document.getElementById('target_role').value);
    formData.append('github_username', document.getElementById('github_username').value);
    
    // 4. Completely clear file selection values instantly on submit and reset to baseline
    fileInput.value = '';
    if (uploadText) {
        uploadText.innerHTML = '<strong>Select file</strong> or drop PDF';
    }
    if (uploadBar) {
        uploadBar.style.borderColor = '#27272a';
        uploadBar.style.backgroundColor = '#09090b';
    }
    
    try {
        const response = await fetch('/analyze', { method: 'POST', body: formData });
        const data = await response.json();
        
        clearInterval(telemetryInterval);
        
        if (data.status === 'success') {
            telemetryNode.style.backgroundColor = "#22c55e";
            telemetryText.innerText = "STATUS: PIPELINE_COMPILATION_SUCCESS // DATA_STREAM_MOUNTED";
            
            // Populate markdown directly using marked parser rules
            document.getElementById('res-job').innerHTML = marked.parse(data.job_search || "Data null.");
            document.getElementById('res-skills').innerHTML = marked.parse(data.skill_gaps || "Data null.");
            document.getElementById('res-projects').innerHTML = marked.parse(data.project_ideas || "Data null.");
            document.getElementById('res-github').innerHTML = marked.parse(data.github_summary || "Data null.");
        } else {
            telemetryNode.style.backgroundColor = "#ef4444";
            telemetryText.innerText = `ERROR: ${data.error || 'Execution interrupted'}`;
        }
    } catch (err) {
        clearInterval(telemetryInterval);
        telemetryNode.style.backgroundColor = "#ef4444";
        telemetryText.innerText = `CRITICAL_NETWORK_FAILURE: ${err.message}`;
    }
});
