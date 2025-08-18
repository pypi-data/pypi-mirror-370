from commercetools.platform import Client
from commercetools.platform.models import CustomerSignin, CustomerSignInResult, CustomerDraft, Address

from machc.configurator.configurator import Configurator
from machc.user.entities import LoginCredential
from machc.user.entities import UserId
from machc.user.interactors import UserException
from machc.user.interactors import UserLoginService
from machc.user.interactors import UserRegistrationService, UserRegistrationData


class CommercetoolsUserAdapter(UserLoginService, UserRegistrationService):
    """
    Adapter for user login operations via Commercetools.

    This class implements the UserLoginService interface and integrates with the Commercetools
    platform to validate login credentials and retrieve the associated User ID.
    """

    client: Client

    def __init__(self, configurator: Configurator):
        """
        Initializes the Commercetools client for user login operations.

        Args:
            configurator (Configurator): Commercetools properties configurator.
        """
        self.project_key = configurator.get("ctp.project_key")

        self.client = Client(
            client_id=configurator.get("ctp.client_id"),
            client_secret=configurator.get("ctp.client_secret"),
            scope=configurator.get("ctp.scope"),
            url=configurator.get("ctp.api_url"),
            token_url=configurator.get("ctp.auth_url")
        )

    def login(self, login_credential: LoginCredential) -> UserId:
        """
        Authenticates the user using provided login credentials via Commercetools.

        Args:
            login_credential (LoginCredential): User login credentials (username and password).

        Returns:
            UserId: A unique user identifier if login is successful.

        Raises:
            UserException: If authentication fails.
        """
        # Simulate the login process using the Commercetools platform's custom object store
        try:
            customer_signin = CustomerSignin(email=login_credential.get_username(),
                                             password=login_credential.get_password())
            customer_signin_result: CustomerSignInResult = self.client.with_project_key(self.project_key).login().post(
                customer_signin)

            # Get the first matched customer
            customer = customer_signin_result.customer

            # Extract the customer ID and return as UserId
            user_id = UserId(customer.id)
            return user_id

        except Exception as err:
            raise UserException(f"Login failed: {str(err)}")

    def register(self, user: UserRegistrationData) -> None:
        try:
            # Validate user registration data
            if not user.email or not user.password:
                raise UserException("Email and Password are required for registration.")

            # Define customer draft
            customer_draft = CustomerDraft(
                email=user.email,
                password=user.password,
                first_name=user.first_name,
                last_name=user.last_name,
                addresses=[
                    Address(
                        first_name=user.first_name,
                        last_name=user.last_name,
                        street_name="123 Example Street",
                        city="Example City",
                        postal_code="12345",
                        country="US"
                    )
                ],
                default_shipping_address=0,
                default_billing_address=0
            )

            self.client.with_project_key(self.project_key).customers().post(customer_draft)
            print(f"Registering user: {user}")

        except UserException as e:
            # Raise exception if validation or registration fails
            raise UserException(f"Failed to register user: {str(e)}")
