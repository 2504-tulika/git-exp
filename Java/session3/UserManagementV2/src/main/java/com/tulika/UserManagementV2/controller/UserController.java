package com.tulika.usermanagementv2.controller;

import com.tulika.usermanagementv2.model.User;
import com.tulika.usermanagementv2.service.UserService;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import jakarta.validation.Valid;

// Controllers- handles API requests
@RestController
@RequestMapping("/users")
public class UserController {

    private final UserService userService;

    // Constructor Injection
    public UserController(UserService userService) {
        this.userService = userService;
    }

    // Search users with optional filters
    @GetMapping("/search")
    public List<User> searchUsers(
            @RequestParam(required = false) String name,
            @RequestParam(required = false) Integer age,
            @RequestParam(required = false) String role
    ) {
        return userService.searchUsers(name, age, role);
    }

    @PostMapping("/submit")
    public String addUser(@Valid @RequestBody User user) {
        userService.addUser(user);
        return "User added successfully";
    }
}