package service.events;

public sealed interface WarehouseEvent permits ProductAddedEvent, ProductRemovedEvent {
}

