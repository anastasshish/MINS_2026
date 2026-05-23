package service.validation;

import exception.ValidationException;
import model.Product;

public final class AddProductValidationChain {

    private AddProductValidationChain() {
    }

    public static ValidationHandler<AddProductRequest> build() {
        ValidationHandler<AddProductRequest> productNotNull = new ValidationHandler<>() {
            @Override
            protected void validate(AddProductRequest input) throws ValidationException {
                if (input == null || input.product() == null) {
                    throw new ValidationException("Товар обязателен");
                }
            }
        };

        ValidationHandler<AddProductRequest> positionValid = new ValidationHandler<>() {
            @Override
            protected void validate(AddProductRequest input) throws ValidationException {
                if (input.cellPosition() < 0) {
                    throw new ValidationException("Некорректный номер ячейки");
                }
            }
        };

        ValidationHandler<AddProductRequest> idValid = new ValidationHandler<>() {
            @Override
            protected void validate(AddProductRequest input) throws ValidationException {
                String id = input.product().getId();
                if (id == null || id.trim().isEmpty()) {
                    throw new ValidationException("ID товара обязателен");
                }
            }
        };

        ValidationHandler<AddProductRequest> nameValid = new ValidationHandler<>() {
            @Override
            protected void validate(AddProductRequest input) throws ValidationException {
                String name = input.product().getName();
                if (name == null || name.trim().isEmpty()) {
                    throw new ValidationException("Название товара обязательно");
                }
            }
        };

        ValidationHandler<AddProductRequest> quantityValid = new ValidationHandler<>() {
            @Override
            protected void validate(AddProductRequest input) throws ValidationException {
                Product product = input.product();
                if (product.getQuantity() < 0) {
                    throw new ValidationException("Количество должно быть неотрицательным");
                }
            }
        };

        productNotNull.setNext(positionValid).setNext(idValid).setNext(nameValid).setNext(quantityValid);
        return productNotNull;
    }
}

