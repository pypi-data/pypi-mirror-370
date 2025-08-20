from tagth.tagth import _normalize_principal, _normalize_resource, _resolve, allowed


def test_normalize_principal():
    p = _normalize_principal('me')
    assert list(p) == ['me']

    p = _normalize_principal('this,that, those')
    assert list(p) == ['this', 'that', 'those']


def test_normalize_resource():
    s = _normalize_resource('me:all')
    assert list(s) == [('me', 'all')]

    s = _normalize_resource('here:admin, there:all, nowhere:user')
    assert list(s) == [('here', 'admin'), ('there', 'all'), ('nowhere', 'user')]

    s = _normalize_resource('my:all,anyone:all,anyone:ro')
    assert list(s) == [('my', 'all'), ('anyone', 'all'), ('anyone', 'ro')]


def test_resolve():
    r = _resolve('me', 'me:all')
    assert r == {'all'}

    r = _resolve('me', 'meme_me:all')
    assert r == {'all'}

    r = _resolve('mememe', 'me:all')
    assert r == set()

    r = _resolve('me', 'mememe:ro, meme:rw')
    assert r == {'ro', 'rw'}

    r = _resolve('me', 'xmememe:ro, meme:rw')
    assert r == {'rw'}


def test_allowed():
    a = allowed('me', 'me:all', 'all')
    assert a

    a = allowed('me', 'me:all', 'ro')
    assert a

    a = allowed('me', 'anyone:ro', 'ro')
    assert a

    a = allowed('me', 'anyone:ro', 'ro')
    assert a

    a = allowed('me', 'they:ro, meme:rw', 'rw')
    assert a

    a = allowed('me', 'ther:ro, meme:rw', 'ro')
    assert not a


def test_root():
    a = allowed('a', 'a:ro', 'ro')
    assert a

    a = allowed('a', 'a:ro', 'rw')
    assert not a

    a = allowed('a,root', 'a:ro', 'rw')
    assert a


def test_emply_resource():
    a = allowed('root', '', 'all')
    assert a

    a = allowed('nonroot', '', 'all')
    assert not a


def test_empty_principal():
    a = allowed('', 'resource:all', 'action')
    assert not a

    a = allowed(',', 'resource:all', 'action')
    assert not a

    a = allowed(',res', 'resource:all', 'action')
    assert a

    a = allowed(',res', 'other:all,resource:all', 'action')
    assert a

    a = allowed('other,another', 'other:all,resource:all', 'action')
    assert a

    a = allowed('other,another', 'another:action', 'action')
    assert a

    a = allowed('other,another', 'another:inaction', 'action')
    assert not a


def test_void():
    a = allowed('resource', 'resource:all', 'action')
    assert a

    a = allowed('void', 'void:all', 'action')
    assert not a


def test_empty_anyone():
    a = allowed('', 'anyone:action', 'action')
    assert a

    a = allowed('', 'anyone:action', 'inaction')
    assert not a

    a = allowed('', 'anyone:all', 'action')
    assert a

    a = allowed('', 'anyone:inaction', 'action')
    assert not a

    a = allowed('', '', 'action')
    assert not a


def test_normalize_emply():
    n = _normalize_resource('')
    assert not n


def test_action_prefixes():
    assert allowed('user', 'user:a_class_action', 'a_class_action')
    assert allowed('user', 'user:a_class', 'a_class_one')
    assert allowed('user', 'user:a_class', 'a_class_two')
    assert not allowed('user', 'user:b_class', 'a_class_action')
    assert not allowed('user', 'user:a_class', 'b_class_action')
