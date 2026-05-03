package com.tulika.eventbooking.eventservice;

import com.tulika.eventbooking.eventservice.dto.EventRequest;
import com.tulika.eventbooking.eventservice.dto.EventResponse;
import com.tulika.eventbooking.eventservice.model.Booking;
import com.tulika.eventbooking.eventservice.model.Event;
import com.tulika.eventbooking.eventservice.repository.BookingRepository;
import com.tulika.eventbooking.eventservice.repository.EventRepository;
import com.tulika.eventbooking.eventservice.service.EventService;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

import java.time.LocalDateTime;
import java.util.List;
import java.util.Optional;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.ArgumentMatchers.*;
import static org.mockito.Mockito.*;

@ExtendWith(MockitoExtension.class)
class EventServiceTest {

    @Mock
    private EventRepository eventRepository;

    @Mock
    private BookingRepository bookingRepository;

    @InjectMocks
    private EventService eventService;

    private Event testEvent;
    private EventRequest eventRequest;

    @BeforeEach
    void setUp() {
        testEvent = new Event();
        testEvent.setId(1L);
        testEvent.setName("Tech Summit 2027");
        testEvent.setDescription("Annual tech conference");
        testEvent.setEventDate(LocalDateTime.now().plusDays(30));
        testEvent.setVenue("Bangalore Convention Center");
        testEvent.setTicketPrice(999.0);
        testEvent.setTotalSeats(200);
        testEvent.setAvailableSeats(200);
        testEvent.setMaxTicketsPerUser(2);
        testEvent.setStatus(Event.EventStatus.ACTIVE);
        testEvent.setOrganizerEmail("organizer@test.com");
        testEvent.setCreatedAt(LocalDateTime.now());

        // use Lombok setters directly — this is the correct approach
        eventRequest = new EventRequest();
        eventRequest.setName("Tech Summit 2027");
        eventRequest.setDescription("Annual tech conference");
        eventRequest.setVenue("Bangalore Convention Center");
        eventRequest.setEventDate(LocalDateTime.now().plusDays(30));
        eventRequest.setTicketPrice(999.0);
        eventRequest.setTotalSeats(200);
        eventRequest.setMaxTicketsPerUser(2);
    }

    // ─── CREATE EVENT ─────────────────────────────────────────────

    @Test
    void createEvent_Success() {
        when(eventRepository.save(any(Event.class))).thenReturn(testEvent);

        EventResponse response = eventService.createEvent(
                eventRequest, "organizer@test.com");

        assertNotNull(response);
        assertEquals("Tech Summit 2027", response.getName());
        assertEquals("organizer@test.com", response.getOrganizerEmail());
        verify(eventRepository, times(1)).save(any(Event.class));
    }

    // ─── GET EVENT BY ID ──────────────────────────────────────────

    @Test
    void getEventById_Success() {
        when(eventRepository.findById(1L)).thenReturn(Optional.of(testEvent));

        EventResponse response = eventService.getEventById(1L);

        assertNotNull(response);
        assertEquals(1L, response.getId());
        assertEquals("Tech Summit 2027", response.getName());
    }

    @Test
    void getEventById_NotFound_ThrowsException() {
        when(eventRepository.findById(anyLong())).thenReturn(Optional.empty());

        RuntimeException exception = assertThrows(RuntimeException.class,
                () -> eventService.getEventById(999L));

        assertTrue(exception.getMessage().contains("Event not found with id: 999"));
    }

    // ─── GET UPCOMING EVENTS ──────────────────────────────────────

    @Test
    void getUpcomingEvents_ReturnsOnlyFutureActiveEvents() {
        when(eventRepository.findByStatusAndEventDateAfter(
                eq(Event.EventStatus.ACTIVE), any(LocalDateTime.class)))
                .thenReturn(List.of(testEvent));

        List<EventResponse> result = eventService.getUpcomingEvents();

        assertEquals(1, result.size());
        assertEquals("ACTIVE", result.get(0).getStatus());
    }

    // ─── GET ORGANIZER EVENTS ─────────────────────────────────────

    @Test
    void getOrganizerEvents_ReturnsOnlyThatOrganizersEvents() {
        when(eventRepository.findByOrganizerEmail("organizer@test.com"))
                .thenReturn(List.of(testEvent));

        List<EventResponse> result = eventService.getOrganizerEvents(
                "organizer@test.com");

        assertEquals(1, result.size());
        assertEquals("organizer@test.com", result.get(0).getOrganizerEmail());
        verify(eventRepository).findByOrganizerEmail("organizer@test.com");
    }

    // ─── UPDATE EVENT ─────────────────────────────────────────────

    @Test
    void updateEvent_Success() {
        when(eventRepository.findById(anyLong())).thenReturn(Optional.of(testEvent));
        when(eventRepository.save(any(Event.class))).thenReturn(testEvent);

        EventResponse response = eventService.updateEvent(
                1L, eventRequest, "organizer@test.com");

        assertNotNull(response);
        verify(eventRepository, times(1)).save(any(Event.class));
    }

    @Test
    void updateEvent_Within4Hours_ThrowsException() {
        testEvent.setEventDate(LocalDateTime.now().plusHours(2));
        when(eventRepository.findById(anyLong())).thenReturn(Optional.of(testEvent));

        RuntimeException exception = assertThrows(RuntimeException.class,
                () -> eventService.updateEvent(
                        1L, eventRequest, "organizer@test.com"));

        assertEquals("Cannot update event within 4 hours of start time",
                exception.getMessage());
        verify(eventRepository, never()).save(any());
    }

    @Test
    void updateEvent_WrongOrganizer_ThrowsException() {
        when(eventRepository.findById(anyLong())).thenReturn(Optional.of(testEvent));

        RuntimeException exception = assertThrows(RuntimeException.class,
                () -> eventService.updateEvent(
                        1L, eventRequest, "other@test.com"));

        assertEquals("You are not authorized to update this event",
                exception.getMessage());
        verify(eventRepository, never()).save(any());
    }

    @Test
    void updateEvent_CancelledEvent_ThrowsException() {
        testEvent.setStatus(Event.EventStatus.CANCELLED);
        when(eventRepository.findById(anyLong())).thenReturn(Optional.of(testEvent));

        RuntimeException exception = assertThrows(RuntimeException.class,
                () -> eventService.updateEvent(
                        1L, eventRequest, "organizer@test.com"));

        assertEquals("Cannot update a cancelled event", exception.getMessage());
    }

    // ─── UPDATE CAPACITY ──────────────────────────────────────────

    @Test
    void updateCapacity_Increase_RecalculatesAvailableSeats() {
        testEvent.setTotalSeats(200);
        testEvent.setAvailableSeats(200);
        when(eventRepository.findById(anyLong())).thenReturn(Optional.of(testEvent));
        when(eventRepository.save(any(Event.class))).thenReturn(testEvent);

        EventResponse response = eventService.updateCapacity(
                1L, 300, "organizer@test.com");

        assertNotNull(response);
        verify(eventRepository, times(1)).save(any(Event.class));
    }

    @Test
    void updateCapacity_BelowBookedSeats_ThrowsException() {
        testEvent.setTotalSeats(200);
        testEvent.setAvailableSeats(150);
        when(eventRepository.findById(anyLong())).thenReturn(Optional.of(testEvent));

        RuntimeException exception = assertThrows(RuntimeException.class,
                () -> eventService.updateCapacity(1L, 30, "organizer@test.com"));

        assertTrue(exception.getMessage().contains(
                "Cannot reduce capacity below already booked seats"));
        verify(eventRepository, never()).save(any());
    }

    @Test
    void updateCapacity_WrongOrganizer_ThrowsException() {
        when(eventRepository.findById(anyLong())).thenReturn(Optional.of(testEvent));

        RuntimeException exception = assertThrows(RuntimeException.class,
                () -> eventService.updateCapacity(1L, 300, "other@test.com"));

        assertEquals("You are not authorized to manage this event",
                exception.getMessage());
    }

    // ─── CANCEL EVENT ─────────────────────────────────────────────

    @Test
    void cancelEvent_Success_CascadesToBookings() {
        Booking booking1 = new Booking();
        booking1.setStatus(Booking.BookingStatus.CONFIRMED);
        booking1.setEvent(testEvent);
        booking1.setTicketsBooked(2);

        Booking booking2 = new Booking();
        booking2.setStatus(Booking.BookingStatus.CONFIRMED);
        booking2.setEvent(testEvent);
        booking2.setTicketsBooked(1);

        when(eventRepository.findById(anyLong()))
                .thenReturn(Optional.of(testEvent));
        when(bookingRepository.findByEventId(anyLong()))
                .thenReturn(List.of(booking1, booking2));
        when(eventRepository.save(any(Event.class))).thenReturn(testEvent);

        EventResponse response = eventService.cancelEvent(
                1L, "organizer@test.com");

        assertNotNull(response);
        assertEquals(Booking.BookingStatus.CANCELLED_BY_ORGANIZER,
                booking1.getStatus());
        assertEquals(Booking.BookingStatus.CANCELLED_BY_ORGANIZER,
                booking2.getStatus());
        verify(bookingRepository, times(1)).saveAll(anyList());
        verify(eventRepository, times(1)).save(any(Event.class));
    }

    @Test
    void cancelEvent_AlreadyCancelled_ThrowsException() {
        testEvent.setStatus(Event.EventStatus.CANCELLED);
        when(eventRepository.findById(anyLong()))
                .thenReturn(Optional.of(testEvent));

        RuntimeException exception = assertThrows(RuntimeException.class,
                () -> eventService.cancelEvent(1L, "organizer@test.com"));

        assertEquals("Event is already cancelled", exception.getMessage());
        verify(bookingRepository, never()).saveAll(any());
    }

    @Test
    void cancelEvent_WrongOrganizer_ThrowsException() {
        when(eventRepository.findById(anyLong()))
                .thenReturn(Optional.of(testEvent));

        RuntimeException exception = assertThrows(RuntimeException.class,
                () -> eventService.cancelEvent(1L, "wrongorganizer@test.com"));

        assertEquals("You are not authorized to cancel this event",
                exception.getMessage());
    }
}