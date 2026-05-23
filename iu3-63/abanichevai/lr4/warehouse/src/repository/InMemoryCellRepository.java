package repository;

import model.Product;
import model.StorageCell;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

public class InMemoryCellRepository implements CellRepository {

    private final Map<Integer, Product> positionToProduct = new HashMap<>();
    private final Map<String, Integer> productIdToPosition = new HashMap<>();

    @Override
    public void save(int position, Product product) {
        Integer oldPosition = productIdToPosition.get(product.getId());
        if (oldPosition != null && oldPosition != position) {
            positionToProduct.remove(oldPosition);
        }
        positionToProduct.put(position, product);
        productIdToPosition.put(product.getId(), position);
    }

    @Override
    public Product findAtPosition(int position) {
        return positionToProduct.get(position);
    }

    @Override
    public Product findById(String id) {
        Integer position = productIdToPosition.get(id);
        return position != null ? positionToProduct.get(position) : null;
    }

    @Override
    public Integer getPositionByProductId(String id) {
        return productIdToPosition.get(id);
    }

    @Override
    public List<Product> findAll() {
        return new ArrayList<>(positionToProduct.values());
    }

    @Override
    public List<StorageCell> findAllCells() {
        return positionToProduct.entrySet().stream()
                .map(e -> new StorageCell(e.getKey(), e.getValue()))
                .sorted((a, b) -> Integer.compare(a.position(), b.position()))
                .toList();
    }

    @Override
    public List<Product> findProductsInRange(int position, int radius) {
        List<Product> result = new ArrayList<>();
        for (int p = position - radius; p <= position + radius; p++) {
            Product product = positionToProduct.get(p);
            if (product != null) {
                result.add(product);
            }
        }
        return result;
    }

    @Override
    public void deleteByProductId(String id) {
        Integer position = productIdToPosition.remove(id);
        if (position != null) {
            positionToProduct.remove(position);
        }
    }
}
