#!/usr/bin/env python3
"""
Web Frontend for Telegram Channel Archives
A Flask-based web interface to browse, search, and manage archived messages.
"""

import os
import json
import re
import subprocess
import threading
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Optional
import markdown
from flask import Flask, render_template, request, jsonify, send_from_directory
from werkzeug.utils import secure_filename


class ArchiveManager:
    def __init__(self, archive_dirs: List[str] = None):
        """Initialize the archive manager."""
        if archive_dirs is None:
            archive_dirs = ["archived_channels", "live_archive"]
        self.archive_dirs = [Path(d) for d in archive_dirs if Path(d).exists()]
        
        # Archiving process management
        self.archiving_process = None
        self.archiving_status = {
            "running": False,
            "progress": 0,
            "current_channel": "",
            "total_channels": 0,
            "processed_channels": 0,
            "start_time": None,
            "logs": [],
            "error": None
        }
        
    def get_all_channels(self) -> List[Dict]:
        """Get all available channels from archives."""
        channels = []
        
        for archive_dir in self.archive_dirs:
            for channel_dir in archive_dir.iterdir():
                if channel_dir.is_dir() and channel_dir.name != "media":
                    # Count files and get latest
                    md_files = list(channel_dir.glob("*.md"))
                    if md_files:
                        latest_file = max(md_files, key=lambda x: x.stat().st_mtime)
                        latest_time = datetime.fromtimestamp(latest_file.stat().st_mtime)
                        
                        # Count messages
                        total_messages = 0
                        for md_file in md_files:
                            try:
                                with open(md_file, 'r', encoding='utf-8') as f:
                                    content = f.read()
                                    total_messages += len(re.findall(r'^## Message \d+', content, re.MULTILINE))
                            except:
                                pass
                        
                        # Check for media
                        media_dir = channel_dir / "media"
                        media_count = len(list(media_dir.glob("*"))) if media_dir.exists() else 0
                        
                        channels.append({
                            "name": channel_dir.name,
                            "path": str(channel_dir),
                            "archive_type": archive_dir.name,
                            "file_count": len(md_files),
                            "message_count": total_messages,
                            "media_count": media_count,
                            "latest_update": latest_time.strftime("%Y-%m-%d %H:%M:%S"),
                            "latest_file": latest_file.name
                        })
        
        return sorted(channels, key=lambda x: x["latest_update"], reverse=True)
    
    def get_channel_files(self, channel_name: str) -> List[Dict]:
        """Get all files for a specific channel."""
        files = []
        
        for archive_dir in self.archive_dirs:
            channel_dir = archive_dir / channel_name
            if channel_dir.exists():
                for md_file in channel_dir.glob("*.md"):
                    # Parse file info
                    with open(md_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Count messages
                    message_count = len(re.findall(r'^## Message \d+', content, re.MULTILINE))
                    
                    # Get date range from content
                    date_match = re.search(r'\*\*Date Range:\*\* (\d{4}-\d{2}-\d{2}) to (\d{4}-\d{2}-\d{2})', content)
                    if date_match:
                        date_range = f"{date_match.group(1)} to {date_match.group(2)}"
                    else:
                        # Try to get date from filename or file stats
                        date_range = datetime.fromtimestamp(md_file.stat().st_mtime).strftime("%Y-%m-%d")
                    
                    files.append({
                        "name": md_file.name,
                        "path": str(md_file),
                        "size": md_file.stat().st_size,
                        "message_count": message_count,
                        "date_range": date_range,
                        "modified": datetime.fromtimestamp(md_file.stat().st_mtime).strftime("%Y-%m-%d %H:%M:%S"),
                        "archive_type": archive_dir.name
                    })
        
        return sorted(files, key=lambda x: x["modified"], reverse=True)
    
    def search_messages(self, query: str, channel_name: str = None, limit: int = 50) -> List[Dict]:
        """Search for messages containing the query."""
        results = []
        query_lower = query.lower()
        
        # Determine which channels to search
        channels_to_search = []
        if channel_name:
            for archive_dir in self.archive_dirs:
                channel_dir = archive_dir / channel_name
                if channel_dir.exists():
                    channels_to_search.append((channel_name, channel_dir))
        else:
            # Search all channels
            for archive_dir in self.archive_dirs:
                for channel_dir in archive_dir.iterdir():
                    if channel_dir.is_dir() and channel_dir.name != "media":
                        channels_to_search.append((channel_dir.name, channel_dir))
        
        for channel_name, channel_dir in channels_to_search:
            for md_file in channel_dir.glob("*.md"):
                try:
                    with open(md_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Split into messages
                    messages = re.split(r'^## Message \d+', content, flags=re.MULTILINE)[1:]
                    
                    for i, message in enumerate(messages):
                        if query_lower in message.lower():
                            # Extract message details
                            lines = message.strip().split('\n')
                            
                            # Find message ID
                            msg_id_match = re.search(r'\*\*Message ID:\*\* (\d+)', message)
                            msg_id = msg_id_match.group(1) if msg_id_match else f"msg_{i}"
                            
                            # Find date
                            date_match = re.search(r'\*\*Date:\*\* ([^\n]+)', message)
                            date = date_match.group(1) if date_match else "Unknown"
                            
                            # Find sender
                            sender_match = re.search(r'\*\*Sender:\*\* ([^\n]+)', message)
                            sender = sender_match.group(1) if sender_match else "Unknown"
                            
                            # Extract content (after ### Content)
                            content_match = re.search(r'### Content\n\n(.*?)(?=\n\n\*\*|$)', message, re.DOTALL)
                            content_text = content_match.group(1).strip() if content_match else ""
                            
                            # Highlight query in content
                            highlighted_content = re.sub(
                                f'({re.escape(query)})', 
                                r'<mark>\1</mark>', 
                                content_text, 
                                flags=re.IGNORECASE
                            )
                            
                            # Check for media
                            has_media = "**Media:**" in message
                            media_type = ""
                            if has_media:
                                if "📷 Photo" in message:
                                    media_type = "Photo"
                                elif "📎 Document" in message:
                                    media_type = "Document"
                                elif "🎬 Video" in message:
                                    media_type = "Video"
                            
                            results.append({
                                "channel": channel_name,
                                "message_id": msg_id,
                                "date": date,
                                "sender": sender,
                                "content": highlighted_content[:300] + "..." if len(highlighted_content) > 300 else highlighted_content,
                                "full_content": content_text,
                                "has_media": has_media,
                                "media_type": media_type,
                                "file": md_file.name
                            })
                            
                            if len(results) >= limit:
                                return results
                                
                except Exception as e:
                    print(f"Error searching {md_file}: {e}")
                    continue
        
        return results
    
    def get_message_content(self, channel_name: str, file_name: str) -> str:
        """Get the full content of a markdown file."""
        for archive_dir in self.archive_dirs:
            file_path = archive_dir / channel_name / file_name
            if file_path.exists():
                with open(file_path, 'r', encoding='utf-8') as f:
                    return f.read()
        return ""
    
    def get_stats(self) -> Dict:
        """Get overall statistics."""
        total_channels = 0
        total_files = 0
        total_messages = 0
        total_media = 0
        
        for archive_dir in self.archive_dirs:
            if archive_dir.exists():
                for channel_dir in archive_dir.iterdir():
                    if channel_dir.is_dir() and channel_dir.name != "media":
                        total_channels += 1
                        
                        # Count files
                        md_files = list(channel_dir.glob("*.md"))
                        total_files += len(md_files)
                        
                        # Count messages
                        for md_file in md_files:
                            try:
                                with open(md_file, 'r', encoding='utf-8') as f:
                                    content = f.read()
                                    total_messages += len(re.findall(r'^## Message \d+', content, re.MULTILINE))
                            except:
                                pass
                        
                        # Count media
                        media_dir = channel_dir / "media"
                        if media_dir.exists():
                            total_media += len(list(media_dir.glob("*")))
        
        return {
            "total_channels": total_channels,
            "total_files": total_files,
            "total_messages": total_messages,
            "total_media": total_media
        }
    
    def start_archiving(self, max_file_size_mb: int = 50, skip_large_files: bool = True):
        """Start the archiving process with smart file handling."""
        if self.archiving_status["running"]:
            return {"error": "Archiving is already running"}
        
        try:
            # Reset status
            self.archiving_status = {
                "running": True,
                "progress": 0,
                "current_channel": "Initializing...",
                "total_channels": 0,
                "processed_channels": 0,
                "start_time": datetime.now().isoformat(),
                "logs": ["🚀 Starting archiving process..."],
                "error": None,
                "max_file_size_mb": max_file_size_mb,
                "skip_large_files": skip_large_files
            }
            
            # Start archiving in a separate thread
            thread = threading.Thread(target=self._run_archiving_process, args=(max_file_size_mb, skip_large_files))
            thread.daemon = True
            thread.start()
            
            return {"success": True, "message": "Archiving started successfully"}
            
        except Exception as e:
            self.archiving_status["running"] = False
            self.archiving_status["error"] = str(e)
            return {"error": f"Failed to start archiving: {str(e)}"}
    
    def stop_archiving(self):
        """Stop the archiving process."""
        if not self.archiving_status["running"]:
            return {"error": "No archiving process is running"}
        
        try:
            if self.archiving_process and self.archiving_process.poll() is None:
                self.archiving_process.terminate()
                time.sleep(2)
                if self.archiving_process.poll() is None:
                    self.archiving_process.kill()
            
            self.archiving_status["running"] = False
            self.archiving_status["logs"].append("🛑 Archiving stopped by user")
            
            return {"success": True, "message": "Archiving stopped successfully"}
            
        except Exception as e:
            return {"error": f"Failed to stop archiving: {str(e)}"}
    
    def get_archiving_status(self):
        """Get current archiving status."""
        return self.archiving_status.copy()
    
    def _run_archiving_process(self, max_file_size_mb: int, skip_large_files: bool):
        """Run the archiving process with smart file handling."""
        try:
            # Check if run_archiver.py exists
            archiver_script = Path("run_archiver.py")
            if not archiver_script.exists():
                archiver_script = Path("telegram_archiver.py")
            
            if not archiver_script.exists():
                raise FileNotFoundError("Archiver script not found")
            
            self.archiving_status["logs"].append(f"📁 Using archiver script: {archiver_script}")
            
            # Prepare command with file size limits
            cmd = ["python", str(archiver_script)]
            
            # Add environment variables for file handling
            env = os.environ.copy()
            env["MAX_FILE_SIZE_MB"] = str(max_file_size_mb)
            env["SKIP_LARGE_FILES"] = str(skip_large_files).lower()
            
            self.archiving_status["logs"].append(f"⚙️ Max file size: {max_file_size_mb}MB, Skip large files: {skip_large_files}")
            
            # Start the process
            self.archiving_process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                universal_newlines=True,
                env=env
            )
            
            self.archiving_status["logs"].append("🔄 Archiving process started")
            
            # Monitor the process
            while self.archiving_process.poll() is None and self.archiving_status["running"]:
                try:
                    output = self.archiving_process.stdout.readline()
                    if output:
                        line = output.strip()
                        if line:
                            self.archiving_status["logs"].append(line)
                            
                            # Parse progress from output
                            if "Processing channel:" in line:
                                channel_name = line.split("Processing channel:")[-1].strip()
                                self.archiving_status["current_channel"] = channel_name
                                self.archiving_status["processed_channels"] += 1
                            
                            elif "Total channels:" in line:
                                try:
                                    total = int(line.split("Total channels:")[-1].strip())
                                    self.archiving_status["total_channels"] = total
                                except:
                                    pass
                            
                            elif "Skipping large file" in line:
                                self.archiving_status["logs"].append(f"⏭️ {line}")
                            
                            elif "Downloaded:" in line:
                                self.archiving_status["logs"].append(f"📥 {line}")
                            
                            # Update progress
                            if self.archiving_status["total_channels"] > 0:
                                self.archiving_status["progress"] = min(
                                    100, 
                                    (self.archiving_status["processed_channels"] / self.archiving_status["total_channels"]) * 100
                                )
                            
                            # Keep only last 100 log entries
                            if len(self.archiving_status["logs"]) > 100:
                                self.archiving_status["logs"] = self.archiving_status["logs"][-100:]
                    
                    time.sleep(0.1)
                    
                except Exception as e:
                    self.archiving_status["logs"].append(f"❌ Error reading output: {str(e)}")
                    break
            
            # Process finished
            return_code = self.archiving_process.wait()
            
            if return_code == 0:
                self.archiving_status["logs"].append("✅ Archiving completed successfully!")
                self.archiving_status["progress"] = 100
                self.archiving_status["current_channel"] = "Completed"
            else:
                self.archiving_status["logs"].append(f"❌ Archiving failed with return code: {return_code}")
                self.archiving_status["error"] = f"Process exited with code {return_code}"
            
        except Exception as e:
            self.archiving_status["logs"].append(f"💥 Fatal error: {str(e)}")
            self.archiving_status["error"] = str(e)
        
        finally:
            self.archiving_status["running"] = False
            self.archiving_process = None


# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'telegram_archiver_secret_key'

# Initialize archive manager
archive_manager = ArchiveManager()


@app.route('/')
def index():
    """Main dashboard."""
    channels = archive_manager.get_all_channels()
    stats = archive_manager.get_stats()
    return render_template('index.html', channels=channels, stats=stats)


@app.route('/channel/<channel_name>')
def channel_detail(channel_name):
    """Channel detail page."""
    files = archive_manager.get_channel_files(channel_name)
    return render_template('channel.html', channel_name=channel_name, files=files)


@app.route('/view/<channel_name>/<file_name>')
def view_file(channel_name, file_name):
    """View a specific markdown file."""
    content = archive_manager.get_message_content(channel_name, file_name)
    if content:
        # Fix media links in markdown content
        # Replace relative media paths with Flask media route
        import re
        
        # Pattern to match media links like [filename](media/filename)
        def fix_media_link(match):
            link_text = match.group(1)
            media_path = match.group(2)
            # Extract just the filename from the media path
            filename = media_path.split('/')[-1]
            # Return the corrected link using Flask's media route
            return f'[{link_text}](/media/{filename})'
        
        # Fix markdown links to media files
        fixed_content = re.sub(r'\[([^\]]+)\]\(media/([^)]+)\)', fix_media_link, content)
        
        # Also fix any direct media references
        fixed_content = re.sub(r'media/([^)\s]+)', r'/media/\1', fixed_content)
        
        # Convert markdown to HTML
        html_content = markdown.markdown(fixed_content, extensions=['extra', 'codehilite'])
        
        # Post-process HTML to ensure media links open in new tabs and have proper styling
        html_content = re.sub(
            r'<a href="/media/([^"]+)"([^>]*)>([^<]+)</a>',
            r'<a href="/media/\1" target="_blank" rel="noopener noreferrer" class="media-link">\3</a>',
            html_content
        )
        
        return render_template('view.html', 
                             channel_name=channel_name, 
                             file_name=file_name, 
                             content=html_content,
                             raw_content=content)
    else:
        return "File not found", 404


@app.route('/search')
def search():
    """Search page."""
    query = request.args.get('q', '')
    channel = request.args.get('channel', '')
    
    results = []
    if query:
        results = archive_manager.search_messages(query, channel if channel else None)
    
    channels = archive_manager.get_all_channels()
    return render_template('search.html', 
                         query=query, 
                         channel=channel, 
                         results=results, 
                         channels=channels)


@app.route('/api/search')
def api_search():
    """API endpoint for search."""
    query = request.args.get('q', '')
    channel = request.args.get('channel', '')
    limit = int(request.args.get('limit', 20))
    
    if not query:
        return jsonify({"error": "Query parameter 'q' is required"}), 400
    
    results = archive_manager.search_messages(query, channel if channel else None, limit)
    return jsonify({"results": results, "count": len(results)})


@app.route('/api/stats')
def api_stats():
    """API endpoint for statistics."""
    return jsonify(archive_manager.get_stats())


@app.route('/media/<path:filename>')
def serve_media(filename):
    """Serve media files."""
    # Find the media file in any archive directory
    for archive_dir in archive_manager.archive_dirs:
        for channel_dir in archive_dir.iterdir():
            if channel_dir.is_dir():
                media_dir = channel_dir / "media"
                if media_dir.exists():
                    file_path = media_dir / filename
                    if file_path.exists():
                        return send_from_directory(str(media_dir), filename)
    
    return "Media file not found", 404


@app.route('/api/archiving/start', methods=['POST'])
def api_start_archiving():
    """API endpoint to start archiving."""
    data = request.get_json() or {}
    max_file_size_mb = data.get('max_file_size_mb', 50)
    skip_large_files = data.get('skip_large_files', True)
    
    result = archive_manager.start_archiving(max_file_size_mb, skip_large_files)
    return jsonify(result)


@app.route('/api/archiving/stop', methods=['POST'])
def api_stop_archiving():
    """API endpoint to stop archiving."""
    result = archive_manager.stop_archiving()
    return jsonify(result)


@app.route('/api/archiving/status')
def api_archiving_status():
    """API endpoint to get archiving status."""
    return jsonify(archive_manager.get_archiving_status())


@app.route('/api/channels')
def api_get_channels():
    """API endpoint to get all channels from config."""
    try:
        config = load_config()
        return jsonify({
            "success": True,
            "channels": config.get("channels", []),
            "archive_settings": config.get("archive_settings", {})
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})


@app.route('/api/channels', methods=['POST'])
def api_add_channel():
    """API endpoint to add a new channel."""
    try:
        data = request.get_json()
        identifier = data.get('identifier', '').strip()
        name = data.get('name', '').strip()
        enabled = data.get('enabled', True)
        
        if not identifier or not name:
            return jsonify({"success": False, "error": "Identifier and name are required"})
        
        # Validate Telegram URL format
        if not (identifier.startswith('https://t.me/') or identifier.startswith('@')):
            return jsonify({"success": False, "error": "Invalid Telegram channel format. Use https://t.me/channel or @channel"})
        
        config = load_config()
        channels = config.get("channels", [])
        
        # Check for duplicates
        for channel in channels:
            if channel.get('identifier') == identifier or channel.get('name') == name:
                return jsonify({"success": False, "error": "Channel already exists"})
        
        # Add new channel
        new_channel = {
            "identifier": identifier,
            "name": name,
            "enabled": enabled
        }
        channels.append(new_channel)
        config["channels"] = channels
        
        save_config(config)
        return jsonify({"success": True, "message": "Channel added successfully", "channel": new_channel})
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})


@app.route('/api/channels/<int:channel_index>', methods=['PUT'])
def api_update_channel(channel_index):
    """API endpoint to update a channel."""
    try:
        data = request.get_json()
        config = load_config()
        channels = config.get("channels", [])
        
        if channel_index < 0 or channel_index >= len(channels):
            return jsonify({"success": False, "error": "Channel not found"})
        
        # Update channel
        if 'identifier' in data:
            channels[channel_index]['identifier'] = data['identifier'].strip()
        if 'name' in data:
            channels[channel_index]['name'] = data['name'].strip()
        if 'enabled' in data:
            channels[channel_index]['enabled'] = data['enabled']
        
        config["channels"] = channels
        save_config(config)
        
        return jsonify({"success": True, "message": "Channel updated successfully", "channel": channels[channel_index]})
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})


@app.route('/api/channels/<int:channel_index>', methods=['DELETE'])
def api_delete_channel(channel_index):
    """API endpoint to delete a channel."""
    try:
        config = load_config()
        channels = config.get("channels", [])
        
        if channel_index < 0 or channel_index >= len(channels):
            return jsonify({"success": False, "error": "Channel not found"})
        
        deleted_channel = channels.pop(channel_index)
        config["channels"] = channels
        save_config(config)
        
        return jsonify({"success": True, "message": "Channel deleted successfully", "deleted_channel": deleted_channel})
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})


@app.route('/api/settings', methods=['GET'])
def api_get_settings():
    """API endpoint to get archive settings."""
    try:
        config = load_config()
        return jsonify({
            "success": True,
            "settings": config.get("archive_settings", {})
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})


@app.route('/api/settings', methods=['POST'])
def api_update_settings():
    """API endpoint to update archive settings."""
    try:
        data = request.get_json()
        config = load_config()
        
        # Update archive settings
        archive_settings = config.get("archive_settings", {})
        
        if 'messages_per_channel' in data:
            archive_settings['messages_per_channel'] = int(data['messages_per_channel'])
        if 'days_back' in data:
            archive_settings['days_back'] = int(data['days_back'])
        if 'output_directory' in data:
            archive_settings['output_directory'] = data['output_directory'].strip()
        if 'download_media' in data:
            archive_settings['download_media'] = bool(data['download_media'])
        
        config["archive_settings"] = archive_settings
        save_config(config)
        
        return jsonify({"success": True, "message": "Settings updated successfully", "settings": archive_settings})
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})


def load_config():
    """Load configuration from config.json."""
    config_path = Path("config.json")
    if config_path.exists():
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}


def save_config(config):
    """Save configuration to config.json."""
    config_path = Path("config.json")
    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)


if __name__ == '__main__':
    print("🌐 Starting Telegram Archive Web Frontend...")
    print("📱 Open your browser to: http://localhost:5000")
    print("🔍 Features: Browse channels, search messages, view media")
    app.run(debug=True, host='0.0.0.0', port=5000)