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
    ![.env](https://carbon.now.sh/?bg=rgba(255,255,255,1)&code=nano%20~%2F.config%2Fdocker-ctp%2F.env%0A%0A%23%20Docker%20Hub%20username%20used%20for%20authentication%0ADOCKER_USERNAME%3D%22dockerhub-user%22%0A%0A%23%20GitHub%20username%20%28personal%20or%20organization%20account%29%20for%20repository%20access.%20Usually%20an%20emailadress%0AGITHUB_USERNAME%3D%22github-user%22%0A%0A%23%20Docker%20Hub%20repository%20name%20%28in%20the%20format%3A%20username%2Frepository-name%29%0ADOCKERHUB_REPO%3D%22dockerhub-user%2F%24%28basename%20%24%7BPWD%7D%29%22%0A%0A%23%20GitHub%20repository%20name%20%28in%20the%20format%3A%20personal-or-organization%2Frepository-name%29%0AGITHUB_REPO%3D%22github-name%2F%24%28basename%20%24%7BPWD%7D%29%22%0A%0A%23%20Name%20of%20the%20Docker%20image%20to%20be%20built%20or%20pushed%0AIMAGE_NAME%3D%22basename%20%24%7BPWD%7D%22%0A%0A%23%20Directory%20where%20the%20Dockerfile%20is%20located%20%28current%20directory%20in%20this%20case%29%0ADOCKERFILE_DIR%3D%22.%22%0A%0A%23%20Registry%20to%20which%20the%20Docker%20image%20will%20be%20pushed%20%28in%20this%20case%2C%20Docker%20Hub%29%0AREGISTRY%3D%22docker%22&ds=false&dsblur=68px&dsyoff=20px&es=4x&fm=Fira%20Code&fs=15px&highlight=true&l=auto&ln=false&ph=0px&pv=0px&save=false&si=false&sl=4,7,10,13,16,19,22&t=one-light&type=png&wa=true&wc=false&wm=false&wt=nonev)

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