from datetime import date, datetime

from .decoders import register
from .collection import JsonAPICollection, JsonAPISingleton, T
from .query import JsonAPIFilterValue, JsonAPIQuery, JsonAPISortValue, JsonAPIIncludeValue
from .schema import JsonAPIResourceIdentifier, JsonAPIResourceSchema

register(date, date.fromisoformat)
register(datetime, datetime.fromisoformat)
