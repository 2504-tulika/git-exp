package com.tulika.usermanagement.exception;

import org.springframework.http.HttpStatus;
import org.springframework.web.bind.annotation.*;

//Global Exception Handler

@RestControllerAdvice
public class GlobalExceptionHandler {

    //Handle UserNotFoundException
    @ExceptionHandler(UserNotFoundException.class)
    @ResponseStatus(HttpStatus.NOT_FOUND)
    public String handleUserNotFound(UserNotFoundException ex) {
        return ex.getMessage();
    }

    //Handle genericException
    @ExceptionHandler(Exception.class)
    @ResponseStatus(HttpStatus.INTERNAL_SERVER_ERROR)
    public String handleGeneralException(Exception ex) {
        return "Something went wrong: " + ex.getMessage();
    }
}