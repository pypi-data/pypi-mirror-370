import pytest

from tagth.tagth import allowed, TagthValidationError


@pytest.mark.parametrize(
    'p, r, action, expected',
    [
        ('user', 'user:read', 'read', True),
        ('user', 'user:read, user:edit', 'read', True),
        ('user', 'user:read, user:edit', 'delete', False),
        ('user', 'user:read', 'delete', False),
        ('user, content', 'user:read, content:view', 'view', True),
        ('user, content', 'user:read, content:view', 'delete', False),
    ]
)
def test_regular_user_with_basic_permission(p, r, action, expected):
    assert allowed(p, r, action) == expected


@pytest.mark.parametrize(
    'p, r, action, expected',
    [
        ('user', 'user:{read, write}', 'read', True),
        ('user', 'user:{read, write}, admin:edit', 'read', True),
        ('user', 'user:{read, write}, admin:edit', 'edit', False),
        ('user', 'user:{read, write}', 'delete', False),
        ('user, content', 'user:{read, write}, content:view', 'view', True),
        ('user, content', 'user:{read, write}, content:view', 'delete', False),
    ]
)
def test_multiple_actions(p, r, action, expected):
    assert allowed(p, r, action) == expected


@pytest.mark.parametrize(
    'p, r, action, expected',
    [
        ('admin', 'admin:create', 'create', True),
        ('admin', 'admin:create', 'create_assest', True),
        ('admin', 'admin:create', 'write_message', False),
        ('admin', 'admin:create, content:view', 'create_assest', True),
        ('admin, user', 'admin:create, user:create', 'create_assest', True),
    ]
)
def test_superactions(p, r, action, expected):
    assert allowed(p, r, action) == expected


def test_empty_resource():
    p = 'user'
    r = ''
    assert not allowed(p, r, 'view')


def test_empty_principal():
    p = ''
    r = 'content:read'
    assert not allowed(p, r, 'read')

    p = ','
    r = 'content:read'
    assert not allowed(p, r, 'read')

    p = ', content'
    r = 'content:read'
    assert allowed(p, r, 'read')


def test_invalid_resource():
    p = 'content'
    r = 'content:view@'
    with pytest.raises(TagthValidationError):
        allowed(p, r, 'view')


def test_root_has_full_access():
    p = 'root'
    r = 'content:read, metadata:write'

    assert allowed(p, r, 'anything')
    assert allowed(p, r, 'write')

    r = 'content:all'
    assert allowed(p, r, 'all')

    r = 'any:read'
    assert allowed(p, r, 'read')

    r = 'anyone:read'
    assert allowed(p, r, 'write')


def test_void_principal():
    p = 'void'
    r = 'anyone:read'

    assert allowed(p, r, 'read')
    assert not allowed(p, r, 'write')

    r = 'content:read'
    assert not allowed(p, r, 'read')

    r = 'content:all'
    assert not allowed(p, r, 'read')


def test_principal_tags_and_supertags():
    p = 'admin'
    r = 'admin_user:write, admin_content:delete'

    assert allowed(p, r, 'write')
    assert allowed(p, r, 'delete')
    assert not allowed(p, r, 'read')


def test_any_resource():
    p = 'user'
    r = 'anyone:read'

    assert allowed(p, r, 'read')
    assert not allowed(p, r, 'delete')


def test_anyone_resource():
    p_root = 'root'
    p_void = 'void'
    p_user = 'user'

    r = 'anyone:read'

    assert allowed(p_root, r, 'read')
    assert allowed(p_void, r, 'read')
    assert allowed(p_user, r, 'read')
    assert allowed(p_root, r, 'write')
    assert not allowed(p_void, r, 'write')
    assert not allowed(p_user, r, 'write')


def test_special_format_any():
    p_root = 'root'
    p_void = 'void'
    p_user = 'user'

    r = 'anyone:read'

    assert allowed(p_root, r, 'read')
    assert allowed(p_void, r, 'read')
    assert allowed(p_user, r, 'read')
    assert allowed(p_root, r, 'write')
    assert not allowed(p_void, r, 'write')
    assert not allowed(p_user, r, 'write')


def test_special_format_all():
    p_root = 'root'
    p_void = 'void'
    p_user = 'user'
    p = 'another'

    r = 'user:all'

    assert allowed(p_root, r, 'read')
    assert not allowed(p_void, r, 'read')
    assert allowed(p_user, r, 'read')
    assert not allowed(p, r, 'read')


def test_all_resource():
    p_root = 'root'
    p_void = 'void'
    p_user = 'user'
    p = 'another'

    r = 'user:all'

    assert allowed(p_root, r, 'read')
    assert not allowed(p_void, r, 'read')
    assert allowed(p_user, r, 'read')
    assert not allowed(p, r, 'read')


def test_special_format_any_and_all():
    p_root = 'root'
    p_void = 'void'
    p_user = 'user'

    r = 'anyone:all'

    assert allowed(p_root, r, 'read')
    assert allowed(p_void, r, 'read')
    assert allowed(p_user, r, 'read')
    assert allowed(p_root, r, 'all')
    assert allowed(p_void, r, 'all')
    assert allowed(p_user, r, 'all')
