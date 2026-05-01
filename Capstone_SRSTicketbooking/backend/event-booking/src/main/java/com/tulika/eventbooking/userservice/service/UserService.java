package com.tulika.eventbooking.userservice.service;

import com.tulika.eventbooking.userservice.dto.LoginRequest;
import com.tulika.eventbooking.userservice.dto.LoginResponse;
import com.tulika.eventbooking.userservice.dto.RegisterRequest;
import com.tulika.eventbooking.userservice.dto.UserResponse;
import com.tulika.eventbooking.userservice.model.User;
import com.tulika.eventbooking.userservice.repository.UserRepository;
import com.tulika.eventbooking.security.JwtUtil;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;

@Service
public class UserService {

    private static final Logger logger = LoggerFactory.getLogger(UserService.class);

    private final UserRepository userRepository;
    private final PasswordEncoder passwordEncoder;
    private final JwtUtil jwtUtil;

    public UserService(UserRepository userRepository,
                       PasswordEncoder passwordEncoder,
                       JwtUtil jwtUtil) {
        this.userRepository = userRepository;
        this.passwordEncoder = passwordEncoder;
        this.jwtUtil = jwtUtil;
    }

    public UserResponse registerUser(RegisterRequest request) {
        if (userRepository.existsByEmail(request.getEmail())) {
            logger.warn("Registration failed - email already exists: {}", request.getEmail());
            throw new RuntimeException("Email is already registered");
        }

        User user = new User();
        user.setName(request.getName());
        user.setEmail(request.getEmail());
        user.setPassword(passwordEncoder.encode(request.getPassword()));
        user.setPhone(request.getPhone());
        user.setRole(User.Role.valueOf(request.getRole().toUpperCase()));

        User savedUser = userRepository.save(user);
        logger.info("New user registered: {} with role {}", savedUser.getEmail(), savedUser.getRole());

        return new UserResponse(
                savedUser.getId(),
                savedUser.getName(),
                savedUser.getEmail(),
                savedUser.getPhone(),
                savedUser.getRole().name()
        );
    }

    public LoginResponse loginUser(LoginRequest request) {
        User user = userRepository.findByEmail(request.getEmail())
                .orElseThrow(() -> {
                    logger.warn("Login failed - email not found: {}", request.getEmail());
                    return new RuntimeException("Invalid email or password");
                });

        if (!passwordEncoder.matches(request.getPassword(), user.getPassword())) {
            logger.warn("Login failed - wrong password for: {}", request.getEmail());
            throw new RuntimeException("Invalid email or password");
        }

        String token = jwtUtil.generateToken(user.getEmail(), user.getRole().name());
        logger.info("User logged in successfully: {} | role: {}", user.getEmail(), user.getRole());

        return new LoginResponse(token, user.getEmail(), user.getName(), user.getRole().name());
    }
}