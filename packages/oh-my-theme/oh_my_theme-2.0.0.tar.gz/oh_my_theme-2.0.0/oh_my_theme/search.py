"""
Search functionality module for Oh My Theme.

This module provides real-time search and filtering capabilities for both
local and remote themes with highlighting and keyboard navigation.
"""

import curses
import re


def show_search_bar(stdscr):
    """Display search input bar at bottom of screen.
    
    Args:
        stdscr: The curses screen object
        
    Returns:
        str or None: Search query string or None if cancelled
    """
    h, w = stdscr.getmaxyx()
    
    # Create search bar at bottom of screen
    search_bar = curses.newwin(1, w, h - 1, 0)
    search_bar.attron(curses.color_pair(2))
    search_bar.addstr(0, 0, "Search: ")
    search_bar.attroff(curses.color_pair(2))
    search_bar.refresh()
    
    # Enable cursor for input
    curses.curs_set(1)
    
    query = ""
    cursor_pos = 8  # Position after "Search: "
    
    while True:
        # Display current query
        search_bar.clear()
        search_bar.attron(curses.color_pair(2))
        display_text = f"Search: {query}"
        if len(display_text) < w:
            search_bar.addstr(0, 0, display_text)
        else:
            # Truncate if too long
            search_bar.addstr(0, 0, display_text[:w-1])
        search_bar.attroff(curses.color_pair(2))
        
        # Position cursor
        if cursor_pos < w:
            search_bar.move(0, cursor_pos)
        search_bar.refresh()
        
        key = search_bar.getch()
        
        if key == 27:  # ESC - cancel search
            curses.curs_set(0)
            return None
        elif key in [10, 13]:  # Enter - confirm search
            curses.curs_set(0)
            return query
        elif key in [curses.KEY_BACKSPACE, 127, 8]:  # Backspace
            if query:
                query = query[:-1]
                cursor_pos = max(8, cursor_pos - 1)
        elif key >= 32 and key <= 126:  # Printable characters
            if len(query) < w - 10:  # Leave some space
                query += chr(key)
                cursor_pos += 1


def filter_themes(themes, query):
    """Filter theme list based on search query.
    
    Args:
        themes (list): List of theme names to filter
        query (str): Search query string
        
    Returns:
        list: Filtered list of theme names that match the query
    """
    if not query or not query.strip():
        return themes
    
    query = query.strip().lower()
    filtered = []
    
    for theme in themes:
        if query in theme.lower():
            filtered.append(theme)
    
    return filtered


def highlight_match(theme_name, query):
    """Create a highlighted version of theme name showing matches.
    
    Args:
        theme_name (str): The theme name to highlight
        query (str): The search query to highlight
        
    Returns:
        list: List of tuples (text, is_highlighted) for rendering
    """
    if not query or not query.strip():
        return [(theme_name, False)]
    
    query = query.strip().lower()
    theme_lower = theme_name.lower()
    
    if query not in theme_lower:
        return [(theme_name, False)]
    
    # Find all matches
    parts = []
    start = 0
    
    while True:
        match_start = theme_lower.find(query, start)
        if match_start == -1:
            # Add remaining text
            if start < len(theme_name):
                parts.append((theme_name[start:], False))
            break
        
        # Add text before match
        if match_start > start:
            parts.append((theme_name[start:match_start], False))
        
        # Add highlighted match
        match_end = match_start + len(query)
        parts.append((theme_name[match_start:match_end], True))
        
        start = match_end
    
    return parts


def handle_search_mode(stdscr, local_themes, remote_themes):
    """Manage search mode interaction and real-time filtering.
    
    Args:
        stdscr: The curses screen object
        local_themes (list): List of local theme names
        remote_themes (list): List of remote theme names
        
    Returns:
        dict: Search state with filtered themes and query, or None if cancelled
    """
    h, w = stdscr.getmaxyx()
    
    # Create search input area
    search_win = curses.newwin(3, w - 4, h // 2 - 1, 2)
    search_win.attron(curses.color_pair(2))
    search_win.box()
    search_win.addstr(0, 2, " Search Themes ")
    search_win.attroff(curses.color_pair(2))
    search_win.addstr(1, 2, "Type to search (ESC to cancel):")
    search_win.refresh()
    
    # Enable cursor
    curses.curs_set(1)
    
    query = ""
    
    while True:
        # Update search display
        search_win.clear()
        search_win.attron(curses.color_pair(2))
        search_win.box()
        search_win.addstr(0, 2, " Search Themes ")
        search_win.attroff(curses.color_pair(2))
        
        # Show current query
        display_query = query if len(query) < w - 10 else query[:w-13] + "..."
        search_win.addstr(1, 2, f"Query: {display_query}")
        
        # Show filtered counts
        filtered_local = filter_themes(local_themes, query)
        filtered_remote = filter_themes(remote_themes, query)
        search_win.addstr(2, 2, f"Found: {len(filtered_local)} local, {len(filtered_remote)} remote")
        
        search_win.refresh()
        
        key = search_win.getch()
        
        if key == 27:  # ESC - cancel search
            curses.curs_set(0)
            return None
        elif key in [10, 13]:  # Enter - apply search
            curses.curs_set(0)
            return {
                'query': query,
                'filtered_local': filtered_local,
                'filtered_remote': filtered_remote,
                'active': True
            }
        elif key in [curses.KEY_BACKSPACE, 127, 8]:  # Backspace
            if query:
                query = query[:-1]
        elif key >= 32 and key <= 126:  # Printable characters
            if len(query) < 50:  # Reasonable limit
                query += chr(key)


def draw_panel_with_search(win, title, items, selection_idx, scroll_top, is_active, 
                          selected_items=None, active_theme=None, search_query=None):
    """Enhanced panel drawing with search highlighting.
    
    Args:
        win: The curses window to draw in
        title (str): Panel title
        items (list): List of items to display
        selection_idx (int): Currently selected item index
        scroll_top (int): Top scroll position
        is_active (bool): Whether this panel is active
        selected_items (set): Set of selected items (for remote themes)
        active_theme (str): Currently active theme name
        search_query (str): Current search query for highlighting
    """
    win.clear()
    border_color = curses.color_pair(2) if is_active else curses.color_pair(1)
    win.attron(border_color)
    win.box()
    win.attroff(border_color)

    # Add search indicator to title if searching
    display_title = title
    if search_query:
        display_title += f" (searching: {search_query[:10]}{'...' if len(search_query) > 10 else ''})"
    
    win.addstr(0, 2, f" {display_title} ", curses.A_BOLD)
    
    h, w = win.getmaxyx()
    menu_height = h - 2
    
    for i in range(menu_height):
        list_idx = scroll_top + i
        if list_idx < len(items):
            item_name = items[list_idx]
            
            # Add checkbox for remote themes or active marker for local themes
            prefix = ""
            if selected_items is not None:  # Remote themes
                prefix = "[✓] " if item_name in selected_items else "[ ] "
            elif active_theme and item_name == active_theme:  # Local themes - mark active
                prefix = "★ "
            
            # Handle highlighting if searching
            if search_query:
                highlight_parts = highlight_match(item_name, search_query)
                display_text = prefix
                
                # Calculate available width
                available_width = w - 4 - len(prefix)
                
                if list_idx == selection_idx:
                    win.attron(curses.color_pair(3) if is_active else curses.color_pair(1))
                
                # Draw prefix
                win.addstr(i + 1, 2, prefix)
                
                # Draw highlighted parts
                x_pos = 2 + len(prefix)
                for part_text, is_highlighted in highlight_parts:
                    if x_pos + len(part_text) >= w - 2:
                        # Truncate if too long
                        remaining_width = w - 2 - x_pos
                        if remaining_width > 1:
                            part_text = part_text[:remaining_width-1] + "…"
                        else:
                            break
                    
                    if is_highlighted:
                        # Highlight the match
                        win.attron(curses.A_REVERSE)
                        win.addstr(i + 1, x_pos, part_text)
                        win.attroff(curses.A_REVERSE)
                    else:
                        win.addstr(i + 1, x_pos, part_text)
                    
                    x_pos += len(part_text)
                    
                    if x_pos >= w - 2:
                        break
                
                if list_idx == selection_idx:
                    win.attroff(curses.color_pair(3) if is_active else curses.color_pair(1))
            else:
                # No search highlighting, use original logic
                display_name = prefix + item_name
                if len(display_name) >= w - 4:
                    display_name = display_name[:w - 5] + "…"
                
                if list_idx == selection_idx:
                    win.attron(curses.color_pair(3) if is_active else curses.color_pair(1))
                    win.addstr(i + 1, 2, display_name)
                    win.attroff(curses.color_pair(3) if is_active else curses.color_pair(1))
                else:
                    win.addstr(i + 1, 2, display_name)
    
    win.refresh()