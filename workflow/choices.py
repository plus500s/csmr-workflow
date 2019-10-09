from extended_choices import Choices

EVIDENCE_CHOICES = (
    ('True', 'Yes'),
    ('False', 'No'),
)
JUDGMENT_CHOICES = (
    ('True', 'Yes'),
    ('False', 'No'),
)

WORKFLOW_TYPE_CHOICES = Choices(
    ['WITHOUT_EVIDENCE_URL_WORKFLOW', 'without evidence url workflow', 'without evidence url workflow'],
    ['EVIDENCE_URL_INPUT_WORKFLOW', 'evidence url input workflow', 'evidence url input workflow'],
    ['EVIDENCE_URLS_JUDGMENT_WORKFLOW', 'evidence urls judgment workflow', 'evidence urls judgment workflow'],
)

JUDGMENT_REMOVE_CHOICES = (
    ('True', 'Yes, platforms should remove the item.'),
    ('False', 'No, platforms should not remove the item.'),
)

JUDGMENT_REDUCE_CHOICES = (
    ('True', 'Yes, platforms should reduce exposure to the item.'),
    ('False', 'No, platforms should not reduce exposure to the item.'),
)

JUDGMENT_INFORM_CHOICES = (
    ('True', 'Yes, platforms should inform users that the item may be misleading.'),
    ('False', 'No, platforms should not inform users that the item may be misleading.'),
)

JUDGMENT_MISLEADING_ITEM_CHOICES = (
    ('1', '1'),
    ('2', '2'),
    ('3', '3'),
    ('4', '4'),
    ('5', '5'),
    ('6', '6'),
    ('7', '7'),
)
