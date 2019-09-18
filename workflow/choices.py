from extended_choices import Choices


EVIDENCE_CHOICES = (
    ('True', 'Yes'),
    ('False', 'No'),
)
JUDGMENT_CHOICES = (
    ('True', 'Yes, confirms.'),
    ('False', 'Yes, contradicts.'),
    ('Im not sure', 'No evidence found.'),
)

WORKFLOW_TYPE_CHOICES = Choices(
    ['WITHOUT_EVIDENCE_URL_WORKFLOW', 'without evidence url workflow', 'without evidence url workflow'],
    ['EVIDENCE_URL_INPUT_WORKFLOW', 'evidence url input workflow', 'evidence url input workflow'],
    ['EVIDENCE_URLS_JUDGMENT_WORKFLOW', 'evidence urls judgment workflow', 'evidence urls judgment workflow'],
)
