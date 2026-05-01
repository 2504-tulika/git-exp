package com.tulika.eventbooking.eventservice.repository;

import com.tulika.eventbooking.eventservice.model.Event;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.time.LocalDateTime;
import java.util.List;

@Repository
public interface EventRepository extends JpaRepository<Event, Long> {

    // all events by a specific organizer
    List<Event> findByOrganizerEmail(String organizerEmail);

    // all upcoming active events for customers
    List<Event> findByStatusAndEventDateAfter(Event.EventStatus status, LocalDateTime date);
}