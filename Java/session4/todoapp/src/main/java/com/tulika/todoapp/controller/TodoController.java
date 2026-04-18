package com.tulika.todoapp.controller;

import org.springframework.web.bind.annotation.*;
import org.springframework.http.ResponseEntity;
import jakarta.validation.Valid;
import java.util.List;

import com.tulika.todoapp.dto.TodoDTO;
import com.tulika.todoapp.entity.Todo;
import com.tulika.todoapp.service.TodoService;

@RestController
@RequestMapping("/todos")
public class TodoController {

    private final TodoService todoService;

    public TodoController(TodoService todoService) {
        this.todoService = todoService;
    }

    // CREATE
    @PostMapping
    public ResponseEntity<Todo> create(@Valid @RequestBody TodoDTO dto) {
        return ResponseEntity.ok(todoService.createTodo(dto));
    }

    // READ ALL
    @GetMapping
    public ResponseEntity<List<Todo>> getAll() {
        return ResponseEntity.ok(todoService.getAllTodos());
    }

    // READ BY ID
    @GetMapping("/{id}")
    public ResponseEntity<Todo> getById(@PathVariable Long id) {
        return ResponseEntity.ok(todoService.getTodoById(id));
    }

    // UPDATE
    @PutMapping("/{id}")
    public ResponseEntity<Todo> update(
            @PathVariable Long id,
            @Valid @RequestBody TodoDTO dto) {

        return ResponseEntity.ok(todoService.updateTodo(id, dto));
    }

    // DELETE
    @DeleteMapping("/{id}")
    public ResponseEntity<String> delete(@PathVariable Long id) {
        todoService.deleteTodo(id);
        return ResponseEntity.ok("Deleted successfully");
    }
}
