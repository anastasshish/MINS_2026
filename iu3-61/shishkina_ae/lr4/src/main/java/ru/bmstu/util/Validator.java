package ru.bmstu.util;

import ru.bmstu.exceptions.ValidationException;

public final class Validator {

    private Validator() {
    }

    public static void requireNonBlank(String value, String fieldName) {
        if (value == null || value.isBlank()) {
            throw new ValidationException("Поле '" + fieldName + "' не должно быть пустым");
        }
    }

    public static void requireNonNegative(double value, String fieldName) {
        if (value < 0) {
            throw new ValidationException("Поле '" + fieldName + "' не должно быть отрицательным");
        }
    }

    public static void requirePositive(double value, String fieldName) {
        if (value <= 0) {
            throw new ValidationException("Поле '" + fieldName + "' должно быть больше нуля");
        }
    }

    public static void requireNonNegative(int value, String fieldName) {
        if (value < 0) {
            throw new ValidationException("Поле '" + fieldName + "' не должно быть отрицательным");
        }
    }

    public static void requirePositive(int value, String fieldName) {
        if (value <= 0) {
            throw new ValidationException("Поле '" + fieldName + "' должно быть больше нуля");
        }
    }

    public static void requireNotNull(Object value, String fieldName) {
        if (value == null) {
            throw new ValidationException("Поле '" + fieldName + "' не должно быть null");
        }
    }
}
