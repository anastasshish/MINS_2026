package service.validation;

import exception.ValidationException;

public abstract class ValidationHandler<T> {

    private ValidationHandler<T> next;

    public ValidationHandler<T> setNext(ValidationHandler<T> next) {
        this.next = next;
        return next;
    }

    public final void handle(T input) throws ValidationException {
        validate(input);
        if (next != null) {
            next.handle(input);
        }
    }

    protected abstract void validate(T input) throws ValidationException;
}