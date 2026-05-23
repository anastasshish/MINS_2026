import repository.CellRepository;
import repository.InMemoryCellRepository;
import repository.RepositorySeed;
import service.DefaultNeighborhoodValidator;
import service.NeighborhoodValidator;
import service.WarehouseService;
import ui.ConsoleUI;

//Подлкючить гит, в новой ветке сделать задание

public class Main {
    public static void main(String[] args) {
        CellRepository repository = new InMemoryCellRepository();
        RepositorySeed.loadSeedData(repository);
        NeighborhoodValidator validator = new DefaultNeighborhoodValidator();
        WarehouseService warehouseService = new WarehouseService(repository, validator);
        ConsoleUI ui = new ConsoleUI(warehouseService);

        System.out.println("Добро пожаловать в склад");
        ui.run();
    }
}
