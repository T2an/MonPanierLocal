"""
Utilitaires pour les producteurs.
"""
from math import radians, cos, sin, asin, sqrt


def haversine_distance(lat1, lon1, lat2, lon2):
    """
    Calcule la distance entre deux points en kilomètres en utilisant la formule de Haversine.
    
    Args:
        lat1, lon1: Coordonnées du premier point (latitude, longitude)
        lat2, lon2: Coordonnées du second point (latitude, longitude)
    
    Returns:
        Distance en kilomètres
    """
    # Convertir les degrés en radians
    lat1, lon1, lat2, lon2 = map(radians, [float(lat1), float(lon1), float(lat2), float(lon2)])
    
    # Formule de Haversine
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    
    # Rayon de la Terre en kilomètres
    r = 6371
    
    return c * r


def get_producers_near_location(latitude, longitude, radius_km, queryset=None):
    """
    Retourne les producteurs dans un rayon donné autour d'une position.
    
    Args:
        latitude: Latitude du point central
        longitude: Longitude du point central
        radius_km: Rayon en kilomètres
        queryset: QuerySet de base (optionnel)
    
    Returns:
        QuerySet filtré des producteurs dans le rayon
    """
    from .models import ProducerProfile
    
    if queryset is None:
        queryset = ProducerProfile.objects.all()
    
    # Filtrer approximativement avec une bounding box pour optimiser
    # 1 degré de latitude ≈ 111 km
    # 1 degré de longitude ≈ 111 km * cos(latitude)
    lat_delta = radius_km / 111.0
    lon_delta = radius_km / (111.0 * abs(cos(radians(float(latitude)))))
    
    # Bounding box approximative
    queryset = queryset.filter(
        latitude__gte=float(latitude) - lat_delta,
        latitude__lte=float(latitude) + lat_delta,
        longitude__gte=float(longitude) - lon_delta,
        longitude__lte=float(longitude) + lon_delta,
    )
    
    # Filtrer précisément avec la distance de Haversine
    # On calcule la distance pour chaque producteur et on filtre
    nearby_ids = [
        producer.id
        for producer in queryset
        if haversine_distance(
            latitude, longitude,
            float(producer.latitude), float(producer.longitude)
        ) <= radius_km
    ]
    
    return ProducerProfile.objects.filter(id__in=nearby_ids)
