import dbsettings
from datetime import timedelta


class HistoryEmailOptions(dbsettings.Group):

    resend_delay_all = dbsettings.DurationValue(
        'The ammount of time that has to pass before the server can send another activation email',
        default=timedelta(minutes=1))

    resend_delay_single = dbsettings.DurationValue(
        'The ammount of time that has to pass before the server can send another activation email',
        default=timedelta(minutes=1))
