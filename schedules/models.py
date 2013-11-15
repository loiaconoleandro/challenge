from django.db import models

#Locations classifier.
class Location(models.Model):
    short_name      = models.CharField(max_length=3)
    full_name       = models.CharField(max_length=60)
    
    def __unicode__(self):
        return self.short_name
    
    #return the location that matches @param="location" short_name
    def getLocation(self, location):
        return Location.objects.get(short_name = location)
    
    #adds the location @param="location" if it not exists already
    def addLocation(self, location_short, fullName):
        if not(self.locationExists(location_short)):
            loc = Location(short_name = location_short, full_name = fullName)
            loc.save()
        return self.getLocation(location_short)            
        
    def locationExists(self, location):
        return Location.objects.filter(short_name = location).exists()    

#Flight Bookings
class Booking(models.Model):
    booking_ref     = models.CharField(max_length=20)
    date_from       = models.DateTimeField ('date')
    location        = models.ForeignKey(Location)
    flight_details  = models.CharField(max_length=20)
    date_updated    = models.DateTimeField ('date updated')
    
    def __unicode__(self):  
        return self.booking_ref 
      
# Email Notifications
class Notify(models.Model):
    email           = models.CharField(max_length=60)
    booking         = models.ForeignKey(Booking)
    
    def __unicode__(self):  
        return self.email 