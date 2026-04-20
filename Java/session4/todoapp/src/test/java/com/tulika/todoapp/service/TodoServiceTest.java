package com.tulika.todoapp.service;

import com.tulika.todoapp.client.NotificationServiceClient;
import com.tulika.todoapp.dto.TodoDTO;
import com.tulika.todoapp.entity.Status;
import com.tulika.todoapp.entity.Todo;
import com.tulika.todoapp.repository.TodoRepository;

import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.mockito.Mock;
import org.mockito.MockitoAnnotations;

import java.util.Optional;
import java.util.List;
import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.Mockito.*;

public class TodoServiceTest {

    private TodoService todoService;

    @Mock
    private TodoRepository todoRepository;

    @Mock
    private NotificationServiceClient notificationServiceClient;

    @BeforeEach
    void setUp() {
        MockitoAnnotations.openMocks(this);
        todoService = new TodoService(todoRepository, notificationServiceClient);
    }

    @Test
    void testGetTodoById() {
        Todo todo = new Todo();
        todo.setTitle("Test");

        when(todoRepository.findById(1L))
                .thenReturn(Optional.of(todo));

        TodoDTO result = todoService.getTodoById(1L);

        assertEquals("Test", result.getTitle());
    }

    @Test
    void testDeleteTodo() {
        Todo todo = new Todo();

        when(todoRepository.findById(1L))
                .thenReturn(Optional.of(todo));

        todoService.deleteTodo(1L);

        verify(todoRepository, times(1)).delete(todo);
    }

    @Test
    void testInvalidStatusTransition() {
        Todo todo = new Todo();
        todo.setStatus(Status.PENDING);

        when(todoRepository.findById(1L))
                .thenReturn(Optional.of(todo));

        TodoDTO dto = new TodoDTO();
        dto.setStatus(Status.PENDING); // same status → invalid transition

        assertThrows(RuntimeException.class, () -> {
            todoService.updateTodo(1L, dto);
        });
    }

    @Test
    void testCreateTodo() {
        TodoDTO dto = new TodoDTO();
        dto.setTitle("Test Todo");

        Todo saved = new Todo();
        saved.setTitle("Test Todo");

        when(todoRepository.save(any(Todo.class)))
                .thenReturn(saved);

        TodoDTO result = todoService.createTodo(dto);

        assertEquals("Test Todo", result.getTitle());

        verify(notificationServiceClient, times(1))
                .sendNotification(anyString());
    }

    @Test
    void testGetAllTodos() {
        Todo todo = new Todo();
        todo.setTitle("Task");

        when(todoRepository.findAll())
                .thenReturn(List.of(todo));

        List<TodoDTO> result = todoService.getAllTodos();

        assertEquals(1, result.size());
    }

    @Test
    void testUpdateTodo_Success() {
        Todo todo = new Todo();
        todo.setTitle("Old");
        todo.setStatus(Status.PENDING);

        when(todoRepository.findById(1L))
                .thenReturn(Optional.of(todo));

        TodoDTO dto = new TodoDTO();
        dto.setTitle("New");
        dto.setStatus(Status.COMPLETED);

        when(todoRepository.save(any(Todo.class)))
                .thenReturn(todo);

        TodoDTO result = todoService.updateTodo(1L, dto);

        assertEquals("New", result.getTitle());
        assertEquals(Status.COMPLETED, result.getStatus());
    }
}