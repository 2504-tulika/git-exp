package com.tulika.eventbooking.eventservice.model;

import jakarta.persistence.*;
import lombok.AllArgsConstructor;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

import java.time.LocalDateTime;

@Entity
@Table(name = "events")
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
public class Event {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable = false)
    private String name;

    @Column(nullable = false, columnDefinition = "TEXT")
    private String description;

    @Column(nullable = false)
    private LocalDateTime eventDate;

    @Column(nullable = false)
    private String venue;

    @Column(nullable = false)
    private Double ticketPrice;

    @Column(nullable = false)
    private Integer totalSeats;

    @Column(nullable = false)
    private Integer availableSeats;

    @Column(nullable = false)
    private Integer maxTicketsPerUser;

    // organizer's email pulled from JWT token
    @Column(nullable = false)
    private String organizerEmail;

    private String organizerName;

    // extra info/theme the organizer wants to display
    private String additionalInfo;

    @Enumerated(EnumType.STRING)
    @Column(nullable = false)
    private EventStatus status;

    @Column(nullable = false, updatable = false)
    private LocalDateTime createdAt;

    @PrePersist
    protected void onCreate() {
        this.createdAt = LocalDateTime.now();
        this.status = EventStatus.ACTIVE;
        this.availableSeats = this.totalSeats;
    }

    public enum EventStatus {
        ACTIVE,
        CANCELLED
    }
}