package ru.bmstu.exceptions;

public class PartNotFoundException extends WorkshopException {
    public PartNotFoundException(Long partId) {
        super("Запчасть с id " + partId + " не найдена");
    }
}

