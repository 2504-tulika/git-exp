package com.tulika.usermanagement.component;

import org.springframework.stereotype.Component;

// Handles Notification logic
@Component
public class NotificationComponent {

    // Method to simulate sending notification
    public String sendNotification(String message) {
        return "Notification sent: " + message;
    }
}