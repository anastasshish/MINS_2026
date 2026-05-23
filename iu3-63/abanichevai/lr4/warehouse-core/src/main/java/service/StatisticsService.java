package service;

import model.ProductCategory;

import java.util.Map;

public interface StatisticsService {

    int getTotalProducts();

    Map<ProductCategory, Integer> getProductsByCategory();
}
