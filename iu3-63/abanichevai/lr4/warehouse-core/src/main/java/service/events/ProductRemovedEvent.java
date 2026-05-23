package service.events;

public record ProductRemovedEvent(String productId, int amount) implements WarehouseEvent {}