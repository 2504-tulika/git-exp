package com.tulika.usermanagement.service;

import com.tulika.usermanagement.model.User;
import com.tulika.usermanagement.repository.UserRepository;
import org.springframework.stereotype.Service;

import java.util.List;

// Service Layer Contains business logic and communicates with Repository
@Service
public class UserService {

    private final UserRepository userRepository;

    // Constructor Injection
    // Spring will automatically inject UserRepository here

    public UserService(UserRepository userRepository) {
        this.userRepository = userRepository;
    }

    // Get all users
    public List<User> getAllUsers() {
        return userRepository.getAllUsers();
    }

    // Create a new user
    public User createUser(User user) {
        return userRepository.saveUser(user);
    }

    //Get user by ID
    public User getUserById(int id) {
        return userRepository.getUserById(id);
    }
}