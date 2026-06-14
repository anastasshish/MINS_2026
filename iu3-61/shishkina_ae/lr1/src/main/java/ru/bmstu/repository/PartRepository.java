package ru.bmstu.repository;

import ru.bmstu.model.Part;

import java.util.List;
import java.util.Optional;

public interface PartRepository {
    void save(Part part);

    Optional<Part> findById(Long id);

    Optional<Part> findByArticle(String article);

    List<Part> findAll();

    //I void printAllParts();
}