package com.tulika.usermanagement.repository;

import com.tulika.usermanagement.model.User;
import org.springframework.stereotype.Repository;

import java.util.ArrayList;
import java.util.List;

//Repository Layer
@Repository
public class UserRepository {

    // In-memory list to store users
    private List<User> userList = new ArrayList<>();

    //Get all users
    public List<User> getAllUsers() {
        return userList;
    }

    //Save a new user
    public User saveUser(User user) {
        userList.add(user);
        return user;
    }

    //Find user by ID
    public User getUserById(int id) {
        for (User user : userList) {
            if (user.getId() == id) {
                return user;
            }
        }
        return null; // if not found
    }
}