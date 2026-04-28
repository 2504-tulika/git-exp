package com.tulika.eventbooking.eventservice.service;

import com.tulika.eventbooking.eventservice.dto.BookingRequest;
import com.tulika.eventbooking.eventservice.dto.BookingResponse;
import com.tulika.eventbooking.eventservice.model.Booking;
import com.tulika.eventbooking.eventservice.model.Event;
import com.tulika.eventbooking.eventservice.repository.BookingRepository;
import com.tulika.eventbooking.eventservice.repository.EventRepository;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDateTime;
import java.util.List;
import java.util.stream.Collectors;

@Service
public class BookingService {

    private static final Logger logger = LoggerFactory.getLogger(BookingService.class);

    private final BookingRepository bookingRepository;
    private final EventRepository eventRepository;

    public BookingService(BookingRepository bookingRepository,
                          EventRepository eventRepository) {
        this.bookingRepository = bookingRepository;
        this.eventRepository = eventRepository;
    }

    // @Transactional ensures the seat count update and booking save
    // happen together — if anything fails, both are rolled back
    // this prevents overbooking when two users book at the same time
    @Transactional
    public BookingResponse bookTickets(BookingRequest request, String customerEmail) {

        // lock the event row in DB during this transaction
        Event event = eventRepository.findById(request.getEventId())
                .orElseThrow(() -> new RuntimeException("Event not found"));

        // cannot book cancelled events
        if (event.getStatus() == Event.EventStatus.CANCELLED) {
            throw new RuntimeException("This event has been cancelled");
        }

        // cannot book past events
        if (event.getEventDate().isBefore(LocalDateTime.now())) {
            throw new RuntimeException("Cannot book tickets for past events");
        }

        // check if customer already has an active booking for this event
        boolean alreadyBooked = bookingRepository
                .findByEventIdAndCustomerEmailAndStatus(
                        event.getId(),
                        customerEmail,
                        Booking.BookingStatus.CONFIRMED)
                .isPresent();

        if (alreadyBooked) {
            throw new RuntimeException("You already have an active booking for this event");
        }

        // check max tickets per user limit
        int alreadyBookedCount = bookingRepository
                .findByEventIdAndCustomerEmailAndStatusNot(
                        event.getId(),
                        customerEmail,
                        Booking.BookingStatus.CANCELLED)
                .stream()
                .mapToInt(Booking::getTicketsBooked)
                .sum();

        if (alreadyBookedCount + request.getTicketsRequested() > event.getMaxTicketsPerUser()) {
            throw new RuntimeException("Cannot book more than "
                    + event.getMaxTicketsPerUser() + " tickets per user for this event");
        }

        // check seat availability
        if (event.getAvailableSeats() < request.getTicketsRequested()) {
            throw new RuntimeException("Not enough seats available. Only "
                    + event.getAvailableSeats() + " seats left");
        }

        // deduct seats immediately
        event.setAvailableSeats(event.getAvailableSeats() - request.getTicketsRequested());
        eventRepository.save(event);

        // create the booking
        Booking booking = new Booking();
        booking.setEvent(event);
        booking.setCustomerEmail(customerEmail);
        booking.setCustomerName(customerEmail); // will be updated when we add user lookup
        booking.setTicketsBooked(request.getTicketsRequested());
        booking.setTotalAmount(event.getTicketPrice() * request.getTicketsRequested());

        Booking saved = bookingRepository.save(booking);
        logger.info("Booking confirmed: customer {} booked {} tickets for event '{}'",
                customerEmail, request.getTicketsRequested(), event.getName());

        return mapToResponse(saved);
    }

    // cancel a booking and restore seats
    @Transactional
    public BookingResponse cancelBooking(Long bookingId, String customerEmail) {

        Booking booking = bookingRepository.findById(bookingId)
                .orElseThrow(() -> new RuntimeException("Booking not found"));

        // only the customer who booked can cancel
        if (!booking.getCustomerEmail().equals(customerEmail)) {
            throw new RuntimeException("You are not authorized to cancel this booking");
        }

        // cannot cancel already cancelled booking
        if (booking.getStatus() == Booking.BookingStatus.CANCELLED) {
            throw new RuntimeException("This booking is already cancelled");
        }

        // restore the seats back to the event
        Event event = booking.getEvent();
        event.setAvailableSeats(event.getAvailableSeats() + booking.getTicketsBooked());
        eventRepository.save(event);

        // mark booking as cancelled
        booking.setStatus(Booking.BookingStatus.CANCELLED);
        booking.setCancelledAt(LocalDateTime.now());
        bookingRepository.save(booking);

        logger.info("Booking {} cancelled by customer {}. {} seats restored for event '{}'",
                bookingId, customerEmail, booking.getTicketsBooked(), event.getName());

        return mapToResponse(booking);
    }

    // get all bookings for a customer
    @Transactional
    public List<BookingResponse> getMyBookings(String customerEmail) {
        return bookingRepository.findByCustomerEmail(customerEmail)
                .stream()
                .map(this::mapToResponse)
                .collect(Collectors.toList());
    }

    // get all bookings for a specific event (organizer use)
    @Transactional
    public List<BookingResponse> getBookingsForEvent(Long eventId) {
        return bookingRepository.findByEventId(eventId)
                .stream()
                .map(this::mapToResponse)
                .collect(Collectors.toList());
    }

    private BookingResponse mapToResponse(Booking booking) {
        return new BookingResponse(
                booking.getId(),
                booking.getEvent().getId(),
                booking.getEvent().getName(),
                booking.getEvent().getVenue(),
                booking.getEvent().getEventDate(),
                booking.getCustomerEmail(),
                booking.getCustomerName(),
                booking.getTicketsBooked(),
                booking.getTotalAmount(),
                booking.getStatus().name(),
                booking.getBookedAt(),
                booking.getCancelledAt()
        );
    }
}