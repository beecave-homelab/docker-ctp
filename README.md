# docker-ctp

This script builds, tags, and pushes a Docker image to the GitHub Container Registry.

## Versions
**Current version**: 0.1.0

## Table of Contents
- [Versions](#versions)
- [Badges](#badges)
- [Installation](#installation)
- [Usage](#usage)
- [License](#license)
- [Contributing](#contributing)

## Badges
![Shell Script](https://img.shields.io/badge/language-shell-blue)
![Version](https://img.shields.io/badge/version-0.1.0-brightgreen)
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

## Usage
To use the script, run it with the following options:
```bash
./docker-ctp.sh [OPTIONS]
```
Options:
- `-u, --github-username` GitHub username (default: `admin@example.com`)
- `-r, --repository-name` Repository name (default: `example_org/example_repo`)
- `-i, --image-name` Docker image name (default: current directory name)
- `-t, --image-tag` Docker image tag (default: `example_tag`)
- `-d, --dockerfile-folder` Path to Dockerfile folder (default: `.`)
- `-h, --help` Display the help message

Example:
```bash
./docker-ctp.sh -u user -r repo/image -i image -t tag -d /path/to/dockerfile
```

## License
This project is licensed under the MIT license. See [LICENSE](LICENSE) for more information.

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.