#!/bin/bash

echo "Running postinstall script..."

# Install Node.js dependencies and build assets
npm install
npm run build

