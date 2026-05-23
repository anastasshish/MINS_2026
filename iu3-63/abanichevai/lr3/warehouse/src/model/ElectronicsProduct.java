package model;

public class ElectronicsProduct extends AbstractProduct {

    public ElectronicsProduct(String id, String name, int quantity) {
        super(id, name, quantity);
    }

    @Override
    public ProductCategory getCategory() {
        return ProductCategory.ELECTRONICS;
    }

    @Override
    public Product withQuantity(int quantity) {
        return new ElectronicsProduct(getId(), getName(), quantity);
    }
}
