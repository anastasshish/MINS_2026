import grpc.ReferenceClient;
import grpc.TraceContext;
import util.LoggingConfig;
import repository.CellRepository;
import repository.InMemoryCellRepository;
import repository.RepositorySeed;
import service.WarehouseService;
import service.commands.CommandExecutor;
import service.events.WarehouseEventPublisher;
import ui.ConsoleWarehouseListener;
import ui.ConsoleUI;

import java.util.UUID;
import java.util.logging.Logger;

public class Main {

    private static final Logger LOGGER = Logger.getLogger(Main.class.getName());
    private static final String REFERENCE_HOST = "127.0.0.1";
    private static final int REFERENCE_PORT = 50051;

    public static void main(String[] args) {
        LoggingConfig.configure();
        TraceContext.set(UUID.randomUUID().toString());
        LOGGER.info(() -> "[trace-id=" + TraceContext.get() + "] Запуск warehouse-core (Core Service)");

        CellRepository repository = new InMemoryCellRepository();
        RepositorySeed.loadSeedData(repository);
        WarehouseEventPublisher eventPublisher = new WarehouseEventPublisher();
        eventPublisher.register(new ConsoleWarehouseListener());

        try (ReferenceClient referenceClient = new ReferenceClient(REFERENCE_HOST, REFERENCE_PORT)) {
            WarehouseService warehouseService = new WarehouseService(repository, referenceClient, eventPublisher);
            CommandExecutor commandExecutor = new CommandExecutor();
            ConsoleUI ui = new ConsoleUI(warehouseService, repository, commandExecutor, referenceClient);

            System.out.println("Добро пожаловать в склад (Core Service)");
            ui.run();
        }
    }
}
