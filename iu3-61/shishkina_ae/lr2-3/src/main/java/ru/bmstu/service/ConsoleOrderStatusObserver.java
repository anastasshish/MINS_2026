package ru.bmstu.service;

import ru.bmstu.model.OrderStatus;
import ru.bmstu.model.RepairOrder;

public class ConsoleOrderStatusObserver implements OrderStatusObserver {
    @Override
    public void onStatusChanged(RepairOrder order, OrderStatus oldStatus, OrderStatus newStatus) {
        System.out.println("[УВЕДОМЛЕНИЕ] Заказ " + order.getId() + ": " + oldStatus + " -> " + newStatus);
    }
}
