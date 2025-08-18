from mjdb.repositories.base.base_repository import BaseSQLAlchemyRepository
from mjdb.model.daily_shareholder_ownership import DailyShareholderOwnership
from mjdb.session.types.session_context import SessionContext
from mjdb.session.types.session_config import SessionConfig
import os

import logging

class ShareholderOwnershipRepository(BaseSQLAlchemyRepository[DailyShareholderOwnership]):
    def __init__(self, db_url: str, log_level: int = logging.INFO):
        ctx = SessionContext(
            db_url=db_url or os.getenv("STOCK_DATABASE_LOCALHOST_URL"),
            session_config=SessionConfig(expire_on_commit=False)
        )

        super().__init__(model=DailyShareholderOwnership, context=ctx, log_level=log_level)

if __name__ == "__main__":
    from dotenv import load_dotenv
    import os
    from datetime import datetime, timedelta


    load_dotenv()

    url = os.getenv("STOCK_DATABASE_LOCALHOST_URL")
    print(url)

    model = DailyShareholderOwnership(
        reference_date=datetime.now() - timedelta(days=1),
        ticker="000660",
        name="SK hynix",
        shareholder_type="Foreign",
        common_shares=1000000,
        ownership_ratio=10.0,
        total_shares_outstanding=10000000,
        floating_shares=5000000,
        floating_share_ratio=50.0,
        last_change_date=datetime.now()
    )
    print(model)

    repo = ShareholderOwnershipRepository(db_url=url, log_level=logging.INFO)
    print(repo)

    repo.serial_upsert_entities([model])


