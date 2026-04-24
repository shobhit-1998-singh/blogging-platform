"""
Entry point for the Flask app.
This file runs the server.
"""

from src import app  # Import Flask app
from src.routes.UserRoutes import UserRoutes
from src.routes.UserLoginRoutes import UserLoginRoutes

# Register routes
UserRoutes.register(app, route_base="/user")
UserLoginRoutes.register(app, route_base="/api/user")

if __name__ == "__main__":
    app.run(debug=True, port= 5001)  # Start server with debug mode
