# README.md

# docker-ctp

This script builds, tags, and pushes a Docker image to Docker Hub or GitHub Container Registry, depending on the selected registry.

## Versions
**Current version**: 0.2.7

## Table of Contents
- [Versions](#versions)
- [Badges](#badges)
- [Installation](#installation)
- [Usage](#usage)
- [License](#license)
- [Contributing](#contributing)

## Badges
![Shell Script](https://img.shields.io/badge/language-shell-blue)
![Version](https://img.shields.io/badge/version-0.2.7-brightgreen)
![License](https://img.shields.io/badge/license-MIT-green)

## Installation
To install and use the script, follow these steps:

1. Clone the repository:
    ```bash
    git clone https://git.beecave-homelab.com/lowie/docker-ctp
    cd docker-ctp
    ```
2. Make the script executable:
    ```bash
    chmod +x docker-ctp.sh
    ```
3. Create a configuration file in the user's home directory:
    ```bash
    mkdir -p ~/.config/docker-ctp/
    cp .env.example ~/.config/docker-ctp/.env
    ```
4. Update the `.env` file with your values:
    ```bash
    nano ~/.config/docker-ctp/.env
    ```
    Example `.env` file:
    ```
    # Docker Hub username used for authentication
    DOCKER_USERNAME="example-user"

    # GitHub username (personal or organization account) for repository access
    GITHUB_USERNAME="github-username"

    # Docker Hub repository name (in the format: username/repository-name)
    DOCKERHUB_REPO="dockerhub-username/repository-name"

    # GitHub repository name (in the format: personal-or-organization/repository-name)
    GITHUB_REPO="github-personal-or-organisation-name/repository-name"

    # Name of the Docker image to be built or pushed
    IMAGE_NAME="repository-name"

    # Directory where the Dockerfile is located (current directory in this case)
    DOCKERFILE_DIR="."

    # Registry to which the Docker image will be pushed (docker or github)
    REGISTRY="docker"
    ```

## Usage
To use the script, run it with the following options:
```bash
./docker-ctp.sh [OPTIONS]
```

Options:
- `-u, --username` Docker Hub or GitHub username (default: from `.env`)
- `-r, --repository-name` Docker or GitHub repository name (default: from `.env`)
- `-i, --image-name` Docker image name (default: current directory name or from `.env`)
- `-t, --image-tag` Docker image tag (default: `latest` for Docker, `main` for GitHub)
- `-d, --dockerfile-dir` Path to Dockerfile folder (default: `.`)
- `-g, --registry` Registry to push the image to: "docker" for Docker Hub or "github" for GitHub Container Registry (default: `docker`)
- `--no-cache` Disable Docker cache and force a clean build (default: use cache)
- `-h, --help` Display the help message

Example usage:
```bash
# Push to Docker Hub (default tag: latest):
./docker-ctp.sh -g docker -u your-docker-username -r your-dockerhub-username/repo -i image -d /path/to/dockerfile

# Push to GitHub Container Registry (default tag: main):
./docker-ctp.sh -g github -u your-github-username -r your-org/repo -i image -d /path/to/dockerfile

# Force a clean build with no cache:
./docker-ctp.sh --no-cache -g docker -u your-docker-username -r your-repo -i image -d /path/to/dockerfile
```

## License
This project is licensed under the MIT license. See [LICENSE](LICENSE) for more information.

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.