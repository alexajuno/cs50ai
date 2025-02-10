#!/bin/bash

# Setup git credentials
echo "https://${GITHUB_USERNAME}:${GITHUB_TOKEN}@github.com" > ~/.git-credentials
chmod 600 ~/.git-credentials

# Setup submit50 credentials
mkdir -p ~/.config/submit50
cat > ~/.config/submit50/credentials.json << EOF
{
    "github": {
        "username": "${GITHUB_USERNAME}",
        "password": "${GITHUB_TOKEN}"
    }
}
EOF
chmod 600 ~/.config/submit50/credentials.json

# Configure git
git config --global user.name "${GITHUB_USERNAME}"
git config --global user.email "${GITHUB_EMAIL:-${GITHUB_USERNAME}@users.noreply.github.com}"

echo "Credentials setup complete!" 