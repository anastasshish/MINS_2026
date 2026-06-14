package ru.bmstu.exceptions;

public class OrderNotFoundException extends WorkshopException {
    public OrderNotFoundException(Long orderId) {
        super("Заказ с id " + orderId + " не найден");
    }
}
