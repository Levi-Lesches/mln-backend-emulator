"""
Config for displaying MLN's models in the django admin.
Most of the code here is for displaying various settings models inline with the model admin interface they correspond to, for example showing blueprint requirements for a blueprint item.
"""
from django.apps import apps
from django.contrib import admin
from django.db.models import Q

from ..models.dynamic import Attachment, Friendship, Message, Profile, InventoryStack
from ..models.module import Module, ModuleSaveConcertArcade, ModuleSaveSoundtrack, module_settings_classes
from ..models.module_settings_arcade import DeliveryArcadeTile
from ..models.static import Answer, ArcadePrize, BlueprintInfo, BlueprintRequirement, ItemInfo, ItemType, MessageBody, MessageTemplate, MessageTemplateAttachment, ModuleEditorType, ModuleExecutionCost, ModuleInfo, ModuleSetupCost, ModuleYieldInfo, NetworkerFriendshipCondition, NetworkerFriendshipConditionSource, NetworkerMessageTriggerLegacy, NetworkerMessageAttachmentLegacy, NetworkerReply, StartingStack, Question
from .make_inline import custom, inlines, make_inline

# Normal but customized admin interfaces

class ProfileAdmin(admin.ModelAdmin):
	list_display = "user", "rank", "is_networker"
	search_fields = "user__username",
	list_filter = "rank", "is_networker"

custom[Profile] = ProfileAdmin

class FriendshipAdmin(admin.ModelAdmin):
	list_display = "from_user", "to_user", "status"
	list_display_links = "from_user", "to_user"
	search_fields = "from_user__username", "to_user__username"
	list_filter = "status",

custom[Friendship] = FriendshipAdmin

has_trigger = lambda obj: NetworkerMessageTriggerLegacy.objects.filter(body=obj).exists() or NetworkerFriendshipCondition.objects.filter(Q(success_body=obj) | Q(failure_body=obj)).exists()
has_trigger.short_description = "has trigger"
has_trigger.boolean = True

class MessageBodyAdmin(admin.ModelAdmin):
	list_display = "subject", "text", has_trigger
	search_fields = "subject", "text"
	filter_vertical = "easy_replies",
	list_filter = "category",

custom[MessageBody] = MessageBodyAdmin

class DeliveryArcadeTileAdmin(admin.ModelAdmin):
	list_display = "module", "tile_id", "x", "y"

custom[DeliveryArcadeTile] = DeliveryArcadeTileAdmin

class StackAdmin(admin.ModelAdmin):
	list_display = "qty", "item"
	list_display_links = "item",
	search_fields = "item__name",
	list_filter = "item__type",

custom[StartingStack] = StackAdmin

class InventoryStackAdmin(StackAdmin):
	list_display = ("owner",) + StackAdmin.list_display
	search_fields = ("owner__username",) + StackAdmin.search_fields

custom[InventoryStack] = InventoryStackAdmin

# Inline display functions

def get_item_info_inlines(obj):
	if obj.type == ItemType.BLUEPRINT:
		yield BlueprintInfo
		yield BlueprintRequirement
	elif obj.type == ItemType.MODULE:
		yield ModuleInfo
		yield ModuleYieldInfo
		if obj.module_info.editor_type not in (ModuleEditorType.LOOP_SHOPPE, ModuleEditorType.NETWORKER_TRADE, ModuleEditorType.STICKER_SHOPPE, ModuleEditorType.TRADE):
			yield ModuleSetupCost
		if obj.module_info.is_executable:
			yield ModuleExecutionCost
		if obj.module_info.editor_type in (ModuleEditorType.CONCERT_I_ARCADE, ModuleEditorType.CONCERT_II_ARCADE, ModuleEditorType.DELIVERY_ARCADE, ModuleEditorType.DESTRUCTOID_ARCADE, ModuleEditorType.DR_INFERNO_ROBOT_SIM, ModuleEditorType.HOP_ARCADE):
			yield	ArcadePrize

def get_settings_inlines(obj):
	inlines = obj.get_settings_classes()
	if inlines == (ModuleSaveConcertArcade,):
		yield ModuleSaveConcertArcade
		yield ModuleSaveSoundtrack
	else:
		yield from inlines

# Misc inlines

make_inline(Question, Answer)

message_admin = make_inline(Message, Attachment)
message_admin.list_display = "sender", "recipient", "body", "is_read"
message_admin.list_display_links = "body",
message_admin.list_filter = "is_read",
message_admin.search_fields = "sender__username", "recipient__username", "body__subject", "body__text"

friend_cond_admin = make_inline(NetworkerFriendshipCondition, NetworkerFriendshipConditionSource)
friend_cond_admin.list_display = "networker", "condition", "success_body", "failure_body", "source"
friend_cond_admin.list_display_links = "networker",
friend_cond_admin.search_fields = "networker", "condition", "success_body__subject", "success_body__text", "failure_body__subject", "failure_body__text", "source__source"

trigger_admin_legacy = make_inline(NetworkerMessageTriggerLegacy, NetworkerMessageAttachmentLegacy)
trigger_admin_legacy.list_display = "networker", "body", "trigger", "source", "notes"
trigger_admin_legacy.list_display_links = "body",
trigger_admin_legacy.search_fields = "networker", "body__subject", "body__text", "trigger", "source", "notes"

message_template_admin = make_inline(MessageTemplate, MessageTemplateAttachment)
message_template_admin.list_display = "body",
message_template_admin.list_display_links = "body",
message_template_admin.search_fields = "body__subject", "body__text"

networker_reply_admin = make_inline(NetworkerReply, NetworkerMessageTriggerLegacy)
networker_reply_admin.networker = lambda _, reply: reply.template.networker
networker_reply_admin.networker.short_description = "Networker"
networker_reply_admin.trigger = lambda _, reply: reply.trigger_attachment or reply.trigger_body
networker_reply_admin.trigger.short_description = "Trigger"
networker_reply_admin.response = lambda _, reply: reply.template.body.subject
networker_reply_admin.response.short_description = "Response"
networker_reply_admin.attachment = lambda _, reply: next(iter(reply.template.attachments.all()), None)
networker_reply_admin.attachment.short_description = "Attachment"
networker_reply_admin.list_display = "networker", "trigger", "response", "attachment"
networker_reply_admin.list_display_links = "response",
networker_reply_admin.search_fields = "template__networker__username", "template__attachments__item__name",  "template__body__subject", "template__body__text", "message_attachment__name", "message_body__subject", "message_body__text"

# Item infos

item_info_admin = make_inline(ItemInfo, ModuleInfo, (ArcadePrize, {"fk_name": "module_item"}), (ModuleExecutionCost, {"fk_name": "module_item"}), (ModuleSetupCost, {"fk_name": "module_item"}), (ModuleYieldInfo, {"fk_name": "item"}), (BlueprintInfo, {"fk_name": "item"}), (BlueprintRequirement, {"fk_name": "blueprint_item"}), get_inlines=get_item_info_inlines)
item_info_admin.list_display = "name", "type"
item_info_admin.search_fields = "name",
item_info_admin.list_filter = "type",

# Modules & module settings

settings = set()
for classes in module_settings_classes.values():
	for cls in classes:
		settings.add(cls)

module_admin = make_inline(Module, *settings, get_inlines=get_settings_inlines)
module_admin.list_display = "owner", "item", "pos_x", "pos_y", "total_clicks"
module_admin.list_display_links = "item",
module_admin.search_fields = "owner__username", "item__name"

# Register admin interfaces

for model in apps.get_app_config("mln").get_models():
	if model in custom:
		admin.site.register(model, custom[model])
	elif model not in inlines:
		admin.site.register(model)
