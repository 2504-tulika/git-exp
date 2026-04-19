package com.tulika.todoapp.controller;

import org.springframework.web.bind.annotation.*;
import org.springframework.http.ResponseEntity;
import jakarta.validation.Valid;
import java.util.List;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import com.tulika.todoapp.dto.TodoDTO;
import com.tulika.todoapp.entity.Todo;
import com.tulika.todoapp.service.TodoService;

@RestController
@RequestMapping("/todos")
public class TodoController {

    private final TodoService todoService;
    private static final Logger logger = LoggerFactory.getLogger(TodoController.class);
    public TodoController(TodoService todoService) {
        this.todoService = todoService;
    }

    @PostMapping
    public ResponseEntity<TodoDTO> create(@Valid @RequestBody TodoDTO dto) {
        logger.info("Received request to create TODO");
        return ResponseEntity.ok(todoService.createTodo(dto));
    }

    @GetMapping
    public ResponseEntity<List<TodoDTO>> getAll() {
        logger.info("Received request to get all TODOs");
        return ResponseEntity.ok(todoService.getAllTodos());
    }

    @GetMapping("/{id}")
    public ResponseEntity<TodoDTO> getById(@PathVariable Long id) {
        logger.info("Received request to get TODOs by id");
        return ResponseEntity.ok(todoService.getTodoById(id));
    }

    @PutMapping("/{id}")
    public ResponseEntity<TodoDTO> update(
            @PathVariable Long id,
            @Valid @RequestBody TodoDTO dto) {

        return ResponseEntity.ok(todoService.updateTodo(id, dto));
    }

    @DeleteMapping("/{id}")
    public ResponseEntity<String> delete(@PathVariable Long id) {
        logger.info("Received request to Delete..");
        todoService.deleteTodo(id);
        return ResponseEntity.ok("Deleted successfully");
    }
}