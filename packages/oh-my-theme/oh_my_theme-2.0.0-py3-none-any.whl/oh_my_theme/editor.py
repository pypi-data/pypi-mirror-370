"""
Theme color editing module for Oh My Theme.

This module provides functionality to customize theme colors through a simple
curses-based interface, allowing users to modify segment colors and save
changes as new themes or overwrite existing ones.
"""

import os
import json
import curses
from typing import Dict, List, Optional, Tuple, Any


def show_color_editor(stdscr, theme_path: str) -> Optional[Dict[str, Any]]:
    """Display color editing interface for theme customization.
    
    Args:
        stdscr: The curses screen object
        theme_path: Path to the theme file to edit
        
    Returns:
        Modified theme data or None if cancelled
    """
    # Initialize color support
    _init_color_support()
    
    try:
        with open(theme_path, 'r', encoding='utf-8') as f:
            theme_data = json.load(f)
    except (json.JSONDecodeError, IOError) as e:
        _show_error_dialog(stdscr, f"Error loading theme: {str(e)}")
        return None
    
    # Extract segment colors for editing
    segment_colors = extract_segment_colors(theme_data)
    
    if not segment_colors:
        _show_error_dialog(stdscr, "No editable colors found in this theme")
        return None
    
    # Show color editing interface
    modified_colors = _show_color_selection_interface(stdscr, segment_colors)
    
    if modified_colors is None:
        return None  # User cancelled
    
    # Apply changes to theme data
    modified_theme_data = _apply_color_changes(theme_data, modified_colors)
    
    return modified_theme_data


def extract_segment_colors(theme_data: Dict[str, Any]) -> Dict[str, Dict[str, str]]:
    """Parse theme JSON to extract segment color information.
    
    Args:
        theme_data: The parsed theme JSON data
        
    Returns:
        Dictionary mapping segment types to their color properties
    """
    segment_colors = {}
    
    # Parse blocks and segments
    blocks = theme_data.get('blocks', [])
    for block_idx, block in enumerate(blocks):
        segments = block.get('segments', [])
        for seg_idx, segment in enumerate(segments):
            segment_type = segment.get('type', 'unknown')
            
            # Create unique identifier for this segment
            segment_id = f"{segment_type}_{block_idx}_{seg_idx}"
            
            colors = {}
            if 'background' in segment:
                colors['background'] = segment['background']
            if 'foreground' in segment:
                colors['foreground'] = segment['foreground']
            
            # Only include segments that have colors
            if colors:
                segment_colors[segment_id] = {
                    'type': segment_type,
                    'colors': colors,
                    'block_idx': block_idx,
                    'seg_idx': seg_idx
                }
    
    return segment_colors


def save_theme_changes(theme_data: Dict[str, Any], original_path: str, new_name: Optional[str] = None) -> Tuple[bool, str]:
    """Save modified theme as new file or overwrite original.
    
    Args:
        theme_data: The modified theme data
        original_path: Path to the original theme file
        new_name: Optional new theme name for saving as new file
        
    Returns:
        Tuple of (success_status, file_path_or_error_message)
    """
    try:
        if new_name:
            # Save as new theme
            themes_dir = os.path.dirname(original_path)
            new_filename = f"{new_name}.omp.json"
            new_path = os.path.join(themes_dir, new_filename)
            
            # Check if file already exists
            if os.path.exists(new_path):
                return False, f"Theme '{new_name}' already exists"
            
            with open(new_path, 'w', encoding='utf-8') as f:
                json.dump(theme_data, f, indent=2)
            
            return True, new_path
        else:
            # Overwrite original
            with open(original_path, 'w', encoding='utf-8') as f:
                json.dump(theme_data, f, indent=2)
            
            return True, original_path
            
    except (IOError, OSError) as e:
        return False, f"Error saving theme: {str(e)}"


def _show_color_selection_interface(stdscr, segment_colors: Dict[str, Dict[str, Any]]) -> Optional[Dict[str, Dict[str, str]]]:
    """Display the color selection interface.
    
    Args:
        stdscr: The curses screen object
        segment_colors: Dictionary of segment colors to edit
        
    Returns:
        Modified colors dictionary or None if cancelled
    """
    curses.curs_set(0)
    
    # Create a list of editable items
    color_items = []
    for segment_id, segment_info in segment_colors.items():
        segment_type = segment_info['type']
        colors = segment_info['colors']
        
        for color_type, color_value in colors.items():
            color_items.append({
                'segment_id': segment_id,
                'segment_type': segment_type,
                'color_type': color_type,
                'color_value': color_value,
                'display': f"{segment_type} - {color_type}: {color_value}"
            })
    
    if not color_items:
        return None
    
    selection = 0
    scroll_top = 0
    modified_colors = {}
    
    h, w = stdscr.getmaxyx()
    color_support = _detect_color_support()
    
    while True:
        stdscr.clear()
        
        # Title
        title = "Theme Color Editor"
        stdscr.addstr(0, (w - len(title)) // 2, title, curses.A_BOLD)
        
        # Color support notice
        notice_y = 1
        if color_support == '256color':
            notice = "Note: Colors approximated to 256-color palette"
            stdscr.addstr(notice_y, 2, notice[:w-4], curses.A_DIM)
            notice_y += 1
        elif color_support in ['16color', 'basic']:
            notice = "Note: Limited color support - showing hex codes only"
            stdscr.addstr(notice_y, 2, notice[:w-4], curses.A_DIM)
            notice_y += 1
        
        # Instructions
        instructions = "UP/DOWN: navigate | ENTER: edit color | S: save | ESC: cancel"
        stdscr.addstr(notice_y, 2, instructions[:w-4])
        
        # Draw color list
        list_start_y = notice_y + 2
        list_height = h - list_start_y - 3
        
        # Handle scrolling
        if selection < scroll_top:
            scroll_top = selection
        elif selection >= scroll_top + list_height:
            scroll_top = selection - list_height + 1
        
        for i in range(list_height):
            list_idx = scroll_top + i
            if list_idx < len(color_items):
                item = color_items[list_idx]
                
                # Get current color value (check if modified)
                segment_id = item['segment_id']
                color_type = item['color_type']
                current_color = item['color_value']
                is_modified = False
                
                if segment_id in modified_colors and color_type in modified_colors[segment_id]:
                    current_color = modified_colors[segment_id][color_type]
                    is_modified = True
                
                # Create display text with color preview
                display_text = _create_color_display_text(
                    item['segment_type'], color_type, current_color, is_modified, w - 4
                )
                
                y_pos = list_start_y + i
                if list_idx == selection:
                    stdscr.attron(curses.color_pair(3))
                    _render_color_line(stdscr, y_pos, 2, display_text, current_color, color_support)
                    stdscr.attroff(curses.color_pair(3))
                else:
                    _render_color_line(stdscr, y_pos, 2, display_text, current_color, color_support)
        
        # Status line
        status = f"Editing {len(color_items)} colors | Modified: {sum(len(colors) for colors in modified_colors.values())}"
        stdscr.addstr(h - 2, 2, status[:w-4])
        
        stdscr.refresh()
        
        key = stdscr.getch()
        
        if key == 27:  # ESC - cancel
            return None
        elif key == ord('s') or key == ord('S'):  # Save
            return modified_colors
        elif key == curses.KEY_UP:
            if selection > 0:
                selection -= 1
        elif key == curses.KEY_DOWN:
            if selection < len(color_items) - 1:
                selection += 1
        elif key == curses.KEY_ENTER or key in [10, 13]:
            # Edit selected color
            item = color_items[selection]
            segment_id = item['segment_id']
            color_type = item['color_type']
            current_value = item['color_value']
            
            # Check if already modified
            if segment_id in modified_colors and color_type in modified_colors[segment_id]:
                current_value = modified_colors[segment_id][color_type]
            
            new_color = _show_color_input_dialog(stdscr, item['segment_type'], color_type, current_value)
            if new_color is not None:
                if segment_id not in modified_colors:
                    modified_colors[segment_id] = {}
                modified_colors[segment_id][color_type] = new_color


def _show_color_input_dialog(stdscr, segment_type: str, color_type: str, current_value: str) -> Optional[str]:
    """Show dialog for color input.
    
    Args:
        stdscr: The curses screen object
        segment_type: Type of segment being edited
        color_type: Type of color (background/foreground)
        current_value: Current color value
        
    Returns:
        New color value or None if cancelled
    """
    h, w = stdscr.getmaxyx()
    dialog_h, dialog_w = 8, min(60, w - 4)
    dialog_y = h // 2 - dialog_h // 2
    dialog_x = w // 2 - dialog_w // 2
    
    dialog = curses.newwin(dialog_h, dialog_w, dialog_y, dialog_x)
    dialog.attron(curses.color_pair(2))
    dialog.box()
    dialog.attroff(curses.color_pair(2))
    
    # Title and current value
    title = f"Edit {segment_type} {color_type}"
    dialog.addstr(1, 2, title[:dialog_w - 4])
    dialog.addstr(2, 2, f"Current: {current_value}"[:dialog_w - 4])
    
    # Input field
    dialog.addstr(4, 2, "New color:")
    dialog.addstr(5, 2, "(hex #RRGGBB or color name)")
    dialog.addstr(6, 2, "ESC: cancel | ENTER: save")
    
    # Input area
    input_y, input_x = 4, 14
    input_width = dialog_w - input_x - 2
    
    curses.curs_set(1)  # Show cursor
    dialog.refresh()
    
    # Simple input handling
    input_text = current_value
    cursor_pos = len(input_text)
    
    while True:
        # Clear input area and show current text
        dialog.addstr(input_y, input_x, " " * input_width)
        display_text = input_text[:input_width]
        dialog.addstr(input_y, input_x, display_text)
        
        # Position cursor
        cursor_display_pos = min(cursor_pos, input_width - 1)
        dialog.move(input_y, input_x + cursor_display_pos)
        dialog.refresh()
        
        key = dialog.getch()
        
        if key == 27:  # ESC - cancel
            curses.curs_set(0)
            return None
        elif key == curses.KEY_ENTER or key in [10, 13]:  # ENTER - save
            curses.curs_set(0)
            return input_text.strip() if input_text.strip() else None
        elif key == curses.KEY_BACKSPACE or key == 127:
            if cursor_pos > 0:
                input_text = input_text[:cursor_pos-1] + input_text[cursor_pos:]
                cursor_pos -= 1
        elif key == curses.KEY_LEFT:
            if cursor_pos > 0:
                cursor_pos -= 1
        elif key == curses.KEY_RIGHT:
            if cursor_pos < len(input_text):
                cursor_pos += 1
        elif 32 <= key <= 126:  # Printable characters
            if len(input_text) < 50:  # Reasonable limit
                input_text = input_text[:cursor_pos] + chr(key) + input_text[cursor_pos:]
                cursor_pos += 1


def _apply_color_changes(theme_data: Dict[str, Any], modified_colors: Dict[str, Dict[str, str]]) -> Dict[str, Any]:
    """Apply color changes to theme data.
    
    Args:
        theme_data: Original theme data
        modified_colors: Dictionary of color changes
        
    Returns:
        Modified theme data
    """
    # Create a deep copy to avoid modifying original
    import copy
    new_theme_data = copy.deepcopy(theme_data)
    
    # Apply changes
    for segment_id, colors in modified_colors.items():
        # Parse segment_id to get block and segment indices
        parts = segment_id.split('_')
        if len(parts) >= 3:
            try:
                block_idx = int(parts[-2])
                seg_idx = int(parts[-1])
                
                # Apply color changes
                blocks = new_theme_data.get('blocks', [])
                if block_idx < len(blocks):
                    segments = blocks[block_idx].get('segments', [])
                    if seg_idx < len(segments):
                        segment = segments[seg_idx]
                        for color_type, color_value in colors.items():
                            segment[color_type] = color_value
            except (ValueError, IndexError):
                continue  # Skip invalid segment IDs
    
    return new_theme_data


def _show_error_dialog(stdscr, message: str):
    """Show an error dialog.
    
    Args:
        stdscr: The curses screen object
        message: Error message to display
    """
    h, w = stdscr.getmaxyx()
    dialog_h, dialog_w = 5, min(len(message) + 10, w - 4)
    dialog_y = h // 2 - dialog_h // 2
    dialog_x = w // 2 - dialog_w // 2
    
    dialog = curses.newwin(dialog_h, dialog_w, dialog_y, dialog_x)
    dialog.attron(curses.color_pair(2))
    dialog.box()
    dialog.attroff(curses.color_pair(2))
    
    dialog.addstr(1, 2, "Error:")
    dialog.addstr(2, 2, message[:dialog_w - 4])
    dialog.addstr(3, 2, "Press any key to continue")
    dialog.refresh()
    
    dialog.getch()


def _show_save_options_dialog(stdscr, theme_name: str) -> Tuple[Optional[str], bool]:
    """Show dialog for save options.
    
    Args:
        stdscr: The curses screen object
        theme_name: Current theme name
        
    Returns:
        Tuple of (new_theme_name_or_None, overwrite_original)
    """
    h, w = stdscr.getmaxyx()
    dialog_h, dialog_w = 8, min(50, w - 4)
    dialog_y = h // 2 - dialog_h // 2
    dialog_x = w // 2 - dialog_w // 2
    
    dialog = curses.newwin(dialog_h, dialog_w, dialog_y, dialog_x)
    dialog.attron(curses.color_pair(2))
    dialog.box()
    dialog.attroff(curses.color_pair(2))
    
    dialog.addstr(1, 2, f"Save changes to '{theme_name}'?")
    dialog.addstr(3, 2, "O - Overwrite original")
    dialog.addstr(4, 2, "N - Save as new theme")
    dialog.addstr(5, 2, "C - Cancel")
    dialog.refresh()
    
    while True:
        key = dialog.getch()
        if key in [ord('o'), ord('O')]:
            return None, True  # Overwrite original
        elif key in [ord('n'), ord('N')]:
            # Get new theme name
            new_name = _show_name_input_dialog(stdscr, f"{theme_name}_custom")
            if new_name:
                return new_name, False
            else:
                continue  # Back to save options if name input was cancelled
        elif key in [ord('c'), ord('C')]:
            return None, False  # Cancel


def _show_name_input_dialog(stdscr, default_name: str) -> Optional[str]:
    """Show dialog for entering new theme name.
    
    Args:
        stdscr: The curses screen object
        default_name: Default theme name
        
    Returns:
        New theme name or None if cancelled
    """
    h, w = stdscr.getmaxyx()
    dialog_h, dialog_w = 6, min(50, w - 4)
    dialog_y = h // 2 - dialog_h // 2
    dialog_x = w // 2 - dialog_w // 2
    
    dialog = curses.newwin(dialog_h, dialog_w, dialog_y, dialog_x)
    dialog.attron(curses.color_pair(2))
    dialog.box()
    dialog.attroff(curses.color_pair(2))
    
    dialog.addstr(1, 2, "Enter new theme name:")
    dialog.addstr(4, 2, "ESC: cancel | ENTER: save")
    
    # Input area
    input_y, input_x = 2, 2
    input_width = dialog_w - 4
    
    curses.curs_set(1)  # Show cursor
    dialog.refresh()
    
    # Simple input handling
    input_text = default_name
    cursor_pos = len(input_text)
    
    while True:
        # Clear input area and show current text
        dialog.addstr(input_y, input_x, " " * input_width)
        display_text = input_text[:input_width]
        dialog.addstr(input_y, input_x, display_text)
        
        # Position cursor
        cursor_display_pos = min(cursor_pos, input_width - 1)
        dialog.move(input_y, input_x + cursor_display_pos)
        dialog.refresh()
        
        key = dialog.getch()
        
        if key == 27:  # ESC - cancel
            curses.curs_set(0)
            return None
        elif key == curses.KEY_ENTER or key in [10, 13]:  # ENTER - save
            curses.curs_set(0)
            result = input_text.strip()
            # Basic validation
            if result and all(c.isalnum() or c in '-_' for c in result):
                return result
            else:
                continue  # Invalid name, stay in dialog
        elif key == curses.KEY_BACKSPACE or key == 127:
            if cursor_pos > 0:
                input_text = input_text[:cursor_pos-1] + input_text[cursor_pos:]
                cursor_pos -= 1
        elif key == curses.KEY_LEFT:
            if cursor_pos > 0:
                cursor_pos -= 1
        elif key == curses.KEY_RIGHT:
            if cursor_pos < len(input_text):
                cursor_pos += 1
        elif 32 <= key <= 126:  # Printable characters
            if len(input_text) < 30:  # Reasonable limit for theme names
                input_text = input_text[:cursor_pos] + chr(key) + input_text[cursor_pos:]
                cursor_pos += 1


# Color support functions
_color_pair_cache = {}
_next_color_pair = 10  # Start after basic pairs


def _init_color_support():
    """Initialize color support for the terminal."""
    global _color_pair_cache, _next_color_pair
    _color_pair_cache = {}
    _next_color_pair = 10
    
    if curses.has_colors():
        curses.start_color()
        curses.use_default_colors()
        
        # Initialize basic color pairs
        curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLACK)
        curses.init_pair(2, curses.COLOR_BLACK, curses.COLOR_WHITE)
        curses.init_pair(3, curses.COLOR_BLACK, curses.COLOR_CYAN)


def _detect_color_support() -> str:
    """Detect terminal color capabilities.
    
    Returns:
        Color support level: 'truecolor', '256color', '16color', or 'basic'
    """
    if os.environ.get('COLORTERM') in ['truecolor', '24bit']:
        return 'truecolor'
    elif curses.COLORS >= 256:
        return '256color'
    elif curses.COLORS >= 16:
        return '16color'
    else:
        return 'basic'


def _hex_to_rgb(hex_color: str) -> Tuple[int, int, int]:
    """Convert hex color to RGB values.
    
    Args:
        hex_color: Hex color string (e.g., '#RRGGBB' or 'RRGGBB')
        
    Returns:
        RGB tuple (r, g, b) with values 0-255
    """
    hex_color = hex_color.lstrip('#')
    if len(hex_color) != 6:
        return (128, 128, 128)  # Default gray for invalid colors
    
    try:
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    except ValueError:
        return (128, 128, 128)  # Default gray for invalid colors


def _get_closest_256_color(hex_color: str) -> int:
    """Convert hex color to closest 256-color palette index.
    
    Args:
        hex_color: Hex color string
        
    Returns:
        Color index in 256-color palette (0-255)
    """
    r, g, b = _hex_to_rgb(hex_color)
    
    # Check grayscale colors (232-255) first
    gray_avg = (r + g + b) // 3
    if abs(r - gray_avg) < 10 and abs(g - gray_avg) < 10 and abs(b - gray_avg) < 10:
        # It's close to grayscale
        gray_index = int((gray_avg / 255.0) * 23)
        return 232 + gray_index
    
    # Find closest color in 216-color RGB cube (colors 16-231)
    # Each component has 6 levels: 0, 95, 135, 175, 215, 255
    levels = [0, 95, 135, 175, 215, 255]
    
    closest_r = min(levels, key=lambda x: abs(x - r))
    closest_g = min(levels, key=lambda x: abs(x - g))
    closest_b = min(levels, key=lambda x: abs(x - b))
    
    # Calculate 256-color index
    r_idx = levels.index(closest_r)
    g_idx = levels.index(closest_g)
    b_idx = levels.index(closest_b)
    
    return 16 + (36 * r_idx) + (6 * g_idx) + b_idx


def _get_color_pair(hex_color: str, color_support: str) -> Optional[int]:
    """Get or create a color pair for the given hex color.
    
    Args:
        hex_color: Hex color string
        color_support: Color support level
        
    Returns:
        Color pair number or None if not supported
    """
    global _color_pair_cache, _next_color_pair
    
    if color_support in ['basic', '16color']:
        return None
    
    if hex_color in _color_pair_cache:
        return _color_pair_cache[hex_color]
    
    if _next_color_pair >= curses.COLOR_PAIRS:
        return None  # No more color pairs available
    
    try:
        if color_support == '256color':
            color_index = _get_closest_256_color(hex_color)
            curses.init_pair(_next_color_pair, color_index, -1)  # -1 for default background
        elif color_support == 'truecolor':
            r, g, b = _hex_to_rgb(hex_color)
            # Convert to curses RGB values (0-1000)
            r_curses = int((r / 255.0) * 1000)
            g_curses = int((g / 255.0) * 1000)
            b_curses = int((b / 255.0) * 1000)
            
            # Define a new color and use it
            color_num = _next_color_pair + 100  # Offset to avoid conflicts
            if color_num < curses.COLORS:
                curses.init_color(color_num, r_curses, g_curses, b_curses)
                curses.init_pair(_next_color_pair, color_num, -1)
        
        _color_pair_cache[hex_color] = _next_color_pair
        _next_color_pair += 1
        return _color_pair_cache[hex_color]
        
    except curses.error:
        return None


def _create_color_display_text(segment_type: str, color_type: str, color_value: str, is_modified: bool, max_width: int) -> str:
    """Create display text for a color item.
    
    Args:
        segment_type: Type of segment
        color_type: Type of color (foreground/background)
        color_value: Hex color value
        is_modified: Whether the color has been modified
        max_width: Maximum width for the text
        
    Returns:
        Formatted display text
    """
    modifier = " *" if is_modified else ""
    base_text = f"{segment_type} - {color_type}: {color_value}{modifier}"
    
    if len(base_text) >= max_width:
        return base_text[:max_width - 3] + "..."
    
    return base_text


def _render_color_line(stdscr, y: int, x: int, text: str, hex_color: str, color_support: str):
    """Render a line with color preview.
    
    Args:
        stdscr: The curses screen object
        y: Y position
        x: X position
        text: Text to display
        hex_color: Hex color for preview
        color_support: Color support level
    """
    if color_support in ['basic', '16color']:
        # Just display the text without color
        stdscr.addstr(y, x, text)
        return
    
    # Find the hex color in the text to colorize it
    hex_start = text.find('#')
    if hex_start == -1:
        stdscr.addstr(y, x, text)
        return
    
    # Split text into parts: before hex, hex color, after hex
    before_hex = text[:hex_start]
    hex_end = hex_start + 7 if hex_start + 7 <= len(text) else len(text)
    hex_part = text[hex_start:hex_end]
    after_hex = text[hex_end:]
    
    # Render before hex
    stdscr.addstr(y, x, before_hex)
    current_x = x + len(before_hex)
    
    # Render hex with color
    color_pair = _get_color_pair(hex_color, color_support)
    if color_pair:
        try:
            stdscr.attron(curses.color_pair(color_pair))
            stdscr.addstr(y, current_x, hex_part)
            stdscr.attroff(curses.color_pair(color_pair))
        except curses.error:
            stdscr.addstr(y, current_x, hex_part)
    else:
        stdscr.addstr(y, current_x, hex_part)
    
    current_x += len(hex_part)
    
    # Render after hex
    if after_hex:
        stdscr.addstr(y, current_x, after_hex)