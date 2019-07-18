from django.contrib import admin
from .models import Item, Rater, Answer, ItemWorkflow, Workflow


admin.site.register(Item)
admin.site.register(Rater)
admin.site.register(Answer)
admin.site.register(ItemWorkflow)
admin.site.register(Workflow)

