package ru.bmstu.ui;

import ru.bmstu.service.InventoryService;
import ru.bmstu.service.OrderPricingService;
import ru.bmstu.service.OrderService;
import ru.bmstu.exceptions.WorkshopException;
import ru.bmstu.model.*;
import ru.bmstu.util.Validator;

import java.util.List;

public class ConsoleMenu {
    private final InputHandler inputHandler;
    private final OrderService orderService;
    private final InventoryService inventoryService;
    private final OrderPricingService pricingService;

    public ConsoleMenu(
            InputHandler inputHandler,
            OrderService orderService,
            InventoryService inventoryService,
            OrderPricingService pricingService
    ) {
        Validator.requireNotNull(inputHandler, "inputHandler");
        Validator.requireNotNull(orderService, "orderService");
        Validator.requireNotNull(inventoryService, "inventoryService");
        Validator.requireNotNull(pricingService, "pricingService");

        this.inputHandler = inputHandler;
        this.orderService = orderService;
        this.inventoryService = inventoryService;
        this.pricingService = pricingService;
    }

    public void start() {
        boolean running = true;

        while (running) {
            printMenu();
            int choice = inputHandler.readInt("Выберите пункт меню: ");

            try {
                switch (choice) {
                    case 1 -> createOrder();
                    case 2 -> showAllOrders();
                    case 3 -> addWorkToOrder();
                    case 4 -> addPartToOrder();
                    case 5 -> changeOrderStatus();
                    case 6 -> addPartToInventory();
                    case 7 -> showAllParts();
                    case 0 -> {
                        running = false;
                        System.out.println("Работа программы завершена");
                    }
                    default -> System.out.println("Неизвестный пункт меню");
                }
            } catch (WorkshopException e) {
                System.out.println("Ошибка: " + e.getMessage());
            } catch (Exception e) {
                System.out.println("Непредвиденная ошибка: " + e.getMessage());
            }

            System.out.println();
        }
    }

    private void printMenu() {
        System.out.println("РЕМОНТНАЯ МАСТЕРСКАЯ");
        System.out.println("1. Создать заказ");
        System.out.println("2. Показать все заказы");
        System.out.println("3. Добавить работу в заказ");
        System.out.println("4. Добавить запчасть в заказ");
        System.out.println("5. Изменить статус заказа");
        System.out.println("6. Добавить запчасть на склад");
        System.out.println("7. Показать все запчасти");
        System.out.println("0. Выход");
    }

    private void createOrder() {
        String customerName = inputHandler.readNonBlankString("Введите имя клиента: ");
        String customerPhone = inputHandler.readNonBlankString("Введите телефон клиента: ");

        String deviceType = inputHandler.readNonBlankString("Введите тип устройства: ");
        String deviceBrand = inputHandler.readNonBlankString("Введите бренд устройства: ");
        String deviceModel = inputHandler.readNonBlankString("Введите модель устройства: ");

        String problemDescription = inputHandler.readNonBlankString("Введите описание неисправности: ");

        RepairOrder order = orderService.createOrder(
                customerName,
                customerPhone,
                deviceType,
                deviceBrand,
                deviceModel,
                problemDescription
        );

        System.out.println("Заказ успешно создан");
        System.out.println("Номер заказа: " + order.getId());
    }

    private void showAllOrders() {
        List<RepairOrder> orders = orderService.getAllOrders();

        if (orders.isEmpty()) {
            System.out.println("Список заказов пуст");
            return;
        }

        for (RepairOrder order : orders) {
            printOrder(order);
            //order.printInfo();
            System.out.println("-----------------------------------");
        }
    }

    private void addWorkToOrder() {
        Long orderId = inputHandler.readLong("Введите id заказа: ");
        String workName = inputHandler.readNonBlankString("Введите название работы: ");
        double standardHours = inputHandler.readDouble("Введите время: ");
        double price = inputHandler.readDouble("Введите стоимость работы: ");

        RepairWork work = new RepairWork(workName, standardHours, price);
        orderService.addWorkToOrder(orderId, work);

        System.out.println("Работа успешно добавлена в заказ");
    }

    private void addPartToOrder() {
        Long orderId = inputHandler.readLong("Введите id заказа: ");

        System.out.println("Доступные запчасти:");
        showAllParts();

        Long partId = inputHandler.readLong("Введите id запчасти: ");
        int quantity = inputHandler.readInt("Введите количество: ");
/*S
        if (quantity > 5) {
            System.out.println("За раз нельзя добавить больше 5 запчастей");
            return;
        }
*/

        orderService.addPartToOrder(orderId, partId, quantity);

        System.out.println("Запчасть успешно добавлена в заказ");
    }

    private void changeOrderStatus() {
        Long orderId = inputHandler.readLong("Введите id заказа: ");

        System.out.println("Доступные статусы:");
        for (OrderStatus status : OrderStatus.values()) {
            System.out.println("- " + status);
        }

        String statusInput = inputHandler.readNonBlankString("Введите новый статус: ").toUpperCase();

        try {
            OrderStatus newStatus = OrderStatus.valueOf(statusInput);
            orderService.changeOrderStatus(orderId, newStatus);
            System.out.println("Статус заказа успешно изменен");
        } catch (IllegalArgumentException e) {
            System.out.println("Ошибка: введен неизвестный статус");
        }
    }

    private void addPartToInventory() {
        String name = inputHandler.readNonBlankString("Введите название запчасти: ");
        double price = inputHandler.readDouble("Введите цену запчасти: ");
        int quantity = inputHandler.readInt("Введите количество на складе: ");

        Part part = inventoryService.createPart(name, price, quantity);

        System.out.println("Запчасть успешно добавлена на склад");

    }

    private void showAllParts() {
        List<Part> parts = inventoryService.getAllParts();

        if (parts.isEmpty()) {
            System.out.println("Склад запчастей пуст");
            return;
        }

        for (Part part : parts) {
            System.out.println("id: " + part.getId() + ", название: " + part.getName() + ", артикул: " + part.getArticle() + ", цена: " + part.getPrice() + ", остаток: " + part.getQuantityInStock());
        }
    }

    private void printOrder(RepairOrder order) {
        System.out.println("Заказ id: " + order.getId());
        System.out.println("Клиент: " + order.getCustomer().getName() + ", телефон: " + order.getCustomer().getPhone());
        System.out.println("Устройство: " + order.getDevice());
        System.out.println("Неисправность: " + order.getProblemDescription());
        System.out.println("Статус: " + order.getStatus());

        printWorks(order);
        printUsedParts(order);

        System.out.println("Итоговая стоимость: " + pricingService.calculateTotalPrice(order));
        System.out.println("Общее время: " + pricingService.calculateTotalStandardHours(order));
    }

    private void printWorks(RepairOrder order) {
        System.out.println("Работы:");
        if (order.getWorks().isEmpty()) {
            System.out.println("  нет");
            return;
        }

        for (RepairWork work : order.getWorks()) {
            System.out.println("  - " + work.getName()
                    + ", нормо-время: " + work.getStandardHours()
                    + ", стоимость: " + work.getPrice());
        }
    }

    private void printUsedParts(RepairOrder order) {
        System.out.println("Запчасти:");
        if (order.getUsedParts().isEmpty()) {
            System.out.println("  нет");
            return;
        }

        for (OrderPart orderPart : order.getUsedParts()) {
            System.out.println("  - " + orderPart.getPart().getName()
                    + ", id запчасти: " + orderPart.getPart().getId()
                    + ", артикул: " + orderPart.getPart().getArticle()
                    + ", количество: " + orderPart.getQuantity()
                    + ", стоимость: " + orderPart.calculateCost());
        }
    }
}