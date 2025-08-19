console.log("main.js loaded");

let canvas, ctx;
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
let initialResizeRect = null;

const HANDLE_SIZE = 12;
const HANDLE_HIT_SIZE = 16;
const RECT_COLOR = '#ff0000';
const LABEL_PADDING = 4;
const MIN_RECT_SIZE = 20;
const RESIZE_DEAD_ZONE = 3;

function updateDebugInfo(text) {
    const debugElement = document.getElementById('debug-info');
    if (debugElement) {
        debugElement.textContent = text;
    }
    console.log("Debug:", text);
}

function getNextRowNumber() {
    if (rectangles.length === 0) return 0;
    
    // Find the highest row number
    let maxNum = -1;
    rectangles.forEach(rect => {
        const match = rect.label.match(/row (\d+)/);
        if (match) {
            const num = parseInt(match[1]);
            if (num > maxNum) maxNum = num;
        }
    });
    return maxNum + 1;
}

function showPropertiesPanel(rect) {
    const panel = document.getElementById('properties-panel');
    const blockId = document.getElementById('block-id');
    const blockType = document.getElementById('block-type');
    const blockText = document.getElementById('block-text');
    
    if (panel && rect) {
        panel.style.display = 'block';
        
        // Set values
        blockId.value = rect.label || '';
        blockType.value = rect.blockType || 'text';
        blockText.value = rect.blockText || '';
        
        // Update canvas section width
        const canvasSection = document.getElementById('canvas-section');
        if (canvasSection) {
            canvasSection.style.width = 'calc(100% - 320px)';
        }
    }
}

function hidePropertiesPanel() {
    const panel = document.getElementById('properties-panel');
    if (panel) {
        panel.style.display = 'none';
        
        // Reset canvas section width
        const canvasSection = document.getElementById('canvas-section');
        if (canvasSection) {
            canvasSection.style.width = '100%';
        }
    }
}

function saveProperties() {
    if (selectedRect && selectedRectIndex >= 0) {
        const blockType = document.getElementById('block-type').value;
        const blockText = document.getElementById('block-text').value;
        
        selectedRect.blockType = blockType;
        selectedRect.blockText = blockText;
        
        rectangles[selectedRectIndex] = selectedRect;
        
        redrawCanvas();
        sendDataToStreamlit();
        updateDebugInfo(`Properties saved for ${selectedRect.label}`);
    }
}

function initCanvas() {
    console.log("Initializing canvas...");
    canvas = document.getElementById('drawing-canvas');
    
    if (!canvas) {
        console.error("Canvas element not found!");
        return;
    }
    
    ctx = canvas.getContext('2d');
    
    // Set initial canvas size
    canvas.width = 800;
    canvas.height = 600;
    
    // Draw a test rectangle to verify canvas is working
    ctx.strokeStyle = '#ddd';
    ctx.strokeRect(0, 0, canvas.width, canvas.height);
    
    // Mouse events
    canvas.addEventListener('mousedown', handleMouseDown);
    canvas.addEventListener('mousemove', handleMouseMove);
    canvas.addEventListener('mouseup', handleMouseUp);
    canvas.addEventListener('mouseout', handleMouseOut);
    canvas.addEventListener('dblclick', handleDoubleClick);
    
    // Keyboard events
    document.addEventListener('keydown', handleKeyDown);
    
    // Control buttons
    const undoBtn = document.getElementById('undo-btn');
    const savePropsBtn = document.getElementById('save-properties');
    
    if (undoBtn) {
        undoBtn.addEventListener('click', undoLastRect);
        console.log("Undo button initialized");
    }
    
    if (savePropsBtn) {
        savePropsBtn.addEventListener('click', saveProperties);
        console.log("Save properties button initialized");
    }
    
    updateDebugInfo("Canvas initialized");
}

function getMousePos(e) {
    const rect = canvas.getBoundingClientRect();
    return {
        x: e.clientX - rect.left,
        y: e.clientY - rect.top
    };
}

function isPointInRect(x, y, rect) {
    return x >= rect.x && x <= rect.x + rect.width &&
           y >= rect.y && y <= rect.y + rect.height;
}

function getResizeHandle(x, y, rect) {
    const handles = getHandlePositions(rect);
    
    for (let handle of handles) {
        if (Math.abs(x - handle.x) <= HANDLE_HIT_SIZE/2 && 
            Math.abs(y - handle.y) <= HANDLE_HIT_SIZE/2) {
            return handle.type;
        }
    }
    return null;
}

function getHandlePositions(rect) {
    return [
        { x: rect.x, y: rect.y, type: 'nw' },
        { x: rect.x + rect.width/2, y: rect.y, type: 'n' },
        { x: rect.x + rect.width, y: rect.y, type: 'ne' },
        { x: rect.x + rect.width, y: rect.y + rect.height/2, type: 'e' },
        { x: rect.x + rect.width, y: rect.y + rect.height, type: 'se' },
        { x: rect.x + rect.width/2, y: rect.y + rect.height, type: 's' },
        { x: rect.x, y: rect.y + rect.height, type: 'sw' },
        { x: rect.x, y: rect.y + rect.height/2, type: 'w' }
    ];
}

function handleMouseDown(e) {
    const pos = getMousePos(e);
    console.log("Mouse down at", pos);
    
    // Check if clicking on a resize handle of selected rectangle
    if (selectedRect) {
        const handle = getResizeHandle(pos.x, pos.y, selectedRect);
        if (handle) {
            isResizing = true;
            resizeHandle = handle;
            startX = pos.x;
            startY = pos.y;
            initialResizeRect = { ...selectedRect };
            updateDebugInfo(`Resizing ${selectedRect.label}`);
            return;
        }
    }
    
    // Check if clicking on any rectangle
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
        // Select the rectangle
        selectedRect = clickedRect;
        selectedRectIndex = clickedIndex;
        
        // Show properties panel
        showPropertiesPanel(clickedRect);
        
        const handle = getResizeHandle(pos.x, pos.y, clickedRect);
        if (!handle) {
            isDragging = true;
            dragOffset.x = pos.x - clickedRect.x;
            dragOffset.y = pos.y - clickedRect.y;
            updateDebugInfo(`Selected ${clickedRect.label}`);
        }
        
        redrawCanvas();
    } else {
        // Start drawing new rectangle
        selectedRect = null;
        selectedRectIndex = -1;
        hidePropertiesPanel();
        
        isDrawing = true;
        startX = pos.x;
        startY = pos.y;
        
        const rowNum = getNextRowNumber();
        currentRect = {
            x: startX,
            y: startY,
            width: 0,
            height: 0,
            label: `row ${rowNum}`,
            blockType: 'text',
            blockText: '',
            color: RECT_COLOR
        };
        
        updateDebugInfo(`Drawing row ${rowNum}`);
    }
}

function handleMouseMove(e) {
    const pos = getMousePos(e);
    
    // Update cursor
    if (selectedRect && getResizeHandle(pos.x, pos.y, selectedRect)) {
        const handle = getResizeHandle(pos.x, pos.y, selectedRect);
        const cursors = {
            'nw': 'nw-resize', 'n': 'n-resize', 'ne': 'ne-resize',
            'e': 'e-resize', 'se': 'se-resize', 's': 's-resize',
            'sw': 'sw-resize', 'w': 'w-resize'
        };
        canvas.style.cursor = cursors[handle];
    } else if (rectangles.some(rect => isPointInRect(pos.x, pos.y, rect))) {
        canvas.style.cursor = 'move';
    } else {
        canvas.style.cursor = 'crosshair';
    }
    
    if (isDrawing && currentRect) {
        currentRect.width = pos.x - startX;
        currentRect.height = pos.y - startY;
        
        redrawCanvas();
        drawRectangle(currentRect, true);
        
        updateDebugInfo(`Drawing: ${Math.abs(currentRect.width).toFixed(0)} x ${Math.abs(currentRect.height).toFixed(0)}`);
    } else if (isResizing && selectedRect && initialResizeRect) {
        const dx = pos.x - startX;
        const dy = pos.y - startY;
        
        if (Math.abs(dx) < RESIZE_DEAD_ZONE && Math.abs(dy) < RESIZE_DEAD_ZONE) {
            return;
        }
        
        let newX = initialResizeRect.x;
        let newY = initialResizeRect.y;
        let newWidth = initialResizeRect.width;
        let newHeight = initialResizeRect.height;
        
        switch(resizeHandle) {
            case 'nw':
                newX = initialResizeRect.x + dx;
                newY = initialResizeRect.y + dy;
                newWidth = initialResizeRect.width - dx;
                newHeight = initialResizeRect.height - dy;
                break;
            case 'n':
                newY = initialResizeRect.y + dy;
                newHeight = initialResizeRect.height - dy;
                break;
            case 'ne':
                newY = initialResizeRect.y + dy;
                newWidth = initialResizeRect.width + dx;
                newHeight = initialResizeRect.height - dy;
                break;
            case 'e':
                newWidth = initialResizeRect.width + dx;
                break;
            case 'se':
                newWidth = initialResizeRect.width + dx;
                newHeight = initialResizeRect.height + dy;
                break;
            case 's':
                newHeight = initialResizeRect.height + dy;
                break;
            case 'sw':
                newX = initialResizeRect.x + dx;
                newWidth = initialResizeRect.width - dx;
                newHeight = initialResizeRect.height + dy;
                break;
            case 'w':
                newX = initialResizeRect.x + dx;
                newWidth = initialResizeRect.width - dx;
                break;
        }
        
        if (Math.abs(newWidth) >= MIN_RECT_SIZE) {
            selectedRect.x = newX;
            selectedRect.width = newWidth;
        }
        if (Math.abs(newHeight) >= MIN_RECT_SIZE) {
            selectedRect.y = newY;
            selectedRect.height = newHeight;
        }
        
        rectangles[selectedRectIndex] = selectedRect;
        redrawCanvas();
        
        updateDebugInfo(`Resizing ${selectedRect.label}: ${Math.abs(selectedRect.width).toFixed(0)} x ${Math.abs(selectedRect.height).toFixed(0)}`);
    } else if (isDragging && selectedRect) {
        selectedRect.x = pos.x - dragOffset.x;
        selectedRect.y = pos.y - dragOffset.y;
        
        selectedRect.x = Math.max(0, Math.min(canvas.width - selectedRect.width, selectedRect.x));
        selectedRect.y = Math.max(0, Math.min(canvas.height - selectedRect.height, selectedRect.y));
        
        rectangles[selectedRectIndex] = selectedRect;
        redrawCanvas();
        
        updateDebugInfo(`Moving ${selectedRect.label}`);
    }
}

function handleMouseUp(e) {
    if (isDrawing) {
        isDrawing = false;
        
        if (currentRect && (Math.abs(currentRect.width) > MIN_RECT_SIZE || Math.abs(currentRect.height) > MIN_RECT_SIZE)) {
            if (currentRect.width < 0) {
                currentRect.x += currentRect.width;
                currentRect.width = Math.abs(currentRect.width);
            }
            if (currentRect.height < 0) {
                currentRect.y += currentRect.height;
                currentRect.height = Math.abs(currentRect.height);
            }
            
            rectangles.push({...currentRect});
            sendDataToStreamlit();
            updateDebugInfo(`${currentRect.label} added (Total: ${rectangles.length})`);
        }
        
        currentRect = null;
        redrawCanvas();
    } else if (isResizing) {
        isResizing = false;
        resizeHandle = null;
        initialResizeRect = null;
        
        if (selectedRect.width < 0) {
            selectedRect.x += selectedRect.width;
            selectedRect.width = Math.abs(selectedRect.width);
        }
        if (selectedRect.height < 0) {
            selectedRect.y += selectedRect.height;
            selectedRect.height = Math.abs(selectedRect.height);
        }
        
        sendDataToStreamlit();
        redrawCanvas();
    } else if (isDragging) {
        isDragging = false;
        sendDataToStreamlit();
    }
}

function handleMouseOut(e) {
    if (isDrawing) {
        handleMouseUp(e);
    }
}

function handleDoubleClick(e) {
    const pos = getMousePos(e);
    
    for (let i = rectangles.length - 1; i >= 0; i--) {
        if (isPointInRect(pos.x, pos.y, rectangles[i])) {
            const deletedLabel = rectangles[i].label;
            rectangles.splice(i, 1);
            selectedRect = null;
            selectedRectIndex = -1;
            hidePropertiesPanel();
            
            redrawCanvas();
            sendDataToStreamlit();
            updateDebugInfo(`${deletedLabel} deleted (Total: ${rectangles.length})`);
            break;
        }
    }
}

function handleKeyDown(e) {
    if ((e.key === 'Delete' || e.key === 'Backspace') && selectedRect && selectedRectIndex >= 0) {
        const deletedLabel = rectangles[selectedRectIndex].label;
        rectangles.splice(selectedRectIndex, 1);
        selectedRect = null;
        selectedRectIndex = -1;
        hidePropertiesPanel();
        
        redrawCanvas();
        sendDataToStreamlit();
        updateDebugInfo(`${deletedLabel} deleted`);
    } else if (e.key === 'Escape') {
        selectedRect = null;
        selectedRectIndex = -1;
        hidePropertiesPanel();
        redrawCanvas();
    }
}

function undoLastRect() {
    if (rectangles.length > 0) {
        const removedRect = rectangles.pop();
        selectedRect = null;
        selectedRectIndex = -1;
        hidePropertiesPanel();
        
        redrawCanvas();
        sendDataToStreamlit();
        updateDebugInfo(`Undo ${removedRect.label} (Total: ${rectangles.length})`);
    }
}

function drawRectangle(rect, isTemporary = false) {
    const isSelected = (rect === selectedRect);
    
    ctx.strokeStyle = RECT_COLOR;
    ctx.lineWidth = isSelected ? 3 : 2;
    
    if (isTemporary) {
        ctx.setLineDash([5, 5]);
    } else if (isSelected) {
        ctx.setLineDash([]);
        ctx.shadowColor = RECT_COLOR;
        ctx.shadowBlur = 5;
    }
    
    ctx.strokeRect(rect.x, rect.y, rect.width, rect.height);
    ctx.shadowBlur = 0;
    
    ctx.globalAlpha = isSelected ? 0.3 : 0.2;
    ctx.fillStyle = RECT_COLOR;
    ctx.fillRect(rect.x, rect.y, rect.width, rect.height);
    ctx.globalAlpha = 1.0;
    
    ctx.setLineDash([]);
    
    if (!isTemporary && rect.label) {
        drawLabel(rect);
    }
    
    if (isSelected && !isTemporary) {
        drawResizeHandles(rect);
    }
}

function drawLabel(rect) {
    const label = rect.label;
    
    ctx.font = 'bold 12px Arial';
    const textMetrics = ctx.measureText(label);
    const textHeight = 12;
    const bgPadding = LABEL_PADDING;
    
    const labelX = rect.x + 2;
    const labelY = rect.y + 2;
    
    ctx.fillStyle = 'rgba(255, 255, 255, 0.9)';
    ctx.fillRect(labelX, labelY, textMetrics.width + bgPadding * 2, textHeight + bgPadding * 2);
    
    ctx.strokeStyle = '#333';
    ctx.lineWidth = 1;
    ctx.strokeRect(labelX, labelY, textMetrics.width + bgPadding * 2, textHeight + bgPadding * 2);
    
    ctx.fillStyle = '#333';
    ctx.textBaseline = 'top';
    ctx.fillText(label, labelX + bgPadding, labelY + bgPadding);
}

function drawResizeHandles(rect) {
    const handles = getHandlePositions(rect);
    
    ctx.fillStyle = '#fff';
    ctx.strokeStyle = '#000';
    ctx.lineWidth = 2;
    
    handles.forEach(handle => {
        ctx.beginPath();
        ctx.arc(handle.x, handle.y, HANDLE_SIZE/2, 0, 2 * Math.PI);
        ctx.fill();
        ctx.stroke();
    });
}

function redrawCanvas() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    
    ctx.strokeStyle = '#ddd';
    ctx.lineWidth = 1;
    ctx.strokeRect(0, 0, canvas.width, canvas.height);
    
    rectangles.forEach(rect => {
        drawRectangle(rect);
    });
}

function sendDataToStreamlit() {
    const data = {
        rectangles: rectangles.map((rect, index) => ({
            id: index,
            label: rect.label,
            blockType: rect.blockType || 'text',
            blockText: rect.blockText || '',
            x: rect.x,
            y: rect.y,
            width: rect.width,
            height: rect.height,
            x_rel: rect.x / canvas.width,
            y_rel: rect.y / canvas.height,
            width_rel: rect.width / canvas.width,
            height_rel: rect.height / canvas.height
        })),
        selected_index: selectedRectIndex,
        canvas_width: canvas.width,
        canvas_height: canvas.height
    };
    
    console.log("Sending to Streamlit:", data);
    Streamlit.setComponentValue(data);
}

function loadImage(imageData) {
    console.log("Loading image...");
    const img = document.getElementById('background-image');
    
    img.onload = function() {
        console.log("Image loaded:", img.width, "x", img.height);
        
        img.style.display = 'block';
        canvas.width = img.width;
        canvas.height = img.height;
        canvas.style.position = 'absolute';
        canvas.style.top = '0';
        canvas.style.left = '0';
        
        imageLoaded = true;
        redrawCanvas();
        
        Streamlit.setFrameHeight(Math.max(img.height + 100, 500));
        updateDebugInfo(`Image loaded: ${img.width}x${img.height}`);
    };
    
    img.onerror = function() {
        console.error("Failed to load image");
        updateDebugInfo("Error loading image");
    };
    
    img.src = imageData;
}

function onRender(event) {
    console.log("Render event received", event.detail);
    
    if (!window.rendered) {
        console.log("First render");
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', initCanvas);
        } else {
            initCanvas();
        }
        window.rendered = true;
    }
    
    const data = event.detail.args;
    
    if (data) {
        if (data.image_data) {
            loadImage(data.image_data);
        }
        
        if (data.rectangles && Array.isArray(data.rectangles)) {
            rectangles = data.rectangles;
            redrawCanvas();
        }
    }
}

console.log("Setting up Streamlit communication...");
Streamlit.events.addEventListener(Streamlit.RENDER_EVENT, onRender);
Streamlit.setComponentReady();
Streamlit.setFrameHeight(700);

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', function() {
        console.log("DOM Content Loaded");
        if (!window.rendered) {
            initCanvas();
            window.rendered = true;
        }
    });
} else {
    console.log("DOM already loaded");
    if (!window.rendered) {
        initCanvas();
        window.rendered = true;
    }
}