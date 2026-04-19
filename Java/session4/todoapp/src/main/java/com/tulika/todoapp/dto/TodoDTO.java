package com.tulika.todoapp.dto;
import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.Size;
import com.tulika.todoapp.entity.Status;

public class TodoDTO {
    @NotNull
    @Size(min = 3, message = "Title must be at least 3 characters")
    private String title;
    private Long id;
    private String description;

    private Status status;

    // Getters & Setters
    public Long getId() {
        return id;
    }

    public void setId(Long id) {
        this.id = id;
    }
    public String getTitle() {
        return title;
    }

    public void setTitle(String title) {
        this.title = title;
    }

    public String getDescription() {
        return description;
    }

    public void setDescription(String description) {
        this.description = description;
    }

    public Status getStatus() {
        return status;
    }

    public void setStatus(Status status) {
        this.status = status;
    }
}
