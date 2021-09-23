# Generated by Django 3.2.7 on 2021-09-20 03:23

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion

def migrate_NFC_to_NFT(apps, schema_editor): 
	# Split each NetworkerFriendshipCondition into 2 NetworkerFriendTriggers
	NetworkerFriendshipCondition = apps.get_model("mln", "NetworkerFriendshipCondition")
	_Source = apps.get_model("mln", "NetworkerFriendshipConditionSource")
	NetworkerFriendTrigger = apps.get_model("mln", "NetworkerFriendTrigger")
	MessageTemplate = apps.get_model("mln", "MessageTemplate")
	for condition in NetworkerFriendshipCondition.objects.all(): 
		# Success message
		message_success = MessageTemplate.objects.create(
			networker=condition.networker,
			body=condition.success_body,
			source=condition.source.source,
		)
		NetworkerFriendTrigger.objects.create(
			messagetemplate_ptr=message_success,
			required_item=condition.condition,
			accept=True,
		)
		# Failure message
		message_failure = MessageTemplate.objects.create(
			networker=condition.networker,
			body=condition.failure_body,
			source=condition.source.source,
		)
		NetworkerFriendTrigger.objects.create(
			messagetemplate_ptr=message_failure,
			required_item=None,
			accept=False,
		)

class Migration(migrations.Migration):
	dependencies = [
		('mln', '0023_message_template'),
	]

	operations = [
		# 1. Create NetworkerFriendTrigger
		# 2. Migrate NetworkerFriendshipConditions to NetworkerFriendTriggers
		# 3. Delete NetworkerFriendshipConditions and -Sources

		# Step 1. Create NetworkerFriendTrigger
		migrations.CreateModel(
			name="NetworkerFriendTrigger",
			fields=[
				("required_item", models.ForeignKey(related_name="+", on_delete=models.CASCADE, blank=True, null=True, to='mln.ItemInfo')),
				("accept", models.BooleanField(default=True)),
				("messagetemplate_ptr", models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='mln.messagetemplate')),
			]
		),

		# Step 2. Migrate all NetworkerFriendshipConditions to NetworkerFriendTrigger
		migrations.RunPython(migrate_NFC_to_NFT, reverse_code=migrations.RunPython.noop),

		# Step 2. Delete NetworkerFriendshipCondition and NetworkerFriendshipSource
		migrations.DeleteModel("NetworkerFriendshipCondition"),
		migrations.DeleteModel("NetworkerFriendshipConditionSource"),
	]
