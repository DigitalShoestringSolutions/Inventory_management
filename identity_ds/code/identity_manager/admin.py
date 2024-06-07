from django.contrib import admin
from . import models
import datetime
import time

#def move_complete(modeladmin,request,queryset):
#    #determine timezone
#    __dt = -1 * (time.timezone if (time.localtime().tm_isdst == 0) else time.altzone)
#    tz = datetime.timezone(datetime.timedelta(seconds = __dt))
#    #generate timestamp with correct timezone
#    timestamp = datetime.datetime.now(tz=tz).isoformat()
#    queryset.update(location=Location.objects.get(name='Complete'),timestamp=timestamp)
#move_complete.short_description="Move to Complete"

@admin.register(models.IdentityType)
class IdentityTypeAdmin(admin.ModelAdmin):
    list_display = ['tag','title','individual']
    fields = ['auto_id','tag','title','individual']
    readonly_fields = ('auto_id',)

class IdentifierInline(admin.TabularInline):
    model = models.Identifier
    extra = 0

@admin.register(models.IdentityEntry)
class IdentityEntryAdmin(admin.ModelAdmin):
    list_display = ['name','type','parent','identifiers_summary']
    fields = ['auto_id','name','description','type','parent']
    inlines = [IdentifierInline]
    readonly_fields = ('auto_id',)
    list_filter = ['type']

    def identifiers_summary(self,obj):
        return ', '.join(str(idfr) for idfr in obj.identifiers.all())

@admin.register(models.IdentifierType)
class IdentifierTypeAdmin(admin.ModelAdmin):
    list_display = ['title','tag']
    fields = ['auto_id','title','tag']
    readonly_fields = ('auto_id',)

@admin.register(models.Identifier)
class IdentifierAdmin(admin.ModelAdmin):
    list_display = ['type','value','target']
    fields = ['auto_id','type','value','target']
    readonly_fields = ('auto_id',)
    list_filter = ['type']

@admin.register(models.IdentifierPattern)
class IdentifierAdmin(admin.ModelAdmin):
    list_display = ['pattern','identifier_type',"id_type",'label']
    fields = ['auto_id','label','identifier_type','id_type','pattern','defaults']
    readonly_fields = ('auto_id',)
    list_filter = ['identifier_type','id_type']

# @admin.register(models.ExtraField)
# class ExtraFieldAdmin(admin.ModelAdmin):
#     list_display = ['for_type','key']
#     fields = ['auto_id','for_type','key']
#     readonly_fields = ('auto_id',)
