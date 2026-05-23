package model;

public class ChemicalProduct extends AbstractProduct {

    public ChemicalProduct(String id, String name, int quantity) {
        super(id, name, quantity);
    }

    @Override
    public ProductCategory getCategory() {
        return ProductCategory.CHEMICALS;
    }

    @Override
    public Product withQuantity(int quantity) {
        return new ChemicalProduct(getId(), getName(), quantity);
    }
}
