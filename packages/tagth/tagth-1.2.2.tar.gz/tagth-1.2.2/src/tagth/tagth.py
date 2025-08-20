from pyparsing import (
    Empty,
    Literal,
    ParseException,
    StringEnd,
    Suppress,
    Word,
    ZeroOrMore,
    delimitedList,
    identbodychars,
    identchars,
)

TAG_LIST_DELIMETER = ','
ACTION_DELIMETER = ':'
ANYONE_PRINCIPAL = 'anyone'
FULL_ACCESS_ACTION = 'all'
ROOT_PRINCIPAL = 'root'
VOID_PRINCIPAL = 'void'
VOID_RESOURCE = ''
BRACE_OPEN = '{'
BRACE_CLOSE = '}'


class TagthException(Exception):
    pass


class TagthValidationError(TagthException):
    pass


def _normalize_principal(principal: str) -> list[str]:
    if not isinstance(principal, str):
        raise TagthValidationError(f'Bad principal {principal}')

    separator = Literal(TAG_LIST_DELIMETER)
    principal_tag = (Word(identchars, identbodychars))('principal_tag')
    empty_principal = (Empty()).setParseAction(lambda _: [VOID_PRINCIPAL])
    principal_module = principal_tag | empty_principal

    parser = ZeroOrMore(principal_module + Suppress(separator)) + principal_module + StringEnd()

    try:
        result = parser.parseString(principal)
        return result.asList()
    except ParseException as e:
        raise TagthValidationError(f"Invalid principal: {principal}") from e


def _normalize_resource(resource: str) -> list[tuple[str, str]]:
    if not resource:
        return []
    if not isinstance(resource, str):
        raise TagthValidationError(f'Bad resource {resource}')

    separator = Literal(TAG_LIST_DELIMETER)
    resource_tag = (Word(identchars, identbodychars))('resource_tag')
    action = (Word(identchars, identbodychars))('action')
    actions = delimitedList(action, delim=TAG_LIST_DELIMETER)('actions')

    single_action_module = (resource_tag + Suppress(ACTION_DELIMETER) + action).setParseAction(
        lambda t: (t.resource_tag, t.action)
    )

    multiple_actions_module = (
        resource_tag + Suppress(ACTION_DELIMETER) + Suppress(BRACE_OPEN) + actions + Suppress(BRACE_CLOSE)
    ).setParseAction(
        lambda t: [(t.resource_tag, act) for act in t.actions]
    )

    empty_module = (Empty()).setParseAction(lambda _: [(VOID_PRINCIPAL, FULL_ACCESS_ACTION)])

    resource_module = single_action_module | multiple_actions_module | empty_module

    parser = ZeroOrMore(resource_module + Suppress(separator)) + resource_module + StringEnd()

    try:
        result = parser.parseString(resource)
        return result.asList()
    except ParseException as e:
        raise TagthValidationError(f"Invalid resource: {resource}") from e


def _resolve_internal(principal: list[str], resource: list[tuple[str, str]]) -> set[str]:
    actions = set()

    for pr_tag in principal:
        if pr_tag == ROOT_PRINCIPAL:
            actions.add(FULL_ACCESS_ACTION)

    if not resource:
        return actions

    for (res_tag, action) in resource:
        if res_tag == ANYONE_PRINCIPAL:
            actions.add(action)

    for pr_tag in principal:
        if pr_tag == VOID_PRINCIPAL:
            continue

        for (res_tag, action) in resource:
            if res_tag.startswith(pr_tag):
                actions.add(action)

    return actions


def _resolve(principal: str, resource: str) -> set[str]:
    principal_list = _normalize_principal(principal)
    resource_list = _normalize_resource(resource)
    return _resolve_internal(principal_list, resource_list)


def allowed(principal: str, resource: str, action: str) -> bool:
    """Checks if a given principal is allowed to perform an action on a resource.

    Args:
        principal (str): A string representing the principal tags.
        resource (str): A string representing the pairs of tags and actions.
        action (str): The action to check for permission.

    Returns:
        bool: True if the action is allowed, False otherwise.
    """
    actions = _resolve(principal, resource)

    if FULL_ACCESS_ACTION in actions:
        return True

    for allowed_action in actions:
        if action.startswith(allowed_action):
            return True

    return False


def validate_principal(principal: str) -> bool:
    """Validates the principal string.

    Args:
        principal (str): A string representing the principal tags.

    Returns:
        bool: True if the principal is valid, False otherwise.
    """
    try:
        _normalize_principal(principal)
    except TagthValidationError:
        return False

    return True


def validate_resource(resource: str) -> bool:
    """Validates the resource string.

    Args:
        resource (str): A string representing the resource-action pairs.

    Returns:
        bool: True if the resource is valid, False otherwise.
    """
    try:
        _normalize_resource(resource)
    except TagthValidationError:
        return False

    return True
