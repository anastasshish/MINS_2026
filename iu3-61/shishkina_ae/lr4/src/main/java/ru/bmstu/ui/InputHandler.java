package ru.bmstu.ui;

import ru.bmstu.util.Validator;

import java.util.Scanner;

public class InputHandler {
    private final Scanner scanner;

    public InputHandler(Scanner scanner) {
        Validator.requireNotNull(scanner, "scanner");
        this.scanner = scanner;
    }

    public String readNonBlankString(String prompt) {
        while (true) {
            System.out.print(prompt);
            String value = scanner.nextLine();

            if (value != null && !value.isBlank()) {
                return value.trim();
            }

            System.out.println("Ошибка: ввод не должен быть пустым");
        }
    }

    public Long readLong(String prompt) {
        while (true) {
            System.out.print(prompt);
            String value = scanner.nextLine();

            try {
                return Long.parseLong(value.trim());
            } catch (NumberFormatException e) {
                System.out.println("Ошибка: введите целое число");
            }
        }
    }

    public int readInt(String prompt) {
        while (true) {
            System.out.print(prompt);
            String value = scanner.nextLine();

            try {
                return Integer.parseInt(value.trim());
            } catch (NumberFormatException e) {
                System.out.println("Ошибка: введите целое число");
            }
        }
    }

    public double readDouble(String prompt) {
        while (true) {
            System.out.print(prompt);
            String value = scanner.nextLine();

            try {
                return Double.parseDouble(value.trim().replace(',', '.'));
            } catch (NumberFormatException e) {
                System.out.println("Ошибка: введите число");
            }
        }
    }
}
