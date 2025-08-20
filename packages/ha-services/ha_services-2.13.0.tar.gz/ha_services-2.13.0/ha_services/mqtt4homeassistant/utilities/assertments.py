from ha_services.mqtt4homeassistant.utilities.string_utils import slugify


def assert_uid(uid: str):
    assert uid
    slug = slugify(uid, sep='_')
    assert uid == slug, f'Invalid: {uid=} (slugify: {slug!r})'
