package model;

public interface Product {

    String getId();

    String getName();

    ProductCategory getCategory();

    int getQuantity();

    Product withQuantity(int quantity);
}
