package ru.bmstu.model;

import ru.bmstu.util.Validator;
import ru.bmstu.exceptions.InsufficientStockException;

public class Part {
    private final Long id;
    private final String article;
    private final String name;
    private final double price;
    private int quantityInStock;

    public Part(Long id, String article, String name, double price, int quantityInStock) {
        Validator.requireNotNull(id, "id");
        Validator.requireNonBlank(article, "article");
        Validator.requireNonBlank(name, "name");
        Validator.requireNonNegative(price, "price");
        Validator.requireNonNegative(quantityInStock, "quantityInStock");

        this.id = id;
        this.article = article;
        this.name = name;
        this.price = price;
        this.quantityInStock = quantityInStock;
    }

    public Long getId() {
        return id;
    }

    public String getArticle() {
        return article;
    }

    public String getName() {
        return name;
    }

    public double getPrice() {
        return price;
    }

    public int getQuantityInStock() {
        return quantityInStock;
    }

    public void increaseStock(int amount) {
        Validator.requirePositive(amount, "amount");
        quantityInStock += amount;
    }

    public void decreaseStock(int amount) {
        Validator.requirePositive(amount, "amount");

        if (amount > quantityInStock) {
            throw new InsufficientStockException(name, amount, quantityInStock);
        }

        quantityInStock -= amount;
    }

    @Override
    public String toString() {
        return "Part{id=" + id + ", article='" + article + '\'' + ", name='" + name + '\'' + ", price=" + price + ", quantityInStock=" + quantityInStock + '}';
    }
}