package ru.bmstu.model;

import ru.bmstu.util.Validator;

public class OrderPart {
    private final Part part;
    private int quantity;

    public OrderPart(Part part, int quantity) {
        Validator.requireNotNull(part, "part");
        Validator.requirePositive(quantity, "quantity");

        this.part = part;
        this.quantity = quantity;
    }

    public Part getPart() {
        return part;
    }

    public int getQuantity() {
        return quantity;
    }

    public void increaseQuantity(int amount) {
        Validator.requirePositive(amount, "amount");
        quantity += amount;
    }

    public double calculateCost() {
        return part.getPrice() * quantity;
    }

    @Override
    public String toString() {
        return "OrderPart{part=" + part.getName() +
                ", article='" + part.getArticle() + '\'' +
                ", quantity=" + quantity +
                ", unitPrice=" + part.getPrice() +
                ", totalCost=" + calculateCost() +
                '}';
    }
}
