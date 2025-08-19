from nautobot.apps.choices import CustomFieldTypeChoices


def create_custom_field(sender, apps, **kwargs):
    CustomField = apps.get_model("extras", "CustomField")
    ContentType = apps.get_model("contenttypes", "ContentType")
    Tag = apps.get_model("extras", "Tag")
    tag_content_type = ContentType.objects.get_for_model(Tag)
    device_specific_field, _ = CustomField.objects.update_or_create(
        key="device_specific",
        defaults={
            "label": "device specific",
            "key": "device_specific",
            "type": CustomFieldTypeChoices.TYPE_BOOLEAN,
            "description": "created by nautobot-move",
        },
    )
    device_specific_field.content_types.set([tag_content_type])
    device_specific_field.save()
