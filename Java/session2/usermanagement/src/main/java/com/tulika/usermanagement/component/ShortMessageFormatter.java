package com.tulika.usermanagement.component;

import org.springframework.stereotype.Component;

// Short message formatter

@Component("SHORT")
public class ShortMessageFormatter implements MessageFormatter {

    @Override
    public String formatMessage(String message) {
        return "Short: " + message;
    }
}