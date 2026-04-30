package com.tulika.eventbooking.eventservice.repository;

import com.tulika.eventbooking.eventservice.model.Booking;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;

@Repository
public interface BookingRepository extends JpaRepository<Booking, Long> {

    // all bookings by a customer
    List<Booking> findByCustomerEmail(String customerEmail);

    // all bookings for a specific event (organizer view)
    List<Booking> findByEventId(Long eventId);

    // check if customer already booked this event
    Optional<Booking> findByEventIdAndCustomerEmailAndStatus(
            Long eventId,
            String customerEmail,
            Booking.BookingStatus status
    );

    // count total tickets booked by a customer for an event
    // used to enforce maxTicketsPerUser
    List<Booking> findByEventIdAndCustomerEmailAndStatusNot(
            Long eventId,
            String customerEmail,
            Booking.BookingStatus status
    );
}