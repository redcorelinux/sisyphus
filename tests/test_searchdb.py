import sisyphus.searchdb


def test_tosql_converts_wildcards():
    assert sisyphus.searchdb.tosql('open*') == 'open%'
    assert sisyphus.searchdb.tosql('na?o') == 'na_o'
    assert sisyphus.searchdb.tosql('x11-wm/*') == 'x11-wm/%'


def test_tosql_leaves_plain_text_alone():
    assert sisyphus.searchdb.tosql('openbox') == 'openbox'


def test_tosql_empty_string_matches_everything():
    assert sisyphus.searchdb.tosql('') == '%%'


def test_tosql_converts_each_item_in_a_list():
    assert sisyphus.searchdb.tosql(['x11-wm', 'open*', '']) == [
        'x11-wm', 'open%', '%%']
