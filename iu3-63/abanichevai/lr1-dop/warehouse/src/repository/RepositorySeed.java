package repository;

import model.ChemicalProduct;
import model.ElectronicsProduct;
import model.FoodProduct;

public final class RepositorySeed {

    private RepositorySeed() {
    }

    public static void loadSeedData(CellRepository repository) {
        repository.save(1, new FoodProduct("f1", "Молоко", 50));
        repository.save(2, new FoodProduct("f2", "Хлеб", 100));
        repository.save(10, new ElectronicsProduct("e1", "Телефон", 25));
        repository.save(20, new ChemicalProduct("c1", "Стиральный порошок", 30));
    }
}
