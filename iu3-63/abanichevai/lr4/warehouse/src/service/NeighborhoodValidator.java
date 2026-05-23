package service;

import model.Product;

public interface NeighborhoodValidator {
    boolean canStoreTogether(Product product1, Product product2);
}
