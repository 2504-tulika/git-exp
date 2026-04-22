package com.tulika.eventbooking.eventservice.controller;

import com.tulika.eventbooking.eventservice.dto.EventRequest;
import com.tulika.eventbooking.eventservice.dto.EventResponse;
import com.tulika.eventbooking.eventservice.service.EventService;
import jakarta.validation.Valid;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.web.bind.annotation.*;

import java.util.HashMap;
import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/api/events")
@CrossOrigin(origins = "*")
public class EventController {

    private final EventService eventService;

    public EventController(EventService eventService) {
        this.eventService = eventService;
    }

    // ORGANIZER — create a new event
    // JWT principal gives us the organizer's email directly
    @PostMapping("/create")
    @PreAuthorize("hasRole('ORGANIZER')")
    public ResponseEntity<?> createEvent(@Valid @RequestBody EventRequest request,
                                         @AuthenticationPrincipal String organizerEmail) {
        try {
            EventResponse response = eventService.createEvent(request, organizerEmail);
            return ResponseEntity.status(HttpStatus.CREATED).body(response);
        } catch (RuntimeException ex) {
            Map<String, String> error = new HashMap<>();
            error.put("message", ex.getMessage());
            return ResponseEntity.status(HttpStatus.BAD_REQUEST).body(error);
        }
    }

    // ORGANIZER — see only their own events
    @GetMapping("/my-events")
    @PreAuthorize("hasRole('ORGANIZER')")
    public ResponseEntity<List<EventResponse>> getMyEvents(
            @AuthenticationPrincipal String organizerEmail) {
        return ResponseEntity.ok(eventService.getOrganizerEvents(organizerEmail));
    }

    // CUSTOMER + ORGANIZER — all upcoming events
    @GetMapping
    public ResponseEntity<List<EventResponse>> getAllUpcomingEvents() {
        return ResponseEntity.ok(eventService.getUpcomingEvents());
    }

    // CUSTOMER + ORGANIZER — single event detail
    @GetMapping("/{id}")
    public ResponseEntity<?> getEventById(@PathVariable Long id) {
        try {
            return ResponseEntity.ok(eventService.getEventById(id));
        } catch (RuntimeException ex) {
            Map<String, String> error = new HashMap<>();
            error.put("message", ex.getMessage());
            return ResponseEntity.status(HttpStatus.NOT_FOUND).body(error);
        }
    }
}