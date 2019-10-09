from django.db import models

from .choices import WORKFLOW_TYPE_CHOICES


class Workflow(models.Model):
    api_id = models.PositiveIntegerField(unique=True)
    name = models.CharField(max_length=255)
    instruction = models.TextField()
    judgment_enough_information = models.TextField(null=True, blank=True)
    judgment_misleading_item = models.TextField(null=True, blank=True)
    judgment_remove_reduce_inform_head = models.TextField(null=True, blank=True)
    judgment_remove = models.TextField(null=True, blank=True)
    judgment_reduce = models.TextField(null=True, blank=True)
    judgment_inform = models.TextField(null=True, blank=True)
    judgment_additional = models.TextField(null=True, blank=True)
    prediction = models.TextField()
    corroborating_question = models.TextField(null=True, blank=True)
    type = models.CharField(max_length=255, choices=WORKFLOW_TYPE_CHOICES,
                            default=WORKFLOW_TYPE_CHOICES.WITHOUT_EVIDENCE_URL_WORKFLOW)

    def __str__(self):
        return str(self.name)


class Rater(models.Model):
    api_id = models.CharField(max_length=255, unique=True, blank=True, null=True)
    worker_id = models.CharField(max_length=255, unique=True, blank=True, null=True)
    rejected_state = models.BooleanField(default=False)
    completed_register_state = models.BooleanField(default=False)
    completed_demographics_state = models.BooleanField(default=False)
    completed_label = models.BooleanField(default=False)
    email = models.EmailField(unique=True, null=True, blank=True)
    age = models.CharField(max_length=255, blank=True, null=True)
    gender = models.CharField(max_length=255, blank=True, null=True)
    location = models.CharField(max_length=255, blank=True, null=True)
    workflow = models.ForeignKey('Workflow', null=True, on_delete=models.SET_NULL)

    def __str__(self):
        return '{} workflow:{}'.format(self.api_id, self.workflow)


class Item(models.Model):
    url = models.URLField()
    category = models.CharField(max_length=255, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)

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
    rater_answer_judgment_remove = models.BooleanField(blank=True, null=True)
    rater_answer_judgment_reduce = models.BooleanField(blank=True, null=True)
    rater_answer_judgment_inform = models.BooleanField(blank=True, null=True)
    judgment_additional_information = models.TextField(blank=True, null=True)
    rater_answer_predict_a = models.TextField(blank=True, null=True)
    rater_answer_predict_b = models.TextField(blank=True, null=True)
    rater_answer_predict_c = models.TextField(blank=True, null=True)
    evidence_url = models.URLField(null=True, blank=True)

    def __str__(self):
        return 'rater:{} item:{} workflow:{}'.format(self.rater, self.item, self.workflow)


class Assignment(models.Model):
    assignment_id = models.CharField(max_length=255, unique=True)
    hit_id = models.CharField(max_length=255)
    rater = models.ForeignKey(Rater, on_delete=models.SET_NULL, null=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return 'assignment:{} hit:{} rater:{}'.format(self.assignment_id, self.hit_id, self.rater)
