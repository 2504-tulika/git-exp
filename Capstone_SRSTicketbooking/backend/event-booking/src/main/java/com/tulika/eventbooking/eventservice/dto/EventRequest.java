package com.tulika.eventbooking.eventservice.dto;

import jakarta.validation.constraints.*;
import lombok.Getter;
import lombok.Setter;

import java.time.LocalDateTime;

@Getter
@Setter
public class EventRequest {

    @NotBlank(message = "Event name is required")
    private String name;

    @NotBlank(message = "Description is required")
    private String description;

    @NotNull(message = "Event date is required")
    @Future(message = "Event date must be in the future")
    private LocalDateTime eventDate;

    @NotBlank(message = "Venue is required")
    private String venue;

    @NotNull(message = "Ticket price is required")
    @PositiveOrZero(message = "Ticket price cannot be negative")
    private Double ticketPrice;

    @NotNull(message = "Total seats is required")
    @Positive(message = "Total seats must be greater than zero")
    private Integer totalSeats;

    @NotNull(message = "Max tickets per user is required")
    @Positive(message = "Max tickets per user must be at least 1")
    private Integer maxTicketsPerUser;

    private String additionalInfo;
}