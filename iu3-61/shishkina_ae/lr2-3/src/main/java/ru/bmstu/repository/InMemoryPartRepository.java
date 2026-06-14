package ru.bmstu.repository;

import ru.bmstu.model.Part;
import ru.bmstu.util.Validator;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Optional;

public class InMemoryPartRepository implements PartRepository {
    private final Map<Long, Part> partsById = new HashMap<>();
    private final Map<String, Part> partsByArticle = new HashMap<>();

    @Override
    public void save(Part part) {
        Validator.requireNotNull(part, "part");
        partsById.put(part.getId(), part);
        partsByArticle.put(part.getArticle(), part);
    }

    @Override
    public Optional<Part> findById(Long id) {
        Validator.requireNotNull(id, "id");
        return Optional.ofNullable(partsById.get(id));
    }

    @Override
    public Optional<Part> findByArticle(String article) {
        Validator.requireNonBlank(article, "article");
        return Optional.ofNullable(partsByArticle.get(article));
    }

    @Override
    public List<Part> findAll() {
        return new ArrayList<>(partsById.values());
    }

}