package ru.bmstu.service;

import ru.bmstu.model.Part;

import java.util.List;

public interface ReferenceCatalogGateway {
    Part getPartById(Long id);

    List<Part> getAllParts();

    Part createPart(String name, double price, int quantityInStock);

    void consumePart(Long partId, int amount);
}
