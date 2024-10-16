#!/usr/bin/env bash

echo 'installing gecko driver v0.31.0'
wget https://github.com/mozilla/geckodriver/releases/download/v0.31.0/geckodriver-v0.31.0-linux64.tar.gz
tar -xvf geckodriver-v0.31.0-linux64.tar.gz


echo 'installing tor browser 13.5.7'
wget https://www.torproject.org/dist/torbrowser/13.5.7/tor-browser-linux-x86_64-13.5.7.tar.xz
tar -xvf tor-browser-linux-x86_64-13.5.7.tar.xz


echo 'now install tor with your systems package manager'
echo 'e.g. sudo dnf install tor'
