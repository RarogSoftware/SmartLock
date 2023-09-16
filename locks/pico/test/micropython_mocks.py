def get_micropython_mocks():
    from mock import MagicMock
    return dict({
        "micropython": MagicMock(),
        "collections": {
            "abc": MagicMock()
        },
        "aioble": MagicMock(),
        "bluetooth": MagicMock()
    })
