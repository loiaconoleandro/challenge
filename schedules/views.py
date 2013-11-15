import json
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.views import generic
from django.utils import timezone
from datetime import datetime
from schedules.models import Booking, Location, Notify
from django.conf import settings
from django.core.mail import send_mail


class IndexView(generic.ListView):
    template_name = 'schedules/index.html'
    context_object_name = 'booking_list'

    def get_queryset(self):
        """
        Return flights, except those in the past.
        """
                   
        return Booking.objects.filter(
              date_from__gte=timezone.now()
          ).order_by('date_from')

#Updates Booking arrival date or displays the current flight status
def check_flight(request):
    try:
        bookingUpdate = Booking.objects.get(id = request.POST['bookings-select'])
    except Booking.DoesNotExist:
        return render(request, 'schedules/error.html', {
            'result' : settings.BOOKING_NOT_FOUND
        })
            
    #update flight arrival date
    if(request.POST['actions'] == 'update'):
        date = datetime.strptime(request.POST['update-flight'], '%d/%m/%Y %H:%M')

        if (datetime.now() - date).days >= 1:
            return render(request, 'schedules/error.html', {
                'result' : settings.BOOKING_UPDATE_DATE_PAST
                })
        
        bookingUpdate.date_updated = datetime.strptime(request.POST['update-flight'], '%d/%m/%Y %H:%M')
        bookingUpdate.save()

        notifications = Notify.objects.filter(booking = bookingUpdate.id)
       
        #if someone has suscribed for a notification, then send emails
        if(len(notifications) > 0):
            send_notification(notifications)
            
        return HttpResponseRedirect(reverse('schedules:index', kwargs={}))
    else:
        return render(request, 'schedules/check_flight.html', {
            'booking': bookingUpdate
        })

#sends notification to 1+ recipients
def send_notification(notifications):
    to = []

    for i, notification in enumerate(notifications):
        if(i < settings.EMAIL_MAX_RECIPIENTS):
            to.append(notification.email)
        else:
            break
        
    message = settings.EMAIL_NOTIFICATION_BODY % {
        'booking_ref': notifications[0].booking.booking_ref,
        'location': notifications[0].booking.location,
        'date_updated': notifications[0].booking.date_updated.strftime('%Y/%b/%d %H:%M')
    }
    
    try:
        #send_mass_mail() would be more effective in a production environment
        send_mail(
            'OFS FL', 
            message, 
            'ofsnotification@gmail.com', 
            to
        )
    except:
        to = []
    
    return len(to)

#show notification form       
def notify(request):
    return render(request, 'schedules/notify.html', {
         'booking_list': Booking.objects.filter(
              date_from__gte=timezone.now()
          ).order_by('date_from')
    })
    
#creates notifications for 1 booking and 1+ emails
def add_notification(request):
    if not request.POST['emails'] or not request.POST['bookings']:
        notify(request)
    else:
        bookingTemp = request.POST['bookings'].split(' - ')[0]
        bookingTemp = Booking.objects.get(booking_ref = bookingTemp)
        
        #remove duplicate entries
        emails = list(set(request.POST['emails'].split(',')))
        
        #Use get_or_create to avoid adding an existing (booking,email) tuple
        for emailTemp in emails:
            Notify.objects.get_or_create(
                email = emailTemp,
                booking = bookingTemp
            )
    
    return render(request, 'schedules/index.html', {
        'booking_list' : Booking.objects.filter(
            date_from__gte=timezone.now()
        ).order_by('date_from')
    }) 



#Load Flight Details into DB form JSON file
def load_data_to_db(request):
    try:
        json_data = open('schedules/data/FlightDetails.json')
    
        #clear both tables first
        Booking.objects.all().delete()
        Location.objects.all().delete()
        
        data = json.load(json_data)
        json_data.close()
        
        bookingsBulk = list()
        
        for booking in data['ofsplatform']['booking_service']['bookings'] :
            
            locationEntity = Location.addLocation(Location(), booking['location'], booking['location'])
            
            #to speed things up, I add the bookings to a list, and later use bulk_create()
            bookingsBulk.append(
                Booking(
                   booking_ref = booking['booking_ref'],
                   date_from = booking['date_from'],
                   location = locationEntity,
                   flight_details = booking['flight_details']
                   )                
                )
    
        Booking.objects.bulk_create(bookingsBulk)    
        
        return render(request, 'schedules/bookings_imported.html', {
            'result' : settings.BOOKING_IMPORTED_OK
        })
    except:
        return render(request, 'schedules/error.html', {
            'result' : settings.BOOKING_IMPORT_FILE_ERROR
        })        