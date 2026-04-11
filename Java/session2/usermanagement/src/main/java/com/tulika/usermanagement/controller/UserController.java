package com.tulika.usermanagement.controller;

import com.tulika.usermanagement.model.User;
import com.tulika.usermanagement.service.UserService;
import org.springframework.web.bind.annotation.*;

import java.util.List;

// Controller Layer: Handles REST API requests
@RestController
@RequestMapping("/users")
public class UserController {

    private final UserService userService;

    // Constructor Injection
    public UserController(UserService userService) {
        this.userService = userService;
    }

    // Fetch all users
    // using endpoint: GET /users
    @GetMapping
    public List<User> getAllUsers() {
        return userService.getAllUsers();
    }

    // Create a new user
    // using endpoint: POST /users
    @PostMapping
    public User createUser(@RequestBody User user) {
        return userService.createUser(user);
    }

    // Fetch user by ID
    // using endpoint: GET /users/{id}
    @GetMapping("/{id}")
    public User getUserById(@PathVariable int id) {
        return userService.getUserById(id);
    }
}