"""
Custom repository management module for Oh My Theme.

This module provides functionality to add custom Git repositories,
fetch .omp.json theme files, and install them locally.
"""

import os
import json
import curses
import re
from urllib import request
from urllib.parse import urlparse


def show_repo_input_dialog(stdscr):
    """Display dialog for Git repository URL input.
    
    Args:
        stdscr: The curses screen object
        
    Returns:
        str or None: Repository URL or None if cancelled
    """
    h, w = stdscr.getmaxyx()
    dialog_h, dialog_w = 8, min(70, w - 4)
    dialog_y = h // 2 - dialog_h // 2
    dialog_x = w // 2 - dialog_w // 2
    
    dialog = curses.newwin(dialog_h, dialog_w, dialog_y, dialog_x)
    dialog.attron(curses.color_pair(2))
    dialog.box()
    dialog.addstr(0, 2, " Add Custom Repository ")
    dialog.attroff(curses.color_pair(2))
    
    dialog.addstr(1, 2, "Enter Git repository URL:")
    dialog.addstr(2, 2, "Example: https://github.com/user/themes")
    dialog.addstr(3, 2, "URL: ")
    dialog.addstr(5, 2, "Press Enter to confirm, ESC to cancel")
    dialog.refresh()
    
    # Enable cursor for input
    curses.curs_set(1)
    
    url = ""
    input_y, input_x = 3, 7
    max_input_width = dialog_w - 10
    
    while True:
        # Clear input area and display current URL
        dialog.addstr(input_y, input_x, " " * max_input_width)
        display_url = url if len(url) <= max_input_width else "..." + url[-(max_input_width-3):]
        dialog.addstr(input_y, input_x, display_url)
        
        # Position cursor
        cursor_x = input_x + len(display_url)
        if cursor_x < dialog_w - 2:
            dialog.move(input_y, cursor_x)
        dialog.refresh()
        
        key = dialog.getch()
        
        if key == 27:  # ESC - cancel
            curses.curs_set(0)
            return None
        elif key in [10, 13]:  # Enter - confirm
            curses.curs_set(0)
            return url.strip() if url.strip() else None
        elif key in [curses.KEY_BACKSPACE, 127, 8]:  # Backspace
            if url:
                url = url[:-1]
        elif key >= 32 and key <= 126:  # Printable characters
            if len(url) < 200:  # Reasonable URL length limit
                url += chr(key)


def validate_repository_url(repo_url):
    """Validate that the provided URL is a valid Git repository URL.
    
    Args:
        repo_url (str): The repository URL to validate
        
    Returns:
        tuple: (is_valid, error_message)
    """
    if not repo_url:
        return False, "URL cannot be empty"
    
    # Parse URL
    try:
        parsed = urlparse(repo_url)
    except Exception:
        return False, "Invalid URL format"
    
    # Check scheme
    if parsed.scheme not in ['http', 'https']:
        return False, "URL must use http or https"
    
    # Check if it looks like a GitHub/GitLab/etc URL
    valid_hosts = ['github.com', 'gitlab.com', 'bitbucket.org']
    if not any(host in parsed.netloc.lower() for host in valid_hosts):
        # Allow other hosts but warn
        pass
    
    # Basic format check - should have at least user/repo structure
    path_parts = [p for p in parsed.path.split('/') if p]
    if len(path_parts) < 2:
        return False, "URL should be in format: https://host.com/user/repository"
    
    return True, ""


def get_github_api_url(repo_url):
    """Convert a GitHub repository URL to its API URL for contents.
    
    Args:
        repo_url (str): The GitHub repository URL
        
    Returns:
        str or None: API URL for repository contents, or None if not GitHub
    """
    try:
        parsed = urlparse(repo_url)
        if 'github.com' not in parsed.netloc.lower():
            return None
        
        # Extract user/repo from path
        path_parts = [p for p in parsed.path.split('/') if p]
        if len(path_parts) < 2:
            return None
        
        user, repo = path_parts[0], path_parts[1]
        # Remove .git suffix if present
        if repo.endswith('.git'):
            repo = repo[:-4]
        
        return f"https://api.github.com/repos/{user}/{repo}/contents"
    
    except Exception:
        return None


def get_raw_file_url(repo_url, filename):
    """Get the raw file URL for a specific file in the repository.
    
    Args:
        repo_url (str): The repository URL
        filename (str): The filename to get raw URL for
        
    Returns:
        str or None: Raw file URL, or None if cannot be constructed
    """
    try:
        parsed = urlparse(repo_url)
        
        if 'github.com' in parsed.netloc.lower():
            # Extract user/repo from path
            path_parts = [p for p in parsed.path.split('/') if p]
            if len(path_parts) < 2:
                return None
            
            user, repo = path_parts[0], path_parts[1]
            # Remove .git suffix if present
            if repo.endswith('.git'):
                repo = repo[:-4]
            
            return f"https://raw.githubusercontent.com/{user}/{repo}/main/{filename}"
        
        # For other hosts, try a common pattern
        # This is a best-guess approach
        base_url = repo_url.rstrip('/')
        if base_url.endswith('.git'):
            base_url = base_url[:-4]
        
        return f"{base_url}/raw/main/{filename}"
    
    except Exception:
        return None


def fetch_themes_from_repo(repo_url):
    """Fetch all .omp.json files from repository root.
    
    Args:
        repo_url (str): The Git repository URL
        
    Returns:
        tuple: (theme_files, error_message)
        theme_files: List of dicts with 'name' and 'download_url' keys
        error_message: Error message if failed, None if successful
    """
    # First validate the URL
    is_valid, error_msg = validate_repository_url(repo_url)
    if not is_valid:
        return [], error_msg
    
    theme_files = []
    
    # Try GitHub API first
    api_url = get_github_api_url(repo_url)
    if api_url:
        try:
            with request.urlopen(api_url) as response:
                if response.status == 200:
                    data = json.loads(response.read().decode())
                    
                    for item in data:
                        if (item.get('type') == 'file' and 
                            item.get('name', '').endswith('.omp.json')):
                            theme_files.append({
                                'name': item['name'],
                                'download_url': item['download_url']
                            })
                    
                    if theme_files:
                        return theme_files, None
                    else:
                        return [], "No .omp.json files found in repository root"
                else:
                    return [], f"Failed to access repository (HTTP {response.status})"
        
        except Exception as e:
            # GitHub API failed, try alternative approach
            pass
    
    # Fallback: Try to guess common theme file names and download them
    common_theme_names = [
        'theme.omp.json', 'default.omp.json', 'main.omp.json',
        'custom.omp.json', 'prompt.omp.json'
    ]
    
    for theme_name in common_theme_names:
        raw_url = get_raw_file_url(repo_url, theme_name)
        if raw_url:
            try:
                with request.urlopen(raw_url) as response:
                    if response.status == 200:
                        # Verify it's valid JSON
                        content = response.read().decode()
                        json.loads(content)  # This will raise if invalid JSON
                        
                        theme_files.append({
                            'name': theme_name,
                            'download_url': raw_url
                        })
            except Exception:
                continue
    
    if theme_files:
        return theme_files, None
    else:
        return [], "Could not find any .omp.json files in repository"


def install_custom_themes(theme_files, repo_url, themes_dir):
    """Download and install themes from custom repository.
    
    Args:
        theme_files (list): List of theme file dicts with 'name' and 'download_url'
        repo_url (str): The source repository URL (for metadata)
        themes_dir (str): Local themes directory path
        
    Returns:
        tuple: (success_count, errors)
        success_count: Number of successfully installed themes
        errors: List of error messages for failed installations
    """
    if not os.path.exists(themes_dir):
        try:
            os.makedirs(themes_dir)
        except Exception as e:
            return 0, [f"Failed to create themes directory: {e}"]
    
    success_count = 0
    errors = []
    
    for theme_file in theme_files:
        theme_name = theme_file['name']
        download_url = theme_file['download_url']
        local_path = os.path.join(themes_dir, theme_name)
        
        try:
            # Download the theme file
            with request.urlopen(download_url) as response:
                if response.status == 200:
                    content = response.read()
                    
                    # Verify it's valid JSON
                    theme_data = json.loads(content.decode())
                    
                    # Add source metadata if possible
                    if isinstance(theme_data, dict):
                        if 'metadata' not in theme_data:
                            theme_data['metadata'] = {}
                        theme_data['metadata']['source'] = repo_url
                        theme_data['metadata']['custom_repo'] = True
                    
                    # Write to local file
                    with open(local_path, 'w', encoding='utf-8') as f:
                        json.dump(theme_data, f, indent=2)
                    
                    success_count += 1
                else:
                    errors.append(f"{theme_name}: HTTP {response.status}")
        
        except json.JSONDecodeError:
            errors.append(f"{theme_name}: Invalid JSON format")
        except Exception as e:
            errors.append(f"{theme_name}: {str(e)}")
    
    return success_count, errors


def show_installation_progress(stdscr, theme_files, repo_url, themes_dir):
    """Show installation progress dialog and perform the installation.
    
    Args:
        stdscr: The curses screen object
        theme_files (list): List of theme files to install
        repo_url (str): Source repository URL
        themes_dir (str): Local themes directory
        
    Returns:
        tuple: (success_count, total_count, errors)
    """
    h, w = stdscr.getmaxyx()
    dialog_h, dialog_w = 10, min(60, w - 4)
    dialog_y = h // 2 - dialog_h // 2
    dialog_x = w // 2 - dialog_w // 2
    
    dialog = curses.newwin(dialog_h, dialog_w, dialog_y, dialog_x)
    dialog.attron(curses.color_pair(2))
    dialog.box()
    dialog.addstr(0, 2, " Installing Custom Themes ")
    dialog.attroff(curses.color_pair(2))
    
    total_themes = len(theme_files)
    dialog.addstr(1, 2, f"Repository: {repo_url[:dialog_w-15]}...")
    dialog.addstr(2, 2, f"Installing {total_themes} theme(s)...")
    dialog.addstr(4, 2, "Progress:")
    dialog.refresh()
    
    # Perform installation
    success_count, errors = install_custom_themes(theme_files, repo_url, themes_dir)
    
    # Show results
    dialog.addstr(5, 2, f"Installed: {success_count}/{total_themes}")
    
    if errors:
        dialog.addstr(6, 2, f"Errors: {len(errors)}")
        if len(errors) <= 2:
            for i, error in enumerate(errors[:2]):
                error_text = error[:dialog_w-6] + "..." if len(error) > dialog_w-6 else error
                dialog.addstr(7 + i, 4, error_text)
    else:
        dialog.addstr(6, 2, "All themes installed successfully!")
    
    dialog.addstr(dialog_h - 2, 2, "Press any key to continue...")
    dialog.refresh()
    
    # Wait for user input
    dialog.getch()
    
    return success_count, total_themes, errors


def handle_add_repository(stdscr, themes_dir):
    """Handle the complete workflow of adding a custom repository.
    
    Args:
        stdscr: The curses screen object
        themes_dir (str): Local themes directory path
        
    Returns:
        tuple: (success, message)
        success: True if themes were successfully added
        message: Status message to display to user
    """
    # Get repository URL from user
    repo_url = show_repo_input_dialog(stdscr)
    if not repo_url:
        return False, "Repository addition cancelled"
    
    # Show fetching status
    h, w = stdscr.getmaxyx()
    status_dialog = curses.newwin(5, min(50, w - 4), h // 2 - 2, w // 2 - 25)
    status_dialog.attron(curses.color_pair(2))
    status_dialog.box()
    status_dialog.addstr(0, 2, " Fetching Repository ")
    status_dialog.attroff(curses.color_pair(2))
    status_dialog.addstr(2, 2, "Checking repository...")
    status_dialog.refresh()
    
    # Fetch themes from repository
    theme_files, error_msg = fetch_themes_from_repo(repo_url)
    
    if error_msg:
        status_dialog.clear()
        status_dialog.attron(curses.color_pair(2))
        status_dialog.box()
        status_dialog.addstr(0, 2, " Error ")
        status_dialog.attroff(curses.color_pair(2))
        status_dialog.addstr(1, 2, "Failed to fetch themes:")
        status_dialog.addstr(2, 2, error_msg[:45] + "..." if len(error_msg) > 45 else error_msg)
        status_dialog.addstr(3, 2, "Press any key to continue...")
        status_dialog.refresh()
        status_dialog.getch()
        return False, f"Failed to fetch themes: {error_msg}"
    
    if not theme_files:
        status_dialog.clear()
        status_dialog.attron(curses.color_pair(2))
        status_dialog.box()
        status_dialog.addstr(0, 2, " No Themes Found ")
        status_dialog.attroff(curses.color_pair(2))
        status_dialog.addstr(1, 2, "No .omp.json files found")
        status_dialog.addstr(2, 2, "in repository root.")
        status_dialog.addstr(3, 2, "Press any key to continue...")
        status_dialog.refresh()
        status_dialog.getch()
        return False, "No themes found in repository"
    
    # Show confirmation dialog
    status_dialog.clear()
    status_dialog.attron(curses.color_pair(2))
    status_dialog.box()
    status_dialog.addstr(0, 2, " Confirm Installation ")
    status_dialog.attroff(curses.color_pair(2))
    status_dialog.addstr(1, 2, f"Found {len(theme_files)} theme(s):")
    
    # Show theme names (up to 2)
    for i, theme_file in enumerate(theme_files[:2]):
        theme_name = theme_file['name'].replace('.omp.json', '')
        status_dialog.addstr(2 + i, 4, theme_name[:40])
    
    if len(theme_files) > 2:
        status_dialog.addstr(4, 4, f"... and {len(theme_files) - 2} more")
    
    status_dialog.addstr(status_dialog.getmaxyx()[0] - 2, 2, "Install? (Y/N)")
    status_dialog.refresh()
    
    # Wait for confirmation
    while True:
        key = status_dialog.getch()
        if key in [ord('y'), ord('Y')]:
            break
        elif key in [ord('n'), ord('N')]:
            return False, "Installation cancelled"
    
    # Perform installation with progress
    success_count, total_count, errors = show_installation_progress(
        stdscr, theme_files, repo_url, themes_dir
    )
    
    if success_count > 0:
        # Add repository to configuration for future remote theme fetching
        try:
            from .config import add_custom_repository
        except ImportError:
            # Fallback for when running directly
            from config import add_custom_repository
        
        add_custom_repository(repo_url)
        return True, f"Installed {success_count}/{total_count} custom themes"
    else:
        return False, f"Failed to install themes: {errors[0] if errors else 'Unknown error'}"