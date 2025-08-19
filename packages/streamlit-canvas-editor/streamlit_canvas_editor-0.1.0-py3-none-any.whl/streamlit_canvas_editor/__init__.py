from pathlib import Path
from typing import Optional, List, Dict, Any, Union
import base64
from io import BytesIO

import streamlit as st
import streamlit.components.v1 as components
from PIL import Image

# Tell streamlit that there is a component called streamlit_canvas_editor,
# and that the code to display that component is in the "frontend" folder
frontend_dir = (Path(__file__).parent / "frontend").absolute()
_component_func = components.declare_component(
    "streamlit_canvas_editor", path=str(frontend_dir)
)

def image_to_base64(image: Union[Image.Image, str, bytes]) -> str:
    """
    Convert an image to base64 string for the canvas component.
    
    Args:
        image: PIL Image object, file path, or bytes
    
    Returns:
        Base64 encoded image string
    """
    if isinstance(image, str):
        # File path
        image = Image.open(image)
    elif isinstance(image, bytes):
        # Bytes data
        image = Image.open(BytesIO(image))
    
    # Convert PIL Image to base64
    buffered = BytesIO()
    image.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode()
    return f"data:image/png;base64,{img_str}"

def normalize_rectangles(rectangles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Normalize rectangle dictionaries to ensure they have all required fields.
    
    Handles various input formats:
    - {x, y, width, height} format
    - {x0, y0, x1, y1} format  
    - {x_min, y_min, x_max, y_max} format
    - Missing fields are filled with defaults
    
    Args:
        rectangles: List of rectangle dictionaries in any format
    
    Returns:
        List of normalized rectangle dictionaries
    """
    normalized = []
    
    for i, rect in enumerate(rectangles):
        # Start with a new normalized rectangle
        norm_rect = {
            "color": "#ff0000"  # Default color
        }
        
        # Handle label/id
        if "label" in rect:
            norm_rect["label"] = rect["label"]
        elif "id" in rect:
            norm_rect["label"] = rect["id"]
        elif "block_id" in rect:
            norm_rect["label"] = rect["block_id"]
        else:
            norm_rect["label"] = f"row {i}"
        
        # Handle block type
        if "blockType" in rect:
            norm_rect["blockType"] = rect["blockType"]
        elif "block_type" in rect:
            norm_rect["blockType"] = rect["block_type"]
        elif "type" in rect:
            norm_rect["blockType"] = rect["type"]
        else:
            norm_rect["blockType"] = "text"
        
        # Handle block text
        if "blockText" in rect:
            norm_rect["blockText"] = rect["blockText"]
        elif "block_text" in rect:
            norm_rect["blockText"] = rect["block_text"]
        elif "text" in rect:
            norm_rect["blockText"] = rect["text"]
        elif "content" in rect:
            norm_rect["blockText"] = rect["content"]
        else:
            norm_rect["blockText"] = ""
        
        # Handle coordinates - multiple format support
        if "x" in rect and "y" in rect and "width" in rect and "height" in rect:
            # Standard format
            norm_rect["x"] = rect["x"]
            norm_rect["y"] = rect["y"]
            norm_rect["width"] = rect["width"]
            norm_rect["height"] = rect["height"]
        elif "x0" in rect and "y0" in rect and "x1" in rect and "y1" in rect:
            # Corner coordinates format
            norm_rect["x"] = min(rect["x0"], rect["x1"])
            norm_rect["y"] = min(rect["y0"], rect["y1"])
            norm_rect["width"] = abs(rect["x1"] - rect["x0"])
            norm_rect["height"] = abs(rect["y1"] - rect["y0"])
        elif "x_min" in rect and "y_min" in rect and "x_max" in rect and "y_max" in rect:
            # Min/max format
            norm_rect["x"] = rect["x_min"]
            norm_rect["y"] = rect["y_min"]
            norm_rect["width"] = rect["x_max"] - rect["x_min"]
            norm_rect["height"] = rect["y_max"] - rect["y_min"]
        elif "left" in rect and "top" in rect and "right" in rect and "bottom" in rect:
            # CSS-style format
            norm_rect["x"] = rect["left"]
            norm_rect["y"] = rect["top"]
            norm_rect["width"] = rect["right"] - rect["left"]
            norm_rect["height"] = rect["bottom"] - rect["top"]
        else:
            # Default values if coordinates missing
            norm_rect["x"] = 10 + i * 20
            norm_rect["y"] = 10 + i * 20
            norm_rect["width"] = 100
            norm_rect["height"] = 50
        
        # Copy any additional custom fields
        for key, value in rect.items():
            if key not in norm_rect and key not in [
                "x0", "y0", "x1", "y1", "x_min", "y_min", "x_max", "y_max",
                "left", "top", "right", "bottom", "block_type", "block_text",
                "block_id", "id", "type", "text", "content"
            ]:
                norm_rect[key] = value
        
        normalized.append(norm_rect)
    
    return normalized

def streamlit_canvas_editor(
    image: Optional[Union[Image.Image, str, bytes]] = None,
    rectangles: Optional[List[Dict[str, Any]]] = None,
    height: int = 700,
    key: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Streamlit Canvas Editor Component for drawing and editing rectangles on images.
    
    This component allows users to:
    - Draw rectangles on a canvas (with or without background image)
    - Load rectangles from any list of dictionaries
    - Select, resize, move, and delete rectangles
    - Edit rectangle properties (type and text content)
    - Export rectangle coordinates and metadata
    
    Args:
        image: Optional background image. Can be:
            - PIL Image object
            - File path string
            - Image bytes
            - None (for blank canvas)
        rectangles: List of dictionaries representing rectangles.
            Supports multiple formats:
            - {x, y, width, height, label, blockType, blockText}
            - {x0, y0, x1, y1, type, text, id}
            - {x_min, y_min, x_max, y_max, ...}
            - Any combination of the above
        height: Height of the component in pixels
        key: Unique key for the component instance
    
    Returns:
        Dictionary containing:
            - rectangles: List of all rectangles with their properties
            - selected_index: Index of currently selected rectangle (-1 if none)
            - canvas_width: Width of the canvas
            - canvas_height: Height of the canvas
    
    Example:
        >>> # Your existing data in any format
        >>> my_data = [
        >>>     {"x0": 10, "y0": 10, "x1": 200, "y1": 50, "text": "Title", "type": "header"},
        >>>     {"x": 10, "y": 60, "width": 190, "height": 40, "content": "Paragraph"},
        >>>     {"x_min": 10, "y_min": 110, "x_max": 200, "y_max": 160, "block_text": "Footer"}
        >>> ]
        >>> 
        >>> # Just pass it directly!
        >>> result = streamlit_canvas_editor(
        >>>     image=my_image,
        >>>     rectangles=my_data,
        >>>     key="my_canvas"
        >>> )
    """
    # Prepare image data if provided
    image_data = None
    if image is not None:
        image_data = image_to_base64(image)
    
    # Normalize rectangles to standard format
    normalized_rectangles = None
    if rectangles is not None and len(rectangles) > 0:
        normalized_rectangles = normalize_rectangles(rectangles)
    
    # Call the frontend component
    component_value = _component_func(
        image_data=image_data,
        rectangles=normalized_rectangles,
        height=height,
        key=key,
        default={"rectangles": [], "selected_index": -1, "canvas_width": 800, "canvas_height": 600}
    )
    
    return component_value


def main():
    """Demo application showing canvas editor usage with various data formats."""
    st.set_page_config(page_title="Canvas Editor Demo", layout="wide")
    st.title("📝 Streamlit Canvas Editor - List of Dicts Demo")
    
    # Sidebar
    with st.sidebar:
        st.header("Data Format Examples")
        
        # Image upload
        uploaded_file = st.file_uploader(
            "Upload an image (optional)", 
            type=['png', 'jpg', 'jpeg']
        )
        
        st.divider()
        
        # Choose data format example
        data_format = st.selectbox(
            "Choose data format example",
            ["Format 1: x0,y0,x1,y1", "Format 2: x,y,width,height", 
             "Format 3: x_min,y_min,x_max,y_max", "Mixed formats", "Custom data"]
        )
    
    # Main content
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("Canvas Editor")
        
        # Prepare image
        image = None
        if uploaded_file is not None:
            image = Image.open(uploaded_file)
        
        # Prepare rectangles based on selected format
        if data_format == "Format 1: x0,y0,x1,y1":
            # Your existing data format
            my_rectangles = [
                {"x0": 50, "y0": 50, "x1": 400, "y1": 100, "text": "Document Title", "type": "title"},
                {"x0": 50, "y0": 120, "x1": 400, "y1": 200, "text": "First paragraph", "type": "text"},
                {"x0": 50, "y0": 220, "x1": 250, "y1": 320, "text": "Left column", "type": "text"},
                {"x0": 270, "y0": 220, "x1": 400, "y1": 320, "text": "Right column", "type": "text"},
            ]
            
        elif data_format == "Format 2: x,y,width,height":
            # Standard rectangle format
            my_rectangles = [
                {"x": 50, "y": 50, "width": 350, "height": 50, "label": "row 0", "blockType": "title", "blockText": "Page Header"},
                {"x": 50, "y": 120, "width": 350, "height": 80, "label": "row 1", "blockType": "text", "blockText": "Content block"},
                {"x": 50, "y": 220, "width": 170, "height": 100, "label": "row 2", "blockType": "image", "blockText": "Image placeholder"},
            ]
            
        elif data_format == "Format 3: x_min,y_min,x_max,y_max":
            # Bounding box format
            my_rectangles = [
                {"x_min": 50, "y_min": 50, "x_max": 400, "y_max": 100, "block_id": "header", "content": "Header Section"},
                {"x_min": 50, "y_min": 120, "x_max": 400, "y_max": 250, "block_id": "main", "content": "Main Content Area"},
                {"x_min": 50, "y_min": 270, "x_max": 400, "y_max": 320, "block_id": "footer", "content": "Footer Section"},
            ]
            
        elif data_format == "Mixed formats":
            # Mix of different formats - the component handles it!
            my_rectangles = [
                {"x0": 50, "y0": 50, "x1": 400, "y1": 100, "text": "Title (x0,y0,x1,y1 format)", "type": "title"},
                {"x": 50, "y": 120, "width": 350, "height": 60, "label": "row 1", "blockText": "Subtitle (x,y,w,h format)"},
                {"x_min": 50, "y_min": 200, "x_max": 200, "y_max": 300, "content": "Left box (min/max format)"},
                {"left": 220, "top": 200, "right": 400, "bottom": 300, "text": "Right box (CSS format)"},
            ]
            
        else:  # Custom data
            # Let user input custom JSON
            custom_json = st.text_area(
                "Enter your rectangle data (JSON format):",
                value='[{"x0": 10, "y0": 10, "x1": 200, "y1": 100, "text": "Custom Rectangle"}]',
                height=150
            )
            try:
                import json
                my_rectangles = json.loads(custom_json)
            except:
                st.error("Invalid JSON format")
                my_rectangles = []
        
        # Show the data being used
        with st.expander("📊 Input Data"):
            st.json(my_rectangles)
        
        # Display the canvas with rectangles
        result = streamlit_canvas_editor(
            image=image,
            rectangles=my_rectangles,  # Just pass your list of dicts!
            height=600,
            key="canvas_demo"
        )
    
    with col2:
        st.subheader("Output Data")
        
        if result and result.get('rectangles'):
            st.success(f"Total rectangles: {len(result['rectangles'])}")
            
            # Display rectangle information
            for rect in result['rectangles']:
                with st.expander(f"{rect['label']} - {rect.get('blockType', 'text')}"):
                    st.json({
                        "id": rect['label'],
                        "type": rect.get('blockType', 'text'),
                        "text": rect.get('blockText', ''),
                        "x": rect['x'],
                        "y": rect['y'],
                        "width": rect['width'],
                        "height": rect['height']
                    })
            
            # Show full output
            with st.expander("📤 Full Output"):
                st.json(result)
        else:
            st.info("Draw rectangles on the canvas or modify the input data!")
    
    # Instructions
    with st.expander("📖 Supported Rectangle Formats"):
        st.markdown("""
        ### The component accepts rectangles in ANY of these formats:
        
        **Format 1: Corner coordinates**
        ```python
        {"x0": 10, "y0": 10, "x1": 200, "y1": 100, "text": "My Text", "type": "title"}
        ```
        
        **Format 2: Position and size**
        ```python
        {"x": 10, "y": 10, "width": 190, "height": 90, "label": "row 0", "blockText": "Content"}
        ```
        
        **Format 3: Min/Max coordinates**
        ```python
        {"x_min": 10, "y_min": 10, "x_max": 200, "y_max": 100, "content": "Text"}
        ```
        
        **Format 4: CSS-style**
        ```python
        {"left": 10, "top": 10, "right": 200, "bottom": 100, "text": "Text"}
        ```
        
        ### Field mappings (all optional):
        - **ID/Label**: `label`, `id`, `block_id` → becomes `label`
        - **Type**: `blockType`, `block_type`, `type` → becomes `blockType`
        - **Text**: `blockText`, `block_text`, `text`, `content` → becomes `blockText`
        - **Coordinates**: Any of the above formats
        
        ### You can mix formats in the same list!
        The component will normalize everything automatically.
        """)


if __name__ == "__main__":
    main()