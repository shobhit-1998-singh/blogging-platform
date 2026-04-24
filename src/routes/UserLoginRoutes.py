from flask_classful import FlaskView, route
from src.actions.UserLoginAction import UserLoginAction


class UserLoginRoutes(FlaskView):
    trailing_slash = False

    @route("/login", methods=["POST"])
    def login_user(self):
        return UserLoginAction.run()
