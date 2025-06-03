from django.core.mail import get_connection
from django_ses import SESBackend


class AmazonSesClient:

    @classmethod
    def get_connection(cls, email_settings:dict):
        ses_backend = SESBackend(
            fail_silently=email_settings.pop('FAIL_SILENTLY', None),
            aws_session_profile=email_settings.pop('AWS_SESSION_PROFILE', None),
            aws_access_key=email_settings.pop('AWS_ACCESS_KEY'),
            aws_secret_key=email_settings.pop('AWS_SECRET_KEY'),
            aws_session_token=email_settings.pop('AWS_SESSION_TOKEN', None),
            aws_region_endpoint=email_settings.pop('AWS_REGION_ENDPOINT', None),
            aws_region_name=email_settings.pop('AWS_REGION_NAME', None),
            aws_auto_throttle=email_settings.pop('AWS_AUTO_THROTTLE', None),
            aws_config=email_settings.pop('AWS_CONFIG', None),
            dkim_domain=email_settings.pop('DKIM_DOMAIN', None),
            dkim_key=email_settings.pop('DKIM_KEY', None),
            dkim_headers=email_settings.pop('DKIM_HEADERS', None),
            dkim_selector=email_settings.pop('DKIM_SELECTOR', None),
            ses_from_arn=email_settings.pop('SES_FROM_ARN', None),
            ses_source_arn=email_settings.pop('SES_SOURCE_ARN', None),
            ses_return_path_arn=email_settings.pop('SES_RETURN_PATH_ARN', None),
            use_ses_v2=email_settings.pop('USE_SES_V2', None),
            **email_settings
        )
        ses_backend.open()
        return ses_backend
