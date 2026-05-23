package service.commands;

import exception.WarehouseException;
import model.Product;
import repository.CellRepository;
import service.WarehouseService;

public class RemoveProductCommand implements WarehouseCommand {

    private final WarehouseService warehouseService;
    private final CellRepository repository;
    private final String productId;
    private final int amount;

    private Integer previousPosition;
    private Product previousProduct;

    public RemoveProductCommand(WarehouseService warehouseService, CellRepository repository, String productId, int amount) {
        this.warehouseService = warehouseService;
        this.repository = repository;
        this.productId = productId;
        this.amount = amount;
    }

    @Override
    public void execute() throws WarehouseException {
        previousProduct = warehouseService.findById(productId);
        previousPosition = previousProduct == null ? null : warehouseService.getPositionByProductId(productId);
        warehouseService.removeProduct(productId, amount);
    }

    @Override
    public void undo() throws WarehouseException {
        if (previousProduct == null) {
            return;
        }
        if (previousPosition == null) {
            return;
        }
        repository.save(previousPosition, previousProduct);
    }
}

