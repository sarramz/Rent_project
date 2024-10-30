def DecodeNotification(notification) -> dict:
    return {
        "_id": str(notification["_id"]),
        "utilisateur_id": str(notification["utilisateur_id"]),
        "contenu": notification.get("contenu"),
        "date": notification.get("date"),
        "lue": notification.get("lue", False)
    }

def DecodeNotifications(notifications) -> list:
    return [DecodeNotification(notification) for notification in notifications]
