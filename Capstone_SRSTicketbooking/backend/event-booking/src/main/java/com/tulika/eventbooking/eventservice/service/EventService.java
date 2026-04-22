package com.tulika.eventbooking.eventservice.service;

import com.tulika.eventbooking.eventservice.dto.EventRequest;
import com.tulika.eventbooking.eventservice.dto.EventResponse;
import com.tulika.eventbooking.eventservice.model.Event;
import com.tulika.eventbooking.eventservice.repository.EventRepository;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Service;

import java.time.LocalDateTime;
import java.util.List;
import java.util.stream.Collectors;

@Service
public class EventService {

    private static final Logger logger = LoggerFactory.getLogger(EventService.class);

    private final EventRepository eventRepository;

    public EventService(EventRepository eventRepository) {
        this.eventRepository = eventRepository;
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