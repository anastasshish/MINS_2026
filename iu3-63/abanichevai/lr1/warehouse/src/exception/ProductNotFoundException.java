package exception;

public class ProductNotFoundException extends WarehouseException {

    public ProductNotFoundException(String productId) {
        super("Товар не найден: " + productId);
    }
}
