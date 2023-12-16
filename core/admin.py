from django.contrib import admin


class BaseAdmin(admin.ModelAdmin):
    def save_model(self, request, obj, form, change):
        if obj.id:
            obj.modified_by = request.user
        else:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

    readonly_fields = (
        "created_by", "created_date", "modified_date")
