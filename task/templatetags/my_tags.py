from django import template

register = template.Library()


@register.filter
def format_name(tester):
    name = tester.strip(' ')
    if ' ' in tester:
        name = name.replace(' ', '<br>')
    if ',' in tester:
        name = name.replace(',', '<br>')
    if '/' in tester:
        name = name.replace('/', '<br>')
    if '-' in tester:
        name = name.replace('-', '<br>')

    return name
