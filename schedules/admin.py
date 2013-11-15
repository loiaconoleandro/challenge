from django.contrib import admin
from schedules.models import Booking, Location, Notify

class BookingAdmin(admin.ModelAdmin):
    list_display = ('booking_ref', 'date_from', 'location', 'flight_details', 'date_updated')
    search_fields = ['booking_ref']

class LocationAdmin(admin.ModelAdmin):
    list_display = ('short_name', 'full_name')
    search_fields = ['short_name']

class NotifyAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {'fields': ['email']}),
        ('Flight', {'fields': ['booking']})
    ]
    list_display = ('email', 'booking')
    search_fields = ['email']
    
    
admin.site.register(Booking, BookingAdmin)
admin.site.register(Location, LocationAdmin)
admin.site.register(Notify, NotifyAdmin)