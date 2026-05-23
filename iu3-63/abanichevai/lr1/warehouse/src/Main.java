import repository.CellRepository;
import repository.InMemoryCellRepository;
import repository.RepositorySeed;
import service.DefaultNeighborhoodValidator;
import service.NeighborhoodValidator;
import service.WarehouseService;
import service.commands.CommandExecutor;
import service.events.WarehouseEventPublisher;
import ui.ConsoleWarehouseListener;
import ui.ConsoleUI;

//Подлкючить гит, в новой ветке сделать задание

public class Main {
    public static void main(String[] args) {
        CellRepository repository = new InMemoryCellRepository();
        RepositorySeed.loadSeedData(repository);
        NeighborhoodValidator validator = new DefaultNeighborhoodValidator();
        WarehouseEventPublisher eventPublisher = new WarehouseEventPublisher();
        eventPublisher.register(new ConsoleWarehouseListener());

        WarehouseService warehouseService = new WarehouseService(repository, validator, eventPublisher);
        CommandExecutor commandExecutor = new CommandExecutor();
        ConsoleUI ui = new ConsoleUI(warehouseService, repository, commandExecutor);

        System.out.println("Добро пожаловать в склад");
        ui.run();
    }
}
