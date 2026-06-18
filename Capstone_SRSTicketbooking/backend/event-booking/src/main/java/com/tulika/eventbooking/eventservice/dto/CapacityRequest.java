package com.tulika.eventbooking.eventservice.dto;

import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.Positive;
import lombok.Getter;
import lombok.Setter;

@Getter
@Setter
public class CapacityRequest {

    @NotNull(message = "New total seats value is required")
    @Positive(message = "Total seats must be greater than zero")
    private Integer newTotalSeats;
}