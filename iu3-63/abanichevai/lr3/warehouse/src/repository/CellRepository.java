package repository;

import model.Product;
import model.StorageCell;

import java.util.List;

public interface CellRepository {

    void save(int position, Product product);

    Product findAtPosition(int position);

    Product findById(String id);

    Integer getPositionByProductId(String id);

    List<Product> findAll();

    List<StorageCell> findAllCells();

    List<Product> findProductsInRange(int position, int radius);

    void deleteByProductId(String id);
}
