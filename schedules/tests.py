from django.utils import timezone
from django.test import TestCase
from django.conf import settings
from schedules.models import Notify, Booking, Location
from schedules import views
from django.core.urlresolvers import reverse
import datetime

class BookingMethodTests(TestCase):
    def test_booking_update_date_in_past(self):
        """
        if the new arrival date of a flight is in the past, 
        then the booking should not be updated, and no notifications should be sent        
        """
        now = timezone.now()
        pastDate = timezone.now() + datetime.timedelta(days=-1)
        
        getNewBooking('ref', now, 'details', timezone.now())
        
        #Send an update request with a date 10 days in the past
        response = self.client.post(
            reverse('schedules:check_flight', args=()), 
            {u'update-flight': pastDate.strftime('%d/%m/%Y %H:%M'), u'bookings-select': 1, u'actions': u'update'}
        )
        
        self.assertEqual(response.context['result'], settings.BOOKING_UPDATE_DATE_PAST)
        
    def test_booking_update_wrong_booking_id(self):
        #the DB is empty so I create one booking that should have ID = 1
        getNewBooking('ref', timezone.now(), 'details', timezone.now())
        
        response = self.client.post(
            reverse('schedules:check_flight', args=()), 
            {u'update-flight': u'15/11/2013 16:00', u'bookings-select': 2, u'actions': u'update'}
        )
        
        self.assertEqual(response.context['result'], settings.BOOKING_NOT_FOUND)
    
    def test_booking_update_with_no_notifications(self):
        pass

class NotifyMethodTests(TestCase):

    def test_notify_recipients_limit(self):
        """
        regardless how many email notifications are registered for one booking, only those
        within the settings.EMAIL_MAX_RECIPIENTS limit should be notified, 
        after all it's just a gmail account        
        """
        notificationList = list()
        
        i= 0
        
        while i <= settings.EMAIL_MAX_RECIPIENTS + 1:
            notificationList.append(
                Notify(
                    email = 'testemail' + str(i) + '@ofs.com', 
                    booking = getNewBooking('ref', timezone.now(), 'details', timezone.now())
                )
            )
            i += 1
        
        self.assertEqual(settings.EMAIL_MAX_RECIPIENTS, views.send_notification(notificationList))
        
def getNewBooking(bookingRef, dateFrom, flightDetails, dateUpdated):
    return Booking.objects.get_or_create(
        booking_ref = bookingRef,
        date_from = dateFrom,
        location = getNewLocation('LON', 'London'),
        flight_details = flightDetails,
        date_updated = dateUpdated
    )[0] 

def getNewLocation(shortName, fullName):
    return Location.objects.get_or_create(short_name = shortName, full_name = fullName)[0]