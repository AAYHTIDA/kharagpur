// Mock API response data for demo
const mockResponses = [
    {
        consistent: true,
        prediction: 1,
        evidence: [
            {
                claim: "Character was born in London in 1985",
                evidence: "The protagonist mentioned growing up near the Thames during the Thatcher era...",
                supports: true
            },
            {
                claim: "Character studied at Oxford University",
                evidence: "She recalled the dreaming spires and late nights in the Bodleian Library...",
                supports: true
            },
            {
                claim: "Character worked as a journalist",
                evidence: "Her press credentials and years covering political scandals were well documented...",
                supports: true
            }
        ]
    },
    {
        consistent: false,
        prediction: 0,
        evidence: [
            {
                claim: "Character was born in New York in 1990",
                evidence: "The novel clearly states the character was born in London in 1985...",
                supports: false
            },
            {
                claim: "Character is afraid of water",
                evidence: "Multiple scenes show the character swimming confidently in the ocean...",
                supports: false
            },
            {
                claim: "Character has never been to Paris",
                evidence: "Chapter 12 describes their childhood summers spent in the French countryside...",
                supports: false
            }
        ]
    }
];

// DOM elements
const novelFileInput = document.getElementById('novel-file');
const backstoryFileInput = document.getElementById('backstory-file');
const novelStatus = document.getElementById('novel-status');
const backstoryStatus = document.getElementById('backstory-status');
const checkButton = document.getElementById('check-btn');
const outputSection = document.getElementById('output-section');
const statusLabel = document.getElementById('status-label');
const predictionText = document.getElementById('prediction-text');
const evidenceHeader = document.getElementById('evidence-header');
const evidenceContent = document.getElementById('evidence-content');
const toggleBtn = document.getElementById('toggle-btn');
const evidenceList = document.getElementById('evidence-list');

// State
let isEvidenceExpanded = true;
let novelContent = '';
let backstoryContent = '';

// Event listeners
checkButton.addEventListener('click', handleCheckConsistency);
evidenceHeader.addEventListener('click', toggleEvidence);
novelFileInput.addEventListener('change', (e) => handleFileUpload(e, 'novel'));
backstoryFileInput.addEventListener('change', (e) => handleFileUpload(e, 'backstory'));

// Handle file upload
async function handleFileUpload(event, type) {
    const file = event.target.files[0];
    const statusElement = type === 'novel' ? novelStatus : backstoryStatus;
    
    if (!file) {
        statusElement.textContent = 'No file selected';
        statusElement.className = 'file-status';
        if (type === 'novel') novelContent = '';
        else backstoryContent = '';
        updateCheckButtonState();
        return;
    }
    
    // Validate file type
    if (!file.name.match(/\.(txt|md)$/i)) {
        statusElement.textContent = 'Please select a .txt or .md file';
        statusElement.className = 'file-status error';
        if (type === 'novel') novelContent = '';
        else backstoryContent = '';
        updateCheckButtonState();
        return;
    }
    
    // Validate file size (max 10MB)
    if (file.size > 10 * 1024 * 1024) {
        statusElement.textContent = 'File too large (max 10MB)';
        statusElement.className = 'file-status error';
        if (type === 'novel') novelContent = '';
        else backstoryContent = '';
        updateCheckButtonState();
        return;
    }
    
    try {
        statusElement.textContent = 'Loading file...';
        statusElement.className = 'file-status';
        
        const content = await readFileContent(file);
        
        if (type === 'novel') {
            novelContent = content;
        } else {
            backstoryContent = content;
        }
        
        statusElement.textContent = `✓ ${file.name} (${formatFileSize(file.size)})`;
        statusElement.className = 'file-status loaded';
        
    } catch (error) {
        console.error('Error reading file:', error);
        statusElement.textContent = 'Error reading file';
        statusElement.className = 'file-status error';
        
        if (type === 'novel') novelContent = '';
        else backstoryContent = '';
    }
    
    updateCheckButtonState();
}

// Read file content as text
function readFileContent(file) {
    return new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.onload = (e) => resolve(e.target.result);
        reader.onerror = (e) => reject(e);
        reader.readAsText(file);
    });
}

// Format file size for display
function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
}

// Update check button state
function updateCheckButtonState() {
    const hasNovel = novelContent.trim().length > 0;
    const hasBackstory = backstoryContent.trim().length > 0;
    
    checkButton.disabled = !(hasNovel && hasBackstory);
}

// Main function to handle consistency check
async function handleCheckConsistency() {
    // Validation is handled by button state
    if (!novelContent.trim() || !backstoryContent.trim()) {
        return;
    }
    
    // Show loading state
    checkButton.disabled = true;
    checkButton.textContent = 'Checking...';
    
    try {
        // Simulate API call delay
        await new Promise(resolve => setTimeout(resolve, 1500));
        
        // Get mock response (randomly pick one for demo)
        const response = mockResponses[Math.floor(Math.random() * mockResponses.length)];
        
        displayResults(response);
        
    } catch (error) {
        console.error('Error checking consistency:', error);
        alert('An error occurred while checking consistency. Please try again.');
    } finally {
        // Reset button state
        updateCheckButtonState();
        checkButton.textContent = 'Check Consistency';
    }
}

// Display the results
function displayResults(data) {
    // Show output section
    outputSection.style.display = 'block';
    
    // Update status
    const isConsistent = data.consistent;
    statusLabel.textContent = isConsistent ? 'CONSISTENT' : 'INCONSISTENT';
    statusLabel.className = `status-label ${isConsistent ? 'consistent' : 'inconsistent'}`;
    
    // Update prediction text
    predictionText.textContent = `Prediction: ${data.prediction} (${isConsistent ? 'Consistent' : 'Contradict'})`;
    
    // Update evidence
    displayEvidence(data.evidence);
    
    // Scroll to results
    outputSection.scrollIntoView({ behavior: 'smooth' });
}

// Display evidence items
function displayEvidence(evidence) {
    evidenceList.innerHTML = '';
    
    evidence.forEach(item => {
        const li = document.createElement('li');
        li.className = `evidence-item ${item.supports ? 'supports' : 'contradicts'}`;
        
        li.innerHTML = `
            <div class="claim">${item.claim}</div>
            <div class="evidence">"${item.evidence}"</div>
            <span class="tag ${item.supports ? 'supports' : 'contradicts'}">
                ${item.supports ? 'Supports' : 'Contradicts'}
            </span>
        `;
        
        evidenceList.appendChild(li);
    });
}

// Toggle evidence section
function toggleEvidence() {
    isEvidenceExpanded = !isEvidenceExpanded;
    
    if (isEvidenceExpanded) {
        evidenceContent.classList.remove('collapsed');
        evidenceContent.classList.add('expanded');
        toggleBtn.classList.remove('collapsed');
        toggleBtn.textContent = '▼';
    } else {
        evidenceContent.classList.remove('expanded');
        evidenceContent.classList.add('collapsed');
        toggleBtn.classList.add('collapsed');
        toggleBtn.textContent = '▶';
    }
}

// Initialize evidence section as expanded
document.addEventListener('DOMContentLoaded', () => {
    evidenceContent.classList.add('expanded');
});