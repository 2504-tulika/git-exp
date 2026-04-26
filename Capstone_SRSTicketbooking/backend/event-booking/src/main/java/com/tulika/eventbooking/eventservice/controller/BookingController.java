package com.tulika.eventbooking.eventservice.controller;

import com.tulika.eventbooking.eventservice.dto.BookingRequest;
import com.tulika.eventbooking.eventservice.dto.BookingResponse;
import com.tulika.eventbooking.eventservice.service.BookingService;
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
@RequestMapping("/api/bookings")
@CrossOrigin(origins = "*")
public class BookingController {

    private final BookingService bookingService;

    public BookingController(BookingService bookingService) {
        this.bookingService = bookingService;
    }

    // CUSTOMER — book tickets for an event
    @PostMapping
    @PreAuthorize("hasRole('CUSTOMER')")
    public ResponseEntity<?> bookTickets(@Valid @RequestBody BookingRequest request,
                                         @AuthenticationPrincipal String customerEmail) {
        try {
            BookingResponse response = bookingService.bookTickets(request, customerEmail);
            return ResponseEntity.status(HttpStatus.CREATED).body(response);
        } catch (RuntimeException ex) {
            Map<String, String> error = new HashMap<>();
            error.put("message", ex.getMessage());
            return ResponseEntity.status(HttpStatus.BAD_REQUEST).body(error);
        }
    }

    // CUSTOMER — cancel their own booking
    @PutMapping("/{bookingId}/cancel")
    @PreAuthorize("hasRole('CUSTOMER')")
    public ResponseEntity<?> cancelBooking(@PathVariable Long bookingId,
                                           @AuthenticationPrincipal String customerEmail) {
        try {
            BookingResponse response = bookingService.cancelBooking(bookingId, customerEmail);
            return ResponseEntity.ok(response);
        } catch (RuntimeException ex) {
            Map<String, String> error = new HashMap<>();
            error.put("message", ex.getMessage());
            return ResponseEntity.status(HttpStatus.BAD_REQUEST).body(error);
        }
    }

    // CUSTOMER — view their own booking history
    @GetMapping("/my-bookings")
    @PreAuthorize("hasRole('CUSTOMER')")
    public ResponseEntity<List<BookingResponse>> getMyBookings(
            @AuthenticationPrincipal String customerEmail) {
        return ResponseEntity.ok(bookingService.getMyBookings(customerEmail));
    }

    // ORGANIZER — view all bookings for their event
    @GetMapping("/event/{eventId}")
    @PreAuthorize("hasRole('ORGANIZER')")
    public ResponseEntity<List<BookingResponse>> getBookingsForEvent(
            @PathVariable Long eventId) {
        return ResponseEntity.ok(bookingService.getBookingsForEvent(eventId));
    }
}