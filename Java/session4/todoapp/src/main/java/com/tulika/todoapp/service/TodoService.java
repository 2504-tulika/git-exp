package com.tulika.todoapp.service;
import org.springframework.stereotype.Service;
import java.time.LocalDateTime;
import java.util.List;

import com.tulika.todoapp.dto.TodoDTO;
import com.tulika.todoapp.entity.Todo;
import com.tulika.todoapp.entity.Status;
import com.tulika.todoapp.repository.TodoRepository;
import com.tulika.todoapp.client.NotificationServiceClient;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;


@Service
public class TodoService {
    private final NotificationServiceClient notificationServiceClient;
    private final TodoRepository todoRepository;
    private Todo getTodoEntityById(Long id) {
        return todoRepository.findById(id)
                .orElseThrow(() -> new RuntimeException("Todo not found"));
    }

    private static final Logger logger = LoggerFactory.getLogger(TodoService.class);

    // Constructor Injection (best practice)

    public TodoService(TodoRepository todoRepository,
                       NotificationServiceClient notificationServiceClient) {
        this.todoRepository = todoRepository;
        this.notificationServiceClient = notificationServiceClient;
    }
    // CREATE
    public TodoDTO createTodo(TodoDTO dto) {
        Todo todo = new Todo();
        logger.info("Creating new TODO with title: {}", dto.getTitle());
        todo.setTitle(dto.getTitle());
        todo.setDescription(dto.getDescription());
        todo.setStatus(dto.getStatus() != null ? dto.getStatus() : Status.PENDING);
        todo.setCreatedAt(LocalDateTime.now());

        Todo saved = todoRepository.save(todo);
        notificationServiceClient.sendNotification("New TODO created: " + dto.getTitle());
        return convertToDTO(saved);

    }

    // READ ALL
    public List<TodoDTO> getAllTodos() {
        logger.info("Fetching all TODOs");
        return todoRepository.findAll()
                .stream()
                .map(this::convertToDTO)
                .toList();
    }

    // READ BY ID
    public TodoDTO getTodoById(Long id) {
        logger.info("Fetching TODO with id: {}", id);
        return convertToDTO(getTodoEntityById(id));
    }

    // UPDATE
    public TodoDTO updateTodo(Long id, TodoDTO dto) {
        Todo todo = getTodoEntityById(id); // FIXED
        logger.info("Updating TODO with id: {}", id);
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
        logger.info("Deleting TODO with id: {}", id);
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
