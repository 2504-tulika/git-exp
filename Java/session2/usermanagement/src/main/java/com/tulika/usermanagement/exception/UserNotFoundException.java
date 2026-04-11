package com.tulika.usermanagement.exception;

// Custom Exception for User Not Found

public class UserNotFoundException extends RuntimeException {

    public UserNotFoundException(String message) {
        super(message);
    }
}