package com.tulika.eventbooking.eventservice;

import com.tulika.eventbooking.eventservice.dto.BookingRequest;
import com.tulika.eventbooking.eventservice.dto.BookingResponse;
import com.tulika.eventbooking.eventservice.model.Booking;
import com.tulika.eventbooking.eventservice.model.Event;
import com.tulika.eventbooking.eventservice.repository.BookingRepository;
import com.tulika.eventbooking.eventservice.repository.EventRepository;
import com.tulika.eventbooking.eventservice.service.BookingService;
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
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.ArgumentMatchers.anyLong;
import static org.mockito.ArgumentMatchers.anyString;
import static org.mockito.Mockito.*;

@ExtendWith(MockitoExtension.class)
class BookingServiceTest {

    @Mock
    private BookingRepository bookingRepository;

    @Mock
    private EventRepository eventRepository;

    @InjectMocks
    private BookingService bookingService;

    private Event testEvent;
    private Booking testBooking;
    private BookingRequest bookingRequest;

    @BeforeEach
    void setUp() {
        testEvent = new Event();
        testEvent.setId(1L);
        testEvent.setName("Test Event");
        testEvent.setVenue("Test Venue");
        testEvent.setEventDate(LocalDateTime.now().plusDays(10));
        testEvent.setTicketPrice(500.0);
        testEvent.setTotalSeats(100);
        testEvent.setAvailableSeats(100);
        testEvent.setMaxTicketsPerUser(2);
        testEvent.setStatus(Event.EventStatus.ACTIVE);
        testEvent.setOrganizerEmail("organizer@test.com");

        testBooking = new Booking();
        testBooking.setId(1L);
        testBooking.setEvent(testEvent);
        testBooking.setCustomerEmail("customer@test.com");
        testBooking.setCustomerName("customer@test.com");
        testBooking.setTicketsBooked(2);
        testBooking.setTotalAmount(1000.0);
        testBooking.setStatus(Booking.BookingStatus.CONFIRMED);
        testBooking.setBookedAt(LocalDateTime.now());

        bookingRequest = new BookingRequest();
        bookingRequest.setEventId(1L);
        bookingRequest.setTicketsRequested(2);
    }

    @Test
    void bookTickets_Success() {
        when(eventRepository.findById(anyLong())).thenReturn(Optional.of(testEvent));
        when(bookingRepository.findByEventIdAndCustomerEmailAndStatus(
                anyLong(), anyString(), any())).thenReturn(Optional.empty());
        when(bookingRepository.findByEventIdAndCustomerEmailAndStatusNot(
                anyLong(), anyString(), any())).thenReturn(List.of());
        when(eventRepository.save(any(Event.class))).thenReturn(testEvent);
        when(bookingRepository.save(any(Booking.class))).thenReturn(testBooking);

        BookingResponse response = bookingService.bookTickets(
                bookingRequest, "customer@test.com");

        assertNotNull(response);
        assertEquals(2, response.getTicketsBooked());
        assertEquals(1000.0, response.getTotalAmount());
        verify(eventRepository, times(1)).save(any(Event.class));
        verify(bookingRepository, times(1)).save(any(Booking.class));
    }

    @Test
    void bookTickets_EventNotFound_ThrowsException() {
        when(eventRepository.findById(anyLong())).thenReturn(Optional.empty());

        RuntimeException exception = assertThrows(RuntimeException.class,
                () -> bookingService.bookTickets(bookingRequest, "customer@test.com"));

        assertEquals("Event not found", exception.getMessage());
    }

    @Test
    void bookTickets_EventCancelled_ThrowsException() {
        testEvent.setStatus(Event.EventStatus.CANCELLED);
        when(eventRepository.findById(anyLong())).thenReturn(Optional.of(testEvent));

        RuntimeException exception = assertThrows(RuntimeException.class,
                () -> bookingService.bookTickets(bookingRequest, "customer@test.com"));

        assertEquals("This event has been cancelled", exception.getMessage());
    }

    @Test
    void bookTickets_NotEnoughSeats_ThrowsException() {
        testEvent.setAvailableSeats(1);
        bookingRequest.setTicketsRequested(2);
        when(eventRepository.findById(anyLong())).thenReturn(Optional.of(testEvent));
        when(bookingRepository.findByEventIdAndCustomerEmailAndStatus(
                anyLong(), anyString(), any())).thenReturn(Optional.empty());
        when(bookingRepository.findByEventIdAndCustomerEmailAndStatusNot(
                anyLong(), anyString(), any())).thenReturn(List.of());

        RuntimeException exception = assertThrows(RuntimeException.class,
                () -> bookingService.bookTickets(bookingRequest, "customer@test.com"));

        assertTrue(exception.getMessage().contains("Not enough seats"));
    }

    @Test
    void bookTickets_AlreadyBooked_ThrowsException() {
        when(eventRepository.findById(anyLong())).thenReturn(Optional.of(testEvent));
        when(bookingRepository.findByEventIdAndCustomerEmailAndStatus(
                anyLong(), anyString(), any())).thenReturn(Optional.of(testBooking));

        RuntimeException exception = assertThrows(RuntimeException.class,
                () -> bookingService.bookTickets(bookingRequest, "customer@test.com"));

        assertEquals("You already have an active booking for this event",
                exception.getMessage());
    }

    @Test
    void cancelBooking_Success() {
        when(bookingRepository.findById(anyLong())).thenReturn(Optional.of(testBooking));
        when(eventRepository.save(any(Event.class))).thenReturn(testEvent);
        when(bookingRepository.save(any(Booking.class))).thenReturn(testBooking);

        BookingResponse response = bookingService.cancelBooking(1L, "customer@test.com");

        assertNotNull(response);
        assertEquals(Booking.BookingStatus.CANCELLED.name(), response.getStatus());
        verify(bookingRepository, times(1)).save(any(Booking.class));
    }

    @Test
    void cancelBooking_WrongCustomer_ThrowsException() {
        when(bookingRepository.findById(anyLong())).thenReturn(Optional.of(testBooking));

        RuntimeException exception = assertThrows(RuntimeException.class,
                () -> bookingService.cancelBooking(1L, "wrong@test.com"));

        assertEquals("You are not authorized to cancel this booking",
                exception.getMessage());
    }

    @Test
    void cancelBooking_AlreadyCancelled_ThrowsException() {
        testBooking.setStatus(Booking.BookingStatus.CANCELLED);
        when(bookingRepository.findById(anyLong())).thenReturn(Optional.of(testBooking));

        RuntimeException exception = assertThrows(RuntimeException.class,
                () -> bookingService.cancelBooking(1L, "customer@test.com"));

        assertEquals("This booking is already cancelled", exception.getMessage());
    }
}