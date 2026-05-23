package service.commands;

import exception.WarehouseException;
import model.Product;
import repository.CellRepository;
import service.WarehouseService;

public class AddProductCommand implements WarehouseCommand {

    private final WarehouseService warehouseService;
    private final CellRepository repository;
    private final Product productToAdd;
    private final int requestedPosition;

    private Integer previousPosition;
    private Product previousProduct;

    public AddProductCommand(WarehouseService warehouseService, CellRepository repository, Product productToAdd, int requestedPosition) {
        this.warehouseService = warehouseService;
        this.repository = repository;
        this.productToAdd = productToAdd;
        this.requestedPosition = requestedPosition;
    }

    @Override
    public void execute() throws WarehouseException {
        previousProduct = warehouseService.findById(productToAdd.getId());
        previousPosition = previousProduct == null ? null : warehouseService.getPositionByProductId(productToAdd.getId());
        warehouseService.addProduct(productToAdd, requestedPosition);
    }

    @Override
    public void undo() throws WarehouseException {
        if (previousProduct == null) {
            repository.deleteByProductId(productToAdd.getId());
            return;
        }
        int position = previousPosition == null ? requestedPosition : previousPosition;
        repository.save(position, previousProduct);
    }
}

