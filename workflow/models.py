from django.db import models

from .choices import WORKFLOW_TYPE_CHOICES


class Workflow(models.Model):
    api_id = models.PositiveIntegerField(unique=True)
    name = models.CharField(max_length=255)
    instruction = models.TextField()
    judgment = models.TextField()
    prediction = models.TextField()
    corroborating_question = models.TextField(null=True, blank=True)
    type = models.CharField(max_length=255, choices=WORKFLOW_TYPE_CHOICES,
                            default=WORKFLOW_TYPE_CHOICES.WITHOUT_EVIDENCE_URL_WORKFLOW)

    def __str__(self):
        return str(self.name)


class Rater(models.Model):
    api_id = models.CharField(max_length=255, unique=True)
    email = models.EmailField(unique=True, null=True)
    age = models.CharField(max_length=255)
    gender = models.CharField(max_length=255)
    location = models.CharField(max_length=255)
    workflow = models.ForeignKey('Workflow', null=True, on_delete=models.SET_NULL)

    def __str__(self):
        return '{} workflow:{}'.format(self.api_id, self.workflow)


class Item(models.Model):
    url = models.URLField()
    category = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return '{} url:{}'.format(self.pk, self.url)


class ItemWorkflow(models.Model):
    item = models.ForeignKey('Item', on_delete=models.CASCADE)
    workflow = models.ForeignKey('Workflow', on_delete=models.CASCADE)
    raters_desired = models.PositiveIntegerField()
    raters_actual = models.PositiveIntegerField()

    def __str__(self):
        return 'item:{} workflow:{}'.format(self.item, self.workflow)


class Answer(models.Model):
    rater = models.ForeignKey('Rater', null=True, on_delete=models.SET_NULL)
    item = models.ForeignKey('Item', null=True, on_delete=models.SET_NULL)
    workflow = models.ForeignKey('Workflow', null=True,  on_delete=models.SET_NULL)
    answer_start = models.DateTimeField()
    answer_end = models.DateTimeField()
    rater_answer_evidence = models.TextField(blank=True, null=True)
    rater_answer_judgment = models.TextField(blank=True, null=True)
    rater_answer_predict_a = models.TextField(blank=True, null=True)
    rater_answer_predict_b = models.TextField(blank=True, null=True)
    rater_answer_predict_c = models.TextField(blank=True, null=True)
    evidence_url = models.URLField(null=True, blank=True)

    def __str__(self):
        return 'rater:{} item:{} workflow:{}'.format(self.rater, self.item, self.workflow)
