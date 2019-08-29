from extended_choices import Choices


EVIDENCE_CHOICES = (
    ('True', 'Yes'),
    ('False', 'No'),
)
JUDGMENT_CHOICES = (
    ('False',
     'A. False or sufficiently misleading that search and social platforms should demote it'),
    ('True',
     'B. True or true enough that search and social media platforms should not demote it'),
    ('C. Im not sure', 'I\'m not sure whether it should be demoted'),
)

WORKFLOW_TYPE_CHOICES = Choices(
    ['WITHOUT_EVIDENCE_URL_WORKFLOW', 'without evidence url workflow', 'without evidence url workflow'],
    ['EVIDENCE_URL_INPUT_WORKFLOW', 'evidence url input workflow', 'evidence url input workflow'],
    ['EVIDENCE_URLS_JUDGMENT_WORKFLOW', 'evidence urls judgment workflow', 'evidence urls judgment workflow'],
)
