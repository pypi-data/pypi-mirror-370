// Canvas Editor - Streamlit Component with Custom Properties
console.log("Canvas Editor initialized");

// State Management
let canvas, ctx;
let canvasContainer, canvasWrapper;
let isDrawing = false;
let isResizing = false;
let isDragging = false;
let startX, startY;
let rectangles = [];
let currentRect = null;
let selectedRect = null;
let selectedRectIndex = -1;
let resizeHandle = null;
let dragOffset = { x: 0, y: 0 };
let imageLoaded = false;
let blockCounter = 0;
let ocrEnabled = false;
let skipNextUpdate = false;
let isProcessingOCR = false;
let justProcessedOCR = false;
let currentOCRRequestId = null;
let currentlyProcessingBlockId = null;

// Color scheme for block types - Initialize with converted colors from BLOCK_TYPE_RGB
let blockTypeColors = {
    'Line': '#FFB6C1',           // [255, 182, 193] - Light Pink
    'Span': '#98FB98',           // [152, 251, 152] - Pale Green
    'FigureGroup': '#ADD8E6',    // [173, 216, 230] - Light Blue
    'TableGroup': '#FFFFE0',     // [255, 255, 224] - Light Yellow
    'ListGroup': '#FFC0CB',      // [255, 192, 203] - Pink
    'PictureGroup': '#E0FFFF',   // [224, 255, 255] - Light Cyan
    'Page': '#FFDAB9',           // [255, 218, 185] - Peach Puff
    'Caption': '#98FB98',        // [152, 251, 152] - Pale Green
    'Code': '#E6E6FA',           // [230, 230, 250] - Lavender
    'Figure': '#FFE4C4',         // [255, 228, 196] - Bisque
    'Footnote': '#DDA0DD',       // [221, 160, 221] - Plum
    'Form': '#AFEEEE',           // [175, 238, 238] - Pale Turquoise
    'Equation': '#D3D3D3',       // [211, 211, 211] - Light Gray
    'Handwriting': '#D3D3D3',    // [211, 211, 211] - Light Gray
    'TextInlineMath': '#FFDAB9', // [255, 218, 185] - Peach Puff
    'ListItem': '#FFB6C1',       // [255, 182, 193] - Light Pink
    'PageFooter': '#D8BFD8',     // [216, 191, 216] - Thistle
    'PageHeader': '#90EE90',     // [144, 238, 144] - Light Green
    'Picture': '#ADD8E6',        // [173, 216, 230] - Light Blue
    'SectionHeader': '#DDA0DD',  // [221, 160, 221] - Plum
    'Table': '#DEB887',          // [222, 184, 135] - Burlywood
    'Text': '#F4A460',           // [244, 164, 96] - Sandy Brown
    'TableOfContents': '#BDB76B',// [189, 183, 107] - Dark Khaki
    'Document': '#FFA07A',       // [255, 160, 122] - Light Salmon
    'ComplexRegion': '#FFB6C1',  // [255, 182, 193] - Light Pink
    'TableCell': '#D8BFD8',      // [216, 191, 216] - Thistle
    'Reference': '#90EE90',      // [144, 238, 144] - Light Green
};

// Zoom state
let zoomLevel = 1.0;
const ZOOM_MIN = 0.25;
const ZOOM_MAX = 4.0;
const ZOOM_STEP = 0.25;

// Store original rectangle state for resizing
let originalRect = null;
let resizeStartPos = null;

// History for undo/redo
let history = [];
let historyStep = -1;
const MAX_HISTORY = 50;

let canvasMode = 'draw'; // 'draw' or 'pan'
let isPanning = false;
let panStartX = 0;
let panStartY = 0;

// Configuration
const HANDLE_SIZE = 10;
const HANDLE_HIT_SIZE = 20;
const SELECTED_COLOR = '#FF5722';  // Red-orange for selection
const DEFAULT_COLOR = '#F4A460';   // Sandy Brown (Text color) as default
const MIN_RECT_SIZE = 30;
const RESIZE_THRESHOLD = 2;

// Initialize the canvas
function initCanvas() {
    console.log("Initializing canvas...");
    canvas = document.getElementById('drawing-canvas');
    canvasContainer = document.getElementById('canvas-container');
    canvasWrapper = document.getElementById('canvas-wrapper');
    
    if (!canvas || !canvasContainer) {
        console.error("Canvas elements not found!");
        return;
    }
    
    ctx = canvas.getContext('2d');
    
    // Set initial canvas size
    canvas.width = 800;
    canvas.height = 600;
    
    // Setup event listeners
    setupEventListeners();
    
    // Initial draw
    redrawCanvas();
    updateStatus("Ready to draw");
    updateZoomDisplay();
    
    // Save initial state
    saveHistory();
}

// Helper function to convert RGB array to hex color
function rgbToHex(rgb) {
    if (Array.isArray(rgb) && rgb.length === 3) {
        const r = rgb[0].toString(16).padStart(2, '0');
        const g = rgb[1].toString(16).padStart(2, '0');
        const b = rgb[2].toString(16).padStart(2, '0');
        return `#${r}${g}${b}`.toUpperCase();
    }
    return null;
}

// Update this helper function for better color visibility
function getLighterColor(hexColor, opacity = 0.15) {
    // Handle case where hexColor might be undefined or invalid
    if (!hexColor || !hexColor.startsWith('#')) {
        hexColor = DEFAULT_COLOR;
    }
    
    // Convert hex to RGB
    const r = parseInt(hexColor.slice(1, 3), 16);
    const g = parseInt(hexColor.slice(3, 5), 16);
    const b = parseInt(hexColor.slice(5, 7), 16);
    
    // Return rgba with specified opacity for colored background
    return `rgba(${r}, ${g}, ${b}, ${opacity})`;
}

// Get color for block type - Updated to always return a valid color
function getBlockTypeColor(blockType) {
    // First check if we have a color for this specific block type
    if (blockTypeColors && blockTypeColors[blockType]) {
        return blockTypeColors[blockType];
    }
    
    // Check for lowercase version
    const lowerType = blockType.toLowerCase();
    if (blockTypeColors && blockTypeColors[lowerType]) {
        return blockTypeColors[lowerType];
    }
    
    // If not, check if we have an 'other' color defined
    if (blockTypeColors && blockTypeColors['other']) {
        return blockTypeColors['other'];
    }
    
    // Final fallback to default color
    return DEFAULT_COLOR;
}

// Update this function in main.js for better color visibility
function updatePanelTheme(blockType) {
    const panel = document.getElementById('properties-panel');
    if (!panel) return;
    
    const panelHeader = panel.querySelector('.panel-header');
    const saveBtn = panel.querySelector('.save-btn');
    const propertySections = panel.querySelectorAll('.property-section');
    
    // Get the color for this block type - will always return a valid color now
    const blockColor = getBlockTypeColor(blockType);
    // Increase opacity for better visibility (was 0.08, now 0.15)
    const lightBgColor = getLighterColor(blockColor, 0.15);
    
    console.log(`Updating panel theme for ${blockType} with color ${blockColor}`);
    
    // Update panel background with more visible tint
    panel.style.background = `linear-gradient(to bottom, ${lightBgColor}, ${getLighterColor(blockColor, 0.05)})`;
    
    // Update header with gradient based on block type color
    if (panelHeader) {
        panelHeader.style.background = `linear-gradient(135deg, ${blockColor} 0%, ${blockColor}dd 100%)`;
        panelHeader.style.color = '#ffffff'; // Ensure text is visible
    }
    
    // Update save button
    if (saveBtn) {
        saveBtn.style.background = `linear-gradient(135deg, ${blockColor} 0%, ${blockColor}dd 100%)`;
        saveBtn.style.color = '#ffffff'; // Ensure text is visible
        
        // Add hover effect inline
        saveBtn.onmouseover = function() {
            this.style.boxShadow = `0 4px 12px ${getLighterColor(blockColor, 0.4)}`;
            this.style.transform = 'translateY(-1px)';
        };
        saveBtn.onmouseout = function() {
            this.style.boxShadow = '';
            this.style.transform = '';
        };
    }
    
    // Update all property sections with more visible background
    propertySections.forEach(section => {
        section.style.background = getLighterColor(blockColor, 0.1);
        section.style.borderLeft = `3px solid ${blockColor}`;
        section.style.paddingLeft = '15px';
        section.style.marginBottom = '10px';
        section.style.borderRadius = '4px';
    });
    
    // Add a colored border to the entire panel for better visibility
    panel.style.border = `2px solid ${blockColor}`;
    panel.style.borderRadius = '8px';
    
    // Update input focus styles WITHOUT replacing the elements
    const inputs = panel.querySelectorAll('input, select, textarea');
    inputs.forEach(input => {
        // Store current values
        const currentValue = input.value;
        const inputId = input.id;
        
        // Style the inputs with a subtle border color
        input.style.borderColor = getLighterColor(blockColor, 0.3);
        
        // Remove existing event listeners by using a cleaner approach
        const focusHandler = function() {
            this.style.borderColor = blockColor;
            this.style.boxShadow = `0 0 0 3px ${getLighterColor(blockColor, 0.2)}`;
        };
        
        const blurHandler = function() {
            this.style.borderColor = getLighterColor(blockColor, 0.3);
            this.style.boxShadow = '';
        };
        
        // Remove old listeners if they exist
        input.removeEventListener('focus', input._focusHandler);
        input.removeEventListener('blur', input._blurHandler);
        
        // Store handlers on the element for future removal
        input._focusHandler = focusHandler;
        input._blurHandler = blurHandler;
        
        // Add new listeners
        input.addEventListener('focus', focusHandler);
        input.addEventListener('blur', blurHandler);
        
        // Restore value (in case it was lost)
        input.value = currentValue;
    });
    
    // Add a color indicator bar at the top of the panel
    let colorBar = panel.querySelector('.color-indicator-bar');
    if (!colorBar) {
        colorBar = document.createElement('div');
        colorBar.className = 'color-indicator-bar';
        panel.insertBefore(colorBar, panel.firstChild);
    }
    colorBar.style.cssText = `
        width: 100%;
        height: 4px;
        background: ${blockColor};
        border-radius: 8px 8px 0 0;
        margin-bottom: -4px;
    `;
}

// Update the setupEventListeners function
function setupEventListeners() {
    // Mouse events
    canvas.addEventListener('mousedown', handleMouseDown);
    canvas.addEventListener('mousemove', handleMouseMove);
    canvas.addEventListener('mouseup', handleMouseUp);
    canvas.addEventListener('mouseout', handleMouseOut);
    
    // Mouse wheel for zoom
    canvasWrapper.addEventListener('wheel', handleWheel);
    
    // Keyboard events
    document.addEventListener('keydown', handleKeyDown);

    // Mode toggle buttons
    document.getElementById('pan-mode-btn')?.addEventListener('click', () => setCanvasMode('pan'));
    document.getElementById('draw-mode-btn')?.addEventListener('click', () => setCanvasMode('draw'));
    
    // Control buttons
    document.getElementById('undo-btn')?.addEventListener('click', undo);
    document.getElementById('redo-btn')?.addEventListener('click', redo);
    document.getElementById('zoom-in-btn')?.addEventListener('click', zoomIn);
    document.getElementById('zoom-out-btn')?.addEventListener('click', zoomOut);
    document.getElementById('zoom-reset-btn')?.addEventListener('click', zoomReset);
    
    // Save properties button - use event delegation to ensure it always works
    document.addEventListener('click', function(e) {
        if (e.target && e.target.id === 'save-properties') {
            e.preventDefault();
            saveProperties();
        }
        if (e.target && e.target.id === 'close-panel') {
            e.preventDefault();
            hidePropertiesPanel();
        }
    });
    
    // Block type change event - use event delegation to avoid losing the handler
    document.addEventListener('change', function(e) {
        if (e.target && e.target.id === 'block-type') {
            autoSaveProperties();
            // Update theme when block type changes
            const blockType = e.target.value;
            if (blockType) {
                updatePanelTheme(blockType);
            }
        }
    });
    
    document.addEventListener('input', function(e) {
        if (e.target && (e.target.id === 'text-content' || e.target.id === 'text-id')) {
            autoSaveProperties();
        }
    });

    // In setupEventListeners function, add:
    document.addEventListener('click', function(e) {
        if (e.target && e.target.id === 'save-properties') {
            e.preventDefault();
            saveProperties();
        }
        if (e.target && e.target.id === 'close-panel') {
            e.preventDefault();
            hidePropertiesPanel();
        }
        // Add reset button handler
        if (e.target && e.target.id === 'reset-properties') {
            e.preventDefault();
            resetProperties();
        }
    });

    // OCR button click handler - use event delegation
    document.addEventListener('click', function(e) {
        if (e.target && (e.target.id === 'ocr-btn' || e.target.closest('#ocr-btn'))) {
        e.preventDefault();
        e.stopPropagation();
        performOCR();
        }
    });
}

// Add this function to handle OCR button click
function performOCR() {
    if (!selectedRect || selectedRectIndex < 0) {
        console.log("Cannot perform OCR: no selection");
        return;
    }
    
    // Check if ANY OCR is currently processing
    if (isProcessingOCR) {
        console.log("Cannot perform OCR: another OCR operation is in progress");
        updateStatus(`OCR already running on ${currentlyProcessingBlockId}. Please wait...`);
        
        // Show alert or notification without changing button style
        const ocrBtn = document.getElementById('ocr-btn');
        if (ocrBtn) {
            const originalText = ocrBtn.innerHTML;
            ocrBtn.innerHTML = `<span class="ocr-icon">⚠️</span> OCR Busy`;
            
            setTimeout(() => {
                // Restore the appropriate text based on current state
                if (isProcessingOCR) {
                    if (currentlyProcessingBlockId === selectedRect.Block_ID) {
                        ocrBtn.innerHTML = '<span class="ocr-icon">⏳</span> Processing...';
                    } else {
                        ocrBtn.innerHTML = `<span class="ocr-icon">⏳</span> Busy (${currentlyProcessingBlockId})`;
                    }
                } else {
                    ocrBtn.innerHTML = '<span class="ocr-icon">🔍</span> OCR';
                }
            }, 2000);
        }
        return;
    }
    
    // Generate unique request ID
    currentOCRRequestId = `ocr_${Date.now()}_${selectedRectIndex}`;
    currentlyProcessingBlockId = selectedRect.Block_ID;  // Store which block is being processed
    
    console.log("Performing OCR for rectangle:", selectedRect, "Request ID:", currentOCRRequestId);
    
    const ocrBtn = document.getElementById('ocr-btn');
    
    if (ocrBtn) {
        ocrBtn.classList.add('loading');
        ocrBtn.disabled = true;
        ocrBtn.innerHTML = '<span class="ocr-icon">⏳</span> Processing...';
    }
    
    isProcessingOCR = true;
    updateStatus(`Running OCR for ${selectedRect.Block_ID}...`);
    
    const ocrRequest = {
        rect_index: selectedRectIndex,
        bbox: rectToBbox(selectedRect),
        request_id: currentOCRRequestId
    };
    
    const data = {
        rectangles: rectangles.map((rect, index) => ({
            Block_ID: rect.Block_ID,
            Block_Type: rect.Block_Type || 'text',
            Text_Content: rect.Text_Content || '',
            Text_ID: rect.Text_ID || '',
            Boundary_Boxes: rectToBbox(rect),
            x: Math.round(rect.x),
            y: Math.round(rect.y),
            width: Math.round(rect.width),
            height: Math.round(rect.height)
        })),
        selected_index: selectedRectIndex,
        canvas_width: canvas.width,
        canvas_height: canvas.height,
        zoom_level: zoomLevel,
        ocr_request: ocrRequest
    };
    
    console.log("Sending OCR request to Streamlit:", ocrRequest);
    
    Streamlit.setComponentValue(data);
    
    // Store timeout with request ID
    setTimeout(() => {
        if (isProcessingOCR && currentOCRRequestId === ocrRequest.request_id) {
            console.log("OCR timeout - resetting button");
            resetOCRButton();
            isProcessingOCR = false;
            currentOCRRequestId = null;
            currentlyProcessingBlockId = null;
            updateStatus("OCR timeout - please try again");
        }
    }, 30000);
}

// Add function to reset OCR button
function resetOCRButton() {
    const ocrBtn = document.getElementById('ocr-btn');
    if (ocrBtn) {
        ocrBtn.classList.remove('loading');
        ocrBtn.disabled = false;
        ocrBtn.innerHTML = '<span class="ocr-icon">🔍</span> OCR';
    }
    isProcessingOCR = false;
    currentlyProcessingBlockId = null;
}


function setCanvasMode(mode) {
    canvasMode = mode;
    
    // Update button states
    const panBtn = document.getElementById('pan-mode-btn');
    const drawBtn = document.getElementById('draw-mode-btn');
    
    if (mode === 'pan') {
        panBtn?.classList.add('active');
        drawBtn?.classList.remove('active');
        updateStatus('Pan mode - Drag empty space to pan, click boxes to select');
    } else {
        panBtn?.classList.remove('active');
        drawBtn?.classList.add('active');
        updateStatus('Draw mode - Click and drag to draw rectangles');
    }
    
    // Clear any ongoing drawing operations (but keep selection)
    isDrawing = false;
    isPanning = false;
    currentRect = null;
    
    // Update cursor based on what's under the mouse
    const rect = canvas.getBoundingClientRect();
    const mouseX = (event.clientX - rect.left) * (canvas.width / rect.width);
    const mouseY = (event.clientY - rect.top) * (canvas.height / rect.height);
    updateCursor({ x: mouseX, y: mouseY });
    
    redrawCanvas();
}

// Add this new function after saveProperties
function resetProperties() {
    console.log("resetProperties called");
    
    if (selectedRect && selectedRectIndex >= 0) {
        // Clear the content fields
        document.getElementById('text-content').value = '';
        document.getElementById('text-id').value = '';
        
        // Reset to default block type
        document.getElementById('block-type').value = 'Text';
        
        // Update the rectangle object
        selectedRect.Text_Content = '';
        selectedRect.Text_ID = '';
        selectedRect.Block_Type = 'Text';
        
        // Update Boundary_Boxes
        selectedRect.Boundary_Boxes = rectToBbox(selectedRect);
        
        rectangles[selectedRectIndex] = selectedRect;
        
        console.log("Reset rectangle:", selectedRect);
        
        // Save to history
        saveHistory();
        
        // Update theme to reflect the reset block type
        updatePanelTheme('Text');
        
        redrawCanvas();
        sendDataToStreamlit();
        updateStatus(`Content reset for ${selectedRect.Block_ID}`);
    } else {
        console.log("No selected rectangle to reset");
    }
}

function saveProperties(addToHistory = true) {
    console.log("saveProperties called");
    
    if (selectedRect && selectedRectIndex >= 0) {
        // Keep the Block_ID unchanged (it's readonly)
        if (!selectedRect.Block_ID) {
            selectedRect.Block_ID = document.getElementById('content-id').value;
        }
        
        const blockTypeElement = document.getElementById('block-type');
        const textContentElement = document.getElementById('text-content');
        const textIdElement = document.getElementById('text-id');
        
        console.log("Block Type Element:", blockTypeElement?.value);
        console.log("Text Content Element:", textContentElement?.value);
        console.log("Text ID Element:", textIdElement?.value);
        
        if (blockTypeElement) {
            selectedRect.Block_Type = blockTypeElement.value;
        }
        if (textContentElement) {
            selectedRect.Text_Content = textContentElement.value;
        }
        if (textIdElement) {
            selectedRect.Text_ID = textIdElement.value;
        }
        
        // Update Boundary_Boxes
        selectedRect.Boundary_Boxes = rectToBbox(selectedRect);
        
        rectangles[selectedRectIndex] = selectedRect;
        
        console.log("Updated rectangle:", selectedRect);
        
        if (addToHistory) {
            saveHistory();
        }
        
        redrawCanvas();
        sendDataToStreamlit();
        updateStatus(`Properties saved for ${selectedRect.Block_ID}`);
    } else {
        console.log("No selected rectangle to save");
    }
}

// Zoom functions
function zoomIn() {
    setZoom(Math.min(zoomLevel + ZOOM_STEP, ZOOM_MAX));
}

function zoomOut() {
    setZoom(Math.max(zoomLevel - ZOOM_STEP, ZOOM_MIN));
}

function zoomReset() {
    setZoom(1.0);
    centerCanvas();
    updateStatus("Zoom reset to 100%");
}

function setZoom(newZoom) {
    // Get the center point of the visible area before zoom
    const scrollCenterX = canvasWrapper.scrollLeft + canvasWrapper.clientWidth / 2;
    const scrollCenterY = canvasWrapper.scrollTop + canvasWrapper.clientHeight / 2;
    
    // Calculate the canvas point at the center
    const canvasCenterX = scrollCenterX / zoomLevel;
    const canvasCenterY = scrollCenterY / zoomLevel;
    
    // Update zoom
    zoomLevel = newZoom;
    canvasContainer.style.transform = `scale(${zoomLevel})`;
    
    // Calculate new scroll position to keep the same point centered
    const newScrollLeft = canvasCenterX * zoomLevel - canvasWrapper.clientWidth / 2;
    const newScrollTop = canvasCenterY * zoomLevel - canvasWrapper.clientHeight / 2;
    
    // Apply new scroll position
    canvasWrapper.scrollLeft = newScrollLeft;
    canvasWrapper.scrollTop = newScrollTop;
    
    updateZoomDisplay();
    updateZoomButtons();
}

function handleWheel(e) {
    if (e.ctrlKey || e.metaKey) {
        e.preventDefault();
        
        const delta = e.deltaY > 0 ? -ZOOM_STEP : ZOOM_STEP;
        const newZoom = Math.max(ZOOM_MIN, Math.min(ZOOM_MAX, zoomLevel + delta));
        
        // Get mouse position relative to canvas wrapper
        const rect = canvasWrapper.getBoundingClientRect();
        const mouseX = e.clientX - rect.left;
        const mouseY = e.clientY - rect.top;
        
        // Calculate the canvas point under the mouse
        const canvasX = (canvasWrapper.scrollLeft + mouseX) / zoomLevel;
        const canvasY = (canvasWrapper.scrollTop + mouseY) / zoomLevel;
        
        // Update zoom
        zoomLevel = newZoom;
        canvasContainer.style.transform = `scale(${zoomLevel})`;
        
        // Calculate new scroll position to keep the mouse over the same canvas point
        canvasWrapper.scrollLeft = canvasX * zoomLevel - mouseX;
        canvasWrapper.scrollTop = canvasY * zoomLevel - mouseY;
        
        updateZoomDisplay();
        updateZoomButtons();
    }
}

function updateCursor(pos) {
    // Only update cursor in draw mode
    if (canvasMode !== 'draw') {
        return;
    }
    
    // Rest of the existing updateCursor code...
    if (selectedRect && getResizeHandle(pos.x, pos.y, selectedRect)) {
        const handle = getResizeHandle(pos.x, pos.y, selectedRect);
        const cursors = {
            'nw': 'nw-resize', 'ne': 'ne-resize',
            'se': 'se-resize', 'sw': 'sw-resize'
        };
        canvas.style.cursor = cursors[handle];
    } else if (rectangles.some(rect => isPointInRect(pos.x, pos.y, rect))) {
        canvas.style.cursor = 'move';
    } else {
        canvas.style.cursor = 'crosshair';
    }
}

function centerCanvas() {
    const containerWidth = canvas.width * zoomLevel;
    const containerHeight = canvas.height * zoomLevel;
    const wrapperWidth = canvasWrapper.clientWidth;
    const wrapperHeight = canvasWrapper.clientHeight;
    
    canvasWrapper.scrollLeft = (containerWidth - wrapperWidth) / 2;
    canvasWrapper.scrollTop = (containerHeight - wrapperHeight) / 2;
}

function updateZoomDisplay() {
    const zoomText = `${Math.round(zoomLevel * 100)}%`;
    document.getElementById('zoom-level').textContent = zoomText;
}

function updateZoomButtons() {
    document.getElementById('zoom-in-btn').disabled = zoomLevel >= ZOOM_MAX;
    document.getElementById('zoom-out-btn').disabled = zoomLevel <= ZOOM_MIN;
}

// Get mouse position adjusted for zoom
function getMousePos(e) {
    const rect = canvas.getBoundingClientRect();
    const scaleX = canvas.width / rect.width;
    const scaleY = canvas.height / rect.height;
    
    return {
        x: (e.clientX - rect.left) * scaleX,
        y: (e.clientY - rect.top) * scaleY
    };
}

// History Management
function saveHistory() {
    historyStep++;
    if (historyStep < history.length) {
        history = history.slice(0, historyStep);
    }
    
    history.push(JSON.parse(JSON.stringify(rectangles)));
    
    if (history.length > MAX_HISTORY) {
        history.shift();
        historyStep--;
    }
    
    updateHistoryButtons();
}

function undo() {
    if (historyStep > 0) {
        historyStep--;
        rectangles = JSON.parse(JSON.stringify(history[historyStep]));
        selectedRect = null;
        selectedRectIndex = -1;
        hidePropertiesPanel();
        redrawCanvas();
        sendDataToStreamlit();
        updateStatus("Undo performed");
        updateHistoryButtons();
    }
}

function redo() {
    if (historyStep < history.length - 1) {
        historyStep++;
        rectangles = JSON.parse(JSON.stringify(history[historyStep]));
        selectedRect = null;
        selectedRectIndex = -1;
        hidePropertiesPanel();
        redrawCanvas();
        sendDataToStreamlit();
        updateStatus("Redo performed");
        updateHistoryButtons();
    }
}

function updateHistoryButtons() {
    const undoBtn = document.getElementById('undo-btn');
    const redoBtn = document.getElementById('redo-btn');
    
    if (undoBtn) undoBtn.disabled = historyStep <= 0;
    if (redoBtn) redoBtn.disabled = historyStep >= history.length - 1;
}

// Status updates
function updateStatus(text) {
    const statusElement = document.getElementById('status-info');
    if (statusElement) {
        statusElement.textContent = text;
    }
}

// Add this function to sort and reassign Block IDs based on position
function reassignBlockIds() {
    // Sort rectangles by position (top to bottom, left to right)
    const sortedRectangles = [...rectangles].sort((a, b) => {
        // First sort by Y position (top to bottom)
        const yDiff = a.y - b.y;
        
        // If Y positions are close (within 10 pixels), sort by X position
        if (Math.abs(yDiff) < 10) {
            return a.x - b.x; // Left to right
        }
        
        return yDiff; // Top to bottom
    });
    
    // Reassign Block IDs based on sorted order
    sortedRectangles.forEach((rect, index) => {
        const newBlockId = `block_${index + 1}`;
        
        // Find the original rectangle and update its Block_ID
        const originalIndex = rectangles.findIndex(r => r === rect);
        if (originalIndex !== -1) {
            rectangles[originalIndex].Block_ID = newBlockId;
            
            // Update selected rectangle if it's the one being modified
            if (selectedRect === rect) {
                selectedRect.Block_ID = newBlockId;
            }
        }
    });
    
    // Update the block counter to the highest number
    blockCounter = rectangles.length;
    
    // Update the properties panel if it's open
    if (selectedRect) {
        const blockIdElement = document.getElementById('content-id');
        if (blockIdElement) {
            blockIdElement.value = selectedRect.Block_ID;
        }
    }
    
    console.log("Block IDs reassigned based on position");
}


// Update the generateBlockId function to use position-based logic
function generateBlockId() {
    // This will be called for new rectangles
    // Temporarily assign a high number that will be corrected after placement
    blockCounter = rectangles.length + 1;
    return `block_${blockCounter}`;
}

// Update the showPropertiesPanel function - FIXED VERSION
function showPropertiesPanel(rect) {
    const panel = document.getElementById('properties-panel');
    if (panel && rect) {
        panel.style.display = 'flex';
        
        // Update panel title based on OCR status
        const panelTitle = panel.querySelector('.panel-title');
        if (panelTitle) {
            if (isProcessingOCR && currentlyProcessingBlockId) {
                if (currentlyProcessingBlockId === rect.Block_ID) {
                    panelTitle.innerHTML = `📝 Properties - <span style="color: #ff9800;">Processing OCR...</span>`;
                } else {
                    panelTitle.innerHTML = `📝 Properties - <span style="color: #f44336;">OCR busy on ${currentlyProcessingBlockId}</span>`;
                }
            } else {
                panelTitle.innerHTML = '📝 Rectangle Properties';
            }
        }
        
        // Force update all fields
        const blockIdField = document.getElementById('content-id');
        const blockTypeField = document.getElementById('block-type');
        const textContentField = document.getElementById('text-content');
        const textIdField = document.getElementById('text-id');
        
        // Set Block ID (readonly)
        if (blockIdField) {
            blockIdField.value = rect.Block_ID || generateBlockId();
        }
        
        // Set Block Type
        const blockType = rect.Block_Type || 'Text';
        if (blockTypeField) {
            blockTypeField.value = blockType;
        }
        
        // Set Text Content
        if (textContentField) {
            textContentField.value = rect.Text_Content || '';
        }
        
        // Set Text ID
        if (textIdField) {
            textIdField.value = rect.Text_ID || '';
        }
        
        // Update boundary box display
        updateBoundaryBoxDisplay();
        
        // Show/hide OCR button based on whether OCR is enabled
        const ocrBtn = document.getElementById('ocr-btn');
        if (ocrBtn) {
            if (ocrEnabled) {
                ocrBtn.style.display = 'inline-flex';
                
                // Update OCR button state based on current processing
                if (isProcessingOCR) {
                    // Keep the same loading class for consistency, just change text
                    ocrBtn.classList.add('loading');
                    ocrBtn.disabled = true;
                    
                    if (currentlyProcessingBlockId === rect.Block_ID) {
                        // This is the block being processed
                        ocrBtn.innerHTML = '<span class="ocr-icon">⏳</span> Processing...';
                    } else {
                        // Another block is being processed - same style, different text
                        ocrBtn.innerHTML = `<span class="ocr-icon">⏳</span> Busy (${currentlyProcessingBlockId})`;
                    }
                } else {
                    // No OCR processing, enable button
                    resetOCRButton();
                }
            } else {
                ocrBtn.style.display = 'none';
            }
        }
        
        // ALWAYS update panel theme based on the current rect's block type
        updatePanelTheme(blockType);
    }
}

// Update the hidePropertiesPanel function to reset styles
function hidePropertiesPanel() {
    const panel = document.getElementById('properties-panel');
    if (panel) {
        panel.style.display = 'none';
        
        // Don't reset isProcessingOCR here - let it continue
        // The OCR will complete and update the rectangle even if panel is hidden
        
        // Reset any inline styles when closing
        panel.style.background = '';
        
        const panelHeader = panel.querySelector('.panel-header');
        if (panelHeader) {
            panelHeader.style.background = '';
        }
        
        const saveBtn = panel.querySelector('.save-btn');
        if (saveBtn) {
            saveBtn.style.background = '';
            saveBtn.onmouseover = null;
            saveBtn.onmouseout = null;
        }
        
        // Reset coordinate section styles
        const coordSection = panel.querySelector('.coordinates-section');
        if (coordSection) {
            coordSection.style.background = '';
        }
        
        // Reset property sections
        const propertySections = panel.querySelectorAll('.property-section');
        propertySections.forEach(section => {
            section.style.background = '';
            section.style.borderBottom = '';
        });
    }
}

// Update the autoSaveProperties function
function autoSaveProperties() {
    if (selectedRect && selectedRectIndex >= 0) {
        saveProperties(false);
    }
}

function saveProperties(addToHistory = true) {
    if (selectedRect && selectedRectIndex >= 0) {
        // Keep the Block_ID unchanged (it's readonly)
        if (!selectedRect.Block_ID) {
            selectedRect.Block_ID = document.getElementById('content-id').value;
        }
        
        selectedRect.Block_Type = document.getElementById('block-type').value;
        selectedRect.Text_Content = document.getElementById('text-content').value;
        selectedRect.Text_ID = document.getElementById('text-id').value;
        
        // Update Boundary_Boxes
        selectedRect.Boundary_Boxes = rectToBbox(selectedRect);
        
        rectangles[selectedRectIndex] = selectedRect;
        
        if (addToHistory) {
            saveHistory();
        }
        
        redrawCanvas();
        sendDataToStreamlit();
        updateStatus(`Properties saved for ${selectedRect.Block_ID}`);
    }
}

// Mouse event handlers
function handleMouseDown(e) {
    const pos = getMousePos(e);
    
    // Store previous selection
    const previousSelectedIndex = selectedRectIndex;
    const wasProcessingOCR = isProcessingOCR;
    
    // Check for resize handle on selected rectangle (works in both modes)
    if (selectedRect) {
        const handle = getResizeHandle(pos.x, pos.y, selectedRect);
        if (handle) {
            isResizing = true;
            resizeHandle = handle;
            resizeStartPos = { x: pos.x, y: pos.y };
            originalRect = {
                x: selectedRect.x,
                y: selectedRect.y,
                width: selectedRect.width,
                height: selectedRect.height
            };
            updateStatus(`Resizing: ${selectedRect.Block_ID}`);
            return;
        }
    }
    
    // Check if clicking on a rectangle (works in both modes)
    let clickedRect = null;
    let clickedIndex = -1;
    
    for (let i = rectangles.length - 1; i >= 0; i--) {
        if (isPointInRect(pos.x, pos.y, rectangles[i])) {
            clickedRect = rectangles[i];
            clickedIndex = i;
            break;
        }
    }
    
    if (clickedRect) {
        // If clicking on a different rectangle while OCR is processing
        if (wasProcessingOCR && clickedIndex !== previousSelectedIndex) {
            console.log("Switching rectangles while OCR is processing");
            // Show warning in status
            updateStatus(`OCR still processing on ${currentlyProcessingBlockId}...`);
        }
        
        // IMPORTANT: Always update selection and show panel, even if same rectangle
        selectedRect = clickedRect;
        selectedRectIndex = clickedIndex;
        
        // Force update the properties panel
        hidePropertiesPanel(); // First hide to reset
        setTimeout(() => {
            showPropertiesPanel(clickedRect); // Then show with new data
        }, 10);
        
        isDragging = true;
        dragOffset.x = pos.x - clickedRect.x;
        dragOffset.y = pos.y - clickedRect.y;
        
        updateStatus(`Selected: ${clickedRect.Block_ID || 'Rectangle'}`);
        redrawCanvas();
        return;
    }
    
    // Rest of the function remains the same...
    // If no rectangle was clicked, handle based on mode
    if (canvasMode === 'pan') {
        // Start panning only if clicking on empty canvas
        isPanning = true;
        panStartX = e.clientX - canvasWrapper.scrollLeft;
        panStartY = e.clientY - canvasWrapper.scrollTop;
        canvas.style.cursor = 'grabbing';
        updateStatus('Panning canvas...');
        
        // Deselect any selected rectangle when panning
        if (selectedRect) {
            // If OCR is processing, let it continue in background
            if (wasProcessingOCR) {
                console.log("OCR continues in background while panning");
            }
            selectedRect = null;
            selectedRectIndex = -1;
            hidePropertiesPanel();
            redrawCanvas();
        }
    } else {
        // Draw mode - start drawing new rectangle
        // If OCR is processing, let it continue in background
        if (wasProcessingOCR) {
            console.log("OCR continues in background while drawing new rectangle");
        }
        
        selectedRect = null;
        selectedRectIndex = -1;
        hidePropertiesPanel();
        
        isDrawing = true;
        startX = pos.x;
        startY = pos.y;
        
        const blockId = generateBlockId();
        currentRect = {
            x: startX,
            y: startY,
            width: 0,
            height: 0,
            Block_ID: blockId,
            Block_Type: 'Text',
            Text_Content: '',
            Text_ID: '',
            Boundary_Boxes: [0, 0, 0, 0]
        };
        
        updateStatus("Drawing new rectangle...");
    }
}

function handleMouseMove(e) {
    const pos = getMousePos(e);
    
    // Handle panning
    if (isPanning) {
        const newScrollLeft = panStartX - e.clientX;
        const newScrollTop = panStartY - e.clientY;
        canvasWrapper.scrollLeft = -newScrollLeft;
        canvasWrapper.scrollTop = -newScrollTop;
        return;
    }
    
    // Update cursor for both modes
    updateCursor(pos);
    
    // Handle drawing, resizing, and dragging
    if (isDrawing && currentRect) {
        currentRect.width = pos.x - startX;
        currentRect.height = pos.y - startY;
        redrawCanvas();
        drawRectangle(currentRect, true);
        
        const w = Math.abs(currentRect.width);
        const h = Math.abs(currentRect.height);
        updateStatus(`Drawing: ${Math.round(w)} × ${Math.round(h)}`);
        
    } else if (isResizing && selectedRect && originalRect && resizeStartPos) {
        resizeRectangle(pos);
    } else if (isDragging && selectedRect) {
        dragRectangle(pos);
    }
}

function handleMouseUp(e) {
    if (isPanning) {
        isPanning = false;
        canvas.style.cursor = canvasMode === 'pan' ? 'grab' : 'crosshair';
        updateStatus(canvasMode === 'pan' ? 'Pan mode' : 'Draw mode');
        return;
    }
    if (isDrawing) {
        finalizeDrawing();
    } else if (isResizing) {
        finalizeResize();
    } else if (isDragging) {
        finalizeDrag();
    }
}

function handleMouseOut(e) {
    const rect = canvas.getBoundingClientRect();
    if (e.clientX < rect.left - 50 || e.clientX > rect.right + 50 ||
        e.clientY < rect.top - 50 || e.clientY > rect.bottom + 50) {
        if (isDrawing || isResizing || isDragging) {
            handleMouseUp(e);
        }
    }
}

// Keyboard shortcuts
function handleKeyDown(e) {
    // Zoom shortcuts
    if (e.ctrlKey || e.metaKey) {
        if (e.key === '=' || e.key === '+') {
            e.preventDefault();
            zoomIn();
        } else if (e.key === '-' || e.key === '_') {
            e.preventDefault();
            zoomOut();
        } else if (e.key === '0') {
            e.preventDefault();
            zoomReset();
        }
    }
    
    // Delete selected rectangle
    if ((e.key === 'Delete' || e.key === 'Backspace') && selectedRect && !e.target.matches('input, textarea')) {
        deleteSelectedRectangle();
    }
    // Undo
    else if (e.ctrlKey && e.key === 'z' && !e.shiftKey) {
        e.preventDefault();
        undo();
    }
    // Redo
    else if (e.ctrlKey && (e.key === 'y' || (e.shiftKey && e.key === 'Z'))) {
        e.preventDefault();
        redo();
    }
    // Escape to deselect
    else if (e.key === 'Escape') {
        selectedRect = null;
        selectedRectIndex = -1;
        hidePropertiesPanel();
        redrawCanvas();
        updateStatus("Selection cleared");
    }

    // Mode switching shortcuts
    if (e.key === 'v' || e.key === 'V') {
        e.preventDefault();
        setCanvasMode('pan');
    } else if (e.key === 'd' || e.key === 'D') {
        e.preventDefault();
        setCanvasMode('draw');
    }
}

// Modify finalizeDrawing to reassign IDs after adding a new rectangle
function finalizeDrawing() {
    isDrawing = false;
    
    if (currentRect && (Math.abs(currentRect.width) > MIN_RECT_SIZE && Math.abs(currentRect.height) > MIN_RECT_SIZE)) {
        if (currentRect.width < 0) {
            currentRect.x += currentRect.width;
            currentRect.width = Math.abs(currentRect.width);
        }
        if (currentRect.height < 0) {
            currentRect.y += currentRect.height;
            currentRect.height = Math.abs(currentRect.height);
        }
        
        // Update boundary boxes
        currentRect.Boundary_Boxes = rectToBbox(currentRect);
        
        rectangles.push(currentRect);
        
        // Reassign all Block IDs based on position
        reassignBlockIds();
        
        saveHistory();
        sendDataToStreamlit();
        updateStatus(`Created: ${currentRect.Block_ID}`);
    }
    
    currentRect = null;
    redrawCanvas();
}

// Update the updateBoundaryBoxDisplay function:
function updateBoundaryBoxDisplay() {
    if (selectedRect) {
        const bbox = rectToBbox(selectedRect);
        
        // Only update if the elements exist
        const bboxX0 = document.getElementById('bbox-x0');
        const bboxY0 = document.getElementById('bbox-y0');
        const bboxX1 = document.getElementById('bbox-x1');
        const bboxY1 = document.getElementById('bbox-y1');
        
        if (bboxX0) bboxX0.value = bbox[0];
        if (bboxY0) bboxY0.value = bbox[1];
        if (bboxX1) bboxX1.value = bbox[2];
        if (bboxY1) bboxY1.value = bbox[3];
        
        // Update size display if it exists
        const width = bbox[2] - bbox[0];
        const height = bbox[3] - bbox[1];
        const sizeDisplay = document.getElementById('size-display');
        if (sizeDisplay) {
            sizeDisplay.textContent = `Size: ${width} × ${height}`;
        }
    }
}

// Modify finalizeResize to potentially reassign IDs if position changed
function finalizeResize() {
    if (!isResizing) return;
    
    isResizing = false;
    resizeHandle = null;
    
    const oldX = originalRect.x;
    const oldY = originalRect.y;
    
    originalRect = null;
    resizeStartPos = null;
    
    if (selectedRect.width < MIN_RECT_SIZE) {
        selectedRect.width = MIN_RECT_SIZE;
    }
    if (selectedRect.height < MIN_RECT_SIZE) {
        selectedRect.height = MIN_RECT_SIZE;
    }
    
    if (selectedRect.x < 0) selectedRect.x = 0;
    if (selectedRect.y < 0) selectedRect.y = 0;
    if (selectedRect.x + selectedRect.width > canvas.width) {
        selectedRect.x = canvas.width - selectedRect.width;
    }
    if (selectedRect.y + selectedRect.height > canvas.height) {
        selectedRect.y = canvas.height - selectedRect.height;
    }
    
    // Update boundary boxes
    selectedRect.Boundary_Boxes = rectToBbox(selectedRect);
    updateBoundaryBoxDisplay();
    
    // Check if position changed significantly (resizing from top-left or top-right corners)
    if (Math.abs(selectedRect.x - oldX) > 5 || Math.abs(selectedRect.y - oldY) > 5) {
        // Reassign Block IDs if position changed
        reassignBlockIds();
    }
    
    saveHistory();
    sendDataToStreamlit();
    redrawCanvas();
    updateStatus(`Resized: ${selectedRect.Block_ID}`);
}

// Modify finalizeDrag to reassign IDs after moving
function finalizeDrag() {
    isDragging = false;
    
    // Update boundary boxes
    selectedRect.Boundary_Boxes = rectToBbox(selectedRect);
    updateBoundaryBoxDisplay();
    
    // Reassign all Block IDs based on new positions
    reassignBlockIds();
    
    saveHistory();
    sendDataToStreamlit();
    updateStatus(`Moved: ${selectedRect.Block_ID}`);
    
    // Redraw to show updated Block IDs
    redrawCanvas();
}

// Modify deleteSelectedRectangle to reassign IDs after deletion
function deleteSelectedRectangle() {
    if (selectedRectIndex >= 0) {
        const deletedId = rectangles[selectedRectIndex].Block_ID;
        rectangles.splice(selectedRectIndex, 1);
        selectedRect = null;
        selectedRectIndex = -1;
        hidePropertiesPanel();
        
        // Reassign all Block IDs after deletion
        reassignBlockIds();
        
        saveHistory();
        redrawCanvas();
        sendDataToStreamlit();
        updateStatus(`Deleted: ${deletedId}`);
    }
}

// Helper functions
function isPointInRect(x, y, rect) {
    return x >= rect.x && x <= rect.x + rect.width &&
           y >= rect.y && y <= rect.y + rect.height;
}

function getResizeHandle(x, y, rect) {
    const handles = getHandlePositions(rect);
    
    for (let handle of handles) {
        const distance = Math.sqrt(Math.pow(x - handle.x, 2) + Math.pow(y - handle.y, 2));
        if (distance <= HANDLE_HIT_SIZE) {
            return handle.type;
        }
    }
    return null;
}

function getHandlePositions(rect) {
    return [
        { x: rect.x, y: rect.y, type: 'nw' },
        { x: rect.x + rect.width, y: rect.y, type: 'ne' },
        { x: rect.x + rect.width, y: rect.y + rect.height, type: 'se' },
        { x: rect.x, y: rect.y + rect.height, type: 'sw' }
    ];
}

function updateCursor(pos) {
    // In pan mode, show appropriate cursor based on what's under the mouse
    if (canvasMode === 'pan') {
        if (selectedRect && getResizeHandle(pos.x, pos.y, selectedRect)) {
            const handle = getResizeHandle(pos.x, pos.y, selectedRect);
            const cursors = {
                'nw': 'nw-resize', 'ne': 'ne-resize',
                'se': 'se-resize', 'sw': 'sw-resize'
            };
            canvas.style.cursor = cursors[handle];
        } else if (rectangles.some(rect => isPointInRect(pos.x, pos.y, rect))) {
            canvas.style.cursor = 'pointer'; // Show pointer when hovering over rectangles in pan mode
        } else {
            canvas.style.cursor = 'grab'; // Show grab cursor for empty areas
        }
        return;
    }
    
    // Draw mode cursors
    if (selectedRect && getResizeHandle(pos.x, pos.y, selectedRect)) {
        const handle = getResizeHandle(pos.x, pos.y, selectedRect);
        const cursors = {
            'nw': 'nw-resize', 'ne': 'ne-resize',
            'se': 'se-resize', 'sw': 'sw-resize'
        };
        canvas.style.cursor = cursors[handle];
    } else if (rectangles.some(rect => isPointInRect(pos.x, pos.y, rect))) {
        canvas.style.cursor = 'move';
    } else {
        canvas.style.cursor = 'crosshair';
    }
}

function resizeRectangle(pos) {
    if (!originalRect || !resizeStartPos) return;
    
    const dx = pos.x - resizeStartPos.x;
    const dy = pos.y - resizeStartPos.y;
    
    if (Math.abs(dx) < RESIZE_THRESHOLD && Math.abs(dy) < RESIZE_THRESHOLD) {
        return;
    }
    
    let newX = originalRect.x;
    let newY = originalRect.y;
    let newWidth = originalRect.width;
    let newHeight = originalRect.height;
    
    switch(resizeHandle) {
        case 'nw':
            newX = Math.min(originalRect.x + originalRect.width - MIN_RECT_SIZE, originalRect.x + dx);
            newY = Math.min(originalRect.y + originalRect.height - MIN_RECT_SIZE, originalRect.y + dy);
            newWidth = originalRect.width - (newX - originalRect.x);
            newHeight = originalRect.height - (newY - originalRect.y);
            break;
            
        case 'ne':
            newY = Math.min(originalRect.y + originalRect.height - MIN_RECT_SIZE, originalRect.y + dy);
            newWidth = Math.max(MIN_RECT_SIZE, originalRect.width + dx);
            newHeight = originalRect.height - (newY - originalRect.y);
            break;
            
        case 'se':
            newWidth = Math.max(MIN_RECT_SIZE, originalRect.width + dx);
            newHeight = Math.max(MIN_RECT_SIZE, originalRect.height + dy);
            break;
            
        case 'sw':
            newX = Math.min(originalRect.x + originalRect.width - MIN_RECT_SIZE, originalRect.x + dx);
            newWidth = originalRect.width - (newX - originalRect.x);
            newHeight = Math.max(MIN_RECT_SIZE, originalRect.height + dy);
            break;
    }
    
    selectedRect.x = newX;
    selectedRect.y = newY;
    selectedRect.width = newWidth;
    selectedRect.height = newHeight;
    
    rectangles[selectedRectIndex] = selectedRect;
    
    // Update boundary box display in real-time
    updateBoundaryBoxDisplay();
    
    redrawCanvas();
    updateStatus(`Resizing: ${Math.round(selectedRect.width)} × ${Math.round(selectedRect.height)}`);
}

function dragRectangle(pos) {
    selectedRect.x = pos.x - dragOffset.x;
    selectedRect.y = pos.y - dragOffset.y;
    
    selectedRect.x = Math.max(0, Math.min(canvas.width - selectedRect.width, selectedRect.x));
    selectedRect.y = Math.max(0, Math.min(canvas.height - selectedRect.height, selectedRect.y));
    
    rectangles[selectedRectIndex] = selectedRect;
    
    // Update boundary box display in real-time
    updateBoundaryBoxDisplay();
    
    redrawCanvas();
    updateStatus(`Moving: ${selectedRect.Block_ID}`);
}

// Drawing functions
function redrawCanvas() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    
    // Draw background image if available
    if (window.backgroundImage && imageLoaded) {
        ctx.drawImage(window.backgroundImage, 0, 0, canvas.width, canvas.height);
    }
    
    // Draw canvas border
    ctx.strokeStyle = '#e0e0e0';
    ctx.lineWidth = 1;
    ctx.strokeRect(0, 0, canvas.width, canvas.height);
    
    // Draw all rectangles
    rectangles.forEach((rect, index) => {
        const isSelected = (index === selectedRectIndex);
        drawRectangle(rect, false, isSelected);
    });
}

// Drawing functions
function drawRectangle(rect, isTemporary = false, isSelected = false) {
    const blockType = rect.Block_Type || 'text';
    const color = isSelected ? SELECTED_COLOR : getBlockTypeColor(blockType);
    
    // Draw rectangle
    ctx.strokeStyle = color;
    ctx.lineWidth = isSelected ? 3 : 2;
    
    if (isTemporary) {
        ctx.setLineDash([5, 5]);
    } else {
        ctx.setLineDash([]);
    }
    
    ctx.strokeRect(rect.x, rect.y, rect.width, rect.height);
    
    // Fill with transparency
    ctx.globalAlpha = isSelected ? 0.15 : 0.08;
    ctx.fillStyle = color;
    ctx.fillRect(rect.x, rect.y, rect.width, rect.height);
    ctx.globalAlpha = 1.0;
    
    ctx.setLineDash([]);
    
    // Draw only Block ID if not temporary (no label)
    if (!isTemporary && rect.Block_ID) {
        drawBlockId(rect, isSelected);
    }
    
    // Draw resize handles if selected
    if (isSelected && !isTemporary) {
        drawResizeHandles(rect);
    }
}

// Get color for block type
function getBlockTypeColor(blockType) {
    // Use provided color scheme, or default color if not found
    if (blockTypeColors && blockTypeColors[blockType]) {
        return blockTypeColors[blockType];
    }
    // If 'other' color is defined, use it for unknown types
    if (blockTypeColors && blockTypeColors['other']) {
        return blockTypeColors['other'];
    }
    // Final fallback to default color
    return DEFAULT_COLOR;
}

function drawBlockId(rect, isSelected) {
    const blockId = rect.Block_ID || '';
    const blockType = rect.Block_Type || 'text';
    const color = isSelected ? SELECTED_COLOR : getBlockTypeColor(blockType);
    
    // Draw Block_ID next to the box (right side, top)
    ctx.font = '11px Arial';
    const idText = blockId;
    const metrics = ctx.measureText(idText);
    
    const padding = 4;
    const margin = 5;
    
    // Position the ID label to the right of the box
    const idX = rect.x + rect.width + margin;
    const idY = rect.y;
    
    // Semi-transparent white background for readability
    ctx.fillStyle = 'rgba(255, 255, 255, 0.95)';
    ctx.fillRect(idX, idY, metrics.width + padding * 2, 16);
    
    // Border
    ctx.strokeStyle = color;
    ctx.lineWidth = 1;
    ctx.strokeRect(idX, idY, metrics.width + padding * 2, 16);
    
    // Text
    ctx.fillStyle = color;
    ctx.textBaseline = 'top';
    ctx.fillText(idText, idX + padding, idY + 2);
}

function drawResizeHandles(rect) {
    const handles = getHandlePositions(rect);
    
    handles.forEach(handle => {
        // Draw larger invisible hit area
        ctx.fillStyle = 'rgba(0, 0, 0, 0)';
        ctx.fillRect(handle.x - HANDLE_HIT_SIZE/2, handle.y - HANDLE_HIT_SIZE/2, HANDLE_HIT_SIZE, HANDLE_HIT_SIZE);
        
        // Draw visible handle
        ctx.fillStyle = '#fff';
        ctx.strokeStyle = SELECTED_COLOR;
        ctx.lineWidth = 2;
        
        ctx.beginPath();
        ctx.rect(handle.x - HANDLE_SIZE/2, handle.y - HANDLE_SIZE/2, HANDLE_SIZE, HANDLE_SIZE);
        ctx.fill();
        ctx.stroke();
    });
}

// Streamlit communication
function sendDataToStreamlit() {
    // Don't send data if we're processing OCR or should skip
    if (isProcessingOCR || skipNextUpdate) {
        console.log("Skipping data send - OCR in progress or skip flag set");
        return;
    }
    
    const data = {
        rectangles: rectangles.map((rect, index) => ({
            Block_ID: rect.Block_ID,
            Block_Type: rect.Block_Type || 'text',
            Text_Content: rect.Text_Content || '',
            Text_ID: rect.Text_ID || '',
            Boundary_Boxes: rectToBbox(rect),
            x: Math.round(rect.x),
            y: Math.round(rect.y),
            width: Math.round(rect.width),
            height: Math.round(rect.height)
        })),
        selected_index: selectedRectIndex,
        canvas_width: canvas.width,
        canvas_height: canvas.height,
        zoom_level: zoomLevel,
    };
    
    console.log("Sending to Streamlit:", data);
    Streamlit.setComponentValue(data);
}

// Convert rectangle coordinates to bbox format [x0, y0, x1, y1]
function rectToBbox(rect) {
    return [
        Math.round(rect.x),                    // x0
        Math.round(rect.y),                    // y0
        Math.round(rect.x + rect.width),       // x1
        Math.round(rect.y + rect.height)       // y1
    ];
}

// Convert bbox format [x0, y0, x1, y1] to rectangle
function bboxToRect(bbox) {
    return {
        x: bbox[0],
        y: bbox[1],
        width: bbox[2] - bbox[0],
        height: bbox[3] - bbox[1]
    };
}

// Update onRender to reassign IDs when loading rectangles
function onRender(event) {
    console.log("Render event received", event.detail);
    
    if (!window.rendered) {
        initCanvas();
        window.rendered = true;
    }
    
    const data = event.detail.args;
    
    if (data) {
        // Load background image if provided
        if (data.image_data && !imageLoaded) {
            console.log("Loading background image...");
            loadImage(data.image_data);
        }
        
        // Check if OCR is enabled
        if (data.ocr_enabled !== undefined) {
            ocrEnabled = data.ocr_enabled;
            console.log("OCR enabled:", ocrEnabled);
        }

        // Check for OCR response - PROCESS THIS FIRST
        if (data.ocr_response && data.ocr_response.text !== undefined) {
            console.log("🎯 OCR Response received:", data.ocr_response);
            
            const ocrText = data.ocr_response.text;
            const rectIndex = data.ocr_response.rect_index;
            const requestId = data.ocr_response.request_id;
            
            // Only process if this is the current OCR request
            if (requestId === currentOCRRequestId || !currentOCRRequestId) {
                // Update the rectangle
                if (rectIndex >= 0 && rectIndex < rectangles.length) {
                    console.log(`Updating rectangle ${rectIndex} with OCR text: ${ocrText}`);
                    
                    rectangles[rectIndex].Text_Content = ocrText;
                    
                    // Update UI if this is the selected rectangle
                    if (rectIndex === selectedRectIndex) {
                        selectedRect = rectangles[rectIndex]; // Update the reference
                        
                        const textContentElement = document.getElementById('text-content');
                        if (textContentElement) {
                            textContentElement.value = ocrText;
                            console.log("✅ Updated text field with OCR result");
                        }
                        
                        // Reset OCR button
                        resetOCRButton();
                    }
                    
                    // Reset OCR state
                    isProcessingOCR = false;
                    currentOCRRequestId = null;
                    currentlyProcessingBlockId = null;
                    
                    // Update panel title back to normal
                    const panel = document.getElementById('properties-panel');
                    if (panel && panel.style.display === 'flex') {
                        const panelTitle = panel.querySelector('.panel-title');
                        if (panelTitle) {
                            panelTitle.innerHTML = '📝 Rectangle Properties';
                        }
                    }
                    
                    // Update canvas
                    redrawCanvas();
                    
                    // Save to history
                    saveHistory();
                    
                    updateStatus(`OCR completed for ${rectangles[rectIndex].Block_ID}`);
                    
                    // Send updated data back to Streamlit
                    sendDataToStreamlit();
                }
            } else {
                console.log(`Ignoring OCR response for request ${requestId} (current: ${currentOCRRequestId})`);
            }
            
            // Don't process rectangles update in the same cycle as OCR response
            return;
        }
        
        // Rest of the function remains the same...
        // Load rectangles if provided (only if not processing OCR response)
        if (data.rectangles && Array.isArray(data.rectangles)) {
            console.log("Loading rectangles:", data.rectangles);
            
            // Check if rectangles have actually changed
            const newRectanglesStr = JSON.stringify(data.rectangles);
            const currentRectanglesStr = JSON.stringify(rectangles);
            
            if (newRectanglesStr !== currentRectanglesStr) {
                rectangles = data.rectangles.map(rect => ({
                    x: rect.x || 0,
                    y: rect.y || 0,
                    width: rect.width || 100,
                    height: rect.height || 50,
                    Block_ID: rect.Block_ID || generateBlockId(),
                    Block_Type: rect.Block_Type || 'Text',
                    Text_Content: rect.Text_Content || '',
                    Text_ID: rect.Text_ID || '',
                    Boundary_Boxes: rect.Boundary_Boxes || [0, 0, 100, 50]
                }));
                
                // Update selected rectangle if it exists
                if (selectedRectIndex >= 0 && selectedRectIndex < rectangles.length) {
                    selectedRect = rectangles[selectedRectIndex];
                    // Update the properties panel if it's open
                    if (document.getElementById('properties-panel').style.display === 'flex') {
                        showPropertiesPanel(selectedRect);
                    }
                }
                
                redrawCanvas();
                updateStatus(`Loaded ${rectangles.length} rectangles`);
            }
        }
        
        // Update block type colors if provided
        if (data.block_type_colors) {
            blockTypeColors = data.block_type_colors;
            console.log("Updated block type colors:", blockTypeColors);
        }
    }
}

// Optional: Add a function to group rectangles by rows for better sorting
function groupRectanglesByRows(threshold = 20) {
    // Group rectangles that are roughly on the same horizontal line
    const rows = [];
    const sorted = [...rectangles].sort((a, b) => a.y - b.y);
    
    sorted.forEach(rect => {
        // Find a row for this rectangle
        let foundRow = false;
        for (let row of rows) {
            // Check if this rectangle belongs to an existing row
            const avgY = row.reduce((sum, r) => sum + r.y, 0) / row.length;
            if (Math.abs(rect.y - avgY) < threshold) {
                row.push(rect);
                foundRow = true;
                break;
            }
        }
        
        // Create a new row if needed
        if (!foundRow) {
            rows.push([rect]);
        }
    });
    
    // Sort each row by X position and flatten
    const sortedRectangles = [];
    rows.forEach(row => {
        row.sort((a, b) => a.x - b.x);
        sortedRectangles.push(...row);
    });
    
    return sortedRectangles;
}

// Alternative version of reassignBlockIds with row grouping
function reassignBlockIdsWithRowGrouping() {
    // Get rectangles sorted by rows
    const sortedRectangles = groupRectanglesByRows();
    
    // Reassign Block IDs based on sorted order
    sortedRectangles.forEach((rect, index) => {
        const newBlockId = `block_${index + 1}`;
        
        // Find the original rectangle and update its Block_ID
        const originalIndex = rectangles.findIndex(r => r === rect);
        if (originalIndex !== -1) {
            rectangles[originalIndex].Block_ID = newBlockId;
            
            // Update selected rectangle if it's the one being modified
            if (selectedRect === rect) {
                selectedRect.Block_ID = newBlockId;
            }
        }
    });
    
    // Update the block counter to the highest number
    blockCounter = rectangles.length;
    
    // Update the properties panel if it's open
    if (selectedRect) {
        const blockIdElement = document.getElementById('content-id');
        if (blockIdElement) {
            blockIdElement.value = selectedRect.Block_ID;
        }
    }
    
    console.log("Block IDs reassigned based on position (with row grouping)");
}

function loadImage(imageData) {
    const img = new Image();
    
    img.onload = function() {
        // Update canvas dimensions to match image
        canvas.width = img.width;
        canvas.height = img.height;
        
        // Store the image for redrawing
        window.backgroundImage = img;
        
        imageLoaded = true;
        redrawCanvas();
        centerCanvas();
        
        Streamlit.setFrameHeight(Math.max(600, Math.min(900, img.height + 150)));
        updateStatus(`Image loaded: ${img.width}x${img.height}`);
    };
    
    img.src = imageData;
}

// Initialize Streamlit communication
Streamlit.events.addEventListener(Streamlit.RENDER_EVENT, onRender);
Streamlit.setComponentReady();
Streamlit.setFrameHeight(700);

// Initialize on DOM ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        if (!window.rendered) {
            initCanvas();
            window.rendered = true;
        }
    });
} else if (!window.rendered) {
    initCanvas();
    window.rendered = true;
}