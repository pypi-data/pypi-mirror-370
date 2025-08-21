from ryft_sdk.client import RyftClient
from ryft_sdk.clients.accounts import AccountsClient
from ryft_sdk.clients.account_links import AccountLinksClient
from ryft_sdk.clients.apple_pay import ApplePayClient
from ryft_sdk.clients.customers import CustomersClient
from ryft_sdk.clients.disputes import DisputesClient
from ryft_sdk.clients.events import EventsClient
from ryft_sdk.clients.files import FilesClient
from ryft_sdk.clients.payment_methods import PaymentMethodsClient
from ryft_sdk.clients.payment_sessions import PaymentSessionsClient
from ryft_sdk.clients.payout_methods import PayoutMethodsClient
from ryft_sdk.clients.payouts import PayoutsClient
from ryft_sdk.clients.persons import PersonsClient
from ryft_sdk.clients.platform_fees import PlatformFeesClient
from ryft_sdk.clients.subscriptions import SubscriptionsClient
from ryft_sdk.clients.transfers import TransfersClient
from ryft_sdk.clients.webhooks import WebhooksClient


class Ryft:
    def __init__(self, secret_key: str):
        self.client = RyftClient(secret_key)
        self.accounts = AccountsClient(self.client)
        self.account_links = AccountLinksClient(self.client)
        self.apple_pay = ApplePayClient(self.client)
        self.customers = CustomersClient(self.client)
        self.disputes = DisputesClient(self.client)
        self.events = EventsClient(self.client)
        self.files = FilesClient(self.client)
        self.payment_methods = PaymentMethodsClient(self.client)
        self.payment_sessions = PaymentSessionsClient(self.client)
        self.payouts = PayoutsClient(self.client)
        self.payout_methods = PayoutMethodsClient(self.client)
        self.persons = PersonsClient(self.client)
        self.platform_fees = PlatformFeesClient(self.client)
        self.subscriptions = SubscriptionsClient(self.client)
        self.transfers = TransfersClient(self.client)
        self.webhooks = WebhooksClient(self.client)
