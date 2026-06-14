package ru.bmstu;

import ru.bmstu.repository.InMemoryOrderRepository;
import ru.bmstu.repository.OrderRepository;
import ru.bmstu.service.ConsoleOrderStatusObserver;
import ru.bmstu.service.DefaultOrderPricingServiceFactory;
import ru.bmstu.service.GrpcReferenceCatalogClient;
import ru.bmstu.service.OrderPricingServiceFactory;
import ru.bmstu.service.OrderService;
import ru.bmstu.service.OrderTierService;
import ru.bmstu.ui.ConsoleMenu;
import ru.bmstu.ui.InputHandler;

import java.util.Scanner;

public class CoreServiceApplication {
    public static void main(String[] args) {
        OrderRepository orderRepository = new InMemoryOrderRepository();

        try (GrpcReferenceCatalogClient referenceCatalogClient = new GrpcReferenceCatalogClient("localhost", 9091)) {
            OrderService orderService = new OrderService(orderRepository, referenceCatalogClient);
            OrderTierService orderTierService = new OrderTierService();
            orderService.addStatusObserver(new ConsoleOrderStatusObserver());

            OrderPricingServiceFactory pricingServiceFactory = new DefaultOrderPricingServiceFactory();

            Scanner scanner = new Scanner(System.in);
            InputHandler inputHandler = new InputHandler(scanner);

            ConsoleMenu consoleMenu = new ConsoleMenu(
                    inputHandler,
                    orderService,
                    referenceCatalogClient,
                    orderTierService,
                    pricingServiceFactory
            );
            consoleMenu.start();
        }
    }
}
