from django.conf import settings as django_settings

ADMINBOOST_PREVIEW_SIZE = getattr(
    django_settings, 'ADMINBOOST_PREVIEW_SIZE', (300,300))


ADMINBOOST_PREVIEW_ENGINE = getattr(django_settings, 'ADMINBOOST_PREVIEW_ENGINE', None)

if ADMINBOOST_PREVIEW_ENGINE is None:
    try:
        import easy_thumbnails
        # Default for legacy reasons (easy_thumbnails used to be the only available engine)
        ADMINBOOST_PREVIEW_ENGINE = 'adminboost.preview.EasyThumbnailEngine'
    except ImportError:
        try:
            from sorl import thumbnail
            ADMINBOOST_PREVIEW_ENGINE = 'adminboost.preview.SorlThumbnailEngine'
        except ImportError:
            pass