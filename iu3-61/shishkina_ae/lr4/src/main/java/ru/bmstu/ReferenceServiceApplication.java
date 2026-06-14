package ru.bmstu;

import io.grpc.Server;
import io.grpc.ServerBuilder;
import ru.bmstu.grpc.ReferenceGrpcService;
import ru.bmstu.infra.ServiceLog;
import ru.bmstu.infra.TraceContext;
import ru.bmstu.repository.InMemoryPartRepository;
import ru.bmstu.repository.PartRepository;
import ru.bmstu.service.InventoryService;

public class ReferenceServiceApplication {
    private static final int PORT = 9091;

    public static void main(String[] args) throws Exception {
        PartRepository partRepository = new InMemoryPartRepository();
        InventoryService inventoryService = new InventoryService(partRepository);
        preloadDemoData(inventoryService);

        Server server = ServerBuilder.forPort(PORT)
                .addService(new ReferenceGrpcService(inventoryService))
                .build()
                .start();

        TraceContext.beginTrace();
        ServiceLog.info("reference-service", "Reference Service запущен на порту " + PORT);
        TraceContext.clear();

        Runtime.getRuntime().addShutdownHook(new Thread(server::shutdown)); //когда приложение будет завершаться нужно корректно остановить gRPC
        server.awaitTermination(); // ждем пока червер не будет корректно остановлен
    }

    private static void preloadDemoData(InventoryService inventoryService) {
        inventoryService.createPart("Защитное стекло", 350, 10);
        inventoryService.createPart("Аккумулятор iPhone 11", 12800, 5);
        inventoryService.createPart("Зарядка Type-C", 300, 7);
    }
}
