package com.tulika.eventbooking.eventservice.dto;

import lombok.AllArgsConstructor;
import lombok.Getter;
import lombok.Setter;

import java.time.LocalDateTime;

@Getter
@Setter
@AllArgsConstructor
public class BookingResponse {

    private Long bookingId;
    private Long eventId;
    private String eventName;
    private String eventVenue;
    private LocalDateTime eventDate;
    private String customerEmail;
    private String customerName;
    private Integer ticketsBooked;
    private Double totalAmount;
    private String status;
    private LocalDateTime bookedAt;
    private LocalDateTime cancelledAt;
}