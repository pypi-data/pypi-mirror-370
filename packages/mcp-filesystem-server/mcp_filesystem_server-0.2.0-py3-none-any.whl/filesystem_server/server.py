import asyncio
import json
import os
import glob
import shutil
import chardet
import re
import zipfile
import tarfile
import stat
import subprocess
import platform
from pathlib import Path
from typing import Any, Dict, List, Optional, Set
from datetime import datetime
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from mcp.server import Server, NotificationOptions
from mcp.server.models import InitializationOptions
import mcp.server.stdio
import mcp.types as types

# Initialize the MCP server
server = Server("filesystem-tools")

# Global file watcher
file_watchers: Dict[str, Observer] = {}
watch_callbacks: Dict[str, List[Dict[str, Any]]] = {}

class MCPFileSystemEventHandler(FileSystemEventHandler):
    def __init__(self, watch_id: str):
        self.watch_id = watch_id
        
    def on_any_event(self, event):
        if self.watch_id in watch_callbacks:
            for callback in watch_callbacks[self.watch_id]:
                callback['events'].append({
                    'type': event.event_type,
                    'path': event.src_path,
                    'is_directory': event.is_directory,
                    'timestamp': datetime.now().isoformat()
                })

@server.list_tools()
async def handle_list_tools() -> List[types.Tool]:
    """List all available tools."""
    return [
        # Original tools
        types.Tool(
            name="search_files",
            description="Search for files using glob patterns",
            inputSchema={
                "type": "object",
                "properties": {
                    "pattern": {
                        "type": "string",
                        "description": "Glob pattern to search (e.g., '**/*.py')"
                    },
                    "directory": {
                        "type": "string",
                        "description": "Base directory to search in (default: current directory)"
                    }
                },
                "required": ["pattern"]
            }
        ),
        types.Tool(
            name="analyze_file",
            description="Analyze file properties (size, lines, encoding)",
            inputSchema={
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Path to the file to analyze"
                    }
                },
                "required": ["path"]
            }
        ),
        types.Tool(
            name="directory_tree",
            description="Generate a directory tree structure",
            inputSchema={
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Path to the directory"
                    },
                    "max_depth": {
                        "type": "integer",
                        "description": "Maximum depth to traverse (default: 3)"
                    }
                },
                "required": ["path"]
            }
        ),
        types.Tool(
            name="batch_rename",
            description="Rename multiple files using patterns",
            inputSchema={
                "type": "object",
                "properties": {
                    "pattern": {
                        "type": "string",
                        "description": "Glob pattern to match files"
                    },
                    "find": {
                        "type": "string",
                        "description": "String to find in filenames"
                    },
                    "replace": {
                        "type": "string",
                        "description": "String to replace with"
                    },
                    "dry_run": {
                        "type": "boolean",
                        "description": "If true, only show what would be renamed"
                    }
                },
                "required": ["pattern", "find", "replace"]
            }
        ),
        # New tools
        types.Tool(
            name="search_content",
            description="Search file contents using regex patterns",
            inputSchema={
                "type": "object",
                "properties": {
                    "pattern": {
                        "type": "string",
                        "description": "Regex pattern to search for"
                    },
                    "file_pattern": {
                        "type": "string",
                        "description": "Glob pattern for files to search (e.g., '*.py')"
                    },
                    "directory": {
                        "type": "string",
                        "description": "Directory to search in (default: current)"
                    },
                    "case_sensitive": {
                        "type": "boolean",
                        "description": "Case sensitive search (default: true)"
                    },
                    "max_results": {
                        "type": "integer",
                        "description": "Maximum number of results (default: 100)"
                    }
                },
                "required": ["pattern", "file_pattern"]
            }
        ),
        types.Tool(
            name="compress_files",
            description="Compress files or directories into zip/tar archives",
            inputSchema={
                "type": "object",
                "properties": {
                    "source": {
                        "type": "string",
                        "description": "Path to file or directory to compress"
                    },
                    "output": {
                        "type": "string",
                        "description": "Output archive path"
                    },
                    "format": {
                        "type": "string",
                        "enum": ["zip", "tar", "tar.gz"],
                        "description": "Archive format (default: zip)"
                    }
                },
                "required": ["source", "output"]
            }
        ),
        types.Tool(
            name="decompress_files",
            description="Extract files from zip/tar archives",
            inputSchema={
                "type": "object",
                "properties": {
                    "archive": {
                        "type": "string",
                        "description": "Path to archive file"
                    },
                    "output_dir": {
                        "type": "string",
                        "description": "Directory to extract to (default: current)"
                    }
                },
                "required": ["archive"]
            }
        ),
        types.Tool(
            name="manage_permissions",
            description="View or modify file permissions (Unix-like systems)",
            inputSchema={
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Path to file or directory"
                    },
                    "action": {
                        "type": "string",
                        "enum": ["view", "modify"],
                        "description": "Action to perform"
                    },
                    "permissions": {
                        "type": "string",
                        "description": "New permissions in octal (e.g., '755') - required for modify"
                    }
                },
                "required": ["path", "action"]
            }
        ),
        types.Tool(
            name="git_status",
            description="Get git repository status and information",
            inputSchema={
                "type": "object",
                "properties": {
                    "repository": {
                        "type": "string",
                        "description": "Path to git repository (default: current)"
                    },
                    "detailed": {
                        "type": "boolean",
                        "description": "Include detailed file changes (default: false)"
                    }
                },
                "required": []
            }
        ),
        types.Tool(
            name="git_log",
            description="Get git commit history",
            inputSchema={
                "type": "object",
                "properties": {
                    "repository": {
                        "type": "string",
                        "description": "Path to git repository (default: current)"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Number of commits to show (default: 10)"
                    },
                    "oneline": {
                        "type": "boolean",
                        "description": "Show compact one-line format (default: false)"
                    }
                },
                "required": []
            }
        ),
        types.Tool(
            name="watch_files",
            description="Monitor files/directories for changes",
            inputSchema={
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Path to watch"
                    },
                    "action": {
                        "type": "string",
                        "enum": ["start", "stop", "status"],
                        "description": "Watch action"
                    },
                    "watch_id": {
                        "type": "string",
                        "description": "Unique identifier for this watch"
                    },
                    "recursive": {
                        "type": "boolean",
                        "description": "Watch subdirectories (default: true)"
                    }
                },
                "required": ["action", "watch_id"]
            }
        )
    ]

@server.call_tool()
async def handle_call_tool(
    name: str,
    arguments: Optional[Dict[str, Any]]
) -> List[types.TextContent]:
    """Handle tool execution."""
    
    # Original tool implementations (keeping them as is)
    if name == "search_files":
        pattern = arguments.get("pattern")
        directory = arguments.get("directory", ".")
        
        try:
            base_path = Path(directory).resolve()
            matches = list(base_path.glob(pattern))
            
            results = []
            for match in matches[:100]:
                relative_path = match.relative_to(base_path)
                results.append({
                    "path": str(relative_path),
                    "absolute_path": str(match),
                    "size": match.stat().st_size if match.is_file() else None,
                    "modified": datetime.fromtimestamp(match.stat().st_mtime).isoformat()
                })
            
            return [types.TextContent(
                type="text",
                text=json.dumps({
                    "found": len(matches),
                    "showing": len(results),
                    "files": results
                }, indent=2)
            )]
        except Exception as e:
            return [types.TextContent(type="text", text=f"Error: {str(e)}")]
    
    elif name == "analyze_file":
        path = arguments.get("path")
        
        try:
            file_path = Path(path).resolve()
            if not file_path.exists():
                return [types.TextContent(type="text", text="Error: File not found")]
            
            stats = file_path.stat()
            
            # Detect encoding
            with open(file_path, 'rb') as f:
                raw_data = f.read(10000)
                encoding_info = chardet.detect(raw_data)
            
            # Count lines if it's a text file
            line_count = None
            if encoding_info['confidence'] > 0.7:
                try:
                    with open(file_path, 'r', encoding=encoding_info['encoding']) as f:
                        line_count = sum(1 for _ in f)
                except:
                    pass
            
            analysis = {
                "path": str(file_path),
                "size_bytes": stats.st_size,
                "size_human": f"{stats.st_size / 1024:.2f} KB" if stats.st_size < 1024*1024 else f"{stats.st_size / (1024*1024):.2f} MB",
                "created": datetime.fromtimestamp(stats.st_ctime).isoformat(),
                "modified": datetime.fromtimestamp(stats.st_mtime).isoformat(),
                "encoding": encoding_info['encoding'],
                "encoding_confidence": encoding_info['confidence'],
                "line_count": line_count,
                "extension": file_path.suffix
            }
            
            return [types.TextContent(
                type="text",
                text=json.dumps(analysis, indent=2)
            )]
        except Exception as e:
            return [types.TextContent(type="text", text=f"Error: {str(e)}")]
    
    elif name == "directory_tree":
        path = arguments.get("path")
        max_depth = arguments.get("max_depth", 3)
        
        try:
            def generate_tree(directory: Path, prefix: str = "", depth: int = 0) -> List[str]:
                if depth > max_depth:
                    return []
                
                lines = []
                items = sorted(directory.iterdir(), key=lambda x: (x.is_file(), x.name))
                
                for i, item in enumerate(items):
                    is_last = i == len(items) - 1
                    current_prefix = "└── " if is_last else "├── "
                    lines.append(f"{prefix}{current_prefix}{item.name}")
                    
                    if item.is_dir() and depth < max_depth:
                        extension = "    " if is_last else "│   "
                        lines.extend(generate_tree(item, prefix + extension, depth + 1))
                
                return lines
            
            dir_path = Path(path).resolve()
            if not dir_path.is_dir():
                return [types.TextContent(type="text", text="Error: Not a directory")]
            
            tree_lines = [str(dir_path)] + generate_tree(dir_path)
            
            return [types.TextContent(
                type="text",
                text="\n".join(tree_lines)
            )]
        except Exception as e:
            return [types.TextContent(type="text", text=f"Error: {str(e)}")]
    
    elif name == "batch_rename":
        pattern = arguments.get("pattern")
        find = arguments.get("find")
        replace = arguments.get("replace")
        dry_run = arguments.get("dry_run", True)
        
        try:
            matches = glob.glob(pattern)
            operations = []
            
            for old_path in matches:
                old_name = os.path.basename(old_path)
                new_name = old_name.replace(find, replace)
                
                if old_name != new_name:
                    new_path = os.path.join(os.path.dirname(old_path), new_name)
                    operations.append({
                        "old": old_path,
                        "new": new_path,
                        "old_name": old_name,
                        "new_name": new_name
                    })
                    
                    if not dry_run:
                        os.rename(old_path, new_path)
            
            result = {
                "mode": "dry_run" if dry_run else "executed",
                "total_files": len(matches),
                "renamed": len(operations),
                "operations": operations
            }
            
            return [types.TextContent(
                type="text",
                text=json.dumps(result, indent=2)
            )]
        except Exception as e:
            return [types.TextContent(type="text", text=f"Error: {str(e)}")]
    
    # New tool implementations
    elif name == "search_content":
        pattern = arguments.get("pattern")
        file_pattern = arguments.get("file_pattern")
        directory = arguments.get("directory", ".")
        case_sensitive = arguments.get("case_sensitive", True)
        max_results = arguments.get("max_results", 100)
        
        try:
            base_path = Path(directory).resolve()
            regex_flags = 0 if case_sensitive else re.IGNORECASE
            regex = re.compile(pattern, regex_flags)
            
            results = []
            files_searched = 0
            
            for file_path in base_path.glob(file_pattern):
                if file_path.is_file():
                    files_searched += 1
                    try:
                        # Detect encoding
                        with open(file_path, 'rb') as f:
                            raw_data = f.read(10000)
                            encoding_info = chardet.detect(raw_data)
                                                # Read and search file
                        if encoding_info['confidence'] > 0.5:
                            with open(file_path, 'r', encoding=encoding_info['encoding']) as f:
                                for line_num, line in enumerate(f, 1):
                                    matches = regex.finditer(line)
                                    for match in matches:
                                        results.append({
                                            "file": str(file_path.relative_to(base_path)),
                                            "line": line_num,
                                            "column": match.start() + 1,
                                            "match": match.group(),
                                            "context": line.strip()
                                        })
                                        if len(results) >= max_results:
                                            break
                                    if len(results) >= max_results:
                                        break
                    except Exception as e:
                        # Skip files that can't be read
                        pass
                    
                    if len(results) >= max_results:
                        break
            
            return [types.TextContent(
                type="text",
                text=json.dumps({
                    "pattern": pattern,
                    "files_searched": files_searched,
                    "matches_found": len(results),
                    "results": results
                }, indent=2)
            )]
        except Exception as e:
            return [types.TextContent(type="text", text=f"Error: {str(e)}")]
    
    elif name == "compress_files":
        source = arguments.get("source")
        output = arguments.get("output")
        format = arguments.get("format", "zip")
        
        try:
            source_path = Path(source).resolve()
            output_path = Path(output).resolve()
            
            if not source_path.exists():
                return [types.TextContent(type="text", text="Error: Source path not found")]
            
            if format == "zip":
                with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                    if source_path.is_file():
                        zipf.write(source_path, source_path.name)
                    else:
                        for file_path in source_path.rglob('*'):
                            if file_path.is_file():
                                arcname = file_path.relative_to(source_path.parent)
                                zipf.write(file_path, arcname)
            
            elif format in ["tar", "tar.gz"]:
                mode = 'w:gz' if format == "tar.gz" else 'w'
                with tarfile.open(output_path, mode) as tar:
                    tar.add(source_path, arcname=source_path.name)
            
            # Get compressed file info
            compressed_size = output_path.stat().st_size
            
            return [types.TextContent(
                type="text",
                text=json.dumps({
                    "source": str(source_path),
                    "output": str(output_path),
                    "format": format,
                    "compressed_size": compressed_size,
                    "compressed_size_human": f"{compressed_size / 1024:.2f} KB" if compressed_size < 1024*1024 else f"{compressed_size / (1024*1024):.2f} MB"
                }, indent=2)
            )]
        except Exception as e:
            return [types.TextContent(type="text", text=f"Error: {str(e)}")]
    
    elif name == "decompress_files":
        archive = arguments.get("archive")
        output_dir = arguments.get("output_dir", ".")
        
        try:
            archive_path = Path(archive).resolve()
            output_path = Path(output_dir).resolve()
            
            if not archive_path.exists():
                return [types.TextContent(type="text", text="Error: Archive file not found")]
            
            output_path.mkdir(parents=True, exist_ok=True)
            extracted_files = []
            
            if archive_path.suffix == '.zip':
                with zipfile.ZipFile(archive_path, 'r') as zipf:
                    extracted_files = zipf.namelist()
                    zipf.extractall(output_path)
            
            elif archive_path.suffix in ['.tar', '.gz', '.tgz']:
                with tarfile.open(archive_path, 'r:*') as tar:
                    extracted_files = tar.getnames()
                    tar.extractall(output_path)
            
            else:
                return [types.TextContent(type="text", text="Error: Unsupported archive format")]
            
            return [types.TextContent(
                type="text",
                text=json.dumps({
                    "archive": str(archive_path),
                    "output_directory": str(output_path),
                    "extracted_files": len(extracted_files),
                    "files": extracted_files[:50]  # Show first 50 files
                }, indent=2)
            )]
        except Exception as e:
            return [types.TextContent(type="text", text=f"Error: {str(e)}")]
    
    elif name == "manage_permissions":
        path = arguments.get("path")
        action = arguments.get("action")
        permissions = arguments.get("permissions")
        
        try:
            file_path = Path(path).resolve()
            if not file_path.exists():
                return [types.TextContent(type="text", text="Error: Path not found")]
            
            if action == "view":
                stats = file_path.stat()
                mode = stats.st_mode
                
                # Get permission string
                perms = stat.filemode(mode)
                
                # Get octal representation
                octal = oct(mode)[-3:]
                
                # Get owner info (Unix-like systems)
                try:
                    import pwd
                    import grp
                    owner = pwd.getpwuid(stats.st_uid).pw_name
                    group = grp.getgrgid(stats.st_gid).gr_name
                except:
                    owner = stats.st_uid
                    group = stats.st_gid
                
                return [types.TextContent(
                    type="text",
                    text=json.dumps({
                        "path": str(file_path),
                        "permissions": perms,
                        "octal": octal,
                        "owner": owner,
                        "group": group,
                        "is_readable": os.access(file_path, os.R_OK),
                        "is_writable": os.access(file_path, os.W_OK),
                        "is_executable": os.access(file_path, os.X_OK)
                    }, indent=2)
                )]
            
            elif action == "modify":
                if not permissions:
                    return [types.TextContent(type="text", text="Error: Permissions required for modify action")]
                
                # Convert octal string to integer
                mode = int(permissions, 8)
                os.chmod(file_path, mode)
                
                # Get new permissions
                new_stats = file_path.stat()
                new_perms = stat.filemode(new_stats.st_mode)
                
                return [types.TextContent(
                    type="text",
                    text=json.dumps({
                        "path": str(file_path),
                        "old_permissions": stat.filemode(stats.st_mode),
                        "new_permissions": new_perms,
                        "octal": permissions
                    }, indent=2)
                )]
            
        except Exception as e:
            return [types.TextContent(type="text", text=f"Error: {str(e)}")]
    
    elif name == "git_status":
        repository = arguments.get("repository", ".")
        detailed = arguments.get("detailed", False)
        
        try:
            repo_path = Path(repository).resolve()
            
            # Check if it's a git repository
            if not (repo_path / ".git").exists():
                return [types.TextContent(type="text", text="Error: Not a git repository")]
            
            # Get branch
            result = subprocess.run(
                ["git", "branch", "--show-current"],
                cwd=repo_path,
                capture_output=True,
                text=True
            )
            current_branch = result.stdout.strip()
            
            # Get status
            result = subprocess.run(
                ["git", "status", "--porcelain"],
                cwd=repo_path,
                capture_output=True,
                text=True
            )
            
            status_lines = result.stdout.strip().split('\n') if result.stdout.strip() else []
            
            # Parse status
            staged = []
            modified = []
            untracked = []
            
            for line in status_lines:
                if line:
                    status = line[:2]
                    filename = line[3:]
                    
                    if status[0] in ['A', 'M', 'D', 'R']:
                        staged.append({"status": status[0], "file": filename})
                    if status[1] in ['M', 'D']:
                        modified.append({"status": status[1], "file": filename})
                    if status == '??':
                        untracked.append(filename)
            
            # Get last commit
            result = subprocess.run(
                ["git", "log", "-1", "--oneline"],
                cwd=repo_path,
                capture_output=True,
                text=True
            )
            last_commit = result.stdout.strip()
            
            response = {
                "repository": str(repo_path),
                "branch": current_branch,
                "last_commit": last_commit,
                "staged_files": len(staged),
                "modified_files": len(modified),
                "untracked_files": len(untracked),
                "clean": len(status_lines) == 0
            }
            
            if detailed:
                response["staged"] = staged
                response["modified"] = modified
                response["untracked"] = untracked
            
            return [types.TextContent(
                type="text",
                text=json.dumps(response, indent=2)
            )]
        except Exception as e:
            return [types.TextContent(type="text", text=f"Error: {str(e)}")]
    
    elif name == "git_log":
        repository = arguments.get("repository", ".")
        limit = arguments.get("limit", 10)
        oneline = arguments.get("oneline", False)
        
        try:
            repo_path = Path(repository).resolve()
            
            # Check if it's a git repository
            if not (repo_path / ".git").exists():
                return [types.TextContent(type="text", text="Error: Not a git repository")]
            
            if oneline:
                result = subprocess.run(
                    ["git", "log", f"-{limit}", "--oneline"],
                    cwd=repo_path,
                    capture_output=True,
                    text=True
                )
                
                commits = []
                for line in result.stdout.strip().split('\n'):
                    if line:
                        parts = line.split(' ', 1)
                        commits.append({
                            "hash": parts[0],
                            "message": parts[1] if len(parts) > 1 else ""
                        })
            else:
                result = subprocess.run(
                    ["git", "log", f"-{limit}", "--pretty=format:%H|%an|%ae|%ad|%s", "--date=iso"],
                    cwd=repo_path,
                    capture_output=True,
                    text=True
                )
                
                commits = []
                for line in result.stdout.strip().split('\n'):
                    if line:
                        parts = line.split('|')
                        commits.append({
                            "hash": parts[0],
                            "author": parts[1],
                            "email": parts[2],
                            "date": parts[3],
                            "message": parts[4]
                        })
            
            return [types.TextContent(
                type="text",
                text=json.dumps({
                    "repository": str(repo_path),
                    "commits": commits,
                    "count": len(commits)
                }, indent=2)
            )]
        except Exception as e:
            return [types.TextContent(type="text", text=f"Error: {str(e)}")]
    
    elif name == "watch_files":
        watch_id = arguments.get("watch_id")
        action = arguments.get("action")
        path = arguments.get("path")
        recursive = arguments.get("recursive", True)
        
        try:
            if action == "start":
                if not path:
                    return [types.TextContent(type="text", text="Error: Path required to start watching")]
                
                watch_path = Path(path).resolve()
                if not watch_path.exists():
                    return [types.TextContent(type="text", text="Error: Path not found")]
                
                # Stop existing watcher if any
                if watch_id in file_watchers:
                    file_watchers[watch_id].stop()
                    file_watchers[watch_id].join()
                
                # Create new watcher
                event_handler = MCPFileSystemEventHandler(watch_id)
                observer = Observer()
                observer.schedule(event_handler, str(watch_path), recursive=recursive)
                observer.start()
                
                file_watchers[watch_id] = observer
                watch_callbacks[watch_id] = [{"events": [], "path": str(watch_path)}]
                
                return [types.TextContent(
                    type="text",
                    text=json.dumps({
                        "status": "started",
                        "watch_id": watch_id,
                        "path": str(watch_path),
                        "recursive": recursive
                    }, indent=2)
                )]
            
            elif action == "stop":
                if watch_id in file_watchers:
                    file_watchers[watch_id].stop()
                    file_watchers[watch_id].join()
                    del file_watchers[watch_id]
                    
                    events = []
                    if watch_id in watch_callbacks:
                        events = watch_callbacks[watch_id][0]["events"]
                        del watch_callbacks[watch_id]
                    
                    return [types.TextContent(
                        type="text",
                        text=json.dumps({
                            "status": "stopped",
                            "watch_id": watch_id,
                            "total_events": len(events)
                        }, indent=2)
                    )]
                else:
                    return [types.TextContent(type="text", text="Error: Watch ID not found")]
            
            elif action == "status":
                if watch_id in file_watchers:
                    events = watch_callbacks[watch_id][0]["events"] if watch_id in watch_callbacks else []
                    recent_events = events[-10:]  # Last 10 events
                    
                    return [types.TextContent(
                        type="text",
                        text=json.dumps({
                            "status": "active",
                            "watch_id": watch_id,
                            "path": watch_callbacks[watch_id][0]["path"],
                            "total_events": len(events),
                            "recent_events": recent_events
                        }, indent=2)
                    )]
                else:
                    return [types.TextContent(type="text", text="Error: Watch ID not found")]
            
        except Exception as e:
            return [types.TextContent(type="text", text=f"Error: {str(e)}")]
    
    return [types.TextContent(type="text", text=f"Unknown tool: {name}")]

async def main():
    """Run the MCP server."""
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="filesystem-tools",
                server_version="0.2.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                )
            )
        )

if __name__ == "__main__":
    asyncio.run(main())