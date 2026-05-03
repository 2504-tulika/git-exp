package com.tulika.eventbooking.eventservice.controller;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.tulika.eventbooking.eventservice.dto.BookingRequest;
import com.tulika.eventbooking.eventservice.dto.BookingResponse;
import com.tulika.eventbooking.eventservice.service.BookingService;
import com.tulika.eventbooking.security.JwtUtil;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.WebMvcTest;
import org.springframework.boot.test.context.TestConfiguration;
import org.springframework.context.annotation.Bean;
import org.springframework.http.MediaType;
import org.springframework.security.test.context.support.WithMockUser;
import org.springframework.test.web.servlet.MockMvc;

import java.util.List;

import static org.mockito.ArgumentMatchers.*;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.when;
import static org.springframework.security.test.web.servlet.request.SecurityMockMvcRequestPostProcessors.csrf;
import static org.springframework.security.test.web.servlet.request.SecurityMockMvcRequestPostProcessors.user;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.*;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.*;

@WebMvcTest(BookingController.class)
class BookingControllerTest {

    @Autowired
    private MockMvc mockMvc;

    @Autowired
    private BookingService bookingService;

    @Autowired
    private ObjectMapper objectMapper;

    @TestConfiguration
    static class MockConfig {
        @Bean
        public BookingService bookingService() { return mock(BookingService.class); }

        @Bean
        public JwtUtil jwtUtil() { return mock(JwtUtil.class); }
    }

    @Test
    @WithMockUser(username = "customer@test.com", roles = "CUSTOMER")
    void bookTickets_ReturnsCreated() throws Exception {
        BookingRequest bookingRequest = new BookingRequest();
        bookingRequest.setEventId(1L);
        bookingRequest.setTicketsRequested(2);

        when(bookingService.bookTickets(any(), any()))
                .thenReturn(mock(BookingResponse.class));

        mockMvc.perform(post("/api/bookings")
                        .with(csrf())
                        .with(user("customer@test.com").roles("CUSTOMER"))
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(bookingRequest)))
                .andExpect(status().isCreated());
    }

    @Test
    void getMyBookings_Unauthenticated_Returns401() throws Exception {
        mockMvc.perform(get("/api/bookings/my-bookings"))
                .andExpect(status().isUnauthorized());
    }

    @Test
    @WithMockUser(username = "customer@test.com", roles = "CUSTOMER")
    void cancelBooking_ReturnsOk() throws Exception {
        when(bookingService.cancelBooking(anyLong(), any()))
                .thenReturn(mock(BookingResponse.class));

        // correct URL is PUT /{bookingId}/cancel not DELETE /1
        mockMvc.perform(put("/api/bookings/1/cancel")
                        .with(csrf())
                        .with(user("customer@test.com").roles("CUSTOMER")))
                .andExpect(status().isOk());
    }

    @Test
    @WithMockUser(username = "organizer@test.com", roles = "ORGANIZER")
    void getBookingsForEvent_ReturnsOk() throws Exception {
        when(bookingService.getBookingsForEvent(anyLong())).thenReturn(List.of());

        mockMvc.perform(get("/api/bookings/event/1")
                        .with(csrf()))
                .andExpect(status().isOk());
    }
}