package ru.bmstu.repository;

import ru.bmstu.model.RepairOrder;

import java.util.List;
import java.util.Optional;

public interface OrderRepository {
    void save(RepairOrder order);

    Optional<RepairOrder> findById(Long id);

    List<RepairOrder> findAll();

}