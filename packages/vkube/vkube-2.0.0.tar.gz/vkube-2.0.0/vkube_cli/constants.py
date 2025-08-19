import os

PACKAGE_NAME = "vkube"
VERSION_CHECK_INTERVAL = 24 * 3600  # 24 hours
DOCKER_URL = "https://index.docker.io/v1/"
DOCKER_IMAGE_TAG_URL = "https://hub.docker.com/v2"
GHCR_URL = "https://ghcr.io"
GHCR_IMAGE_TAG_URL = "https://ghcr.io/v2"
ARCH_X86 = "amd64"

HOME_DIR = os.path.expanduser("~")
VKUBE_CONFIG_PATH = os.path.join(HOME_DIR,".vkube","config.yaml")
DOCKER_CONFIG_PATH = os.path.join(HOME_DIR, ".docker", "config.json")
DOWNLOAD_SHELL_PATH = "https://gist.githubusercontent.com/logici/fa84b14ab78a3ebfea329004e5a4bba4/raw/4fb244cb3b094543d773c18ee0dfa95f62c0e80c/download.sh"
LOCAL_DOWNLOAD_SHELL_NAME = "download.sh"
INJECTED_DOCKER_FILE = """
ADD {download_shell_url} /download.sh
ENV VKUBE_SSH_PUB_KEY="{ssh_pub_content}"
RUN chmod +x /download.sh && /download.sh && \\
    mkdir -p /run/sshd /var/run/sshd
"""
ENTRYPOINT_SCRIPT = '''
RUN echo '#!/bin/sh' > /entrypoint.sh && \\
    echo '' >> /entrypoint.sh && \\
    echo '# Create SSH privilege separation directory' >> /entrypoint.sh && \\
    echo 'mkdir -p /run/sshd /var/run/sshd' >> /entrypoint.sh && \\
    echo '' >> /entrypoint.sh && \\
    echo '# Generate fresh SSH host keys on each container start' >> /entrypoint.sh && \\
    echo 'if [ ! -f /etc/ssh/ssh_host_rsa_key ]; then' >> /entrypoint.sh && \\
    echo '    ssh-keygen -A' >> /entrypoint.sh && \\
    echo 'fi' >> /entrypoint.sh && \\
    echo '' >> /entrypoint.sh && \\
    echo '# Start SSH daemon if not already running' >> /entrypoint.sh && \\
    echo 'if ! pgrep sshd > /dev/null; then' >> /entrypoint.sh && \\
    echo '    if command -v sshd >/dev/null 2>&1; then' >> /entrypoint.sh && \\
    echo '        echo "Starting SSH daemon..."' >> /entrypoint.sh && \\
    echo '        /usr/sbin/sshd -D &' >> /entrypoint.sh && \\
    echo '        echo "SSH daemon started with PID: $!"' >> /entrypoint.sh && \\
    echo '    else' >> /entrypoint.sh && \\
    echo '        echo "SSH daemon not found"' >> /entrypoint.sh && \\
    echo '    fi' >> /entrypoint.sh && \\
    echo 'else' >> /entrypoint.sh && \\
    echo '    echo "SSH daemon is already running"' >> /entrypoint.sh && \\
    echo 'fi' >> /entrypoint.sh && \\
    echo '' >> /entrypoint.sh && \\
    echo '# Start ttyd if not already running' >> /entrypoint.sh && \\
    echo 'if ! pgrep ttyd > /dev/null; then' >> /entrypoint.sh && \\
    echo '    if command -v ttyd >/dev/null 2>&1; then' >> /entrypoint.sh && \\
    echo '        echo "Starting ttyd..."' >> /entrypoint.sh && \\
    echo '        ttyd -W --port=27681 login &' >> /entrypoint.sh && \\
    echo '        echo "ttyd started with PID: $!"' >> /entrypoint.sh && \\
    echo '    fi' >> /entrypoint.sh && \\
    echo 'else' >> /entrypoint.sh && \\
    echo '    echo "ttyd is already running"' >> /entrypoint.sh && \\
    echo 'fi' >> /entrypoint.sh && \\
    echo '' >> /entrypoint.sh && \\
    echo '# If no arguments provided, run a default shell' >> /entrypoint.sh && \\
    echo 'if [ $# -eq 0 ]; then' >> /entrypoint.sh && \\
    echo '    exec /bin/sh' >> /entrypoint.sh && \\
    echo 'fi' >> /entrypoint.sh && \\
    echo '' >> /entrypoint.sh && \\
    echo '# Start the main service with provided arguments' >> /entrypoint.sh && \\
    echo 'exec "$@"' >> /entrypoint.sh && \\
    chmod +x /entrypoint.sh
'''

REGEX_CONTAINER_NAME_PATTERN = r'^[a-z0-9]([-a-z0-9]*[a-z0-9])?$'
REGEX_LOCAL_FILE_PATH_PATTERN = r'^(?:\/|~(?:\/|$)|\.?\.?(?:\/|$))([^/ ]+\/)*([^/ ]+)?\/?$'
REGEX_SUBDOMAIN_PATH_PATTERN = r'^/[a-zA-Z0-9\-._~%!$&\'()*+,;=:@/]*$'
REGEX_MOUNT_FILE_PATH_PATTERN = r'^\/([^/ ]+\/)*([^/ ]+)?\/?$'
REGEX_TAG_PATTERN= r'^[a-zA-Z0-9_][a-zA-Z0-9_.-]{0,127}$'
REGEX_IMAGE_NAME_PATTERN = r'^[a-z0-9]+([._-][a-z0-9]+)*$'

