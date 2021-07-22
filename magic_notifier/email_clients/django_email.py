from django.core.mail import get_connection


class DjangoEmailClient:

    @classmethod
    def get_connection(cls, email_settings:dict):
        smtp_host = email_settings["HOST"]
        smtp_port = email_settings["PORT"]
        smtp_use_tls = email_settings.get("USE_TLS", False)
        smtp_use_ssl = email_settings.get("USE_SSL", False)
        smtp_username = email_settings["USER"]
        smtp_password = email_settings["PASSWORD"]

        return get_connection(
            host=smtp_host,
            port=smtp_port,
            username=smtp_username,
            password=smtp_password,
            use_tls=smtp_use_tls,
            use_ssl=smtp_use_ssl,
        )