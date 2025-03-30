from django.conf import settings
from elasticsearch_dsl import analyzer, tokenizer


def build_index_name( name, app_name=None, ):
    if app_name is None:
        app_name = getattr( settings, 'PROJECT_NAME', None )
    if not app_name:
        result = name
    else:
        result = f"{app_name}__{name}"

    is_test = getattr( settings, 'TEST_MODE', False )
    if is_test:
        return f"test__{result}"
    return result


name = analyzer(
    'name',
    tokenizer=tokenizer( 'trigram', 'nGram', min_gram=3, max_gram=4 ),
    filter=[ "lowercase", ],
)

name_space = analyzer(
    'name_space',
    tokenizer='whitespace',
    filter=[ "lowercase", ],
)
