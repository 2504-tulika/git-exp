package com.tulika.usermanagement.service;

import com.tulika.usermanagement.component.MessageFormatter;
import com.tulika.usermanagement.exception.UserNotFoundException;
import com.tulika.usermanagement.model.User;
import com.tulika.usermanagement.repository.UserRepository;
import org.springframework.stereotype.Service;
import com.tulika.usermanagement.component.NotificationComponent;

import java.util.List;
import java.util.Map;
// Service Layer Contains business logic and communicates with Repository
@Service
public class UserService {

    private final UserRepository userRepository;
    private final NotificationComponent notificationComponent;
    private final Map<String, MessageFormatter> formatterMap;

    // Constructor Injection
    // Spring will automatically inject UserRepository here

    public UserService(UserRepository userRepository,
                       NotificationComponent notificationComponent,
                       Map<String, MessageFormatter> formatterMap) {
        this.userRepository = userRepository;
        this.notificationComponent = notificationComponent;
        this.formatterMap = formatterMap;
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
        User user = userRepository.getUserById(id);

        if (user == null) {
            throw new UserNotFoundException("User with ID " + id + " not found");
        }

        return user;
    }

    //Trigger notification

    public String triggerNotification(String message) {
        return notificationComponent.sendNotification(message);
    }

    // Dynamic message formatter

    public String getFormattedMessage(String type, String message) {

        MessageFormatter formatter = formatterMap.get(type.toUpperCase());

        if (formatter == null) {
            return "Invalid message type";
        }

        return formatter.formatMessage(message);
    }
}