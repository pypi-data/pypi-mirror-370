import factory
from faker import Faker
from pandas._libs.tslibs.offsets import BDay

from wbportfolio.models import OrderProposal

fake = Faker()


class OrderProposalFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = OrderProposal

    trade_date = factory.LazyAttribute(lambda o: (fake.date_object() + BDay(1)).date())
    comment = factory.Faker("paragraph")
    portfolio = factory.SubFactory("wbportfolio.factories.PortfolioFactory")
    creator = factory.SubFactory("wbcore.contrib.directory.factories.PersonFactory")
