package exception;

public class InsufficientQuantityException extends WarehouseException {

    public InsufficientQuantityException(String productId, int requested, int available) {
        super(String.format("Недостаточно товара %s: запрошено %d, доступно %d", productId, requested, available));
    }
}
