package service;

import exception.InsufficientQuantityException;
import exception.NeighborhoodViolationException;
import exception.ProductNotFoundException;
import model.Product;
import model.ProductCategory;
import model.StorageCell;
import repository.CellRepository;

import java.util.EnumMap;
import java.util.List;
import java.util.Map;

public class WarehouseService implements StatisticsService {

    private static final int NEIGHBORHOOD_RADIUS = 5;

    private final CellRepository repository;
    private final NeighborhoodValidator validator;

    public WarehouseService(CellRepository repository, NeighborhoodValidator validator) {
        this.repository = repository;
        this.validator = validator;
    }

    public void addProduct(Product product, int cellPosition) throws NeighborhoodViolationException {
        List<Product> productsInRange = repository.findProductsInRange(cellPosition, NEIGHBORHOOD_RADIUS);
        for (Product existingProduct : productsInRange) {
            if (existingProduct.getId().equals(product.getId())) {
                continue;
            }
            if (!validator.canStoreTogether(product, existingProduct)) {
                throw new NeighborhoodViolationException(
                        "Товарное соседство нарушено: " + product.getCategory() + " нельзя хранить в окрестности " + NEIGHBORHOOD_RADIUS + " ячеек от " + existingProduct.getCategory());
            }
        }
        Product existingProduct = repository.findById(product.getId());
        int position = cellPosition;
        if (existingProduct != null) {
            product = existingProduct.withQuantity(existingProduct.getQuantity() + product.getQuantity());
            position = repository.getPositionByProductId(product.getId());
        }
        repository.save(position, product);
    }

    public void removeProduct(String id, int amount) throws ProductNotFoundException, InsufficientQuantityException {
        Product product = repository.findById(id);
        if (product == null) {
            throw new ProductNotFoundException(id);
        }
        if (product.getQuantity() < amount) {
            throw new InsufficientQuantityException(id, amount, product.getQuantity());
        }
        int newQuantity = product.getQuantity() - amount;
        int position = repository.getPositionByProductId(id);
        if (newQuantity == 0) {
            repository.deleteByProductId(id);
        } else {
            repository.save(position, product.withQuantity(newQuantity));
        }
    }

    public List<StorageCell> getAllCells() {
        return repository.findAllCells();
    }

    @Override
    public int getTotalProducts() {
        return repository.findAll().stream()
                .mapToInt(Product::getQuantity)
                .sum();
    }

    @Override
    public Map<ProductCategory, Integer> getProductsByCategory() {
        Map<ProductCategory, Integer> stats = new EnumMap<>(ProductCategory.class);
        for (ProductCategory category : ProductCategory.values()) {
            stats.put(category, 0);
        }
        for (Product product : repository.findAll()) {
            stats.merge(product.getCategory(), product.getQuantity(), Integer::sum);
        }
        return stats;
    }
}
