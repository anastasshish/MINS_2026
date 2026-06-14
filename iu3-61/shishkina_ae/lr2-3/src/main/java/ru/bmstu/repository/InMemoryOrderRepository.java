package ru.bmstu.repository;

import ru.bmstu.model.RepairOrder;
import ru.bmstu.util.Validator;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Optional;

public class InMemoryOrderRepository implements OrderRepository {
    private final Map<Long, RepairOrder> orders = new HashMap<>();

    @Override
    public void save(RepairOrder order) {
        Validator.requireNotNull(order, "order");
        orders.put(order.getId(), order);
    }

    @Override
    public Optional<RepairOrder> findById(Long id) {
        Validator.requireNotNull(id, "id");
        return Optional.ofNullable(orders.get(id));
    }

    @Override
    public List<RepairOrder> findAll() {
        return new ArrayList<>(orders.values());
    }

}
