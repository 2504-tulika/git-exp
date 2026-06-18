package com.tulika.eventbooking.eventservice.controller;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.tulika.eventbooking.eventservice.dto.CapacityRequest;
import com.tulika.eventbooking.eventservice.dto.EventResponse;
import com.tulika.eventbooking.eventservice.service.EventService;
import com.tulika.eventbooking.security.JwtUtil;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.WebMvcTest;
import org.springframework.boot.test.context.TestConfiguration;
import org.springframework.context.annotation.Bean;
import org.springframework.http.MediaType;
import org.springframework.security.test.context.support.WithMockUser;
import org.springframework.test.web.servlet.MockMvc;

import java.time.LocalDateTime;
import java.util.List;
import java.util.Map;

import static org.mockito.ArgumentMatchers.*;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.when;
import static org.springframework.security.test.web.servlet.request.SecurityMockMvcRequestPostProcessors.csrf;
import static org.springframework.security.test.web.servlet.request.SecurityMockMvcRequestPostProcessors.user;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.*;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.*;

@WebMvcTest(EventController.class)
class EventControllerTest {

    @Autowired
    private MockMvc mockMvc;

    @Autowired
    private EventService eventService;

    @Autowired
    private ObjectMapper objectMapper;

    @TestConfiguration
    static class MockConfig {
        @Bean
        public EventService eventService() { return mock(EventService.class); }

        @Bean
        public JwtUtil jwtUtil() { return mock(JwtUtil.class); }
    }

    // Build request as a raw Map — avoids Lombok setter issues entirely
    private Map<String, Object> buildEventRequestMap() {
        Map<String, Object> map = new java.util.HashMap<>();
        map.put("name", "Test Event");
        map.put("description", "Test Description");
        map.put("venue", "Test Venue");
        map.put("eventDate", LocalDateTime.now().plusDays(10).toString());
        map.put("ticketPrice", 100.0);
        map.put("totalSeats", 50);
        map.put("maxTicketsPerUser", 2);
        return map;
    }

    @Test
    void createEvent_ReturnsCreated() throws Exception {
        when(eventService.createEvent(any(), any()))
                .thenReturn(mock(EventResponse.class));

        mockMvc.perform(post("/api/events/create")
                        .with(csrf())
                        .with(user("organizer@test.com").roles("ORGANIZER"))
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(buildEventRequestMap())))
                .andExpect(status().isCreated());
    }

    @Test
    @WithMockUser
    void getUpcomingEvents_ReturnsList() throws Exception {
        when(eventService.getUpcomingEvents()).thenReturn(List.of());

        mockMvc.perform(get("/api/events").with(csrf()))
                .andExpect(status().isOk());
    }

    @Test
    @WithMockUser
    void getEventById_ReturnsOk() throws Exception {
        when(eventService.getEventById(anyLong()))
                .thenReturn(mock(EventResponse.class));

        mockMvc.perform(get("/api/events/1").with(csrf()))
                .andExpect(status().isOk());
    }

    @Test
    void getMyEvents_ReturnsOk() throws Exception {
        when(eventService.getOrganizerEvents(any())).thenReturn(List.of());

        mockMvc.perform(get("/api/events/my-events")
                        .with(csrf())
                        .with(user("organizer@test.com").roles("ORGANIZER")))
                .andExpect(status().isOk());
    }

    @Test
    void updateEvent_ReturnsOk() throws Exception {
        when(eventService.updateEvent(anyLong(), any(), any()))
                .thenReturn(mock(EventResponse.class));

        mockMvc.perform(put("/api/events/1")
                        .with(csrf())
                        .with(user("organizer@test.com").roles("ORGANIZER"))
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(buildEventRequestMap())))
                .andExpect(status().isOk());
    }

    @Test
    void cancelEvent_ReturnsOk() throws Exception {
        when(eventService.cancelEvent(anyLong(), any()))
                .thenReturn(mock(EventResponse.class));

        mockMvc.perform(put("/api/events/1/cancel")
                        .with(csrf())
                        .with(user("organizer@test.com").roles("ORGANIZER")))
                .andExpect(status().isOk());
    }
}