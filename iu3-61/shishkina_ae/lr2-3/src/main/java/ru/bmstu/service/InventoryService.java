package ru.bmstu.service;

import ru.bmstu.repository.PartRepository;
import ru.bmstu.exceptions.PartNotFoundException;
import ru.bmstu.model.Part;
import ru.bmstu.util.Validator;

import java.util.List;

public class InventoryService {
    private final PartRepository partRepository;

    private long nextPartId = 1;
    private long nextArticleNumber = 1;

    public InventoryService(PartRepository partRepository) {
        Validator.requireNotNull(partRepository, "partRepository");
        this.partRepository = partRepository;
    }

    public Part createPart(String name, double price, int quantityInStock) {
        Validator.requireNonBlank(name, "name");
        Validator.requireNonNegative(price, "price");
        Validator.requireNonNegative(quantityInStock, "quantityInStock");

        Long id = nextPartId++;
        String article = generateArticle();

        Part part = new Part(id, article, name, price, quantityInStock);
        partRepository.save(part);

        return part;
    }

    public Part getPartById(Long id) {
        return partRepository.findById(id)
                .orElseThrow(() -> new PartNotFoundException(id));
    }

    public List<Part> getAllParts() {
        return partRepository.findAll();
    }

    public void consumePart(Long partId, int amount) {
        Validator.requirePositive(amount, "amount");
        Part part = getPartById(partId);
        part.decreaseStock(amount);
    }

    private String generateArticle() {
        return "PART-" + nextArticleNumber++;
    }
}