from machc.user.interactors.user.stud.user_registration_service import UserRegistrationService, UserRegistrationData


class UserRegister:
    """
    The UserRegister class is responsible for orchestrating the user registration process.
    It acts as an intermediary, delegating the registration logic to a provided UserRegistrationService.
    """

    def __init__(self, registration_service: UserRegistrationService):
        """
        Initializes UserRegister with a concrete implementation of UserRegistrationService.

        Args:
            registration_service (UserRegistrationService): The service used to register a user.
        """
        self.registration_service = registration_service

    def execute(self, user: UserRegistrationData) -> None:
        """
        Executes the user registration process by delegating to the UserRegistrationService.

        Args:
            user (UserRegistrationData): The data of the user to register.
        """
        self.registration_service.register(user)
