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
        if (quantity > 100) {
            throw new IllegalArgumentException("FoodProduct quantity cannot exceed 100");
        }
        return new FoodProduct(getId(), getName(), quantity);
    }
}
