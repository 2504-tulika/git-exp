package com.tulika.eventbooking.eventservice.service;

import com.tulika.eventbooking.eventservice.dto.EventRequest;
import com.tulika.eventbooking.eventservice.dto.EventResponse;
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
public class EventService {

    private static final Logger logger = LoggerFactory.getLogger(EventService.class);

    private final EventRepository eventRepository;
    private final BookingRepository bookingRepository;

    public EventService(EventRepository eventRepository,
                        BookingRepository bookingRepository) {
        this.eventRepository = eventRepository;
        this.bookingRepository = bookingRepository;
    }

    public EventResponse createEvent(EventRequest request, String organizerEmail) {
        Event event = new Event();
        event.setName(request.getName());
        event.setDescription(request.getDescription());
        event.setEventDate(request.getEventDate());
        event.setVenue(request.getVenue());
        event.setTicketPrice(request.getTicketPrice());
        event.setTotalSeats(request.getTotalSeats());
        event.setMaxTicketsPerUser(request.getMaxTicketsPerUser());
        event.setOrganizerEmail(organizerEmail);
        event.setAdditionalInfo(request.getAdditionalInfo());

        Event saved = eventRepository.save(event);
        logger.info("Event created: '{}' by organizer: {}", saved.getName(), organizerEmail);

        return mapToResponse(saved);
    }

    // organizer sees their own events
    public List<EventResponse> getOrganizerEvents(String organizerEmail) {
        return eventRepository.findByOrganizerEmail(organizerEmail)
                .stream()
                .map(this::mapToResponse)
                .collect(Collectors.toList());
    }

    // customers see all upcoming active events
    public List<EventResponse> getUpcomingEvents() {
        return eventRepository
                .findByStatusAndEventDateAfter(Event.EventStatus.ACTIVE, LocalDateTime.now())
                .stream()
                .map(this::mapToResponse)
                .collect(Collectors.toList());
    }

    // get single event detail
    public EventResponse getEventById(Long id) {
        Event event = eventRepository.findById(id)
                .orElseThrow(() -> new RuntimeException("Event not found with id: " + id));
        return mapToResponse(event);
    }

    // organizer updates event details
// only allowed if event is more than 4 hours away
    @Transactional
    public EventResponse updateEvent(Long eventId, EventRequest request, String organizerEmail) {

        Event event = eventRepository.findById(eventId)
                .orElseThrow(() -> new RuntimeException("Event not found"));

        // only the organizer who created it can update
        if (!event.getOrganizerEmail().equals(organizerEmail)) {
            throw new RuntimeException("You are not authorized to update this event");
        }

        if (event.getStatus() == Event.EventStatus.CANCELLED) {
            throw new RuntimeException("Cannot update a cancelled event");
        }

        // 4 hour restriction before event start
        LocalDateTime cutoffTime = event.getEventDate().minusHours(4);
        if (LocalDateTime.now().isAfter(cutoffTime)) {
            throw new RuntimeException("Cannot update event within 4 hours of start time");
        }

        event.setName(request.getName());
        event.setDescription(request.getDescription());
        event.setEventDate(request.getEventDate());
        event.setVenue(request.getVenue());
        event.setTicketPrice(request.getTicketPrice());
        event.setAdditionalInfo(request.getAdditionalInfo());
        event.setMaxTicketsPerUser(request.getMaxTicketsPerUser());

        Event updated = eventRepository.save(event);
        logger.info("Event '{}' updated by organizer: {}", updated.getName(), organizerEmail);

        return mapToResponse(updated);
    }

    // organizer manages seat capacity
    @Transactional
    public EventResponse updateCapacity(Long eventId, int newTotalSeats, String organizerEmail) {

        Event event = eventRepository.findById(eventId)
                .orElseThrow(() -> new RuntimeException("Event not found"));

        if (!event.getOrganizerEmail().equals(organizerEmail)) {
            throw new RuntimeException("You are not authorized to manage this event");
        }

        if (event.getStatus() == Event.EventStatus.CANCELLED) {
            throw new RuntimeException("Cannot update capacity of a cancelled event");
        }

        // seats already booked = total - available
        int seatsAlreadyBooked = event.getTotalSeats() - event.getAvailableSeats();

        // cannot reduce below already booked count
        if (newTotalSeats < seatsAlreadyBooked) {
            throw new RuntimeException("Cannot reduce capacity below already booked seats ("
                    + seatsAlreadyBooked + " seats booked)");
        }

        // recalculate available seats based on new total
        int newAvailableSeats = newTotalSeats - seatsAlreadyBooked;

        event.setTotalSeats(newTotalSeats);
        event.setAvailableSeats(newAvailableSeats);

        Event updated = eventRepository.save(event);
        logger.info("Capacity updated for event '{}': total={}, available={}",
                updated.getName(), newTotalSeats, newAvailableSeats);

        return mapToResponse(updated);
    }

    // organizer cancels event — all confirmed bookings get marked cancelled
    @Transactional
    public EventResponse cancelEvent(Long eventId, String organizerEmail) {

        Event event = eventRepository.findById(eventId)
                .orElseThrow(() -> new RuntimeException("Event not found"));

        if (!event.getOrganizerEmail().equals(organizerEmail)) {
            throw new RuntimeException("You are not authorized to cancel this event");
        }

        if (event.getStatus() == Event.EventStatus.CANCELLED) {
            throw new RuntimeException("Event is already cancelled");
        }

        // mark all confirmed bookings as cancelled by organizer
        List<Booking> activeBookings = bookingRepository.findByEventId(eventId)
                .stream()
                .filter(b -> b.getStatus() == Booking.BookingStatus.CONFIRMED)
                .collect(Collectors.toList());

        for (Booking booking : activeBookings) {
            booking.setStatus(Booking.BookingStatus.CANCELLED_BY_ORGANIZER);
            booking.setCancelledAt(LocalDateTime.now());
        }
        bookingRepository.saveAll(activeBookings);

        // cancel the event
        event.setStatus(Event.EventStatus.CANCELLED);
        Event cancelled = eventRepository.save(event);

        logger.info("Event '{}' cancelled by organizer {}. {} bookings affected.",
                event.getName(), organizerEmail, activeBookings.size());

        return mapToResponse(cancelled);
    }

    private EventResponse mapToResponse(Event event) {
        return new EventResponse(
                event.getId(),
                event.getName(),
                event.getDescription(),
                event.getEventDate(),
                event.getVenue(),
                event.getTicketPrice(),
                event.getTotalSeats(),
                event.getAvailableSeats(),
                event.getMaxTicketsPerUser(),
                event.getOrganizerEmail(),
                event.getOrganizerName(),
                event.getAdditionalInfo(),
                event.getStatus().name(),
                event.getCreatedAt()
        );
    }
}