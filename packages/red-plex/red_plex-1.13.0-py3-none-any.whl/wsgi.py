"""WSGI entry point for the application."""

from red_plex.infrastructure.gui.app import create_app

app, socketio = create_app()
