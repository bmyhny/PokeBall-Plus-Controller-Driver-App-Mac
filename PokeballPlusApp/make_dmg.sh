#!/bin/bash
# Create a DMG using create-dmg tool
npm install -g create-dmg 2>/dev/null || true
create-dmg dist/PokeballApp --overwrite
