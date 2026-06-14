package ru.bmstu.model;

import ru.bmstu.util.Validator;

public class Device {
    private final String type;
    private final String brand;
    private final String model;

    public Device(String type, String brand, String model) {
        Validator.requireNonBlank(type, "type");
        Validator.requireNonBlank(brand, "brand");
        Validator.requireNonBlank(model, "model");

        this.type = type;
        this.brand = brand;
        this.model = model;
    }



    public String getModel() {
        return model;
    }

    @Override
    public String toString() {
        return type + " " + brand + " " + model;
    }
}
