package model;

public abstract class AbstractProduct implements Product {

    private final String id;
    private final String name;
    private int quantity;

    protected AbstractProduct(String id, String name, int quantity) {
        this.id = id;
        this.name = name;
        this.quantity = quantity;
    }

    @Override
    public String getId() {
        return id;
    }

    @Override
    public String getName() {
        return name;
    }

    @Override
    public int getQuantity() {
        return quantity;
    }
}
