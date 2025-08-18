# Updating Documentation

This project uses [MkDocs](https://www.mkdocs.org/) for documentation generation and hosting.

## Documentation Structure

- Documentation source files are located in the `docs/` directory
- The main configuration is in `mkdocs.yml` at the project root
- Documentation is written in Markdown format

## When to Update Documentation

Documentation should be updated whenever:

- New features are added
- Existing functionality changes
- APIs or interfaces are modified
- Configuration options are added or changed
- Setup/installation instructions need updates
- Examples or usage patterns change

## How to Update Documentation

1. Edit the relevant `.md` files in the `docs/` directory
2. **Update navigation**: If adding new documentation files, update the `nav:` section in `mkdocs.yml` to include the new pages
3. Test your changes locally by running: `mkdocs serve`
4. Preview the documentation at `http://localhost:8000`
5. Once satisfied, commit your changes along with the code changes

## Building and Deploying

- Local development: `mkdocs serve`
- Build static site: `mkdocs build`
- Deploy to GitHub Pages: `mkdocs gh-deploy` (if configured)

## MkDocs Configuration

The `mkdocs.yml` file contains:

- Site metadata (name, description, etc.)
- **Navigation structure** (`nav:` section) - must be updated when adding new documentation files
- Theme configuration
- Plugin settings
- Markdown extensions

Please ensure any documentation updates maintain consistency with the existing style and structure. When adding new documentation files, always remember to update the navigation in `mkdocs.yml`.