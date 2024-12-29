from datetime import datetime

def DecodeNotification(notification: dict) -> dict:
    """
    Sérialiser une notification pour le retour au client.

    :param notification: Dictionnaire brut contenant les données de la notification.
    :return: Dictionnaire sérialisé prêt pour le retour.
    """
    return {
        "_id": str(notification.get("_id")), 
        "contenu": notification.get("contenu"),
        "utilisateur_id": str(notification.get("utilisateur_id")) if notification.get("utilisateur_id") else None, 
        "date": notification.get("date").isoformat() if isinstance(notification.get("date"), datetime) else None,  
    }

def DecodeNotifications(notifications: list) -> list:
    """
    Sérialiser une liste de notifications.

    :param notifications: Liste brute contenant les notifications.
    :return: Liste de dictionnaires sérialisés.
    """
    return [DecodeNotification(notification) for notification in notifications]
