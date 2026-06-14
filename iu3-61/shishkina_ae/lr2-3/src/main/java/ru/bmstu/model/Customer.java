package ru.bmstu.model;

import ru.bmstu.util.Validator;

public class Customer {
    private final Long id;
    private final String name;
    private final String phone;

    public Customer(Long id, String name, String phone) {
        Validator.requireNotNull(id, "id");
        Validator.requireNonBlank(name, "name");
        Validator.requireNonBlank(phone, "phone");

        this.id = id;
        this.name = name;
        this.phone = phone;
    }

    public Long getId() {
        return id;
    }

    public String getName() {
        return name;
    }

    public String getPhone() {
        return phone;
    }

    @Override
    public String toString() {
        return "Customer{id=" + id + ", name='" + name + "', phone='" + phone + "'}";
    }
}