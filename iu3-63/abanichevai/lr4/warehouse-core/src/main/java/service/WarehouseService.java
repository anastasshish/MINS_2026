package service;

import exception.InsufficientQuantityException;
import exception.NeighborhoodViolationException;
import exception.ProductNotFoundException;
import exception.ReferenceServiceUnavailableException;
import exception.ValidationException;
import grpc.ReferenceClient;
import model.Product;
import model.ProductCategory;
import model.StorageCell;
import repository.CellRepository;
import service.events.ProductAddedEvent;
import service.events.ProductRemovedEvent;
import service.events.WarehouseEventPublisher;
import service.validation.RemoveProductRequest;
import service.validation.RemoveProductValidationChain;
import service.validation.ValidationHandler;

import java.util.EnumMap;
import java.util.List;
import java.util.Map;

public class WarehouseService implements StatisticsService {

    private final CellRepository repository;
    private final ReferenceClient referenceClient;
    private final WarehouseEventPublisher eventPublisher;
    private final ValidationHandler<RemoveProductRequest> removeProductValidator;

    public WarehouseService(CellRepository repository, ReferenceClient referenceClient, WarehouseEventPublisher eventPublisher) {
        this.repository = repository;
        this.referenceClient = referenceClient;
        this.eventPublisher = eventPublisher;
        this.removeProductValidator = RemoveProductValidationChain.build();
    }

    public Product findById(String id) {
        return repository.findById(id);
    }

    public Integer getPositionByProductId(String id) {
        return repository.getPositionByProductId(id);
    }

    public void addProduct(Product product, int cellPosition)
            throws ValidationException, NeighborhoodViolationException, ReferenceServiceUnavailableException {
        referenceClient.validateAddProduct(product, cellPosition);

        int radius = referenceClient.getNeighborhoodRadius();
        List<Product> productsInRange = repository.findProductsInRange(cellPosition, radius);
        for (Product existingProduct : productsInRange) {
            if (existingProduct.getId().equals(product.getId())) {
                continue;
            }
            try {
                referenceClient.ensureCanStoreTogether(product.getCategory(), existingProduct.getCategory());
            } catch (ValidationException e) {
                throw new NeighborhoodViolationException(
                        "Товарное соседство нарушено: " + product.getCategory()
                                + " нельзя хранить в окрестности " + radius + " ячеек от " + existingProduct.getCategory());
            }
        }

        Product existingProduct = repository.findById(product.getId());
        int position = cellPosition;
        if (existingProduct != null) {
            product = existingProduct.withQuantity(existingProduct.getQuantity() + product.getQuantity());
            position = repository.getPositionByProductId(product.getId());
        }
        repository.save(position, product);
        eventPublisher.publish(new ProductAddedEvent(product, position));
    }

    public void removeProduct(String id, int amount)
            throws ValidationException, ProductNotFoundException, InsufficientQuantityException {
        removeProductValidator.handle(new RemoveProductRequest(id, amount));

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
        eventPublisher.publish(new ProductRemovedEvent(id, amount));
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
