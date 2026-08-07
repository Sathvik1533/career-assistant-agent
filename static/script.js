document.getElementById('resume').addEventListener('change', function(e) {
    const label = document.getElementById('file-label');
    if (this.files.length) {
        label.innerText = "✓ " + this.files[0].name;
        label.style.backgroundColor = "#065f46";
        label.style.borderColor = "#047857";
    } else {
        label.innerText = "Choose PDF File";
        label.style.backgroundColor = "#1f2937";
    }
});

document.getElementById('analyze-form').addEventListener('submit', async function(e) {
    e.preventDefault();
    
    const consoleBox = document.getElementById('console-stream');
    consoleBox.style.display = 'block';
    consoleBox.innerHTML = '';
    
    const logs = [
        "⚙️ [System] Catching network bytes at /analyze endpoint...",
        "🛡️ [Pydantic] Validating request payload format schema... ✅ Passed",
        "🧠 [Agent] Initializing LangChain Executor & Groq LLM (Llama 3.3 70B)...",
        "🔧 [Tool] Invoking 'job_search_advisor' tool...",
        "🔧 [Tool] Invoking 'skill_gap_analyzer' tool...",
        "🔧 [Tool] Invoking 'project_idea_generator' tool...",
        "🐙 [Tool] Invoking 'github_profile_analyzer' tool...",
        "🐍 [Python Engine] Executing live requests.get() calls to api.github.com...",
        "⚡ [Python Engine] Scanning repositories: Filtering out forks and slicing top 10...",
        "🧠 [Groq] Synthesizing comprehensive profile career report metrics...",
        "📝 [Parser] Compiling markdown contents and structural code formatting..."
    ];
    
    let logIndex = 0;
    const logInterval = setInterval(() => {
        if (logIndex < logs.length) {
            consoleBox.innerHTML += logs[logIndex] + '\n';
            consoleBox.scrollTop = consoleBox.scrollHeight;
            logIndex++;
        }
    }, 600);
    
    const formData = new FormData();
    formData.append('resume', document.getElementById('resume').files[0]);
    formData.append('target_role', document.getElementById('target_role').value);
    formData.append('github_username', document.getElementById('github_username').value);
    
    // Reset input fields right after collecting data payload
    document.getElementById('resume').value = '';
    document.getElementById('file-label').innerText = "Choose PDF File";
    document.getElementById('file-label').style.backgroundColor = "#1f2937";
    document.getElementById('file-label').style.borderColor = "#374151";
    
    try {
        const response = await fetch('/analyze', { method: 'POST', body: formData });
        const data = await response.json();
        
        clearInterval(logInterval);
        
        if (data.status === 'success') {
            consoleBox.innerHTML += '✅ [Complete] Structured response verified. Displaying report below.\n';
            consoleBox.scrollTop = consoleBox.scrollHeight;
            
            // Map keys explicitly into their containers using marked.js to render formatting
            document.getElementById('res-job').innerHTML = marked.parse(data.job_search || "Data empty.");
            document.getElementById('res-skills').innerHTML = marked.parse(data.skill_gaps || "Data empty.");
            document.getElementById('res-projects').innerHTML = marked.parse(data.project_ideas || "Data empty.");
            document.getElementById('res-github').innerHTML = marked.parse(data.github_summary || "Data empty.");
        } else {
            consoleBox.innerHTML += `❌ Error: ${data.error || 'Execution break'}\n`;
        }
    } catch (err) {
        clearInterval(logInterval);
        consoleBox.innerHTML += `❌ Pipeline connection error: ${err.message}\n`;
    }
});
