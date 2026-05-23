package model;

import java.util.function.Function;

public enum ProductCategory {
    FOOD("Продукты питания", (args) -> new FoodProduct(args[0], args[1], Integer.parseInt(args[2]))),
    CHEMICALS("Химия", (args) -> new ChemicalProduct(args[0], args[1], Integer.parseInt(args[2]))),
    ELECTRONICS("Электроника", (args) -> new ElectronicsProduct(args[0], args[1], Integer.parseInt(args[2])));

    private final String displayName;
    private final Function<String[], Product> factory;

    ProductCategory(String displayName, Function<String[], Product> factory) {
        this.displayName = displayName;
        this.factory = factory;
    }

    public String getDisplayName() {
        return displayName;
    }

    public Product createProduct(String id, String name, int quantity) {
        return factory.apply(new String[]{id, name, String.valueOf(quantity)});
    }
}
