package service.events;

public interface WarehouseEventListener {
    void onEvent(WarehouseEvent event);
}