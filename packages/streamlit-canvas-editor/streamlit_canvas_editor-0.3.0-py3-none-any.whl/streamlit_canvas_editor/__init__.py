from pathlib import Path
from typing import Optional, List, Dict, Any, Union
import base64
from io import BytesIO
import streamlit as st
import streamlit.components.v1 as components
from PIL import Image
import json

# Tell streamlit that there is a component called streamlit_canvas_editor,
# and that the code to display that component is in the "frontend" folder
frontend_dir = (Path(__file__).parent / "frontend").absolute()
_component_func = components.declare_component(
    "streamlit_canvas_editor", path=str(frontend_dir)
)

def image_to_base64(image: Union[Image.Image, str, bytes]) -> str:
    """Convert an image to base64 string for the canvas component."""
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

def normalize_rectangles_to_component(rectangles: List[Dict[str, Any]], page_number: int = 1) -> List[Dict[str, Any]]:
    """Normalize rectangle dictionaries to the format expected by the component."""
    normalized = []
    
    for i, rect in enumerate(rectangles):
        norm_rect = {}
        
        # Handle Block_ID
        if "Block_ID" in rect:
            norm_rect["Block_ID"] = rect["Block_ID"]
        else:
            norm_rect["Block_ID"] = f"page_{page_number}_block_{i+1}"
        
        # Handle Block_Type
        norm_rect["Block_Type"] = rect.get("Block_Type", "text")
        
        # Handle Text_Content
        norm_rect["Text_Content"] = rect.get("Text_Content", "")
        
        # Handle Text_ID
        norm_rect["Text_ID"] = rect.get("Text_ID", "")
        
        # Handle coordinates from Boundary_Boxes [x0, y0, x1, y1]
        if "Boundary_Boxes" in rect and len(rect["Boundary_Boxes"]) == 4:
            bbox = rect["Boundary_Boxes"]
            norm_rect["x"] = bbox[0]
            norm_rect["y"] = bbox[1]
            norm_rect["width"] = bbox[2] - bbox[0]
            norm_rect["height"] = bbox[3] - bbox[1]
            norm_rect["Boundary_Boxes"] = bbox
        else:
            # Default coordinates if missing
            norm_rect["x"] = 10 + i * 20
            norm_rect["y"] = 10 + i * 20
            norm_rect["width"] = 100
            norm_rect["height"] = 50
            norm_rect["Boundary_Boxes"] = [
                norm_rect["x"],
                norm_rect["y"],
                norm_rect["x"] + norm_rect["width"],
                norm_rect["y"] + norm_rect["height"]
            ]
        
        normalized.append(norm_rect)
    
    return normalized

def convert_component_output(result: Dict[str, Any]) -> Dict[str, Any]:
    """Convert component output to match your JSON format."""
    if not result:
        return result

    # Convert rectangles to your format
    if "rectangles" in result and result["rectangles"]:
        formatted_rectangles = []
        for rect in result["rectangles"]:
            formatted_rect = {
                "Block_ID": rect.get("Block_ID", ""),
                "Block_Type": rect.get("Block_Type", "text"),
                "Text_Content": rect.get("Text_Content", ""),
                "Text_ID": rect.get("Text_ID", ""),
                "Boundary_Boxes": rect.get("Boundary_Boxes", [0, 0, 0, 0])
            }
            # Optionally include the Image field (None by default)
            formatted_rect["Image"] = None

            formatted_rectangles.append(formatted_rect)

        result["rectangles"] = formatted_rectangles

    return result

def streamlit_canvas_editor(
    image: Optional[Union[Image.Image, str, bytes]] = None,
    rectangles: Optional[List[Dict[str, Any]]] = None,
    page_number: int = 1,
    height: int = 700,
    ocr_function: Optional[callable] = None,
    key: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Streamlit Canvas Editor Component for drawing and editing rectangles on images.
    """
    
    # Initialize OCR tracking in session state
    if 'ocr_requests' not in st.session_state:
        st.session_state.ocr_requests = {}
    
    # Check if we have a pending OCR response to send
    ocr_response_to_send = None
    if 'pending_ocr_response' in st.session_state:
        ocr_response_to_send = st.session_state.pending_ocr_response
        del st.session_state.pending_ocr_response

    # Prepare image data if provided
    image_data = None
    image_for_ocr = None
    if image is not None:
        if isinstance(image, str):
            image_for_ocr = Image.open(image)
        elif isinstance(image, bytes):
            image_for_ocr = Image.open(BytesIO(image))
        else:
            image_for_ocr = image

        image_data = image_to_base64(image_for_ocr)

    # Normalize rectangles to component format
    normalized_rectangles = None
    if rectangles is not None and len(rectangles) > 0:
        normalized_rectangles = normalize_rectangles_to_component(rectangles, page_number)

    # Call the frontend component with OCR response if available
    component_value = _component_func(
        image_data=image_data,
        rectangles=normalized_rectangles,
        page_number=page_number,
        height=height,
        ocr_enabled=ocr_function is not None,
        ocr_response=ocr_response_to_send,  # Pass the OCR response
        key=key,
        default={
            "rectangles": [],
            "selected_index": -1,
            "canvas_width": 800,
            "canvas_height": 600,
            "ocr_request": None,
        }
    )

    # Handle OCR request from frontend
    if component_value and component_value.get('ocr_request') and ocr_function and image_for_ocr:
        ocr_req = component_value['ocr_request']
        rect_index = ocr_req.get('rect_index')
        bbox = ocr_req.get('bbox')
        request_id = ocr_req.get('request_id')

        # Check if we've already processed this request
        if request_id not in st.session_state.ocr_requests:
            st.session_state.ocr_requests[request_id] = 'processing'
            
            print(f"Processing NEW OCR request {request_id} for rect {rect_index}")
            
            # Show progress indicator for long-running OCR
            with st.spinner(f'🔍 Running OCR on block {rect_index + 1}...'):
                try:
                    x0, y0, x1, y1 = bbox
                    x0, y0, x1, y1 = max(0, x0), max(0, y0), x1, y1

                    cropped_image = image_for_ocr.crop((x0, y0, x1, y1))
                    
                    # Add progress bar for visual feedback
                    progress_placeholder = st.empty()
                    progress_bar = progress_placeholder.progress(0, text="Initializing OCR...")
                    
                    # Simulate progress updates (you can make this more granular if your OCR function supports it)
                    progress_bar.progress(25, text="Preprocessing image...")
                    
                    # Process OCR
                    extracted_text = ocr_function(cropped_image, bbox)
                    
                    progress_bar.progress(90, text="Finalizing...")
                    
                    # Mark as completed
                    st.session_state.ocr_requests[request_id] = 'completed'
                    
                    # Store the OCR response to be sent on next render
                    st.session_state.pending_ocr_response = {
                        "text": extracted_text,
                        "rect_index": rect_index,
                        "request_id": request_id,
                        "success": True
                    }
                    
                    # Update the rectangles in the component value directly
                    if component_value and 'rectangles' in component_value:
                        if rect_index < len(component_value['rectangles']):
                            component_value['rectangles'][rect_index]['Text_Content'] = extracted_text
                    
                    progress_bar.progress(100, text="OCR Complete!")
                    
                    # Clean up progress bar
                    progress_placeholder.empty()
                    
                    # Clean up old requests (keep only last 10)
                    if len(st.session_state.ocr_requests) > 10:
                        oldest_keys = list(st.session_state.ocr_requests.keys())[:-10]
                        for k in oldest_keys:
                            del st.session_state.ocr_requests[k]
                    
                    # Show success message
                    st.success(f"✅ OCR completed for block {rect_index + 1}")
                    
                    # Force a rerun ONLY AFTER OCR is complete
                    st.rerun()

                except Exception as e:
                    print(f"OCR error: {str(e)}")
                    st.session_state.ocr_requests[request_id] = 'error'
                    st.session_state.pending_ocr_response = {
                        "text": f"[OCR Error: {str(e)}]",
                        "rect_index": rect_index,
                        "request_id": request_id,
                        "success": False
                    }
                    
                    # Clean up progress bar if it exists
                    if 'progress_placeholder' in locals():
                        progress_placeholder.empty()
                    
                    st.error(f"❌ OCR failed: {str(e)}")
                    st.rerun()
        else:
            print(f"Skipping duplicate OCR request {request_id} (status: {st.session_state.ocr_requests[request_id]})")

    return convert_component_output(component_value)

def main():
    """Demo application showing canvas editor usage with OCR."""
    st.set_page_config(page_title="Canvas Editor Demo with OCR", layout="wide")
    st.title("📝 Document Block Extraction Editor with OCR")
    
    # Example OCR function - replace with real OCR in production
    def demo_ocr_function(image, bbox):
        """
        Demo OCR function. Replace with real OCR implementation like:
        - pytesseract.image_to_string(image)
        - Google Vision API
        - Azure Computer Vision
        - AWS Textract
        """
        import time
        import random
        
        # Simulate processing time
        time.sleep(0.5)
        
        # Generate demo text based on image size
        width = image.width
        height = image.height
        
        sample_texts = [
            f"Extracted text from region ({width}x{height} pixels)",
            f"Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
            f"Sample OCR output for block at position [{bbox[0]}, {bbox[1]}]",
            f"This is automatically extracted text content.",
            f"Document section {random.randint(1, 10)}: Important information here.",
        ]
        
        return random.choice(sample_texts)
    
    # For real OCR with Tesseract:
    def real_ocr_function(image, bbox):
        """
        Real OCR function using marker OCR converter.
        
        Args:
            image: PIL Image object (cropped region)
            bbox: Bounding box coordinates [x0, y0, x1, y1]
        """
        import tempfile
        import os
        from marker.converters.pdf import PdfConverter
        from marker.output import text_from_rendered
        from marker.models import create_model_dict
        from marker.config.parser import ConfigParser

        # Log the image dimensions for debugging
        print(f"OCR Image size: {image.size} (width x height)")
        print(f"OCR Image mode: {image.mode}")
        print(f"OCR Bounding box: {bbox}")
        
        # Calculate the actual pixel dimensions
        width, height = image.size
        print(f"Processing {width}x{height} pixels region")
        
        # Optional: Ensure minimum resolution for better OCR
        MIN_WIDTH = 300  # Minimum width in pixels
        MIN_HEIGHT = 100  # Minimum height in pixels
        
        # Upscale if image is too small
        if width < MIN_WIDTH or height < MIN_HEIGHT:
            scale_factor = max(MIN_WIDTH / width, MIN_HEIGHT / height)
            new_width = int(width * scale_factor)
            new_height = int(height * scale_factor)
            
            # Use high-quality resampling
            image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
            print(f"Upscaled image to {new_width}x{new_height} for better OCR quality")
        
        # Ensure image is in RGB mode for better compatibility
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Optional: Enhance image quality for OCR
        from PIL import ImageEnhance
        
        # Increase contrast slightly
        enhancer = ImageEnhance.Contrast(image)
        image = enhancer.enhance(1.2)
        
        # Increase sharpness
        enhancer = ImageEnhance.Sharpness(image)
        image = enhancer.enhance(1.5)
        
        config = {
            "output_format": "markdown",
            # Add any specific OCR configurations here
        }
        config_parser = ConfigParser(config)
        
        # Create a temporary file to save the cropped image
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp_file:
            temp_filepath = tmp_file.name
            
            # Save with high quality and DPI information
            # PNG is lossless, ensuring maximum quality
            dpi = (300, 300)  # Set high DPI for better OCR
            image.save(temp_filepath, 'PNG', dpi=dpi, optimize=False)
            
            print(f"Saved temporary image with DPI: {dpi}")
        
        try:
            # Initialize the OCR converter
            converter = PdfConverter(
                config=config_parser.generate_config_dict(),
                artifact_dict=create_model_dict(),
            )
            
            # Run OCR on the temporary file
            rendered = converter(temp_filepath)

            extracted_text, _, _ = text_from_rendered(rendered)
            
            # Log the extracted text length
            print(f"Extracted text length: {len(extracted_text) if extracted_text else 0} characters")
            
            return extracted_text if extracted_text else "No text detected"
            
        except Exception as e:
            print(f"OCR Error: {str(e)}")
            return f"OCR Error: {str(e)}"
        
        finally:
            # Clean up the temporary file
            if os.path.exists(temp_filepath):
                os.remove(temp_filepath)
    
    # Initialize session state for rectangles if not exists
    if 'canvas_rectangles' not in st.session_state:
        st.session_state.canvas_rectangles = [
            {
                "Block_ID": "block_1",
                "Block_Type": "PageHeader",
                "Text_Content": "Document Title",
                "Text_ID": "title_001",
                "Boundary_Boxes": [50, 50, 400, 100],
                "Image": None
            },
            {
                "Block_ID": "block_2",
                "Block_Type": "SectionHeader",
                "Text_Content": "",  # Empty - can be filled with OCR
                "Text_ID": "header_001",
                "Boundary_Boxes": [50, 120, 400, 160],
                "Image": None
            },
            {
                "Block_ID": "block_3",
                "Block_Type": "Text",
                "Text_Content": "",  # Empty - can be filled with OCR
                "Text_ID": "",
                "Boundary_Boxes": [50, 180, 400, 260],
                "Image": None
            },
        ]
    
    # Initialize page number in session state
    if 'page_number' not in st.session_state:
        st.session_state.page_number = 1
    
    # Sidebar
    with st.sidebar:
        st.header("Configuration")
        
        # Image upload
        uploaded_file = st.file_uploader(
            "Upload an image (optional)",
            type=['png', 'jpg', 'jpeg']
        )
        
        st.divider()
        
        # OCR Settings
        st.subheader("🔍 OCR Settings")
        use_ocr = st.checkbox("Enable OCR", value=True, help="Enable OCR button in rectangle properties")
        
        if use_ocr:
            st.info("Click the OCR button in any rectangle's properties to extract text from that region")
        
        st.divider()
        
        # Show built-in color scheme
        st.subheader("Built-in Color Scheme")
        st.info("The component uses a predefined color scheme for different block types")
        
        # Reset button
        if st.button("🔄 Reset to Default Blocks"):
            st.session_state.canvas_rectangles = [
                {
                    "Block_ID": "block_1",
                    "Block_Type": "PageHeader",
                    "Text_Content": "Document Title",
                    "Text_ID": "title_001",
                    "Boundary_Boxes": [50, 50, 400, 100],
                    "Image": None
                },
                {
                    "Block_ID": "block_2",
                    "Block_Type": "SectionHeader",
                    "Text_Content": "",
                    "Text_ID": "header_001",
                    "Boundary_Boxes": [50, 120, 400, 160],
                    "Image": None
                },
                {
                    "Block_ID": "block_3",
                    "Block_Type": "Text",
                    "Text_Content": "",
                    "Text_ID": "",
                    "Boundary_Boxes": [50, 180, 400, 260],
                    "Image": None
                },
            ]
            st.session_state.ocr_processed = set()
            st.rerun()
        
        # Clear all button
        if st.button("🗑️ Clear All Blocks"):
            st.session_state.canvas_rectangles = []
            st.session_state.ocr_processed = set()
            st.rerun()
    
    # Main content
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.subheader("Canvas Editor")
        
        # Prepare image
        image = None
        if uploaded_file is not None:
            image = Image.open(uploaded_file)
        
        # Display the canvas with OCR function if enabled
        result = streamlit_canvas_editor(
            image=image,
            rectangles=st.session_state.canvas_rectangles,
            page_number=st.session_state.page_number,
            height=800,
            ocr_function=real_ocr_function if use_ocr else None,
            key="canvas_demo"
        )
        
        # Update session state with any changes from the canvas
        # But don't trigger rerun if we just processed OCR (it's already handled)
        if result and result.get('rectangles') is not None:
            current_rects_str = json.dumps(st.session_state.canvas_rectangles, sort_keys=True)
            new_rects_str = json.dumps(result['rectangles'], sort_keys=True)
            
            # Only update if there's a real change and not just from OCR processing
            if current_rects_str != new_rects_str and 'pending_ocr_response' not in st.session_state:
                st.session_state.canvas_rectangles = result['rectangles']
                st.rerun()
    
    with col2:
        st.subheader("Extracted Blocks")
        
        # Use rectangles from session state for display
        if st.session_state.canvas_rectangles:
            st.success(f"Total blocks: {len(st.session_state.canvas_rectangles)}")
            
            # Display each block
            for i, rect in enumerate(st.session_state.canvas_rectangles):
                # Use a unique key for each expander based on content, not index
                expander_key = f"{rect['Block_ID']}_{rect['Block_Type']}"
                with st.expander(f"🔲 {rect['Block_ID']} - {rect['Block_Type']}", expanded=False):
                    # Show the JSON object
                    json_obj = {
                        "Block_ID": rect["Block_ID"],
                        "Block_Type": rect["Block_Type"],
                        "Text_Content": rect["Text_Content"],
                        "Text_ID": rect["Text_ID"],
                        "Boundary_Boxes": rect["Boundary_Boxes"],
                        "Image": rect.get("Image")
                    }
                    st.json(json_obj)
                    
                    # Show coordinates breakdown
                    if rect["Boundary_Boxes"] and len(rect["Boundary_Boxes"]) == 4:
                        bbox = rect["Boundary_Boxes"]
                        st.caption(f"📍 Position: ({bbox[0]}, {bbox[1]}) to ({bbox[2]}, {bbox[3]})")
                        st.caption(f"📐 Size: {bbox[2]-bbox[0]} × {bbox[3]-bbox[1]}")
                        
                        # Show OCR status
                        if rect["Text_Content"]:
                            st.caption("✅ Has text content")
                        else:
                            st.caption("⚠️ No text content (use OCR to extract)")
            
            # Export button
            if st.button("📥 Export to JSON"):
                json_str = json.dumps(st.session_state.canvas_rectangles, indent=2)
                st.download_button(
                    label="Download JSON",
                    data=json_str,
                    file_name=f"page_{st.session_state.page_number}_blocks.json",
                    mime="application/json"
                )
        else:
            st.info("Draw rectangles on the canvas to create blocks!")
    
    # Instructions
    with st.expander("📖 How to Use OCR", expanded=False):
        st.markdown("""
        ### Using OCR to Extract Text
        
        1. **Enable OCR**: Check "Enable OCR" in the sidebar
        2. **Select a Rectangle**: Click on any rectangle on the canvas
        3. **Click OCR Button**: In the properties panel, click the "🔍 OCR" button
        4. **Wait for Processing**: The text will be extracted and filled automatically
        5. **Review & Edit**: You can manually edit the extracted text if needed
        
        ### OCR Tips
        - Upload a clear image for better OCR results
        - Draw rectangles tightly around text regions
        - The OCR function can be customized to use any OCR engine
        - Extracted text is automatically saved to the rectangle
        """)

if __name__ == "__main__":
    main()