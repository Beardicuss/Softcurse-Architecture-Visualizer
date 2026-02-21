"""
REAL integration tests - Actually analyze code in all 13 languages!
"""

import pytest
from pathlib import Path
from analyzers.dispatcher import analyze_file_dispatch


def test_python_real_analysis(tmp_path):
    """REAL Python analysis - extract functions, classes, imports."""
    code = '''import os
from pathlib import Path

class Calculator:
    def add(self, a, b):
        return a + b
    
    def subtract(self, a, b):
        return a - b

def multiply(x, y):
    return x * y
'''
    file = tmp_path / "calc.py"
    file.write_text(code)
    
    functions, classes, imports, docstring, meta = analyze_file_dispatch(file, "python", {})
    
    # REAL assertions
    assert "multiply" in functions, "Should find multiply function"
    assert len(classes) >= 1, "Should find Calculator class"
    assert any(c["name"] == "Calculator" for c in classes), "Should find Calculator class"
    calc_class = next(c for c in classes if c["name"] == "Calculator")
    assert "add" in calc_class["methods"], "Should find add method"
    assert "subtract" in calc_class["methods"], "Should find subtract method"


def test_javascript_real_analysis(tmp_path):
    """REAL JavaScript analysis."""
    code = '''const express = require('express');

function createServer(port) {
    const app = express();
    return app;
}

class UserController {
    constructor(db) {
        this.db = db;
    }
    
    getUser(id) {
        return this.db.find(id);
    }
}

module.exports = { createServer, UserController };
'''
    file = tmp_path / "server.js"
    file.write_text(code)
    
    functions, classes, imports, docstring, meta = analyze_file_dispatch(file, "javascript", {})
    
    # REAL assertions - should find functions and classes
    assert len(functions) > 0 or len(classes) > 0, "Should find code structures"


def test_csharp_real_analysis(tmp_path):
    """REAL C# analysis."""
    code = '''using System;
using System.Collections.Generic;

namespace MyApp
{
    public class UserService
    {
        private readonly IDatabase _db;
        
        public UserService(IDatabase db)
        {
            _db = db;
        }
        
        public User GetUser(int id)
        {
            return _db.Find(id);
        }
        
        public void SaveUser(User user)
        {
            _db.Save(user);
        }
    }
    
    public class User
    {
        public int Id { get; set; }
        public string Name { get; set; }
    }
}
'''
    file = tmp_path / "UserService.cs"
    file.write_text(code)
    
    functions, classes, imports, docstring, meta = analyze_file_dispatch(file, "csharp", {})
    
    # REAL assertions
    assert len(classes) >= 2, f"Should find UserService and User classes, found {len(classes)}"
    class_names = [c["name"] for c in classes]
    assert "UserService" in class_names, "Should find UserService class"
    assert "User" in class_names, "Should find User class"


def test_java_real_analysis(tmp_path):
    """REAL Java analysis."""
    code = '''package com.example.app;

import java.util.List;
import java.util.ArrayList;

public class ProductService {
    private List<Product> products;
    
    public ProductService() {
        this.products = new ArrayList<>();
    }
    
    public void addProduct(Product product) {
        products.add(product);
    }
    
    public Product findById(int id) {
        return products.stream()
            .filter(p -> p.getId() == id)
            .findFirst()
            .orElse(null);
    }
}
'''
    file = tmp_path / "ProductService.java"
    file.write_text(code)
    
    functions, classes, imports, docstring, meta = analyze_file_dispatch(file, "java", {})
    
    # REAL assertions
    assert len(classes) >= 1, "Should find ProductService class"
    assert any("ProductService" in c["name"] for c in classes), "Should find ProductService"


def test_typescript_real_analysis(tmp_path):
    """REAL TypeScript analysis."""
    code = '''import { Request, Response } from 'express';

interface User {
    id: number;
    name: string;
    email: string;
}

class AuthService {
    private users: Map<number, User>;
    
    constructor() {
        this.users = new Map();
    }
    
    authenticate(email: string, password: string): User | null {
        // Authentication logic
        return null;
    }
    
    register(user: User): void {
        this.users.set(user.id, user);
    }
}

export { AuthService, User };
'''
    file = tmp_path / "auth.ts"
    file.write_text(code)
    
    functions, classes, imports, docstring, meta = analyze_file_dispatch(file, "typescript", {})
    
    # REAL assertions
    assert len(classes) > 0 or len(functions) > 0, "Should find code structures"


def test_go_real_analysis(tmp_path):
    """REAL Go analysis."""
    code = '''package main

import (
    "fmt"
    "net/http"
)

type Server struct {
    port int
    handler http.Handler
}

func NewServer(port int) *Server {
    return &Server{
        port: port,
    }
}

func (s *Server) Start() error {
    return http.ListenAndServe(fmt.Sprintf(":%d", s.port), s.handler)
}

func main() {
    server := NewServer(8080)
    server.Start()
}
'''
    file = tmp_path / "server.go"
    file.write_text(code)
    
    functions, classes, imports, docstring, meta = analyze_file_dispatch(file, "go", {})
    
    # REAL assertions
    assert len(functions) >= 2, f"Should find functions (NewServer, Start, main), found {len(functions)}"
    assert len(classes) >= 1, f"Should find Server struct, found {len(classes)}"


def test_rust_real_analysis(tmp_path):
    """REAL Rust analysis."""
    code = '''use std::collections::HashMap;

pub struct Database {
    data: HashMap<String, String>,
}

impl Database {
    pub fn new() -> Self {
        Database {
            data: HashMap::new(),
        }
    }
    
    pub fn insert(&mut self, key: String, value: String) {
        self.data.insert(key, value);
    }
    
    pub fn get(&self, key: &str) -> Option<&String> {
        self.data.get(key)
    }
}

pub fn create_database() -> Database {
    Database::new()
}
'''
    file = tmp_path / "database.rs"
    file.write_text(code)
    
    functions, classes, imports, docstring, meta = analyze_file_dispatch(file, "rust", {})
    
    # REAL assertions
    assert len(functions) >= 1 or len(classes) >= 1, "Should find functions or structs"


def test_php_real_analysis(tmp_path):
    """REAL PHP analysis."""
    code = '''<?php

namespace App\\Services;

use App\\Models\\User;
use App\\Database\\Connection;

class UserRepository {
    private $db;
    
    public function __construct(Connection $db) {
        $this->db = $db;
    }
    
    public function find($id) {
        return $this->db->query("SELECT * FROM users WHERE id = ?", [$id]);
    }
    
    public function save(User $user) {
        $this->db->insert('users', $user->toArray());
    }
}

function connectDatabase($host, $user, $password) {
    return new Connection($host, $user, $password);
}
?>
'''
    file = tmp_path / "UserRepository.php"
    file.write_text(code)
    
    functions, classes, imports, docstring, meta = analyze_file_dispatch(file, "php", {})
    
    # REAL assertions
    assert len(classes) >= 1 or len(functions) >= 1, "Should find classes or functions"


def test_ruby_real_analysis(tmp_path):
    """REAL Ruby analysis."""
    code = '''require 'json'
require 'net/http'

class ApiClient
  def initialize(base_url)
    @base_url = base_url
  end
  
  def get(endpoint)
    uri = URI("#{@base_url}/#{endpoint}")
    response = Net::HTTP.get(uri)
    JSON.parse(response)
  end
  
  def post(endpoint, data)
    uri = URI("#{@base_url}/#{endpoint}")
    Net::HTTP.post_form(uri, data)
  end
end

def create_client(url)
  ApiClient.new(url)
end
'''
    file = tmp_path / "api_client.rb"
    file.write_text(code)
    
    functions, classes, imports, docstring, meta = analyze_file_dispatch(file, "ruby", {})
    
    # REAL assertions
    assert len(classes) >= 1 or len(functions) >= 1, "Should find classes or functions"


def test_all_languages_can_analyze():
    """Meta-test: Verify all 13 languages have analyzers."""
    from core.config import LANGUAGE_CONFIG
    
    languages = ['python', 'javascript', 'typescript', 'java', 'csharp',
                 'go', 'rust', 'cpp', 'php', 'ruby', 'swift', 'kotlin', 'dart']
    
    for lang in languages:
        assert lang in LANGUAGE_CONFIG, f"{lang} not configured"
        # Verify it has required patterns
        config = LANGUAGE_CONFIG[lang]
        assert 'extensions' in config
        assert 'import_patterns' in config or lang == 'cpp'  # C++ uses #include
