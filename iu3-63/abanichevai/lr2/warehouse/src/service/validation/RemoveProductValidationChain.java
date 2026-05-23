package service.validation;

import exception.ValidationException;

public final class RemoveProductValidationChain {

    private RemoveProductValidationChain() {
    }

    public static ValidationHandler<RemoveProductRequest> build() {
        ValidationHandler<RemoveProductRequest> idValid = new ValidationHandler<>() {
            @Override
            protected void validate(RemoveProductRequest input) throws ValidationException {
                if (input == null) {
                    throw new ValidationException("Запрос обязателен");
                }
                String id = input.productId();
                if (id == null || id.trim().isEmpty()) {
                    throw new ValidationException("ID товара обязателен");
                }
            }
        };

        ValidationHandler<RemoveProductRequest> amountValid = new ValidationHandler<>() {
            @Override
            protected void validate(RemoveProductRequest input) throws ValidationException {
                if (input.amount() <= 0) {
                    throw new ValidationException("Количество должно быть положительным");
                }
            }
        };

        idValid.setNext(amountValid);
        return idValid;
    }
}

