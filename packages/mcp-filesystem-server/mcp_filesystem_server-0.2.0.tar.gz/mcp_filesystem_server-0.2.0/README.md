# MCP Filesystem Server

A powerful and extensible MCP server for advanced filesystem operations.

This server provides a set of tools to interact with the filesystem, including file searching, analysis, manipulation, and version control with Git.

## Features

*   **File Search:** Search for files using glob patterns (`search_files`).
*   **File Analysis:** Analyze file properties like size, encoding, and line count (`analyze_file`).
*   **Directory Tree:** Generate a visual directory tree structure (`directory_tree`).
*   **Batch Rename:** Rename multiple files at once (`batch_rename`).
*   **Content Search:** Search for text within files using regular expressions (`search_content`).
*   **File Compression:** Compress files and directories into `.zip` or `.tar.gz` archives (`compress_files`).
*   **File Decompression:** Extract files from archives (`decompress_files`).
*   **Permission Management:** View and modify file permissions (`manage_permissions`).
*   **Git Integration:** Get Git repository status and logs (`git_status`, `git_log`).
*   **File Watching:** Monitor files and directories for changes (`watch_files`).

## Installation

You can install the MCP Filesystem Server using pip:

```bash
pip install mcp-filesystem-server
```

*(Note: This will work once the package is published to PyPI)*

Alternatively, you can install it directly from the GitHub repository:

```bash
pip install git+https://github.com/Vamsiindugu/mcp-filesystem-server.git
```

## Usage

To run the server, execute the following command in your terminal:

```bash
mcp-filesystem-server
```

This will start the MCP server and it will be ready to receive requests from an MCP client.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please feel free to open an issue or submit a pull request.
