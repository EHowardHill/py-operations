#!/bin/bash
# Clocker restarter

tmux kill-session -t clocker
tmux kill-session -t clocker_5001
tmux add -s clocker 'cd /scripts/python/clocker ; gunicorn --bind 0.0.0.0:5000 wsgi'
tmux add -s clocker 'cd /scripts/python/clocker ; gunicorn --bind 0.0.0.0:5001 wsgi'