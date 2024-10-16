#!/usr/bin/env bash

mkdir -p lib

echo 'installing gecko driver v0.31.0'
wget https://github.com/mozilla/geckodriver/releases/download/v0.31.0/geckodriver-v0.31.0-linux64.tar.gz -O lib/geckodriver-v0.31.0-linux64.tar.gz
tar -xvf lib/geckodriver-v0.31.0-linux64.tar.gz -C lib

echo 'installing tor browser 13.5.7'
wget https://www.torproject.org/dist/torbrowser/13.5.7/tor-browser-linux-x86_64-13.5.7.tar.xz -O lib/tor-browser-linux-x86_64-13.5.7.tar.xz
tar -xvf lib/tor-browser-linux-x86_64-13.5.7.tar.xz -C lib

echo 'installing tor cli'
wget https://archive.torproject.org/tor-package-archive/torbrowser/13.5.7/tor-expert-bundle-linux-x86_64-13.5.7.tar.gz -O lib/tor-expert-bundle-linux-x86_64-13.5.7.tar.gz
tar -xvf lib/tor-expert-bundle-linux-x86_64-13.5.7.tar.gz -C lib
