package com.tulika.usermanagement.model;

// This class represents the User entity in our system
public class User {
    private int id; //unique identifier for user
    private String name; //Name of User
    private String email; //Email of user

    // Parameterized constructor used to create User objeect with initial values

    public User(int id, String name, String email) {
        this.id = id;
        this.name = name;
        this.email = email;
    }
    // Default Constructor
    public User(){
    }

    public String getName() {
        return name;
    }

    public void setName(String name) {
        this.name = name;
    }

    public int getId() {
        return id;
    }

    public void setId(int id) {
        this.id = id;
    }

    public String getEmail() {
        return email;
    }

    public void setEmail(String email) {
        this.email = email;
    }


    //toString method for debugging/logging
    @Override
    public String toString(){
        return "User{" +
                "id=" + id +
                ", name='" + name + '\'' +
                ", email=' " + email + '\'' +
                '}';
    }
}