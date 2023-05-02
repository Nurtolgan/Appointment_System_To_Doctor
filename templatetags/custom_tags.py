from django import template

register = template.Library()

@register.simple_tag
def count_comments(post):
    return post.comments.filter(active=True).count()
