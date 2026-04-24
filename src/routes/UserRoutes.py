from flask_classful import FlaskView, route
from src.actions.UserSignupVerifyOtpAction import UserSignupVerifyOtpAction
from src.actions.UserSignupInitiateAction import UserSignupInitiateAction
from src.actions.UserSignupCompleteAction import UserSignupCompleteAction
from src.actions.ForgotPasswordAction import ForgotPasswordAction
from src.actions.ForgotPasswordVerifyResetOtpAction import ForgotPasswordVerifyResetOtpAction
from src.actions.ResetPasswordAction import ResetPasswordAction


class UserRoutes(FlaskView):
    trailing_slash = False

    @route("/signup", methods=["POST"])
    def signup(self):
        return UserSignupInitiateAction.run(self)

    @route("/verify-otp", methods=["POST"])
    def verify_otp(self):
        return UserSignupVerifyOtpAction.run(self)

    @route("/complete-signup", methods=["POST"])
    def complete_signup(self):
        return UserSignupCompleteAction.run(self)
    
   
    # ── Password Reset ─────────────────────────────────────────────────────────

    @route("/forgot-password", methods=["POST"])
    def forgot_password(self):
        return ForgotPasswordAction.run(self)

    @route("/verify-reset-otp", methods=["POST"])
    def verify_reset_otp(self):
        return ForgotPasswordVerifyResetOtpAction.run(self)

    @route("/reset-password", methods=["POST"])
    def reset_password(self):
        return ResetPasswordAction.run(self)