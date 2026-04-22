package com.tulika.eventbooking.eventservice.dto;

import lombok.AllArgsConstructor;
import lombok.Getter;
import lombok.Setter;

import java.time.LocalDateTime;

@Getter
@Setter
@AllArgsConstructor
public class EventResponse {

    private Long id;
    private String name;
    private String description;
    private LocalDateTime eventDate;
    private String venue;
    private Double ticketPrice;
    private Integer totalSeats;
    private Integer availableSeats;
    private Integer maxTicketsPerUser;
    private String organizerEmail;
    private String organizerName;
    private String additionalInfo;
    private String status;
    private LocalDateTime createdAt;
}