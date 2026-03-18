# Rift Patch Watcher

Automatically posts League of Legends patch highlights to a Discord channel through discord webhook.

## Status
![status](https://github.com/bbryanchenn/rift-patch-watcher/actions/workflows/patch_v2.yml/badge.svg?style=for-the-badge)

## Features
- Detects new Riot patch notes
- Extracts Patch Highlights image
- Sends image directly to a Discord webhook
- Prevents duplicate posts
- Runs automatically via GitHub Actions

## Deployment
Add a repository secret:

DISCORD_WEBHOOK_URL

Then enable GitHub Actions.

