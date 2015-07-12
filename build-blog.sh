#!/usr/bin/env bash

sudo apt-get install ruby rubygems build-essential ruby-dev
gem install bundler
bundle install
bundle exec jekyll serve
