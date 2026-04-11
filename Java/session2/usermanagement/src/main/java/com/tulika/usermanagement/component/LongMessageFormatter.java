package com.tulika.usermanagement.component;

import org.springframework.stereotype.Component;

// Long message formatter

@Component("LONG")
public class LongMessageFormatter implements MessageFormatter {

    @Override
    public String formatMessage(String message) {
        return "Long Message Format: " + message + " (processed successfully)";
    }
}