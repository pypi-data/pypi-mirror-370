# Another Alteryx Plugin CLI

A command-line interface tool for developing Alteryx plugins using the Alteryx Python SDK.

## Overview

The Another Alteryx Plugin CLI provides a streamlined workflow for creating, testing, and deploying Alteryx plugins. It helps developers manage their plugin development workspace, generate necessary files, and package their plugins for distribution.

## Features

- Initialize a new Alteryx SDK workspace
- Create new plugins with various input/output configurations
- Generate UI components for plugins
- Generate test files
- Create and install YXI packages
- Update tool help URLs
- Version management and updates

## Installation

```bash
pip install another-ayx-plugin-cli
```

## Requirements

- Python 3.7 or higher
- Node.js (for UI generation)
- NPM (for UI generation)

## Usage

### Initialize a Workspace

```bash
another-ayx-plugin-cli sdk-workspace-init
```

This will prompt you for:
- Package Name
- Tool Category
- Description
- Author
- Company
- Backend Language

### Create a New Plugin

```bash
another-ayx-plugin-cli create-ayx-plugin
```

This will prompt you for:
- Tool Name
- Tool Type
- Output Data Settings
- Description
- Tool Version
- DCM Namespace
- UI Generation Options

### Generate UI Components

```bash
another-ayx-plugin-cli generate-ui [tool-name]
```

### Generate Tests

```bash
another-ayx-plugin-cli generate-tests [tool-name]
```

### Create YXI Package

```bash
another-ayx-plugin-cli create-yxi
```

### Install to Designer

```bash
another-ayx-plugin-cli designer-install
```

## Tool Types

The CLI supports various tool types:
- Single Input Single Output
- Multiple Inputs
- Multiple Outputs
- Input
- Output
- Optional
- Multiple Input Connections

## Development

### Project Structure

```
.
├── ayx_workspace/     # Workspace configuration and models
├── assets/           # Static assets
├── backend/          # Backend code
├── configuration/    # Tool configuration files
├── ui/              # UI components
└── tests/           # Test files
```

### Dependencies

- typer: CLI framework
- pydantic: Data validation
- packaging: Version handling
- jinja2: Template engine
- requests: HTTP client

## License

Licensed under the ALTERYX SDK AND API LICENSE AGREEMENT. See the LICENSE file for details.

## Support

For support, please visit [Alteryx Developer Help](https://help.alteryx.com/developer-help). 