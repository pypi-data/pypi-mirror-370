#!/bin/bash
cd /home/vlad/tech/job/modus/claude-helper
rm -rf dist/
uv build
echo "Build completed"
ls -la dist/