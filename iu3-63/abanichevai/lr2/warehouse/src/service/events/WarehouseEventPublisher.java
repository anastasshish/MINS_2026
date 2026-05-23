package service.events;

import java.util.ArrayList;
import java.util.List;

public class WarehouseEventPublisher {

    private final List<WarehouseEventListener> listeners = new ArrayList<>();

    public void register(WarehouseEventListener listener) {
        if (listener == null || listeners.contains(listener)) {
            return;
        }
        listeners.add(listener);
    }

    public void unregister(WarehouseEventListener listener) {
        listeners.remove(listener);
    }

    public void publish(WarehouseEvent event) {
        if (event == null) {
            return;
        }
        for (WarehouseEventListener listener : listeners) {
            listener.onEvent(event);
        }
    }
}

