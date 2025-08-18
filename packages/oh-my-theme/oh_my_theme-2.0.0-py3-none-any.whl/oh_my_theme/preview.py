"""
Simple theme preview module for Oh My Theme.
Shows basic metadata and prompt structure.
"""

import os
import json


def extract_theme_metadata(theme_path):
    """Extract Name, Version, Source, Colors from theme file.
    
    Returns:
        dict: {'name', 'version', 'source', 'colors'}
    """
    if not os.path.exists(theme_path):
        return None
    
    try:
        with open(theme_path, 'r', encoding='utf-8') as f:
            theme_data = json.load(f)
        
        name = os.path.basename(theme_path).replace('.omp.json', '')
        version = str(theme_data.get('version', 'unknown'))
        
        # Check for custom repository source in metadata
        metadata = theme_data.get('metadata', {})
        if metadata.get('custom_repo') and metadata.get('source'):
            source = metadata['source']
        else:
            source = "https://github.com/JanDeDobbeleer/oh-my-posh"
        
        # Count colors
        color_count = 0
        blocks = theme_data.get('blocks', [])
        for block in blocks:
            for segment in block.get('segments', []):
                if segment.get('foreground'):
                    color_count += 1
                if segment.get('background'):
                    color_count += 1
        
        return {
            'name': name,
            'version': version, 
            'source': source,
            'colors': f"{color_count} colors" if color_count > 0 else "default colors"
        }
        
    except:
        name = os.path.basename(theme_path).replace('.omp.json', '') if theme_path else 'unknown'
        return {
            'name': name,
            'version': 'unknown',
            'source': 'unknown', 
            'colors': 'unknown'
        }


def show_enhanced_preview(stdscr, theme_name, is_local=True):
    """Show simple preview dialog."""
    import curses
    
    themes_dir = os.path.expanduser("~/.poshthemes")
    theme_path = os.path.join(themes_dir, f"{theme_name}.omp.json")
    
    downloaded_for_preview = False
    
    # Download if needed
    if not os.path.exists(theme_path) and not is_local:
        if _download_theme(theme_name):
            downloaded_for_preview = True
        else:
            _show_error(stdscr, f"Could not download {theme_name}")
            return False
    
    # Get metadata
    metadata = extract_theme_metadata(theme_path)
    if not metadata:
        _show_error(stdscr, f"Could not read {theme_name}")
        return False
    
    # Show preview
    _show_preview_dialog(stdscr, theme_name, metadata, theme_path)
    
    # Ask to keep if downloaded
    if downloaded_for_preview:
        return _ask_keep_theme(stdscr, theme_name)
    
    return True


def _show_preview_dialog(stdscr, theme_name, metadata, theme_path):
    """Show the preview dialog."""
    import curses
    
    h, w = stdscr.getmaxyx()
    dialog_h, dialog_w = 15, min(60, w - 4)
    dialog_y = h // 2 - dialog_h // 2
    dialog_x = w // 2 - dialog_w // 2
    
    dialog = curses.newwin(dialog_h, dialog_w, dialog_y, dialog_x)
    dialog.box()
    dialog.addstr(0, 2, f" Preview: {theme_name} ", curses.A_BOLD)
    
    # Show metadata
    y = 2
    dialog.addstr(y, 2, f"Name: {metadata['name']}")
    y += 1
    dialog.addstr(y, 2, f"Version: {metadata['version']}")
    y += 1
    dialog.addstr(y, 2, f"Source: {metadata['source']}")
    y += 1
    dialog.addstr(y, 2, f"Colors: {metadata['colors']}")
    y += 2
    
    # Show sample prompt
    dialog.addstr(y, 2, "Sample Prompt:", curses.A_BOLD)
    y += 1
    sample = _get_sample_prompt(theme_path)
    for line in sample.split('\n'):
        if y < dialog_h - 2 and line.strip():
            dialog.addstr(y, 2, line[:dialog_w - 4])
            y += 1
    
    # Footer
    dialog.addstr(dialog_h - 2, 2, "Press ESC to close")
    dialog.refresh()
    
    # Wait for ESC
    while dialog.getch() != 27:
        pass


def _get_sample_prompt(theme_path):
    """Get realistic sample prompt from theme structure."""
    try:
        with open(theme_path, 'r') as f:
            theme_data = json.load(f)
        
        # Build sample from actual theme structure
        sample_lines = []
        blocks = theme_data.get('blocks', [])
        
        for block in blocks:
            block_parts = []
            alignment = block.get('alignment', 'left')
            
            for segment in block.get('segments', []):
                seg_type = segment.get('type', '')
                template = segment.get('template', '')
                
                # Generate realistic content based on segment type and template
                if seg_type == 'session':
                    if '{{ .UserName }}' in template:
                        block_parts.append('john')
                    elif '{{ .HostName }}' in template:
                        block_parts.append('laptop')
                elif seg_type == 'path':
                    if 'full' in str(segment.get('properties', {})):
                        block_parts.append('/home/john/projects/my-app')
                    else:
                        block_parts.append('~/projects/my-app')
                elif seg_type == 'git':
                    if '{{ .HEAD }}' in template:
                        block_parts.append('main')
                    else:
                        block_parts.append('git(main)')
                elif seg_type == 'time':
                    block_parts.append('15:04:32')
                elif seg_type == 'python':
                    block_parts.append('🐍 3.11.0')
                elif seg_type == 'node':
                    block_parts.append('⬢ 18.17.0')
                elif seg_type == 'os':
                    block_parts.append('🐧')
                elif seg_type == 'root':
                    block_parts.append('⚡')
                elif seg_type == 'text':
                    # For text segments, try to extract meaningful content
                    if template and not any(x in template for x in ['{{', '}}', '\\u']):
                        block_parts.append(template.strip())
                    elif '\\u256d\\u2500' in template:  # Box drawing characters
                        block_parts.append('╭─')
                    elif '\\u2570\\u2500' in template:
                        block_parts.append('╰─')
                elif seg_type == 'executiontime':
                    block_parts.append('⏱ 2.3s')
                elif seg_type == 'exit':
                    # Only show if there's an error
                    pass
            
            if block_parts:
                if alignment == 'right':
                    sample_lines.append(' ' * 20 + ' '.join(block_parts))
                else:
                    sample_lines.append(' '.join(block_parts))
        
        # Handle newline and transient prompts
        if theme_data.get('newline'):
            sample_lines.append('')
        
        # Add final prompt symbol
        final_prompt = theme_data.get('final_space', True)
        if sample_lines:
            if theme_data.get('transient_prompt'):
                sample_lines.append('❯ ')
            else:
                sample_lines.append('❯ ')
        else:
            # Fallback if no segments found
            sample_lines = ['john ~/projects/my-app git(main) 15:04', '❯ ']
        
        return '\n'.join(sample_lines)
            
    except Exception as e:
        # Fallback for any parsing errors
        return 'john ~/projects/my-app git(main) 15:04\n❯ '


def _download_theme(theme_name):
    """Download theme file."""
    from urllib import request
    
    themes_dir = os.path.expanduser("~/.poshthemes")
    if not os.path.exists(themes_dir):
        os.makedirs(themes_dir)
    
    url = f"https://raw.githubusercontent.com/JanDeDobbeleer/oh-my-posh/main/themes/{theme_name}.omp.json"
    path = os.path.join(themes_dir, f"{theme_name}.omp.json")
    
    try:
        request.urlretrieve(url, path)
        return True
    except:
        return False


def _ask_keep_theme(stdscr, theme_name):
    """Ask user if they want to keep downloaded theme."""
    import curses
    
    h, w = stdscr.getmaxyx()
    dialog = curses.newwin(6, 50, h//2 - 3, w//2 - 25)
    dialog.box()
    dialog.addstr(1, 2, f"Keep downloaded theme '{theme_name}'?")
    dialog.addstr(2, 2, "Y - Keep theme")
    dialog.addstr(3, 2, "N - Remove theme")
    dialog.addstr(4, 2, "Press Y/N:")
    dialog.refresh()
    
    while True:
        key = dialog.getch()
        if key in [ord('y'), ord('Y')]:
            return True
        elif key in [ord('n'), ord('N')]:
            return False


def _show_error(stdscr, message):
    """Show error message."""
    import curses
    
    h, w = stdscr.getmaxyx()
    dialog = curses.newwin(5, len(message) + 10, h//2 - 2, w//2 - len(message)//2 - 5)
    dialog.box()
    dialog.addstr(1, 2, "Error:")
    dialog.addstr(2, 2, message)
    dialog.addstr(3, 2, "Press any key")
    dialog.refresh()
    dialog.getch()