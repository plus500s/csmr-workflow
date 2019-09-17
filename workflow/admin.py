from django.contrib import admin
from .models import Item, Rater, Answer, ItemWorkflow, Workflow


@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):

    list_display = ('pk', 'url', 'is_active', 'created_at')


admin.site.register(Rater)
admin.site.register(Answer)
admin.site.register(ItemWorkflow)
admin.site.register(Workflow)
