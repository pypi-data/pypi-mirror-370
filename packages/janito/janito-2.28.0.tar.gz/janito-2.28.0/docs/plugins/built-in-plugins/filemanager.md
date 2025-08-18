# File Manager Plugin

## Overview

The File Manager plugin provides essential file and directory operations for managing project files. This plugin enables basic file system operations that are crucial for code editing and project management.

## Resources Provided

### Tools

| Tool Name | Function | Description |
|-----------|----------|-------------|
| `create_file` | Create new files with content | Creates a new file at the specified path with optional content and overwrite capability |
| `read_files` | Read multiple files at once | Reads the contents of multiple files and returns them as a concatenated string |
| `view_file` | Read specific portions of files | Reads specific lines or the entire content of a file with optional line range |
| `replace_text_in_file` | Find and replace text in files | Searches for exact text in a file and replaces it with new text (single or all occurrences) |
| `validate_file_syntax` | Check file syntax | Validates the syntax of various file types (Python, Markdown, JSON, etc.) |
| `create_directory` | Create new directories | Creates a new directory at the specified path |
| `remove_directory` | Remove directories | Deletes directories, with optional recursive removal of non-empty directories |
| `remove_file` | Delete files | Removes a file at the specified path |
| `copy_file` | Copy files or directories | Copies one or more files/directories to a target location |
| `move_file` | Move or rename files/directories | Moves or renames files and directories |
| `find_files` | Search for files by pattern | Finds files matching a pattern in specified directories, respecting .gitignore |

## Usage Examples

### Creating a New File
```json
{
  "tool": "create_file",
  "path": "src/hello.py",
  "content": "print('Hello, World!')"
}
```

### Reading Multiple Files
```json
{
  "tool": "read_files",
  "paths": ["src/main.py", "src/utils.py"]
}
```

### Finding Python Files
```json
{
  "tool": "find_files",
  "paths": ".",
  "pattern": "*.py"
}
```

## Configuration

This plugin does not require any specific configuration and uses the system's default file permissions and access controls.

## Security Considerations

- File operations are subject to the user's file system permissions
- Path validation prevents directory traversal attacks
- Sensitive file operations require explicit user confirmation in interactive mode

## Integration

The File Manager plugin integrates with the core Janito system to provide file operations that can be used in automation scripts, code generation workflows, and project management tasks.