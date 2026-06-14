package ru.bmstu.exceptions;

public class InsufficientStockException extends WorkshopException {
    public InsufficientStockException(String partName, int requested, int available) {
        super("Недостаточно запчастей на складе: " + partName + ". Запрошено: " + requested + ", доступно: " + available + ".");
    }
}
