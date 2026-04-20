package com.tulika.todoapp.controller;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.tulika.todoapp.dto.TodoDTO;
import com.tulika.todoapp.entity.Status;
import com.tulika.todoapp.service.TodoService;

import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.WebMvcTest;
import org.springframework.boot.test.mock.mockito.MockBean;
import org.springframework.http.MediaType;
import org.springframework.test.web.servlet.MockMvc;

import java.util.List;

import static org.mockito.Mockito.when;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.*;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.*;

@WebMvcTest(TodoController.class)
class TodoControllerTest {

    @Autowired
    private MockMvc mockMvc;

    @MockBean
    private TodoService todoService;

    @Autowired
    private ObjectMapper objectMapper;

    @Test
    void createTodo_shouldReturn201() throws Exception {
        TodoDTO dto = new TodoDTO();
        dto.setTitle("Test Todo");

        when(todoService.createTodo(org.mockito.Mockito.any()))
                .thenReturn(dto);

        mockMvc.perform(post("/todos")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(dto)))
                .andExpect(status().isCreated());
    }

    @Test
    void getAllTodos_shouldReturnList() throws Exception {
        TodoDTO dto = new TodoDTO();
        dto.setTitle("Task");

        when(todoService.getAllTodos())
                .thenReturn(List.of(dto));

        mockMvc.perform(get("/todos"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$[0].title").value("Task"));
    }

    @Test
    void getTodoById_shouldReturnTodo() throws Exception {
        TodoDTO dto = new TodoDTO();
        dto.setTitle("Task");

        when(todoService.getTodoById(1L))
                .thenReturn(dto);

        mockMvc.perform(get("/todos/1"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.title").value("Task"));
    }

    @Test
    void updateTodo_shouldReturnUpdated() throws Exception {
        TodoDTO dto = new TodoDTO();
        dto.setTitle("Updated");
        dto.setStatus(Status.COMPLETED);

        when(todoService.updateTodo(org.mockito.Mockito.eq(1L), org.mockito.Mockito.any()))
                .thenReturn(dto);

        mockMvc.perform(put("/todos/1")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(dto)))
                .andExpect(status().isOk());
    }

    @Test
    void deleteTodo_shouldReturn200() throws Exception {
        mockMvc.perform(delete("/todos/1"))
                .andExpect(status().isOk());
    }
}