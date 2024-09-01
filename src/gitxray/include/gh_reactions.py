from collections import defaultdict
from .gx_definitions import REACTIONS_POSITIVE, REACTIONS_NEUTRAL, REACTIONS_NEGATIVE

def sort_reactions(d):
    return sorted(d.items(), key=lambda item: item[1], reverse=True)

def categorize_reactions(comment, positive_reactions, negative_reactions, neutral_reactions):

    for reaction in REACTIONS_POSITIVE:
        positive_reactions[comment.get('html_url')] += comment.get('reactions').get(reaction, 0)

    for reaction in REACTIONS_NEGATIVE:
        negative_reactions[comment.get('html_url')] += comment.get('reactions').get(reaction, 0)

    for reaction in REACTIONS_NEUTRAL:
        neutral_reactions[comment.get('html_url')] += comment.get('reactions').get(reaction, 0)

    return
