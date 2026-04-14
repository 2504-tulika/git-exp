package com.tulika.usermanagementv2.service;

import com.tulika.usermanagementv2.model.User;
import com.tulika.usermanagementv2.repository.UserRepository;
import org.springframework.stereotype.Service;

import java.util.List;
import java.util.stream.Collectors;

// UserService contains business logic
@Service
public class UserService {

    private final UserRepository userRepository;

    // Constructor Injection
    public UserService(UserRepository userRepository) {
        this.userRepository = userRepository;
    }

    // Search users based on optional filters
    public List<User> searchUsers(String name, Integer age, String role) {

        List<User> users = userRepository.getAllUsers();

        // If no filters → return all users
        if (name == null && age == null && role == null) {
            return users;
        }

        // Apply filters
        return users.stream()
                .filter(user ->
                        (name == null || user.getName().equalsIgnoreCase(name)) &&
                                (age == null || user.getAge() == age) &&
                                (role == null || user.getRole().equalsIgnoreCase(role))
                )
                .collect(Collectors.toList());
    }

    // Add user
    public void addUser(User user) {
        userRepository.addUser(user);
    }

    // Delete user with confirmation
    public String deleteUser(int id, boolean confirm) {

        if (!confirm) {
            return "Confirmation required";
        }

        boolean deleted = userRepository.deleteUserById(id);

        if (deleted) {
            return "User deleted successfully";
        } else {
            return "User not found";
        }
    }
}