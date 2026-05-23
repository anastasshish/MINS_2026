package ui;

import exception.ReferenceServiceUnavailableException;
import exception.WarehouseException;
import grpc.ReferenceClient;
import grpc.TraceContext;
import model.Product;
import model.ProductCategory;
import model.StorageCell;
import repository.CellRepository;
import service.WarehouseService;
import service.commands.AddProductCommand;
import service.commands.CommandExecutor;
import service.commands.RemoveProductCommand;
import warehouse.reference.grpc.CategoryInfo;

import java.util.List;
import java.util.Scanner;
import java.util.UUID;
import java.util.logging.Logger;

public class ConsoleUI {

    private static final Logger LOGGER = Logger.getLogger(ConsoleUI.class.getName());

    private final WarehouseService warehouseService;
    private final CellRepository repository;
    private final CommandExecutor commandExecutor;
    private final ReferenceClient referenceClient;
    private final Scanner scanner = new Scanner(System.in);

    public ConsoleUI(WarehouseService warehouseService, CellRepository repository,
                     CommandExecutor commandExecutor, ReferenceClient referenceClient) {
        this.warehouseService = warehouseService;
        this.repository = repository;
        this.commandExecutor = commandExecutor;
        this.referenceClient = referenceClient;
    }

    public void run() {
        while (true) {
            printMenu();
            String choice = scanner.nextLine().trim();
            if ("7".equals(choice)) {
                break;
            }
            handleChoice(choice);
        }
    }

    private void printMenu() {
        System.out.println("\n--- Меню ---");
        System.out.println("1. Добавить товар");
        System.out.println("2. Убрать товар со склада");
        System.out.println("3. Показать все товары");
        System.out.println("4. Статистика по категориям");
        System.out.println("5. Проверить склад (audit)");
        System.out.println("6. Отменить последнюю операцию");
        System.out.println("7. Выход");
        System.out.print("Выбор: ");
    }

    private void handleChoice(String choice) {
        String traceId = UUID.randomUUID().toString();
        TraceContext.set(traceId);
        LOGGER.info(() -> "[trace-id=" + traceId + "] Пользовательская операция: " + choice);

        try {
            switch (choice) {
                case "1" -> handleAddProduct();
                case "2" -> handleRemoveProduct();
                case "3" -> handleShowProducts();
                case "4" -> handleShowStatistics();
                case "5" -> handleAudit();
                case "6" -> handleUndoLast();
                default -> System.out.println("Неверный выбор");
            }
        } finally {
            TraceContext.clear();
        }
    }

    private void handleAddProduct() {
        System.out.print("Номер ячейки: ");
        int cellPosition = readInt();
        if (cellPosition < 0) {
            System.out.println("Некорректный номер ячейки");
            return;
        }
        System.out.print("ID товара: ");
        String id = scanner.nextLine().trim();
        System.out.print("Название: ");
        String name = scanner.nextLine().trim();
        System.out.print("Количество: ");
        int quantity = readInt();
        if (quantity < 0) {
            System.out.println("Количество должно быть неотрицательным");
            return;
        }

        List<CategoryInfo> categories;
        try {
            categories = referenceClient.listCategories();
        } catch (ReferenceServiceUnavailableException e) {
            System.out.println(e.getMessage());
            return;
        }

        printCategoryMenu(categories);
        int categoryChoice = readInt();
        if (categoryChoice < 1 || categoryChoice > categories.size()) {
            System.out.println("Неверная категория");
            return;
        }

        CategoryInfo selected = categories.get(categoryChoice - 1);
        ProductCategory category = referenceClient.fromGrpcCategory(selected.getCategory());
        Product product = category.createProduct(id, name, quantity);
        try {
            commandExecutor.execute(new AddProductCommand(warehouseService, repository, product, cellPosition));
            System.out.println("Товар добавлен");
        } catch (WarehouseException e) {
            System.out.println("Ошибка: " + e.getMessage());
        }
    }

    private void printCategoryMenu(List<CategoryInfo> categories) {
        StringBuilder sb = new StringBuilder("Категория: ");
        for (int i = 0; i < categories.size(); i++) {
            CategoryInfo info = categories.get(i);
            sb.append(i + 1).append("-").append(info.getDisplayName());
            if (i < categories.size() - 1) {
                sb.append(", ");
            }
        }
        System.out.println(sb);
        System.out.print("Выбор: ");
    }

    private void handleRemoveProduct() {
        System.out.print("ID товара: ");
        String id = scanner.nextLine().trim();
        System.out.print("Количество для удаления: ");
        int amount = readInt();
        if (amount <= 0) {
            System.out.println("Количество должно быть положительным");
            return;
        }
        try {
            commandExecutor.execute(new RemoveProductCommand(warehouseService, repository, id, amount));
            System.out.println("Товар убран");
        } catch (WarehouseException e) {
            System.out.println("Ошибка: " + e.getMessage());
        }
    }

    private void handleUndoLast() {
        try {
            boolean undone = commandExecutor.undoLast();
            if (!undone) {
                System.out.println("Нечего отменять");
                return;
            }
            System.out.println("Последняя операция отменена");
        } catch (WarehouseException e) {
            System.out.println("Ошибка: " + e.getMessage());
        }
    }

    private void handleAudit() {
        new WarehouseAuditGodClass(repository).runAudit();
    }

    private void handleShowProducts() {
        List<StorageCell> cells = warehouseService.getAllCells();
        if (cells.isEmpty()) {
            System.out.println("Склад пуст");
            return;
        }
        System.out.printf("%-8s | %-6s | %-20s | %-11s | %s%n", "Ячейка", "ID", "Название", "Категория", "Кол-во");
        System.out.println("-".repeat(60));
        for (StorageCell cell : cells) {
            Product p = cell.product();
            System.out.printf("%-8d | %-6s | %-20s | %-11s | %d шт.%n",
                    cell.position(), p.getId(), p.getName(), p.getCategory(), p.getQuantity());
        }
    }

    private void handleShowStatistics() {
        int total = warehouseService.getTotalProducts();
        var byCategory = warehouseService.getProductsByCategory();
        System.out.println("Всего единиц товара: " + total);
        System.out.printf("%-12s | %s%n", "Категория", "Кол-во");
        System.out.println("-".repeat(25));
        for (var entry : byCategory.entrySet()) {
            System.out.printf("%-12s | %d%n", entry.getKey(), entry.getValue());
        }
    }

    private int readInt() {
        try {
            return Integer.parseInt(scanner.nextLine().trim());
        } catch (NumberFormatException e) {
            return -1;
        }
    }
}
