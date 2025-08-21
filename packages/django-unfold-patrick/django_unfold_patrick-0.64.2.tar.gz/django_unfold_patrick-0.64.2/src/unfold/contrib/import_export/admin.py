from datetime import date, datetime

from django.contrib.admin.models import ADDITION, CHANGE, DELETION, LogEntry
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import PermissionDenied
from django.template.response import TemplateResponse
from django.utils.decorators import method_decorator
from django.utils.timezone import localtime
from django.utils.translation import gettext_lazy as _
from django.views.decorators.http import require_POST

from import_export.admin import ImportMixin as BaseImportMixin
from import_export.results import RowResult

import json


class CustomImportMixin(BaseImportMixin):
    @method_decorator(require_POST)
    def process_import(self, request, **kwargs):
        """
        Perform the actual import action (after the user has confirmed the import)
        """
        if not self.has_import_permission(request):
            raise PermissionDenied

        confirm_form = self.create_confirm_form(request)
        if confirm_form.is_valid():
            import_formats = self.get_import_formats()
            input_format = import_formats[int(confirm_form.cleaned_data["format"])](
                encoding=self.from_encoding
            )
            encoding = None if input_format.is_binary() else self.from_encoding
            tmp_storage_cls = self.get_tmp_storage_class()
            tmp_storage = tmp_storage_cls(
                name=confirm_form.cleaned_data["import_file_name"],
                encoding=encoding,
                read_mode=input_format.get_read_mode(),
                **self.get_tmp_storage_class_kwargs(),
            )

            data = tmp_storage.read()
            dataset = input_format.create_dataset(data)

            # Store original values before import
            original_objects = {}
            res_kwargs = self.get_import_resource_kwargs(request=request, form=confirm_form, **kwargs)
            resource = self.choose_import_resource_class(confirm_form, request)(**res_kwargs)
            
            # Get a preview of the changes without committing
            dry_run_result = resource.import_data(
                dataset,
                dry_run=True,
                file_name=confirm_form.cleaned_data.get("original_file_name"),
                user=request.user,
            )
            
            # Save original values of objects that will be updated
            for row in dry_run_result.rows:
                if row.import_type == row.IMPORT_TYPE_UPDATE and row.object_id:
                    try:
                        obj = self.model.objects.get(pk=row.object_id)
                        # Store a copy of original values
                        original_values = {}
                        for field in self.model._meta.fields:
                            original_values[field.name] = getattr(obj, field.name)
                        original_objects[obj.pk] = original_values
                    except self.model.DoesNotExist:
                        pass
                    
            result = self.process_dataset(dataset, confirm_form, request, **kwargs)

            result.original_objects = original_objects

            tmp_storage.remove()

            return self.process_result(result, request)
        else:
            context = self.admin_site.each_context(request)
            context.update(
                {
                    "title": _("Import"),
                    "confirm_form": confirm_form,
                    "opts": self.model._meta,
                    "errors": confirm_form.errors,
                }
            )
            return TemplateResponse(request, [self.import_template_name], context)
        
    def _log_actions(self, result, request):
        """
        Create appropriate LogEntry instances for the result.
        """
        rows = {}
        for row in result:
            rows.setdefault(row.import_type, [])
            rows[row.import_type].append(row.instance)

        # Pass original_objects directly from result
        original_objects = getattr(result, 'original_objects', {})
        self._create_log_entries(request.user.pk, rows, original_objects)

    def _create_log_entries(self, user_pk, rows, original_objects):
        logentry_map = {
            RowResult.IMPORT_TYPE_NEW: ADDITION,
            RowResult.IMPORT_TYPE_UPDATE: CHANGE,
            RowResult.IMPORT_TYPE_DELETE: DELETION,
        }
        content_type = ContentType.objects.get_for_model(self.model)

        for import_type, instances in rows.items():
            if import_type in logentry_map:
                action_flag = logentry_map[import_type]
                for instance in instances:
                    # Reset change_message for each instance
                    change_message = ""
                    
                    # Use the stored original values for comparison
                    if import_type == RowResult.IMPORT_TYPE_UPDATE and hasattr(instance, 'pk') and instance.pk in original_objects:
                        original_values = original_objects[instance.pk]
                        
                        # Compare and find changes
                        changed_fields = []
                        for field in self.model._meta.fields:
                            field_name = field.name
                            if field_name in original_values:
                                original_value = original_values[field_name]
                                new_value = getattr(instance, field_name)

                                # Apply localtime for date/datetime fields
                                if isinstance(original_value, datetime):
                                    original_value = localtime(original_value).strftime('%Y-%m-%d %H:%M:%S')
                                if isinstance(new_value, datetime):
                                    new_value = localtime(new_value).strftime('%Y-%m-%d %H:%M:%S')
                                
                                # Format date objects for better display
                                if isinstance(original_value, date):
                                    original_value = original_value.strftime('%Y-%m-%d')
                                if isinstance(new_value, date):
                                    new_value = new_value.strftime('%Y-%m-%d')

                                if original_value != new_value:
                                    changed_fields.append(
                                        f"[{field.verbose_name}] \"{original_value}\" => \"{new_value}\""
                                    )
                        if changed_fields:
                            change_message = '[{"import_changed": {"fields": ' + json.dumps(changed_fields) + '}}]'
                    elif import_type == RowResult.IMPORT_TYPE_NEW:
                        change_message = '[{"added": {}}]'
                    elif import_type == RowResult.IMPORT_TYPE_DELETE:
                        change_message = '[{"deleted": {}}]'
                    else:
                        change_message = _("{} via custom import_export".format(import_type))

                    # Create log entry for EACH instance
                    LogEntry.objects.log_action(
                        user_id=user_pk,
                        content_type_id=content_type.pk,
                        object_id=instance.pk,
                        object_repr=str(instance),
                        action_flag=action_flag,
                        change_message=change_message,
                    )