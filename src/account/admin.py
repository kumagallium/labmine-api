from django.contrib import admin
from django.contrib.auth.models import Group
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .forms import UserChangeForm, UserCreationForm
from .models import User
from webapi.models import Post, Project, Library, Experiment, Type, Node, Datum, Property, Unit, Quantity, Figure, Metakey, Metadata, Blueprint, Template,Tag, Pin, Entity, Product,Definition, Item, Description, Image

class UserAdmin(BaseUserAdmin):
    form = UserChangeForm
    add_form = UserCreationForm

    list_display = ('email', 'username', 'is_admin')
    list_filter = ('is_admin',)
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('username',)}),
        ('Permissions', {'fields': ('is_admin',)}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'username', 'password1', 'password2')}
         ),
    )
    search_fields = ('email',)
    ordering = ('email',)
    filter_horizontal = ()


admin.site.register(User, UserAdmin)
admin.site.register(Post)
admin.site.register(Project)
admin.site.register(Experiment)
admin.site.register(Library)
admin.site.register(Type)
admin.site.register(Node)
admin.site.register(Datum)
admin.site.register(Property)
admin.site.register(Unit)
admin.site.register(Quantity)
admin.site.register(Figure)
admin.site.register(Metakey)
admin.site.register(Metadata)
admin.site.register(Blueprint)
admin.site.register(Template)
admin.site.register(Tag)
admin.site.register(Pin)
admin.site.register(Entity)
admin.site.register(Product)
admin.site.register(Definition)
admin.site.register(Item)
admin.site.register(Description)
admin.site.register(Image)
admin.site.unregister(Group)