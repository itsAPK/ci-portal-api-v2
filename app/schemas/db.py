from beanie import (
    Document,
    Insert,
    Replace,
    Save,
    SaveChanges,
    Update,
    before_event,
    init_beanie,
)
from datetime import datetime, timezone


class BaseDocument(Document):
    created_at: datetime | None = None
    updated_at: datetime | None = None

    @before_event(Insert)
    def set_created_at(self):
        self.created_at = datetime.now(timezone.utc)
        self.updated_at = datetime.now(timezone.utc)

    @before_event(Update, SaveChanges, Save, Replace)
    def set_updated_at(self):
        self.updated_at = datetime.now(timezone.utc)