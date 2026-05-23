package ui;

import service.events.ProductAddedEvent;
import service.events.ProductRemovedEvent;
import service.events.WarehouseEvent;
import service.events.WarehouseEventListener;

public class ConsoleWarehouseListener implements WarehouseEventListener {
    @Override
    public void onEvent(WarehouseEvent event) {
        if (event instanceof ProductAddedEvent added) {
            System.out.println("[Событие] Добавлен товар: " + added.product().getId() + " (+" + added.product().getQuantity() + ") в ячейку " + added.position());
            return;
        }
        if (event instanceof ProductRemovedEvent removed) {
            System.out.println("[Событие] Убран товар: " + removed.productId() + " (-" + removed.amount() + ")");
        }
    }
}

