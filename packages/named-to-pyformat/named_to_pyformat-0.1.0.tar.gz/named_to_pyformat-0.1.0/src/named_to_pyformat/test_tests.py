from . import s


def test_single_param():
    input = "SELECT * FROM users WHERE name = :name"
    result = "SELECT * FROM users WHERE name = %(name)s"
    assert s(input) == result


def test_multiple_params():
    assert (
        s("SELECT * FROM users WHERE name = :name AND age = :age")
        == "SELECT * FROM users WHERE name = %(name)s AND age = %(age)s"
    )


def test_no_params():
    assert s("SELECT * FROM users") == "SELECT * FROM users"


def test_param_with_underscore():
    assert (
        s("SELECT * FROM users WHERE user_id = :user_id")
        == "SELECT * FROM users WHERE user_id = %(user_id)s"
    )


def test_param_at_start():
    assert s(":id SELECT") == "%(id)s SELECT"
