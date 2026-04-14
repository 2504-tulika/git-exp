package com.tulika.usermanagementv2.repository;

import com.tulika.usermanagementv2.model.User;
import org.springframework.stereotype.Repository;

import java.util.ArrayList;
import java.util.List;

// Repository class to store data
@Repository
public class UserRepository {

    private final List<User> users = new ArrayList<>();

    // Constructor to preload dummy users
    public UserRepository() {

        users.add(new User(1, "Tulika", 21, "Developer"));
        users.add(new User(2, "Rahul", 25, "Tester"));
        users.add(new User(3, "Anjali", 22, "Designer"));
        users.add(new User(4, "Amit", 28, "Manager"));
        users.add(new User(5, "Sneha", 24, "Developer"));
        users.add(new User(6, "Karan", 26, "Tester"));
    }

    // Get all users
    public List<User> getAllUsers() {
        return users;
    }

    // Adding user
    public void addUser(User user) {
        users.add(user);
    }

    // Delete user by id
    public boolean deleteUserById(int id) {
        return users.removeIf(user -> user.getId() == id);
    }
}