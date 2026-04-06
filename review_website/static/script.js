const state = {
    files: [],
    currentFile: '',
    data: [],
    currentIndex: 0,
    currentLabels: [],
    skippedIndices: [],
    reviewingSkippedIndex: null
};

const LABEL_NAMES = [
    "Food quality",
    "Price",
    "Service quality",
    "Hygiene and safety",
    "Atmosphere"
];

// DOM elements
const fileSelect = document.getElementById('file-select');
const uiLoading = document.getElementById('loading');
const uiNoData = document.getElementById('no-data');
const uiCard = document.getElementById('review-card');

const elTitle = document.getElementById('item-title');
const elDate = document.getElementById('item-date');
const elText = document.getElementById('item-text');
const elReasoningContainer = document.getElementById('reasoning-container');
const elReasoning = document.getElementById('item-reasoning');
const elLabelsGrid = document.getElementById('labels-grid');

const elReviewed = document.getElementById('reviewed-count');
const elTotal = document.getElementById('total-count');
const elProgress = document.getElementById('progress-bar');
const elSkippedList = document.getElementById('skipped-list');

const btnSkip = document.getElementById('btn-skip');
const btnSave = document.getElementById('btn-save');

async function init() {
    await loadFiles();
    
    fileSelect.addEventListener('change', (e) => {
        const file = e.target.value;
        if (file) {
            loadFile(file);
        } else {
            resetView();
        }
    });

    btnSkip.addEventListener('click', skipItem);
    btnSave.addEventListener('click', saveItem);

    document.addEventListener('keydown', handleGlobalKeydown);
}

async function loadFiles() {
    try {
        const res = await fetch('/api/files');
        const json = await res.json();
        state.files = json.files || [];
        
        fileSelect.innerHTML = '<option value="">Select a file...</option>';
        state.files.forEach(f => {
            const opt = document.createElement('option');
            opt.value = f;
            opt.textContent = f;
            fileSelect.appendChild(opt);
        });

        // Restore from localStorage
        const savedFile = localStorage.getItem('selectedFile');
        if (savedFile && state.files.includes(savedFile)) {
            fileSelect.value = savedFile;
            loadFile(savedFile);
        }
    } catch (e) {
        console.error("Failed to load files", e);
    }
}

function resetView() {
    state.currentFile = '';
    state.data = [];
    localStorage.removeItem('selectedFile');
    uiNoData.classList.remove('hidden');
    uiCard.classList.add('hidden');
    updateStats();
}

async function loadFile(filename) {
    localStorage.setItem('selectedFile', filename);
    state.currentFile = filename;
    
    uiNoData.classList.add('hidden');
    uiCard.classList.add('hidden');
    uiLoading.classList.remove('hidden');

    try {
        const res = await fetch(`/api/data?file=${encodeURIComponent(filename)}`);
        const json = await res.json();
        
        state.data = json.data || [];
        
        // Restore progress
        const savedIndex = localStorage.getItem(`currentIndex_${filename}`);
        state.currentIndex = savedIndex ? parseInt(savedIndex, 10) : 0;
        
        const savedSkipped = localStorage.getItem(`skippedIndices_${filename}`);
        state.skippedIndices = savedSkipped ? JSON.parse(savedSkipped) : [];
        state.reviewingSkippedIndex = null;
        
        if (state.currentIndex >= state.data.length) {
            state.currentIndex = 0; // reset if out of bounds
        }
        
        renderSkippedList();
        renderCurrentItem();
    } catch (e) {
        console.error("Failed to load data", e);
        alert("Error loading file: " + e.message);
        resetView();
    } finally {
        uiLoading.classList.add('hidden');
    }
}

function renderSkippedList() {
    elSkippedList.innerHTML = '';
    
    if (state.skippedIndices.length === 0) {
        elSkippedList.innerHTML = '<li class="empty-state">No skipped items</li>';
        return;
    }
    
    state.skippedIndices.forEach((idx) => {
        const li = document.createElement('li');
        li.className = 'skipped-item';
        if (state.reviewingSkippedIndex === idx) {
            li.classList.add('active-review');
        }
        
        const itemData = state.data[idx] || {};
        let titleBlock = 'Unknown';
        if (itemData.original_data) {
            titleBlock = itemData.original_data.title || 'Review';
        } else if (itemData.title) {
            titleBlock = itemData.title;
        }
        
        li.textContent = `#${idx} - ${titleBlock}`;
        li.title = `Index ${idx}: Click to review again`;
        
        li.onclick = () => {
            state.reviewingSkippedIndex = idx;
            renderSkippedList();
            renderCurrentItem();
        };
        elSkippedList.appendChild(li);
    });
}

function updateStats() {
    elReviewed.textContent = state.currentIndex;
    elTotal.textContent = state.data.length;
    
    if (state.data.length > 0) {
        const pct = (state.currentIndex / state.data.length) * 100;
        elProgress.style.width = `${pct}%`;
    } else {
        elProgress.style.width = '0%';
    }
}

function renderCurrentItem() {
    updateStats();
    
    const isShowingMain = state.reviewingSkippedIndex === null;
    const itemIndexToRender = isShowingMain ? state.currentIndex : state.reviewingSkippedIndex;
    
    if (!state.data || state.data.length === 0) {
        uiCard.classList.add('hidden');
        uiNoData.classList.remove('hidden');
        return;
    }

    if (isShowingMain && state.currentIndex >= state.data.length) {
        uiCard.classList.add('hidden');
        uiNoData.classList.remove('hidden');
        uiNoData.innerHTML = `<i class="fa-solid fa-check-circle" style="color: var(--pos-text)"></i><p>All items reviewed in this file!</p>`;
        return;
    }

    const item = state.data[itemIndexToRender];
    if (!item) return;
    
    // Handle both raw and previously labeled schemas
    let title = "No Title";
    let text = "No Text";
    let date = "N/A";
    let reasoning = "";
    let labels = [];

    if (item.original_data) {
        title = item.original_data.title || title;
        text = item.original_data.textTranslated || item.original_data.text || text;
        date = item.original_data.publishedAtDate || date;
        reasoning = item.reasoning || "";
        labels = item.labels || [];
    } else {
        title = item.title || title;
        text = item.textTranslated || item.text || text;
        date = item.publishedAtDate || date;
    }

    elTitle.textContent = title;
    elDate.textContent = date;
    elText.textContent = text;

    if (reasoning) {
        elReasoningContainer.style.display = 'block';
        elReasoning.textContent = reasoning;
    } else {
        elReasoningContainer.style.display = 'none';
        elReasoning.textContent = '';
    }

    buildLabels(labels);
    uiCard.classList.remove('hidden');
}

function buildLabels(existingLabels) {
    elLabelsGrid.innerHTML = '';
    state.currentLabels = [];

    LABEL_NAMES.forEach((name, idx) => {
        const existing = existingLabels.find(l => l.name === name);
        const value = existing !== undefined ? existing.value : 0.5; // neutral by default
        
        state.currentLabels.push({ name, value });

        const row = document.createElement('div');
        row.className = 'label-row';
        row.innerHTML = `
            <div class="label-name"><span style="color: var(--text-muted); margin-right: 8px;">[${idx + 1}]</span>${name}</div>
            <div class="segmented-control" data-idx="${idx}">
                <button class="segment-btn ${value === 0.0 ? 'active' : ''}" data-val="0.0">Negative</button>
                <button class="segment-btn ${value === 0.5 ? 'active' : ''}" data-val="0.5">Neutral</button>
                <button class="segment-btn ${value === 1.0 ? 'active' : ''}" data-val="1.0">Positive</button>
            </div>
        `;
        
        const btns = row.querySelectorAll('.segment-btn');
        btns.forEach(btn => {
            btn.addEventListener('click', (e) => {
                const val = parseFloat(e.target.dataset.val);
                setLabelValue(idx, val);
            });
        });

        elLabelsGrid.appendChild(row);
    });
}

function setLabelValue(idx, val) {
    state.currentLabels[idx].value = val;
    
    // Update local DOM
    const control = document.querySelector(`.segmented-control[data-idx="${idx}"]`);
    if (control) {
        control.querySelectorAll('.segment-btn').forEach(btn => btn.classList.remove('active'));
        control.querySelector(`.segment-btn[data-val="${val.toFixed(1)}"]`)?.classList.add('active');
    }
}

function cycleLabel(idx) {
    if (idx < 0 || idx >= state.currentLabels.length) return;
    const currentVal = state.currentLabels[idx].value;
    let nextVal = 0.5;
    if (currentVal === 0.0) nextVal = 0.5;
    else if (currentVal === 0.5) nextVal = 1.0;
    else if (currentVal === 1.0) nextVal = 0.0;
    
    setLabelValue(idx, nextVal);
}

function handleGlobalKeydown(e) {
    // If no card is active or loading, ignore
    if (uiCard.classList.contains('hidden') || !uiLoading.classList.contains('hidden')) return;
    
    if (e.key >= '1' && e.key <= '5') {
        const idx = parseInt(e.key) - 1;
        cycleLabel(idx);
    } else if (e.key === 'Enter') {
        e.preventDefault();
        saveItem();
    } else if (e.code === 'Space') {
        e.preventDefault();
        skipItem();
    }
}

function handlePostActionRemoval() {
    if (state.reviewingSkippedIndex !== null) {
        // If we were reviewing a skipped item, remove it from skipped list
        state.skippedIndices = state.skippedIndices.filter(i => i !== state.reviewingSkippedIndex);
        localStorage.setItem(`skippedIndices_${state.currentFile}`, JSON.stringify(state.skippedIndices));
        
        // Go back to main
        state.reviewingSkippedIndex = null;
        renderSkippedList();
        renderCurrentItem();
    } else {
        // Was on main item, just move forward
        state.currentIndex++;
        localStorage.setItem(`currentIndex_${state.currentFile}`, state.currentIndex);
        renderCurrentItem();
    }
}

function skipItem() {
    if (state.reviewingSkippedIndex === null) {
        // On main item, add to skipped list
        if (!state.skippedIndices.includes(state.currentIndex)) {
            state.skippedIndices.push(state.currentIndex);
            localStorage.setItem(`skippedIndices_${state.currentFile}`, JSON.stringify(state.skippedIndices));
        }
        renderSkippedList();
    } else {
        // Just leaving the skipped item as skipped, go back to main
        state.reviewingSkippedIndex = null;
        renderSkippedList();
        renderCurrentItem();
        return;
    }
    
    handlePostActionRemoval();
}

async function saveItem() {
    const processIndex = state.reviewingSkippedIndex !== null ? state.reviewingSkippedIndex : state.currentIndex;
    const originalItem = state.data[processIndex];
    
    // Construct payload
    const payload = {
        original_data: originalItem.original_data || {
            title: originalItem.title,
            textTranslated: originalItem.textTranslated,
            publishedAtDate: originalItem.publishedAtDate
        },
        reasoning: originalItem.reasoning || "Manually reviewed",
        labels: state.currentLabels
    };

    // Include original index
    if (originalItem.index !== undefined) {
        payload.index = originalItem.index;
    } else {
        payload.index = processIndex;
    }

    try {
        const res = await fetch('/api/save', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        
        if (!res.ok) throw new Error("Save request failed");
        
        showToast();
        handlePostActionRemoval();
    } catch (e) {
        console.error(e);
        alert("Failed to save: " + e.message);
    }
}

function showToast() {
    const toast = document.getElementById('toast');
    toast.classList.add('show');
    setTimeout(() => {
        toast.classList.remove('show');
    }, 2000);
}

// Boot
init();
