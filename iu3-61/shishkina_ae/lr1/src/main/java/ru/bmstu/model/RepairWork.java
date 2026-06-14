package ru.bmstu.model;

import ru.bmstu.util.Validator;

public class RepairWork {
    private final String name;
    private final double standardHours;
    private final double price;

    public RepairWork(String name, double standardHours, double price) {
        Validator.requireNonBlank(name, "name");
        Validator.requirePositive(standardHours, "standardHours");
        Validator.requireNonNegative(price, "price");

        this.name = name;
        this.standardHours = standardHours;
        this.price = price;
    }

    public String getName() {
        return name;
    }

    public double getStandardHours() {
        return standardHours;
    }

    public double getPrice() {
        return price;
    }

    @Override
    public String toString() {
        return "RepairWork{name='" + name + "', standardHours=" + standardHours + ", price=" + price + "}";
    }
}