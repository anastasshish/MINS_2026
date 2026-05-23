package service.validation;

import model.Product;

public record AddProductRequest(Product product, int cellPosition) {
}

