package service.events;

import model.Product;

public record ProductAddedEvent(Product product, int position) implements WarehouseEvent {
}

