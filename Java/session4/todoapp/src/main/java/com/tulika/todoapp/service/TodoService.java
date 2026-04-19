package com.tulika.todoapp.service;
import org.springframework.stereotype.Service;
import java.time.LocalDateTime;
import java.util.List;

import com.tulika.todoapp.dto.TodoDTO;
import com.tulika.todoapp.entity.Todo;
import com.tulika.todoapp.entity.Status;
import com.tulika.todoapp.repository.TodoRepository;

@Service
public class TodoService {

    private final TodoRepository todoRepository;
    private Todo getTodoEntityById(Long id) {
        return todoRepository.findById(id)
                .orElseThrow(() -> new RuntimeException("Todo not found"));
    }

    // Constructor Injection (best practice)
    public TodoService(TodoRepository todoRepository) {
        this.todoRepository = todoRepository;
    }

    // CREATE
    public TodoDTO createTodo(TodoDTO dto) {
        Todo todo = new Todo();

        todo.setTitle(dto.getTitle());
        todo.setDescription(dto.getDescription());
        todo.setStatus(dto.getStatus() != null ? dto.getStatus() : Status.PENDING);
        todo.setCreatedAt(LocalDateTime.now());

        Todo saved = todoRepository.save(todo);
        return convertToDTO(saved);
    }

    // READ ALL
    public List<TodoDTO> getAllTodos() {
        return todoRepository.findAll()
                .stream()
                .map(this::convertToDTO)
                .toList();
    }

    // READ BY ID
    public TodoDTO getTodoById(Long id) {
        return convertToDTO(getTodoEntityById(id));
    }

    // UPDATE
    public TodoDTO updateTodo(Long id, TodoDTO dto) {
        Todo todo = getTodoEntityById(id); // FIXED

        if (dto.getStatus() != null) {
            validateStatusTransition(todo.getStatus(), dto.getStatus());
            todo.setStatus(dto.getStatus());
        }

        todo.setTitle(dto.getTitle());
        todo.setDescription(dto.getDescription());

        Todo updated = todoRepository.save(todo);
        return convertToDTO(updated);
    }

    // DELETE
    public void deleteTodo(Long id) {
        Todo todo = getTodoEntityById(id); // FIXED
        todoRepository.delete(todo);
    }

    public TodoDTO convertToDTO(Todo todo) {
        TodoDTO dto = new TodoDTO();

        dto.setId(todo.getId());
        dto.setTitle(todo.getTitle());
        dto.setDescription(todo.getDescription());
        dto.setStatus(todo.getStatus());
        return dto;
    }

    // BUSINESS RULE
    private void validateStatusTransition(Status oldStatus, Status newStatus) {
        if ((oldStatus == Status.PENDING && newStatus == Status.COMPLETED) ||
                (oldStatus == Status.COMPLETED && newStatus == Status.PENDING)) {
            return;
        }
        throw new RuntimeException("Invalid status transition");
    }
}
