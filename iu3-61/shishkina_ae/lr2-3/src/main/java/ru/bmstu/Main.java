package ru.bmstu;

import ru.bmstu.repository.InMemoryOrderRepository;
import ru.bmstu.repository.InMemoryPartRepository;
import ru.bmstu.repository.OrderRepository;
import ru.bmstu.repository.PartRepository;
import ru.bmstu.service.DefaultOrderPricingServiceFactory;
import ru.bmstu.service.InventoryService;
import ru.bmstu.service.OrderTierService;
import ru.bmstu.service.OrderPricingServiceFactory;
import ru.bmstu.service.OrderService;
import ru.bmstu.service.ConsoleOrderStatusObserver;
import ru.bmstu.promo.WednesdaySparePartsPromo;
import ru.bmstu.ui.ConsoleMenu;
import ru.bmstu.ui.InputHandler;
import java.util.Scanner;



public class Main {
    public static void main(String[] args) {
        PartRepository partRepository = new InMemoryPartRepository();
        OrderRepository orderRepository = new InMemoryOrderRepository();

        InventoryService inventoryService = new InventoryService(partRepository);
        OrderService orderService = new OrderService(orderRepository, inventoryService);
        OrderTierService orderTierService = new OrderTierService();
        orderService.addStatusObserver(new ConsoleOrderStatusObserver());

        OrderPricingServiceFactory pricingServiceFactory = new DefaultOrderPricingServiceFactory();

        Scanner scanner = new Scanner(System.in);
        InputHandler inputHandler = new InputHandler(scanner);

        preloadDemoData(inventoryService);

        ConsoleMenu consoleMenu = new ConsoleMenu(
                inputHandler,
                orderService,
                inventoryService,
                orderTierService,
                pricingServiceFactory,
                new WednesdaySparePartsPromo()
        );
        consoleMenu.start();
    }

    private static void preloadDemoData(InventoryService inventoryService) {
        inventoryService.createPart("Защитное стекло", 350, 10);
        inventoryService.createPart("Аккумулятор iPhone 11", 12800, 5);
        inventoryService.createPart("Зарядка Type-C", 300, 7);
    }
}