package com.tulika.todoapp.repository;
import org.springframework.data.jpa.repository.JpaRepository;
import com.tulika.todoapp.entity.Todo;

public interface TodoRepository extends JpaRepository<Todo, Long> {
}