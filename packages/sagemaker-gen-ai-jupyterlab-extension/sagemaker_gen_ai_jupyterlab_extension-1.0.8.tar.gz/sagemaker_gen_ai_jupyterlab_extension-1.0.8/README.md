# SageMakerGenAIJupyterLabExtension

[![Github Actions Status](/workflows/Build/badge.svg)](/actions/workflows/build.yml)

A JupyterLab extension.

This extension is composed of a Python package named `SageMakerGenAIJupyterLabExtension`
for the server extension and a NPM package named `SageMakerGenAIJupyterLabExtension`
for the frontend extension.

## Requirements

- JupyterLab >= 4.0.0

## Install

To install the extension, execute:

```bash
pip install SageMakerGenAIJupyterLabExtension
```

## Uninstall

To remove the extension, execute:

```bash
pip uninstall SageMakerGenAIJupyterLabExtension
```

## Troubleshoot

If you are seeing the frontend extension, but it is not working, check
that the server extension is enabled:

```bash
jupyter server extension list
```

If the server extension is installed and enabled, but you are not seeing
the frontend extension, check the frontend extension is installed:

```bash
jupyter labextension list
```

## Contributing

### Development install

Note: You will need NodeJS to build the extension package.

The `jlpm` command is JupyterLab's pinned version of
[yarn](https://yarnpkg.com/) that is installed with JupyterLab. You may use
`yarn` or `npm` in lieu of `jlpm` below.

```bash
# Clone the repo to your local environment
# Change directory to the SageMakerGenAIJupyterLabExtension directory
# Install package in development mode
pip install -e "."
# Link your development version of the extension with JupyterLab
jupyter labextension develop . --overwrite
# Server extension must be manually installed in develop mode
jupyter server extension enable sagemaker_gen_ai_jupyterlab_extension
```

You can watch the source directory and run JupyterLab at the same time in different terminals to watch for changes in the extension's source and automatically rebuild the extension.

```bash
# Watch the source directory in one terminal, automatically rebuilding when needed
jlpm watch
# Run JupyterLab in another terminal
jupyter lab
```

With the watch command running, every saved change will immediately be built locally and available in your running JupyterLab. Refresh JupyterLab to load the change in your browser (you may need to wait several seconds for the extension to be rebuilt).

By default, the `jlpm build` command generates the source maps for this extension to make it easier to debug using the browser dev tools. To also generate source maps for the JupyterLab core extensions, you can run the following command:

```bash
jupyter lab build --minimize=False
```

### Development uninstall

```bash
# Server extension must be manually disabled in develop mode
jupyter server extension disable SageMakerGenAIJupyterLabExtension
pip uninstall SageMakerGenAIJupyterLabExtension
```

In development mode, you will also need to remove the symlink created by `jupyter labextension develop`
command. To find its location, you can run `jupyter labextension list` to figure out where the `labextensions`
folder is located. Then you can remove the symlink named `SageMakerGenAIJupyterLabExtension` within that folder.

### Packaging the extension

See [RELEASE](RELEASE.md)

---

## Development Workflow

This extension supports two development environments:

1. **Local Development** - For rapid iteration and testing
2. **SageMaker Unified Studio** - For final verification before commits

### Prerequisites

- Node.js (check version with `which node`)
- Python build tools (`pip install build`)
- Access to SMUS team resources for bearer token generation

### Local Development Setup

#### 1. Configure Environment

Update the following values in `__init__.py`:

```
# Retrieve `AWS access portal URL` from `IAM Identity Center`
START_URL = "https://d-xxxxx.awsapps.com/start"

# Run `which node`
NODE_PATH = "/Users/xxxxx/.local/share/mise/installs/node/20.9.0/bin/node"

# Copy the absolute path to `SageMakerGenAIJupyterLabExtension` and prepend `file://`
WORKSPACE_FOLDER = "file:///Users/xxxxx/Desktop/workplace/Flare/src/SageMakerGenAIJupyterLabExtension"

# Please reach out to SMUS team for the `generate_bearer_token` notebook
def extract_bearer_token():
  return "<CUSTOM BEARER TOKEN>"
```

Update the following values in `lsp_server_connection.py`:

```
"developerProfiles": False # Change this to False
```

#### 2. Build and Run

```bash
# Build the extension and start JupyterLab
python -m build && jupyter lab
```

#### 3. Development Tips

- Use the watch mode from the Contributing section for live reloading
- Test changes immediately in your local JupyterLab instance
- Verify functionality before proceeding to SageMaker testing

### SageMaker Unified Studio Testing

#### 1. Build Distribution

```bash
# Generate distribution package
python -m build
```

This creates a `.tar.gz` file in the `dist/` folder.

#### 2. Deploy to SageMaker

```bash
# Upload the generated .tar.gz to your SMUS workspace
# Then run the following commands in the SageMaker terminal:

pip install sagemaker_gen_ai_jupyterlab_extension-<Version>.tar.gz
restart-sagemaker-ui-jupyter-server
```

#### 3. Verify Installation

1. Wait for server restart (terminal will disappear)
2. Refresh your browser page
3. Test the side widget chat functionality

### Development Best Practices

- Always test locally first for faster iteration
- Verify in SageMaker Unified Studio before committing
- Keep bearer tokens secure and never commit them
- Update version numbers appropriately when building distributions
1. Run `python -m build` - will generate a .tar.gz file in the `dist` folder.
2. Upload the .tar.gz in the MD workspace
3. Run `pip install sagemaker_gen_ai_jupyterlab_extension-<VERSION>.tar.gz` in a terminal
4. Run `restart-sagemaker-ui-jupyter-server` in a terminal
5. Wait until the server restarts (Terminal disappears)
6. Refresh your page
7. Start chatting using the side widget

## Instructions for setting up SMUS remote MCP server alpha
1. paste bin/mcp_dev_setup.sh in your space
2. make sure its executable: `chmod +x mcp_dev_setup.sh`
3. Set your desired MCP server URL: `export MCP_URL="https://your-custom-url.com/mcp"`
3. execute the script `./mcp_dev_setup.sh`
4. The server will restart. Refresh the page once the restart is complete.

