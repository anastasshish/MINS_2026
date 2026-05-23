package model;

public class FoodProduct extends AbstractProduct {

    public FoodProduct(String id, String name, int quantity) {
        super(id, name, quantity);
    }

    @Override
    public ProductCategory getCategory() {
        return ProductCategory.FOOD;
    }

    @Override
    public Product withQuantity(int quantity) {
        return new FoodProduct(getId(), getName(), quantity);
    }
}
