from django.db.models import Q

from apps.data.models import Client


def _get_clients_for_sending(clients_quantity, sending):
    """  """
    return Client.objects.filter(
        Q(is_invited=False),
        ~Q(telegram_username=''),
        Q(total_sum__gte=sending.min_total_sum),
        Q(total_sum__lte=sending.max_total_sum),
        Q(visits_quantity__gte=sending.min_visits_quantity),
        Q(visits_quantity__lte=sending.max_visits_quantity),
    )[:clients_quantity]
