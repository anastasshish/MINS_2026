package service;

import model.Product;
import model.ProductCategory;

import java.util.Set;

public class DefaultNeighborhoodValidator implements NeighborhoodValidator {

    private static final Set<Set<ProductCategory>> INCOMPATIBLE_PAIRS = Set.of(
            Set.of(ProductCategory.FOOD, ProductCategory.CHEMICALS)
    );

    @Override
    public boolean canStoreTogether(Product product1, Product product2) {
        Set<ProductCategory> pair = Set.of(product1.getCategory(), product2.getCategory());
        return !INCOMPATIBLE_PAIRS.contains(pair);
    }
}
